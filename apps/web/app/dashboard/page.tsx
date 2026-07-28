"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { BackupReminderCard } from "@/components/BackupReminderCard";
import { DashboardQuickActions } from "@/components/DashboardQuickActions";
import {
  DashboardRecentSessions,
  type DashboardRecentSessionItem,
} from "@/components/DashboardRecentSessions";
import { DashboardTodayCard } from "@/components/DashboardTodayCard";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { DashboardShell } from "@/components/ui/DashboardShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  ApiError,
  getCashSessionByDate,
  getCashSessionSummary,
  getCurrentUser,
  listCashSessions,
} from "@/lib/api";
import { getToken, removeToken, saveUser } from "@/lib/auth";
import type { CurrentUser } from "@/types/auth";
import type { CashSession } from "@/types/cashSession";
import type { CashSessionSummary } from "@/types/summary";

type TodayDashboardData = {
  cashSession: CashSession;
  summary: CashSessionSummary;
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [todayData, setTodayData] = useState<TodayDashboardData | null>(null);
  const [recentSessions, setRecentSessions] = useState<
    DashboardRecentSessionItem[]
  >([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    loadDashboard(token);
  }, [router]);

  async function loadDashboard(activeToken: string) {
    setIsLoading(true);
    setError("");

    try {
      const todayDate = getTodayISODate();
      const [currentUser, loadedTodayData, loadedCashSessions] =
        await Promise.all([
          getCurrentUser(activeToken),
          loadTodayCashSession(activeToken, todayDate),
          listCashSessions(activeToken),
        ]);
      const loadedRecentSessions = await loadRecentSessions(
        activeToken,
        getRecentCashSessions(loadedCashSessions),
        loadedTodayData,
      );

      setUser(currentUser);
      saveUser(currentUser);
      setTodayData(loadedTodayData);
      setRecentSessions(loadedRecentSessions);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadTodayCashSession(
    activeToken: string,
    todayDate: string,
  ): Promise<TodayDashboardData | null> {
    try {
      const cashSession = await getCashSessionByDate(activeToken, todayDate);
      const summary = await getCashSessionSummary(activeToken, cashSession.id);

      return { cashSession, summary };
    } catch (loadError) {
      if (loadError instanceof ApiError && loadError.status === 404) {
        return null;
      }

      throw loadError;
    }
  }

  async function loadRecentSessions(
    activeToken: string,
    cashSessions: CashSession[],
    loadedTodayData: TodayDashboardData | null,
  ): Promise<DashboardRecentSessionItem[]> {
    return Promise.all(
      cashSessions.map(async (cashSession) => {
        if (loadedTodayData?.cashSession.id === cashSession.id) {
          return {
            cashSession,
            summary: loadedTodayData.summary,
          };
        }

        return {
          cashSession,
          summary: await getCashSessionSummary(activeToken, cashSession.id),
        };
      }),
    );
  }

  function redirectIfUnauthorized(possibleError: unknown): boolean {
    if (
      possibleError instanceof ApiError &&
          possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return true;
    }

    return false;
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6">
        <div className="mx-auto w-full max-w-6xl">
          <LoadingState label="Cargando dashboard..." />
        </div>
      </main>
    );
  }

  if (!user && !error) {
    return null;
  }

  return (
    <DashboardShell
      activeHref="/dashboard"
      alertsHref="#alertas"
      dateLabel={formatTopbarDate(new Date())}
      moduleHref="#modulos"
      roleLabel={
        user?.role === "admin_auditor"
          ? "Administrador / auditor"
          : "Operador"
      }
      userName={user?.username}
    >
      <div className="mx-auto flex w-full max-w-screen-2xl flex-col gap-8 px-4 py-7 sm:px-6 sm:py-9 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description="Consulta el estado de caja, retoma las tareas frecuentes y accede a cada área del ERP desde un solo lugar."
          eyebrow="Panel operativo"
          meta={
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge
                label={
                  user?.role === "admin_auditor"
                    ? "Acceso administrador"
                    : "Acceso operador"
                }
                tone="info"
              />
              <span className="text-sm text-slate-500">
                {formatLongDate(new Date())}
              </span>
            </div>
          }
          title={`Buen día, ${user?.username ?? "equipo"}`}
        />

        {error ? <ErrorMessage message={error} /> : null}

        {!error ? (
          <>
            <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(280px,0.8fr)]">
              <DashboardTodayCard
                cashSession={todayData?.cashSession ?? null}
                summary={todayData?.summary ?? null}
              />
              <BackupReminderCard />
            </div>
            <DashboardQuickActions role={user?.role} />
            <DashboardRecentSessions items={recentSessions} />
          </>
        ) : null}
      </div>
    </DashboardShell>
  );
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function getRecentCashSessions(cashSessions: CashSession[]): CashSession[] {
  return [...cashSessions].sort(compareCashSessionDesc).slice(0, 5);
}

function compareCashSessionDesc(
  first: CashSession,
  second: CashSession,
): number {
  const dateComparison = second.session_date.localeCompare(first.session_date);
  if (dateComparison !== 0) {
    return dateComparison;
  }

  return second.id - first.id;
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }

  return "No se pudo cargar el panel operativo.";
}

function formatTopbarDate(value: Date): string {
  return new Intl.DateTimeFormat("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(value);
}

function formatLongDate(value: Date): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "full",
  }).format(value);
}

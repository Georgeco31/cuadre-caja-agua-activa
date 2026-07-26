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
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-water-700">Agua Activa</p>
            <h1 className="mt-1 text-2xl font-semibold text-slate-950">
              Panel operativo de caja
            </h1>
            {user ? (
              <p className="mt-2 text-sm text-slate-600">
                Bienvenido, {user.username} ·{" "}
                {user.role === "admin_auditor"
                  ? "Administrador / auditor"
                  : "Operador"}
              </p>
            ) : null}
          </div>
          <LogoutButton />
        </header>

        {error ? <ErrorMessage message={error} /> : null}

        {!error ? (
          <>
            <DashboardTodayCard
              cashSession={todayData?.cashSession ?? null}
              summary={todayData?.summary ?? null}
            />
            <DashboardQuickActions role={user?.role} />
            <DashboardRecentSessions items={recentSessions} />
            <BackupReminderCard />
          </>
        ) : null}
      </div>
    </main>
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

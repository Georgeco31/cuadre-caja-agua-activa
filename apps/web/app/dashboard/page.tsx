"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { BackupReminderCard } from "@/components/BackupReminderCard";
import {
  DashboardAlertPanel,
  type DashboardAlertItem,
} from "@/components/DashboardAlertPanel";
import {
  DashboardKpiGrid,
  type DashboardKpiItem,
} from "@/components/DashboardKpiGrid";
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

  const dashboardKpis = getDashboardKpis(todayData?.summary ?? null);
  const dashboardAlerts = getDashboardAlerts(todayData);

  return (
    <DashboardShell
      activeHref="/dashboard"
      alertsHref="#alertas"
      dateLabel={formatTopbarDate(new Date())}
      moduleHref="#modulos"
      role={user?.role}
      roleLabel={
        user
          ? user.role === "admin_auditor"
            ? "Administrador / auditor"
            : "Operador"
          : undefined
      }
      userName={user?.username}
    >
      <div className="mx-auto flex w-full min-w-0 max-w-screen-2xl flex-col gap-8 px-4 py-7 sm:px-6 sm:py-9 xl:gap-10 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description={
            user?.role === "admin_auditor"
              ? "Gestiona caja, ventas, rutas, producción y reportes desde un solo lugar."
              : "Gestiona las tareas operativas asignadas del día."
          }
          eyebrow="Agua Activa ERP"
          meta={
            <div className="flex flex-wrap items-center gap-2">
              {user ? (
                <StatusBadge
                  label={
                    user.role === "admin_auditor"
                      ? "Acceso administrador"
                      : "Acceso operador"
                  }
                  tone="info"
                />
              ) : null}
              <span className="text-sm text-slate-500">
                {formatLongDate(new Date())}
              </span>
            </div>
          }
          title="Panel operativo"
        />

        {error ? (
          <section
            aria-label="Alerta de carga del dashboard"
            className="scroll-mt-24"
            id="alertas"
          >
            <ErrorMessage message={error} />
          </section>
        ) : null}

        {!error ? (
          <>
            <DashboardKpiGrid items={dashboardKpis} />

            <div className="grid min-w-0 items-start gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(320px,0.75fr)]">
              <DashboardTodayCard
                cashSession={todayData?.cashSession ?? null}
                summary={todayData?.summary ?? null}
              />
              <DashboardAlertPanel alerts={dashboardAlerts}>
                <BackupReminderCard />
              </DashboardAlertPanel>
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

function getDashboardKpis(
  summary: CashSessionSummary | null,
): DashboardKpiItem[] {
  if (!summary) {
    return [];
  }

  return [
    {
      icon: "TC",
      label: "Total contado",
      value: formatMoney(summary.total_counted),
    },
    {
      icon: "GA",
      label: "Gastos antes",
      value: formatMoney(summary.total_pre_count_expenses),
    },
    {
      icon: "GD",
      label: "Gastos después",
      value: formatMoney(summary.total_post_count_expenses),
    },
    {
      hint: "Resultado oficial",
      icon: "TF",
      label: "Total final",
      tone: "water",
      value: formatMoney(summary.final_total),
    },
  ];
}

function getDashboardAlerts(
  todayData: TodayDashboardData | null,
): DashboardAlertItem[] {
  if (todayData) {
    return [];
  }

  return [
    {
      description:
        "No existe una sesión de caja para la fecha de hoy. Puedes registrarla desde el bloque principal.",
      id: "cash-session-pending",
      title: "Cuadre pendiente",
      tone: "warning",
    },
  ];
}

function formatMoney(value: string): string {
  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) {
    return `$${value}`;
  }

  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(numberValue);
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

"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { DailySummaryAlerts } from "@/components/DailySummaryAlerts";
import { DailySummaryCards } from "@/components/DailySummaryCards";
import { DailySummaryDetails } from "@/components/DailySummaryDetails";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { DashboardShell } from "@/components/ui/DashboardShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { ReportSection } from "@/components/ui/ReportSection";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ApiError, getDailyOperationalSummary } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { DailyOperationalSummary } from "@/types/dailyOperationalSummary";

const quickLinks = [
  ["/dashboard/cash-session", "Cuadre de caja"],
  ["/dashboard/production", "Producción"],
  ["/dashboard/route-loads", "Carga de camión"],
  ["/dashboard/route-returns", "Retorno de ruta"],
  ["/dashboard/route-closures", "Cierre de ruta"],
  ["/dashboard/route-cash-receipts", "Dinero de ruta en caja"],
  ["/dashboard/route-cash-comparison", "Rutas vs caja"],
  ["/dashboard/sales/cash", "Ventas de contado"],
  ["/dashboard/sales/credit", "Ventas a crédito"],
  ["/dashboard/receivables", "Cobros"],
] as const;

export default function DailySummaryPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState(() => getTodayISODate());
  const [report, setReport] = useState<DailyOperationalSummary | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    const today = getTodayISODate();
    setToken(storedToken);
    setSelectedDate(today);
    loadReport(storedToken, today);
  }, [router]);

  async function loadReport(activeToken: string, reportDate: string) {
    setIsLoading(true);
    setError("");

    try {
      const loadedReport = await getDailyOperationalSummary(
        activeToken,
        reportDate,
      );
      setReport(loadedReport);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setReport(null);
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (token && selectedDate) {
      loadReport(token, selectedDate);
    }
  }

  function handleToday() {
    if (!token) {
      return;
    }
    const today = getTodayISODate();
    setSelectedDate(today);
    loadReport(token, today);
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

  return (
    <DashboardShell
      activeHref="/dashboard/reports"
      dateLabel={formatTopbarDate(new Date())}
    >
      <div className="mx-auto flex w-full min-w-0 max-w-screen-2xl flex-col gap-7 px-4 py-7 sm:px-6 sm:py-9 xl:gap-9 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description="Consulta en una sola vista la caja, producción, rutas, ventas, cobros y alertas del día. Este reporte no modifica información."
          eyebrow="Reportes y control"
          meta={
            <div className="flex flex-wrap items-center gap-3">
              <StatusBadge label="Solo lectura" tone="success" />
              <Link
                className="inline-flex min-h-10 items-center text-sm font-semibold text-water-700 hover:text-water-600"
                href="/dashboard"
              >
                ← Volver al dashboard
              </Link>
            </div>
          }
          title="Resumen operativo diario"
        />

        <form
          className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:p-5"
          onSubmit={handleSubmit}
        >
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
              Período
            </p>
            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Selecciona la fecha de consulta
            </h2>
          </div>
          <div className="mt-4 grid min-w-0 gap-3 sm:grid-cols-[minmax(180px,260px)_auto_auto] sm:items-end">
            <label className="block min-w-0">
              <span className="text-sm font-semibold text-slate-800">
                Fecha del resumen
              </span>
              <input
                className="mt-2 h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
                disabled={isLoading}
                onChange={(event) => setSelectedDate(event.target.value)}
                required
                type="date"
                value={selectedDate}
              />
            </label>
            <button
              className="min-h-11 rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
              disabled={isLoading || !selectedDate}
              type="submit"
            >
              Consultar resumen
            </button>
            <button
              className="min-h-11 rounded-xl border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
              disabled={isLoading}
              onClick={handleToday}
              type="button"
            >
              Volver a hoy
            </button>
          </div>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Consultando operación del día..." />
        ) : report ? (
          <>
            <div className="flex flex-col gap-2 rounded-2xl border border-water-100 bg-water-50 px-4 py-3 text-sm text-water-900 sm:flex-row sm:items-center sm:justify-between sm:px-5">
              <span>
                Mostrando información del{" "}
                <strong className="font-semibold">
                  {formatReportDate(report.date)}
                </strong>
                .
              </span>
              <span className="text-xs font-medium text-water-700">
                Información consolidada del día
              </span>
            </div>
            <DailySummaryAlerts alerts={report.alerts} />
            <DailySummaryCards report={report} />
            <DailySummaryDetails report={report} />
            <QuickLinks />
          </>
        ) : null}
      </div>
    </DashboardShell>
  );
}

function QuickLinks() {
  return (
    <ReportSection
      description="Abre el módulo relacionado cuando necesites revisar el origen de un dato."
      eyebrow="Navegación"
      id="daily-quick-links-title"
      title="Accesos relacionados"
    >
      <div className="grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {quickLinks.map(([href, label]) => (
            <Link
              className="flex min-h-16 min-w-0 items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-800 shadow-card transition hover:border-water-200 hover:text-water-700 hover:shadow-md"
              href={href}
              key={href}
            >
              <span>{label}</span>
              <span aria-hidden="true" className="text-water-600">
                →
              </span>
            </Link>
          ))}
      </div>
    </ReportSection>
  );
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function formatReportDate(value: string): string {
  const [year, month, day] = value.split("-");
  if (!year || !month || !day) {
    return value;
  }
  return `${day}/${month}/${year}`;
}

function formatTopbarDate(value: Date): string {
  return new Intl.DateTimeFormat("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(value);
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo cargar el resumen operativo diario.";
}

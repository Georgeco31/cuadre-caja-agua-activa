"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { MonthlySummaryAlerts } from "@/components/MonthlySummaryAlerts";
import { MonthlySummaryCards } from "@/components/MonthlySummaryCards";
import { MonthlySummaryDetails } from "@/components/MonthlySummaryDetails";
import { DashboardShell } from "@/components/ui/DashboardShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  ApiError,
  downloadFile,
  getMonthlyOperationalSummary,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { MonthlyOperationalSummary } from "@/types/monthlyOperationalSummary";

export default function MonthlySummaryPage() {
  const canExport = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState(() =>
    getCurrentMonthValue(),
  );
  const [report, setReport] = useState<MonthlyOperationalSummary | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [exportingFormat, setExportingFormat] = useState<
    "xlsx" | "pdf" | null
  >(null);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    const currentMonth = getCurrentMonthValue();
    setToken(storedToken);
    setSelectedMonth(currentMonth);
    loadReport(storedToken, currentMonth);
  }, [router]);

  async function loadReport(activeToken: string, periodValue: string) {
    const period = parseMonthValue(periodValue);
    if (!period) {
      setError("Selecciona un mes válido.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const loadedReport = await getMonthlyOperationalSummary(
        activeToken,
        period.year,
        period.month,
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
    if (token && selectedMonth) {
      loadReport(token, selectedMonth);
    }
  }

  function handleCurrentMonth() {
    if (!token) {
      return;
    }
    const currentMonth = getCurrentMonthValue();
    setSelectedMonth(currentMonth);
    loadReport(token, currentMonth);
  }

  async function handleExport(format: "xlsx" | "pdf") {
    if (!token) {
      return;
    }
    const period = parseMonthValue(selectedMonth);
    if (!period) {
      setError("Selecciona un mes válido.");
      return;
    }

    setExportingFormat(format);
    setError("");
    try {
      await downloadFile(
        token,
        `/reports/exports/monthly-summary.${format}?year=${period.year}&month=${period.month}`,
        `resumen-mensual-${selectedMonth}.${format}`,
      );
    } catch (exportError) {
      if (redirectIfUnauthorized(exportError)) {
        return;
      }
      setError(getErrorMessage(exportError));
    } finally {
      setExportingFormat(null);
    }
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
      roleLabel={canExport ? "Administrador / auditor" : "Operador"}
    >
      <div className="mx-auto flex w-full min-w-0 max-w-screen-2xl flex-col gap-7 px-4 py-7 sm:px-6 sm:py-9 xl:gap-9 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description="Revisa caja, producción, ventas, cobros, rutas y alertas de todo el mes. Esta pantalla es de consulta y no modifica información."
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
          title="Reporte mensual operativo"
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
              Selecciona el mes y el formato
            </h2>
          </div>
          <div className="mt-4 grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(190px,260px)_auto_auto_auto_auto] xl:items-end">
            <label className="block min-w-0">
              <span className="text-sm font-semibold text-slate-800">
                Mes del reporte
              </span>
              <input
                className="mt-2 h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
                disabled={isLoading}
                onChange={(event) => setSelectedMonth(event.target.value)}
                required
                type="month"
                value={selectedMonth}
              />
            </label>
            {canExport ? (
              <button
                className="min-h-11 rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
                disabled={isLoading || !selectedMonth}
                type="submit"
              >
                Consultar reporte
              </button>
            ) : null}
            {canExport ? (
              <button
                className="min-h-11 rounded-xl border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
                disabled={isLoading}
                onClick={handleCurrentMonth}
                type="button"
              >
                Mes actual
              </button>
            ) : null}
            <button
              className="min-h-11 rounded-xl border border-water-200 bg-water-50 px-5 text-sm font-semibold text-water-800 transition hover:border-water-500 hover:bg-water-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-100 disabled:text-slate-400"
              disabled={isLoading || exportingFormat !== null || !selectedMonth}
              onClick={() => handleExport("xlsx")}
              type="button"
            >
              {exportingFormat === "xlsx" ? "Exportando..." : "Exportar Excel"}
            </button>
            <button
              className="min-h-11 rounded-xl border border-slate-300 bg-slate-50 px-5 text-sm font-semibold text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400"
              disabled={isLoading || exportingFormat !== null || !selectedMonth}
              onClick={() => handleExport("pdf")}
              type="button"
            >
              {exportingFormat === "pdf" ? "Exportando..." : "Exportar PDF"}
            </button>
          </div>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Consultando operación del mes..." />
        ) : report ? (
          <>
            <div className="flex flex-col gap-2 rounded-2xl border border-water-100 bg-water-50 px-4 py-3 text-sm text-water-900 sm:flex-row sm:items-center sm:justify-between sm:px-5">
              <span>
                Mostrando información de{" "}
                <strong className="font-semibold">
                  {formatPeriod(report.period.year, report.period.month)}
                </strong>
                .
              </span>
              <span className="text-xs font-medium text-water-700">
                {report.period.days_in_month} días incluidos
              </span>
            </div>
            <MonthlySummaryAlerts summary={report.alerts_summary} />
            <MonthlySummaryCards report={report} />
            <MonthlySummaryDetails report={report} />
          </>
        ) : null}
      </div>
    </DashboardShell>
  );
}

function getCurrentMonthValue(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 7);
}

function parseMonthValue(
  value: string,
): { year: number; month: number } | null {
  const match = /^(\d{4})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (!Number.isInteger(year) || month < 1 || month > 12) {
    return null;
  }
  return { year, month };
}

function formatPeriod(year: number, month: number): string {
  return new Intl.DateTimeFormat("es-EC", {
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, 1));
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
  return "No se pudo cargar el reporte mensual operativo.";
}

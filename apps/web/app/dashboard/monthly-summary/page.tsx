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
import {
  ApiError,
  downloadFile,
  getMonthlyOperationalSummary,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { MonthlyOperationalSummary } from "@/types/monthlyOperationalSummary";

export default function MonthlySummaryPage() {
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
      (possibleError.status === 401 || possibleError.status === 403)
    ) {
      removeToken();
      router.replace("/login");
      return true;
    }
    return false;
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-7 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Reporte mensual operativo
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Revisa caja, producción, ventas, cobros, rutas y alertas de todo
              el mes. Esta pantalla es de consulta y no modifica información.
            </p>
          </div>
          <LogoutButton />
        </header>

        <form
          className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-2 xl:grid-cols-[minmax(190px,260px)_auto_auto_auto_auto] xl:items-end"
          onSubmit={handleSubmit}
        >
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Mes del reporte
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              disabled={isLoading}
              onChange={(event) => setSelectedMonth(event.target.value)}
              required
              type="month"
              value={selectedMonth}
            />
          </label>
          <button
            className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={isLoading || !selectedMonth}
            type="submit"
          >
            Consultar reporte
          </button>
          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
            disabled={isLoading}
            onClick={handleCurrentMonth}
            type="button"
          >
            Mes actual
          </button>
          <button
            className="h-10 rounded-md border border-emerald-600 bg-emerald-50 px-4 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-100 disabled:text-slate-400"
            disabled={isLoading || exportingFormat !== null || !selectedMonth}
            onClick={() => handleExport("xlsx")}
            type="button"
          >
            {exportingFormat === "xlsx" ? "Exportando..." : "Exportar Excel"}
          </button>
          <button
            className="h-10 rounded-md border border-slate-700 bg-slate-50 px-4 text-sm font-semibold text-slate-800 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-100 disabled:text-slate-400"
            disabled={isLoading || exportingFormat !== null || !selectedMonth}
            onClick={() => handleExport("pdf")}
            type="button"
          >
            {exportingFormat === "pdf" ? "Exportando..." : "Exportar PDF"}
          </button>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Consultando operación del mes..." />
        ) : report ? (
          <>
            <p className="text-sm text-slate-600">
              Mostrando información de{" "}
              <span className="font-semibold text-slate-900">
                {formatPeriod(report.period.year, report.period.month)}
              </span>
              .
            </p>
            <MonthlySummaryAlerts summary={report.alerts_summary} />
            <MonthlySummaryCards report={report} />
            <MonthlySummaryDetails report={report} />
          </>
        ) : null}
      </div>
    </main>
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

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo cargar el reporte mensual operativo.";
}

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
              Resumen operativo diario
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Consulta en una sola vista la caja, producción, rutas, ventas,
              cobros y alertas del día. Este reporte no modifica información.
            </p>
          </div>
          <LogoutButton />
        </header>

        <form
          className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(180px,240px)_auto_auto] sm:items-end"
          onSubmit={handleSubmit}
        >
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha del resumen
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              disabled={isLoading}
              onChange={(event) => setSelectedDate(event.target.value)}
              required
              type="date"
              value={selectedDate}
            />
          </label>
          <button
            className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={isLoading || !selectedDate}
            type="submit"
          >
            Consultar resumen
          </button>
          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
            disabled={isLoading}
            onClick={handleToday}
            type="button"
          >
            Volver a hoy
          </button>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Consultando operación del día..." />
        ) : report ? (
          <>
            <p className="text-sm text-slate-600">
              Mostrando información del{" "}
              <span className="font-semibold text-slate-900">
                {formatReportDate(report.date)}
              </span>
              .
            </p>
            <DailySummaryAlerts alerts={report.alerts} />
            <DailySummaryCards report={report} />
            <DailySummaryDetails report={report} />
            <QuickLinks />
          </>
        ) : null}
      </div>
    </main>
  );
}

function QuickLinks() {
  return (
    <section aria-labelledby="daily-quick-links-title" className="space-y-3">
      <div>
        <p className="text-sm font-medium text-water-700">Navegación</p>
        <h2
          className="mt-1 text-xl font-semibold text-slate-950"
          id="daily-quick-links-title"
        >
          Accesos rápidos
        </h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {quickLinks.map(([href, label]) => (
          <Link
            className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-800 shadow-sm transition hover:border-water-500 hover:text-water-700"
            href={href}
            key={href}
          >
            {label}
          </Link>
        ))}
      </div>
    </section>
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

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo cargar el resumen operativo diario.";
}

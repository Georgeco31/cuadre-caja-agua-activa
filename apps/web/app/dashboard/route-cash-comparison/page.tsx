"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { RouteCashComparisonTable } from "@/components/RouteCashComparisonTable";
import { ApiError, getRouteCashComparisonReport } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type {
  RouteCashComparisonFilters,
  RouteCashComparisonReport,
} from "@/types/routeCashComparison";

export default function RouteCashComparisonPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [filters, setFilters] = useState<RouteCashComparisonFilters>(() =>
    getTodayFilters(),
  );
  const [report, setReport] = useState<RouteCashComparisonReport | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    const initialFilters = getTodayFilters();
    setToken(storedToken);
    setFilters(initialFilters);
    loadReport(storedToken, initialFilters);
  }, [router]);

  async function loadReport(
    activeToken: string,
    activeFilters: RouteCashComparisonFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedReport = await getRouteCashComparisonReport(
        activeToken,
        activeFilters,
      );
      setReport(loadedReport);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (token) {
      loadReport(token, filters);
    }
  }

  function handleReset() {
    if (!token) {
      return;
    }
    const todayFilters = getTodayFilters();
    setFilters(todayFilters);
    loadReport(token, todayFilters);
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
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Comparación rutas vs caja
            </h1>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-water-100 bg-water-50 px-4 py-3 text-sm leading-6 text-water-800">
          Compara el efectivo entregado por rutas cerradas contra el dinero
          contado en caja. Esta comparación no modifica caja y no representa
          automáticamente un faltante, porque caja puede incluir otros
          ingresos.
        </p>

        <form
          className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(160px,220px)_minmax(160px,220px)_auto_auto] sm:items-end"
          onSubmit={handleSubmit}
        >
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha desde
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              disabled={isLoading}
              onChange={(event) =>
                setFilters({ ...filters, date_from: event.target.value })
              }
              type="date"
              value={filters.date_from ?? ""}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha hasta
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              disabled={isLoading}
              onChange={(event) =>
                setFilters({ ...filters, date_to: event.target.value })
              }
              type="date"
              value={filters.date_to ?? ""}
            />
          </label>

          <button
            className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={isLoading}
            type="submit"
          >
            Consultar reporte
          </button>

          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
            disabled={isLoading}
            onClick={handleReset}
            type="button"
          >
            Volver a hoy
          </button>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Consultando rutas y caja..." />
        ) : report ? (
          <RouteCashComparisonTable report={report} />
        ) : null}
      </div>
    </main>
  );
}

function getTodayFilters(): RouteCashComparisonFilters {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  const today = localDate.toISOString().slice(0, 10);
  return { date_from: today, date_to: today };
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo cargar la comparación entre rutas y caja.";
}

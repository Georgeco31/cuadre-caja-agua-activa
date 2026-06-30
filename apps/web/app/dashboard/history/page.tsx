"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CashSessionHistoryTable } from "@/components/CashSessionHistoryTable";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { ApiError, listCashSessions } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { CashSession, CashSessionStatus } from "@/types/cashSession";

export default function CashSessionHistoryPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [cashSessions, setCashSessions] = useState<CashSession[]>([]);
  const [dateFilter, setDateFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<CashSessionStatus | "">("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadCashSessions(storedToken);
  }, [router]);

  async function loadCashSessions(
    activeToken: string,
    filters: { date?: string; status?: CashSessionStatus | "" } = {},
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedCashSessions = await listCashSessions(activeToken, {
        ...(filters.date
          ? { date_from: filters.date, date_to: filters.date }
          : {}),
        ...(filters.status ? { status: filters.status } : {}),
      });
      setCashSessions(loadedCashSessions);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleFilterSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    loadCashSessions(token, {
      date: dateFilter,
      status: statusFilter,
    });
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }

    setDateFilter("");
    setStatusFilter("");
    loadCashSessions(token);
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
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Historial de cuadres
            </h1>
          </div>
          <LogoutButton />
        </header>

        <form
          className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[180px_180px_auto_auto] sm:items-end"
          onSubmit={handleFilterSubmit}
        >
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Fecha</span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              type="date"
              value={dateFilter}
              onChange={(event) => setDateFilter(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Estado</span>
            <select
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value as CashSessionStatus | "")
              }
            >
              <option value="">Todos</option>
              <option value="open">open</option>
              <option value="closed">closed</option>
            </select>
          </label>

          <button
            className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            type="submit"
            disabled={isLoading}
          >
            Filtrar
          </button>

          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
            type="button"
            onClick={handleClearFilters}
            disabled={isLoading}
          >
            Limpiar
          </button>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando historial..." />
        ) : (
          <CashSessionHistoryTable cashSessions={cashSessions} />
        )}
      </div>
    </main>
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }

  return "No se pudo completar la solicitud.";
}

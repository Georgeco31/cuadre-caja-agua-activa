"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  CashSessionHistoryFilters,
  type CashSessionHistoryFilterValues,
} from "@/components/CashSessionHistoryFilters";
import { CashSessionHistoryTable } from "@/components/CashSessionHistoryTable";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { ApiError, listCashSessions } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { CashSession } from "@/types/cashSession";

const emptyFilters: CashSessionHistoryFilterValues = {
  dateFrom: "",
  dateTo: "",
  status: "",
};

export default function CashSessionHistoryPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [cashSessions, setCashSessions] = useState<CashSession[]>([]);
  const [filters, setFilters] =
    useState<CashSessionHistoryFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<CashSessionHistoryFilterValues>(emptyFilters);
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
    activeFilters: CashSessionHistoryFilterValues = emptyFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedCashSessions = await listCashSessions(activeToken, {
        ...(activeFilters.dateFrom
          ? { date_from: activeFilters.dateFrom }
          : {}),
        ...(activeFilters.dateTo ? { date_to: activeFilters.dateTo } : {}),
        ...(activeFilters.status ? { status: activeFilters.status } : {}),
      });
      setCashSessions(sortCashSessionsDesc(loadedCashSessions));
      setAppliedFilters(activeFilters);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleFilterSubmit() {
    if (!token) {
      return;
    }

    if (filters.dateFrom && filters.dateTo && filters.dateFrom > filters.dateTo) {
      setError("La fecha desde no puede ser posterior a la fecha hasta.");
      return;
    }

    loadCashSessions(token, filters);
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }

    setFilters(emptyFilters);
    loadCashSessions(token, emptyFilters);
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

        <CashSessionHistoryFilters
          filters={filters}
          disabled={isLoading}
          onChange={setFilters}
          onSubmit={handleFilterSubmit}
          onClear={handleClearFilters}
        />

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando historial..." />
        ) : (
          <CashSessionHistoryTable
            cashSessions={cashSessions}
            hasActiveFilters={hasActiveFilters(appliedFilters)}
          />
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

function hasActiveFilters(filters: CashSessionHistoryFilterValues): boolean {
  return Boolean(filters.dateFrom || filters.dateTo || filters.status);
}

function sortCashSessionsDesc(cashSessions: CashSession[]): CashSession[] {
  return [...cashSessions].sort((first, second) => {
    const dateComparison = second.session_date.localeCompare(first.session_date);
    if (dateComparison !== 0) {
      return dateComparison;
    }

    return second.id - first.id;
  });
}

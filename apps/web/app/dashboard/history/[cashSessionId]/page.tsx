"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { CashSessionDetailCard } from "@/components/CashSessionDetailCard";
import { CountItemsList } from "@/components/CountItemsList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { ExpenseList } from "@/components/ExpenseList";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { SummaryCard } from "@/components/SummaryCard";
import {
  ApiError,
  getCashSession,
  getCashSessionSummary,
  listCashCountItems,
  listExpenses,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { CashSession } from "@/types/cashSession";
import type { CountItemDetail } from "@/types/countItem";
import type { Expense } from "@/types/expense";
import type { CashSessionSummary } from "@/types/summary";

export default function CashSessionHistoryDetailPage() {
  const router = useRouter();
  const params = useParams<{ cashSessionId: string }>();
  const [cashSession, setCashSession] = useState<CashSession | null>(null);
  const [summary, setSummary] = useState<CashSessionSummary | null>(null);
  const [countItems, setCountItems] = useState<CountItemDetail[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    const cashSessionId = Number(params.cashSessionId);
    if (!Number.isInteger(cashSessionId) || cashSessionId <= 0) {
      setError("El cuadre solicitado no es válido.");
      setIsLoading(false);
      return;
    }

    loadCashSessionDetail(storedToken, cashSessionId);
  }, [params.cashSessionId, router]);

  async function loadCashSessionDetail(activeToken: string, cashSessionId: number) {
    setIsLoading(true);
    setError("");

    try {
      const [
        loadedCashSession,
        loadedSummary,
        loadedCountItems,
        loadedExpenses,
      ] = await Promise.all([
        getCashSession(activeToken, cashSessionId),
        getCashSessionSummary(activeToken, cashSessionId),
        listCashCountItems(activeToken, cashSessionId),
        listExpenses(activeToken, cashSessionId),
      ]);

      setCashSession(loadedCashSession);
      setSummary(loadedSummary);
      setCountItems(loadedCountItems);
      setExpenses(loadedExpenses);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
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
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard/history"
            >
              Volver al historial
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Detalle de cuadre
            </h1>
          </div>
          <LogoutButton />
        </header>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando detalle..." />
        ) : cashSession && summary ? (
          <>
            <CashSessionDetailCard cashSession={cashSession} />
            <SummaryCard summary={summary} />
            <CountItemsList countItems={countItems} />
            <ExpenseList expenses={expenses} />
          </>
        ) : null}
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

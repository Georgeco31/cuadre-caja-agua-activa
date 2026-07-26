"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { CashSessionDetailCard } from "@/components/CashSessionDetailCard";
import { CorrectionCountForm } from "@/components/CorrectionCountForm";
import { CorrectionExpenseForm } from "@/components/CorrectionExpenseForm";
import { CorrectionLogsList } from "@/components/CorrectionLogsList";
import { CountItemsList } from "@/components/CountItemsList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { ExpenseList } from "@/components/ExpenseList";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { SummaryCard } from "@/components/SummaryCard";
import {
  ApiError,
  correctCashCountItem,
  createCorrectiveExpense,
  getCurrentUser,
  getCashSession,
  getCashSessionSummary,
  listCashCountItems,
  listCorrections,
  listDenominations,
  listExpenses,
} from "@/lib/api";
import { getToken, removeToken, saveUser } from "@/lib/auth";
import type { CashSession } from "@/types/cashSession";
import type { CountItemDetail } from "@/types/countItem";
import type {
  CorrectionCountItemPayload,
  CorrectionExpensePayload,
  CorrectionLog,
} from "@/types/correction";
import type { Denomination } from "@/types/denomination";
import type { Expense } from "@/types/expense";
import type { CashSessionSummary } from "@/types/summary";

export default function CashSessionHistoryDetailPage() {
  const router = useRouter();
  const params = useParams<{ cashSessionId: string }>();
  const [token, setToken] = useState<string | null>(null);
  const [cashSession, setCashSession] = useState<CashSession | null>(null);
  const [summary, setSummary] = useState<CashSessionSummary | null>(null);
  const [countItems, setCountItems] = useState<CountItemDetail[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [denominations, setDenominations] = useState<Denomination[]>([]);
  const [correctionLogs, setCorrectionLogs] = useState<CorrectionLog[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingCountCorrection, setIsSubmittingCountCorrection] =
    useState(false);
  const [isSubmittingExpenseCorrection, setIsSubmittingExpenseCorrection] =
    useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const cashSessionId = Number(params.cashSessionId);
  const isClosed = cashSession?.status === "closed";
  const preCountExpenses = useMemo(
    () =>
      expenses.filter((expense) => expense.expense_timing === "before_count"),
    [expenses],
  );
  const postCountExpenses = useMemo(
    () =>
      expenses.filter((expense) => expense.expense_timing === "after_count"),
    [expenses],
  );

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);

    if (!Number.isInteger(cashSessionId) || cashSessionId <= 0) {
      setError("El cuadre solicitado no es valido.");
      setIsLoading(false);
      return;
    }

    loadCashSessionDetail(storedToken, cashSessionId);
  }, [cashSessionId, router]);

  async function loadCashSessionDetail(
    activeToken: string,
    activeCashSessionId: number,
  ) {
    setIsLoading(true);
    setError("");
    setMessage("");

    try {
      const currentUser = await getCurrentUser(activeToken);
      saveUser(currentUser);
      const canCorrect = currentUser.role === "admin_auditor";
      setIsAdmin(canCorrect);
      const [
        loadedCashSession,
        loadedSummary,
        loadedCountItems,
        loadedExpenses,
        loadedDenominations,
      ] = await Promise.all([
        getCashSession(activeToken, activeCashSessionId),
        getCashSessionSummary(activeToken, activeCashSessionId),
        listCashCountItems(activeToken, activeCashSessionId),
        listExpenses(activeToken, activeCashSessionId),
        listDenominations(activeToken),
      ]);
      const loadedCorrectionLogs = canCorrect
        ? await listCorrections(activeToken, activeCashSessionId)
        : [];

      setCashSession(loadedCashSession);
      setSummary(loadedSummary);
      setCountItems(loadedCountItems);
      setExpenses(loadedExpenses);
      setDenominations(loadedDenominations);
      setCorrectionLogs(loadedCorrectionLogs);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCorrectCountItem(
    payload: CorrectionCountItemPayload,
  ): Promise<boolean> {
    if (!token || !cashSession || !isClosed) {
      return false;
    }

    setIsSubmittingCountCorrection(true);
    setError("");
    setMessage("");

    try {
      await correctCashCountItem(token, cashSession.id, payload);
      const [updatedSummary, updatedCountItems, updatedCorrectionLogs] =
        await Promise.all([
          getCashSessionSummary(token, cashSession.id),
          listCashCountItems(token, cashSession.id),
          listCorrections(token, cashSession.id),
        ]);

      setSummary(updatedSummary);
      setCountItems(updatedCountItems);
      setCorrectionLogs(updatedCorrectionLogs);
      setMessage("Correccion de conteo registrada correctamente.");
      return true;
    } catch (correctionError) {
      if (redirectIfUnauthorized(correctionError)) {
        return false;
      }

      setError(getErrorMessage(correctionError));
      return false;
    } finally {
      setIsSubmittingCountCorrection(false);
    }
  }

  async function handleCreateCorrectiveExpense(
    payload: CorrectionExpensePayload,
  ): Promise<boolean> {
    if (!token || !cashSession || !isClosed) {
      return false;
    }

    setIsSubmittingExpenseCorrection(true);
    setError("");
    setMessage("");

    try {
      await createCorrectiveExpense(token, cashSession.id, payload);
      const [updatedSummary, updatedExpenses, updatedCorrectionLogs] =
        await Promise.all([
          getCashSessionSummary(token, cashSession.id),
          listExpenses(token, cashSession.id),
          listCorrections(token, cashSession.id),
        ]);

      setSummary(updatedSummary);
      setExpenses(updatedExpenses);
      setCorrectionLogs(updatedCorrectionLogs);
      setMessage("Gasto correctivo registrado correctamente.");
      return true;
    } catch (correctionError) {
      if (redirectIfUnauthorized(correctionError)) {
        return false;
      }

      setError(getErrorMessage(correctionError));
      return false;
    } finally {
      setIsSubmittingExpenseCorrection(false);
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
        {message ? (
          <p className="rounded-md border border-water-100 bg-water-50 px-3 py-2 text-sm text-water-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando detalle..." />
        ) : cashSession && summary ? (
          <>
            <CashSessionDetailCard cashSession={cashSession} />
            <SummaryCard summary={summary} />
            <CountItemsList countItems={countItems} />
            <div className="grid gap-6 lg:grid-cols-2">
              <ExpenseList
                titleId="detail-pre-count-expenses-title"
                title="Gastos antes del conteo"
                emptyMessage="No hay gastos antes del conteo en este cuadre."
                expenses={preCountExpenses}
              />
              <ExpenseList
                titleId="detail-post-count-expenses-title"
                title="Gastos después del conteo"
                emptyMessage="No hay gastos después del conteo en este cuadre."
                expenses={postCountExpenses}
              />
            </div>

            {isAdmin ? (
            <section
              aria-labelledby="corrections-title"
              className="space-y-4"
            >
              <div>
                <p className="text-sm font-medium text-water-700">
                  Auditoria
                </p>
                <h2
                  id="corrections-title"
                  className="mt-1 text-xl font-semibold text-slate-950"
                >
                  Correcciones del cuadre
                </h2>
              </div>

              {!isClosed ? (
                <p className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
                  Las correcciones solo aplican para cuadres cerrados.
                </p>
              ) : (
                <div className="grid gap-6 lg:grid-cols-2">
                  <CorrectionCountForm
                    denominations={denominations}
                    disabled={!isClosed}
                    isSubmitting={isSubmittingCountCorrection}
                    onSubmit={handleCorrectCountItem}
                  />
                  <CorrectionExpenseForm
                    disabled={!isClosed}
                    isSubmitting={isSubmittingExpenseCorrection}
                    onSubmit={handleCreateCorrectiveExpense}
                  />
                </div>
              )}

              <CorrectionLogsList correctionLogs={correctionLogs} />
            </section>
            ) : (
              <p className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
                Las correcciones de cuadres cerrados y su auditoría están
                disponibles solo para el administrador/auditor.
              </p>
            )}
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

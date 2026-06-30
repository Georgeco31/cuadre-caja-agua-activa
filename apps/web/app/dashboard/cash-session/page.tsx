"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { CashSessionCard } from "@/components/CashSessionCard";
import { DenominationCountTable } from "@/components/DenominationCountTable";
import { ErrorMessage } from "@/components/ErrorMessage";
import { ExpenseForm } from "@/components/ExpenseForm";
import { ExpenseList } from "@/components/ExpenseList";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { SummaryCard } from "@/components/SummaryCard";
import {
  ApiError,
  closeCashSession,
  createCashSession,
  createExpense,
  getCashSessionByDate,
  getCashSessionSummary,
  listExpenses,
  listDenominations,
  setCashCountItem,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { CashSession } from "@/types/cashSession";
import type { Denomination } from "@/types/denomination";
import type { Expense, ExpensePayload } from "@/types/expense";
import type { CashSessionSummary } from "@/types/summary";

export default function CashSessionPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [cashSession, setCashSession] = useState<CashSession | null>(null);
  const [denominations, setDenominations] = useState<Denomination[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [summary, setSummary] = useState<CashSessionSummary | null>(null);
  const [quantities, setQuantities] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [isClosing, setIsClosing] = useState(false);
  const [isSubmittingExpense, setIsSubmittingExpense] = useState(false);

  const coins = useMemo(
    () =>
      denominations
        .filter((denomination) => denomination.type === "coin")
        .sort(compareDenominationValue),
    [denominations],
  );
  const bills = useMemo(
    () =>
      denominations
        .filter((denomination) => denomination.type === "bill")
        .sort(compareDenominationValue),
    [denominations],
  );
  const isClosed = cashSession?.status === "closed";

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadCashSession(storedToken);
  }, [router]);

  async function loadCashSession(activeToken: string) {
    setIsLoading(true);
    setError("");

    try {
      const sessionDate = getTodayISODate();
      const [loadedDenominations, loadedSession] = await Promise.all([
        listDenominations(activeToken),
        getOrCreateCashSession(activeToken, sessionDate),
      ]);
      const [loadedSummary, loadedExpenses] = await Promise.all([
        getCashSessionSummary(activeToken, loadedSession.id),
        listExpenses(activeToken, loadedSession.id),
      ]);

      setDenominations(loadedDenominations);
      setCashSession(loadedSession);
      setExpenses(loadedExpenses);
      setSummary(loadedSummary);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function getOrCreateCashSession(activeToken: string, sessionDate: string) {
    try {
      return await getCashSessionByDate(activeToken, sessionDate);
    } catch (sessionError) {
      if (sessionError instanceof ApiError && sessionError.status === 404) {
        try {
          return await createCashSession(activeToken, { session_date: sessionDate });
        } catch (createError) {
          if (createError instanceof ApiError && createError.status === 409) {
            return getCashSessionByDate(activeToken, sessionDate);
          }

          throw createError;
        }
      }

      throw sessionError;
    }
  }

  function handleQuantityChange(denominationId: number, value: string) {
    if (value === "" || /^\d+$/.test(value)) {
      setQuantities((currentQuantities) => ({
        ...currentQuantities,
        [denominationId]: value,
      }));
    }
  }

  async function handleSaveCount(denomination: Denomination) {
    if (!token || !cashSession || isClosed) {
      return;
    }

    const quantity = Number(quantities[denomination.id]);
    if (!Number.isInteger(quantity) || quantity < 0) {
      setError("Ingresa una cantidad válida mayor o igual a cero.");
      setMessage("");
      return;
    }

    setSavingId(denomination.id);
    setError("");
    setMessage("");

    try {
      const savedItem = await setCashCountItem(token, cashSession.id, {
        denomination_id: denomination.id,
        quantity,
      });
      const updatedSummary = await getCashSessionSummary(token, cashSession.id);

      setQuantities((currentQuantities) => ({
        ...currentQuantities,
        [denomination.id]: String(savedItem.quantity),
      }));
      setSummary(updatedSummary);
      setMessage(`Cantidad guardada para ${denomination.label}.`);
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return;
      }

      setError(getErrorMessage(saveError));
    } finally {
      setSavingId(null);
    }
  }

  async function handleCloseCashSession() {
    if (!token || !cashSession || isClosed) {
      return;
    }

    const shouldClose = window.confirm(
      "¿Cerrar el cuadre diario? Después no podrás editar sus cantidades.",
    );
    if (!shouldClose) {
      return;
    }

    setIsClosing(true);
    setError("");
    setMessage("");

    try {
      const closedSession = await closeCashSession(token, cashSession.id);
      const updatedSummary = await getCashSessionSummary(token, cashSession.id);

      setCashSession(closedSession);
      setSummary(updatedSummary);
      setMessage("Cuadre cerrado correctamente.");
    } catch (closeError) {
      if (redirectIfUnauthorized(closeError)) {
        return;
      }

      setError(getErrorMessage(closeError));
    } finally {
      setIsClosing(false);
    }
  }

  async function handleCreateExpense(payload: ExpensePayload): Promise<boolean> {
    if (!token || !cashSession || isClosed) {
      return false;
    }

    setIsSubmittingExpense(true);
    setError("");
    setMessage("");

    try {
      const createdExpense = await createExpense(token, cashSession.id, payload);
      const updatedSummary = await getCashSessionSummary(token, cashSession.id);

      setExpenses((currentExpenses) => [...currentExpenses, createdExpense]);
      setSummary(updatedSummary);
      setMessage(`Gasto registrado: ${createdExpense.description}.`);
      return true;
    } catch (expenseError) {
      if (redirectIfUnauthorized(expenseError)) {
        return false;
      }

      setError(getErrorMessage(expenseError));
      return false;
    } finally {
      setIsSubmittingExpense(false);
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

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6">
        <div className="mx-auto w-full max-w-6xl">
          <LoadingState label="Cargando cuadre diario..." />
        </div>
      </main>
    );
  }

  if (!cashSession || !summary) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6">
        <div className="mx-auto w-full max-w-6xl space-y-4">
          {error ? <ErrorMessage message={error} /> : null}
          <Link className="text-sm font-semibold text-water-700" href="/dashboard">
            Volver al dashboard
          </Link>
        </div>
      </main>
    );
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
              Cuadre diario
            </h1>
          </div>
          <LogoutButton />
        </header>

        <CashSessionCard
          cashSession={cashSession}
          isClosing={isClosing}
          onClose={handleCloseCashSession}
        />

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-water-100 bg-water-50 px-3 py-2 text-sm text-water-700">
            {message}
          </p>
        ) : null}

        <SummaryCard summary={summary} />

        <div className="grid gap-6 lg:grid-cols-2">
          <DenominationCountTable
            title="Monedas"
            denominations={coins}
            disabled={isClosed}
            quantities={quantities}
            savingId={savingId}
            onQuantityChange={handleQuantityChange}
            onSave={handleSaveCount}
          />
          <DenominationCountTable
            title="Billetes"
            denominations={bills}
            disabled={isClosed}
            quantities={quantities}
            savingId={savingId}
            onQuantityChange={handleQuantityChange}
            onSave={handleSaveCount}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <ExpenseForm
            disabled={isClosed}
            isSubmitting={isSubmittingExpense}
            onSubmit={handleCreateExpense}
          />
          <ExpenseList expenses={expenses} />
        </div>
      </div>
    </main>
  );
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function compareDenominationValue(
  first: Denomination,
  second: Denomination,
): number {
  return Number(first.value) - Number(second.value);
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }

  return "No se pudo completar la solicitud.";
}

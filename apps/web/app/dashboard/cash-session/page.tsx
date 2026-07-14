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
  getCashSession,
  getCashSessionByDate,
  getCashSessionSummary,
  listCashCountItems,
  listExpenses,
  listDenominations,
  setCashCountItem,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import {
  formatCentsAsMoneyInput,
  isValidMoneyInputDraft,
  parseMoneyInputToCents,
} from "@/lib/money";
import type { CashSession } from "@/types/cashSession";
import type { CountItemDetail } from "@/types/countItem";
import type { Denomination } from "@/types/denomination";
import type { Expense, ExpensePayload } from "@/types/expense";
import type { CashSessionSummary } from "@/types/summary";

export default function CashSessionPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [cashSession, setCashSession] = useState<CashSession | null>(null);
  const [denominations, setDenominations] = useState<Denomination[]>([]);
  const [countItems, setCountItems] = useState<CountItemDetail[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [summary, setSummary] = useState<CashSessionSummary | null>(null);
  const [countedAmounts, setCountedAmounts] = useState<Record<number, string>>(
    {},
  );
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
  const savedDenominationIds = useMemo(
    () => new Set(countItems.map((item) => item.denomination_id)),
    [countItems],
  );
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
      const [loadedSummary, loadedExpenses, loadedCountItems] =
        await Promise.all([
          getCashSessionSummary(activeToken, loadedSession.id),
          listExpenses(activeToken, loadedSession.id),
          listCashCountItems(activeToken, loadedSession.id),
        ]);

      setDenominations(loadedDenominations);
      setCashSession(loadedSession);
      setExpenses(loadedExpenses);
      setSummary(loadedSummary);
      setCountItems(loadedCountItems);
      setCountedAmounts(
        buildCountedAmountMap(loadedDenominations, loadedCountItems),
      );
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

  function handleCountedAmountChange(denominationId: number, value: string) {
    if (isValidMoneyInputDraft(value)) {
      setCountedAmounts((currentAmounts) => ({
        ...currentAmounts,
        [denominationId]: value,
      }));
    }
  }

  async function handleSaveCount(denomination: Denomination) {
    if (!token || !cashSession || !summary || isClosed) {
      return;
    }

    const quantityResult = getQuantityFromCountedAmount(
      countedAmounts[denomination.id] ?? "",
      denomination,
    );
    if (!quantityResult.ok) {
      setError(quantityResult.message);
      setMessage("");
      return;
    }

    setSavingId(denomination.id);
    setError("");
    setMessage("");

    try {
      await setCashCountItem(token, cashSession.id, {
        denomination_id: denomination.id,
        quantity: quantityResult.quantity,
      });
      const [updatedSummary, updatedCountItems] = await Promise.all([
        getCashSessionSummary(token, cashSession.id),
        listCashCountItems(token, cashSession.id),
      ]);

      setSummary(updatedSummary);
      setCountItems(updatedCountItems);
      setCountedAmounts(buildCountedAmountMap(denominations, updatedCountItems));
      setMessage(`Monto contado guardado para ${denomination.label}.`);
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
    if (!token || !cashSession || !summary || isClosed) {
      return;
    }

    const shouldClose = window.confirm(buildCloseConfirmation(summary));
    if (!shouldClose) {
      return;
    }

    setIsClosing(true);
    setError("");
    setMessage("");

    try {
      await closeCashSession(token, cashSession.id);
      const [
        refreshedSession,
        updatedSummary,
        updatedCountItems,
        updatedExpenses,
      ] = await Promise.all([
        getCashSession(token, cashSession.id),
        getCashSessionSummary(token, cashSession.id),
        listCashCountItems(token, cashSession.id),
        listExpenses(token, cashSession.id),
      ]);

      setCashSession(refreshedSession);
      setSummary(updatedSummary);
      setCountItems(updatedCountItems);
      setExpenses(updatedExpenses);
      setCountedAmounts(buildCountedAmountMap(denominations, updatedCountItems));
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
      const [updatedSummary, updatedExpenses] = await Promise.all([
        getCashSessionSummary(token, cashSession.id),
        listExpenses(token, cashSession.id),
      ]);

      setExpenses(updatedExpenses);
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
            countedAmounts={countedAmounts}
            savedDenominationIds={savedDenominationIds}
            savingId={savingId}
            onCountedAmountChange={handleCountedAmountChange}
            onSave={handleSaveCount}
          />
          <DenominationCountTable
            title="Billetes"
            denominations={bills}
            disabled={isClosed}
            countedAmounts={countedAmounts}
            savedDenominationIds={savedDenominationIds}
            savingId={savingId}
            onCountedAmountChange={handleCountedAmountChange}
            onSave={handleSaveCount}
          />
        </div>

        <section aria-labelledby="expenses-title" className="space-y-4">
          <div>
            <p className="text-sm font-medium text-water-700">Gastos</p>
            <h2
              id="expenses-title"
              className="mt-1 text-xl font-semibold text-slate-950"
            >
              Gastos del cuadre
            </h2>
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <div className="grid gap-6">
              <ExpenseForm
                title="Gastos antes del conteo"
                eyebrow="Control"
                helpText="Se registran para control, pero no se restan del total contado."
                disabled={isClosed}
                isSubmitting={isSubmittingExpense}
                expenseTiming="before_count"
                onSubmit={handleCreateExpense}
              />
              <ExpenseList
                titleId="pre-count-expenses-title"
                title="Gastos antes del conteo"
                emptyMessage="Todavía no hay gastos antes del conteo."
                expenses={preCountExpenses}
              />
            </div>

            <div className="grid gap-6">
              <ExpenseForm
                title="Gastos después del conteo"
                eyebrow="Caja"
                helpText="Estos gastos sí se restan del total contado."
                disabled={isClosed}
                isSubmitting={isSubmittingExpense}
                expenseTiming="after_count"
                onSubmit={handleCreateExpense}
              />
              <ExpenseList
                titleId="post-count-expenses-title"
                title="Gastos después del conteo"
                emptyMessage="Todavía no hay gastos después del conteo."
                expenses={postCountExpenses}
              />
            </div>
          </div>
        </section>
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

function buildCountedAmountMap(
  denominations: Denomination[],
  countItems: CountItemDetail[],
): Record<number, string> {
  const countedAmountMap: Record<number, string> = {};

  denominations.forEach((denomination) => {
    countedAmountMap[denomination.id] = "0.00";
  });

  countItems.forEach((item) => {
    const subtotalCents = parseMoneyInputToCents(item.subtotal);
    countedAmountMap[item.denomination_id] =
      subtotalCents === null
        ? item.subtotal
        : formatCentsAsMoneyInput(subtotalCents);
  });

  return countedAmountMap;
}

type QuantityResult =
  | { ok: true; quantity: number }
  | { ok: false; message: string };

function getQuantityFromCountedAmount(
  countedAmount: string,
  denomination: Denomination,
): QuantityResult {
  const amountCents = parseMoneyInputToCents(countedAmount);
  if (amountCents === null) {
    return {
      ok: false,
      message: "Ingresa un monto contado válido mayor o igual a cero.",
    };
  }

  const denominationCents = parseMoneyInputToCents(denomination.value);
  if (denominationCents === null || denominationCents <= 0) {
    return {
      ok: false,
      message: "No se pudo validar la denominación seleccionada.",
    };
  }

  if (amountCents % denominationCents !== 0) {
    return {
      ok: false,
      message:
        "El monto ingresado no coincide con esta denominación. " +
        `Debe ser múltiplo de ${formatMoney(denomination.value)}.`,
    };
  }

  return {
    ok: true,
    quantity: amountCents / denominationCents,
  };
}

function buildCloseConfirmation(summary: CashSessionSummary): string {
  return [
    "Cerrar el cuadre diario?",
    "",
    `Total monedas: ${formatMoney(summary.total_coins)}`,
    `Total billetes: ${formatMoney(summary.total_bills)}`,
    `Total contado: ${formatMoney(summary.total_counted)}`,
    `Gastos antes del conteo: ${formatMoney(summary.total_pre_count_expenses)}`,
    `Gastos después del conteo: ${formatMoney(summary.total_post_count_expenses)}`,
    `Total final: ${formatMoney(summary.final_total)}`,
    "",
    "Despues del cierre las cantidades y gastos normales quedaran bloqueados.",
    "Cualquier ajuste posterior debera registrarse como correccion con motivo.",
  ].join("\n");
}

function formatMoney(value: string): string {
  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) {
    return `$${value}`;
  }

  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(numberValue);
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }

  return "No se pudo completar la solicitud.";
}

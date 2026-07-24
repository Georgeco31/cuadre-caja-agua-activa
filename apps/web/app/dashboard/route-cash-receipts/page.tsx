"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createRouteCashReceipt,
  getRouteClosureCashReceipt,
  listCashSessions,
  listRouteCashReceipts,
  listRouteClosures,
  voidRouteCashReceipt,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import {
  formatCentsAsMoneyInput,
  isValidMoneyInputDraft,
  parseMoneyInputToCents,
} from "@/lib/money";
import type { CashSession } from "@/types/cashSession";
import type { RouteClosure } from "@/types/routeClosure";
import {
  ROUTE_CASH_RECEIPT_STATUS_LABELS,
  type RouteCashReceipt,
  type RouteCashReceiptFilters,
  type RouteCashReceiptStatus,
  type RouteClosureCashReceipt,
} from "@/types/routeCashReceipt";

type ReceiptFilterValues = {
  search: string;
  dateFrom: string;
  dateTo: string;
  status: RouteCashReceiptStatus | "";
};

const emptyFilters: ReceiptFilterValues = {
  search: "",
  dateFrom: "",
  dateTo: "",
  status: "",
};

export default function RouteCashReceiptsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [closures, setClosures] = useState<RouteClosure[]>([]);
  const [cashSessions, setCashSessions] = useState<CashSession[]>([]);
  const [receipts, setReceipts] = useState<RouteCashReceipt[]>([]);
  const [allReceipts, setAllReceipts] = useState<RouteCashReceipt[]>([]);
  const [selectedClosureId, setSelectedClosureId] = useState("");
  const [selectedCashSessionId, setSelectedCashSessionId] = useState("");
  const [receiptDate, setReceiptDate] = useState(getTodayISODate());
  const [receivedAmount, setReceivedAmount] = useState("");
  const [notes, setNotes] = useState("");
  const [receiptCheck, setReceiptCheck] =
    useState<RouteClosureCashReceipt | null>(null);
  const [filters, setFilters] = useState<ReceiptFilterValues>(emptyFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isCheckingClosure, setIsCheckingClosure] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [voidingReceiptId, setVoidingReceiptId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const selectedClosure = useMemo(
    () =>
      closures.find((closure) => closure.id === Number(selectedClosureId)) ??
      null,
    [closures, selectedClosureId],
  );
  const selectedCashSession = useMemo(
    () =>
      cashSessions.find(
        (cashSession) => cashSession.id === Number(selectedCashSessionId),
      ) ?? null,
    [cashSessions, selectedCashSessionId],
  );
  const activeReceiptClosureIds = useMemo(
    () =>
      new Set(
        allReceipts
          .filter((receipt) => receipt.status === "active")
          .map((receipt) => receipt.route_closure_id),
      ),
    [allReceipts],
  );
  const estimatedDifference = useMemo(() => {
    if (!selectedClosure) {
      return null;
    }
    const receivedCents = parseMoneyInputToCents(receivedAmount);
    const deliveredCents = parseMoneyInputToCents(
      selectedClosure.delivered_cash_total,
    );
    if (receivedCents === null || deliveredCents === null) {
      return null;
    }
    return receivedCents - deliveredCents;
  }, [receivedAmount, selectedClosure]);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    void loadInitialData(storedToken);
  }, [router]);

  async function loadInitialData(activeToken: string) {
    setIsLoading(true);
    clearNotices();
    try {
      const [loadedClosures, loadedCashSessions, loadedReceipts] =
        await Promise.all([
          listRouteClosures(activeToken, { status: "active" }),
          listCashSessions(activeToken, { status: "open" }),
          listRouteCashReceipts(activeToken),
        ]);
      setClosures(loadedClosures);
      setCashSessions(loadedCashSessions);
      setReceipts(loadedReceipts);
      setAllReceipts(loadedReceipts);
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleClosureChange(closureId: string) {
    setSelectedClosureId(closureId);
    setReceiptCheck(null);
    setError("");
    setMessage("");
    const closure = closures.find((item) => item.id === Number(closureId));
    setReceivedAmount(closure?.delivered_cash_total ?? "");
    if (!token || !closure) {
      return;
    }

    setIsCheckingClosure(true);
    try {
      setReceiptCheck(await getRouteClosureCashReceipt(token, closure.id));
    } catch (checkError) {
      handleError(checkError);
    } finally {
      setIsCheckingClosure(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedClosure || !selectedCashSession) {
      setError("Seleccione un cierre de ruta y un cuadre de caja abierto.");
      return;
    }
    const receivedCents = parseMoneyInputToCents(receivedAmount);
    if (receivedCents === null || receivedCents < 0) {
      setError("Ingrese un monto recibido válido, con máximo dos decimales.");
      return;
    }
    if (!receiptDate) {
      setError("La fecha de registro es obligatoria.");
      return;
    }

    setIsSaving(true);
    clearNotices();
    try {
      const saved = await createRouteCashReceipt(token, {
        receipt_date: receiptDate,
        route_closure_id: selectedClosure.id,
        cash_session_id: selectedCashSession.id,
        received_amount: formatCentsAsMoneyInput(receivedCents),
        notes: notes.trim() || null,
      });
      setMessage(
        `${saved.receipt_number} registrado. Diferencia: ${formatSignedMoney(
          saved.difference_amount,
        )}.`,
      );
      resetForm();
      await refreshReceipts(token);
    } catch (saveError) {
      handleError(saveError);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleVoid(receipt: RouteCashReceipt) {
    if (!token) {
      return;
    }
    const reason = window.prompt(
      `Motivo para anular ${receipt.receipt_number}:`,
    );
    const normalizedReason = reason?.trim() ?? "";
    if (!normalizedReason) {
      if (reason !== null) {
        setError("El motivo de anulación es obligatorio.");
      }
      return;
    }

    setVoidingReceiptId(receipt.id);
    clearNotices();
    try {
      const voided = await voidRouteCashReceipt(
        token,
        receipt.id,
        normalizedReason,
      );
      setMessage(`${voided.receipt_number} fue anulado sin modificar la caja.`);
      await refreshReceipts(token);
    } catch (voidError) {
      handleError(voidError);
    } finally {
      setVoidingReceiptId(null);
    }
  }

  async function applyFilters(activeFilters: ReceiptFilterValues) {
    if (!token) {
      return;
    }
    setIsFiltering(true);
    clearNotices();
    try {
      setReceipts(
        await listRouteCashReceipts(token, toApiFilters(activeFilters)),
      );
    } catch (filterError) {
      handleError(filterError);
    } finally {
      setIsFiltering(false);
    }
  }

  async function refreshReceipts(activeToken: string) {
    const [loadedReceipts, loadedAllReceipts] = await Promise.all([
      listRouteCashReceipts(activeToken, toApiFilters(filters)),
      listRouteCashReceipts(activeToken),
    ]);
    setReceipts(loadedReceipts);
    setAllReceipts(loadedAllReceipts);
  }

  function resetForm() {
    setSelectedClosureId("");
    setSelectedCashSessionId("");
    setReceivedAmount("");
    setNotes("");
    setReceiptCheck(null);
  }

  function clearNotices() {
    setError("");
    setMessage("");
  }

  function handleError(possibleError: unknown) {
    if (
      possibleError instanceof ApiError &&
      (possibleError.status === 401 || possibleError.status === 403)
    ) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(
      possibleError instanceof Error
        ? possibleError.message
        : "No se pudo completar la operación.",
    );
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6">
        <div className="mx-auto w-full max-w-7xl">
          <LoadingState label="Cargando dinero de rutas en caja..." />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Dinero de ruta en caja
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra que el efectivo entregado por una ruta cerrada fue
              recibido en un cuadre de caja abierto. Esto no modifica
              automáticamente monedas, billetes ni el total contado.
            </p>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
          Este registro es solo de trazabilidad. El total oficial de caja sigue
          viniendo exclusivamente del conteo físico de monedas y billetes.
        </p>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div>
            <p className="text-sm font-medium text-water-700">Nuevo registro</p>
            <h2 className="mt-1 text-xl font-semibold text-slate-950">
              Recibir efectivo de una ruta
            </h2>
          </div>

          {closures.length === 0 ? (
            <EmptyNotice text="No hay cierres financieros activos disponibles." />
          ) : null}
          {closures.length > 0 &&
          closures.every((closure) =>
            activeReceiptClosureIds.has(closure.id),
          ) ? (
            <EmptyNotice text="Todos los cierres activos ya están registrados en caja." />
          ) : null}
          {cashSessions.length === 0 ? (
            <EmptyNotice text="No hay cuadres de caja abiertos. Este módulo no crea cuadres automáticamente." />
          ) : null}

          <form
            className="mt-5 grid gap-4 lg:grid-cols-2"
            onSubmit={handleSubmit}
          >
            <Field label="Cierre de ruta">
              <select
                className={fieldClassName}
                value={selectedClosureId}
                disabled={isSaving || closures.length === 0}
                required
                onChange={(event) =>
                  void handleClosureChange(event.target.value)
                }
              >
                <option value="">Seleccione un cierre</option>
                {closures.map((closure) => {
                  const received = activeReceiptClosureIds.has(closure.id);
                  return (
                    <option
                      key={closure.id}
                      value={closure.id}
                      disabled={received}
                    >
                      {closure.closure_number} · {closure.route_name_snapshot} ·{" "}
                      {formatMoney(closure.delivered_cash_total)}
                      {received ? " · ya recibido" : ""}
                    </option>
                  );
                })}
              </select>
            </Field>
            <Field label="Cuadre de caja abierto">
              <select
                className={fieldClassName}
                value={selectedCashSessionId}
                disabled={isSaving || cashSessions.length === 0}
                required
                onChange={(event) =>
                  setSelectedCashSessionId(event.target.value)
                }
              >
                <option value="">Seleccione un cuadre</option>
                {cashSessions.map((cashSession) => (
                  <option key={cashSession.id} value={cashSession.id}>
                    {formatDate(cashSession.session_date)} · Caja #
                    {cashSession.id}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Fecha de registro">
              <input
                className={fieldClassName}
                type="date"
                value={receiptDate}
                disabled={isSaving}
                required
                onChange={(event) => setReceiptDate(event.target.value)}
              />
            </Field>
            <Field label="Monto recibido">
              <input
                className={fieldClassName}
                type="text"
                inputMode="decimal"
                placeholder="0.00"
                value={receivedAmount}
                disabled={isSaving || !selectedClosure}
                required
                onChange={(event) => {
                  if (isValidMoneyInputDraft(event.target.value)) {
                    setReceivedAmount(event.target.value);
                  }
                }}
              />
            </Field>
            <Field label="Observaciones" className="lg:col-span-2">
              <textarea
                className={`${fieldClassName} min-h-24 resize-y`}
                value={notes}
                disabled={isSaving}
                placeholder="Detalle opcional de la entrega"
                onChange={(event) => setNotes(event.target.value)}
              />
            </Field>

            {selectedClosure ? (
              <div className="grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 lg:col-span-2 xl:grid-cols-5">
                <SummaryItem
                  label="Cierre"
                  value={selectedClosure.closure_number}
                />
                <SummaryItem
                  label="Ruta"
                  value={selectedClosure.route_name_snapshot}
                />
                <SummaryItem
                  label="Vehículo"
                  value={selectedClosure.vehicle_name_snapshot}
                />
                <SummaryItem
                  label="Entregado"
                  value={formatMoney(selectedClosure.delivered_cash_total)}
                />
                <SummaryItem
                  label="Diferencia estimada"
                  value={
                    estimatedDifference === null
                      ? "—"
                      : formatSignedCents(estimatedDifference)
                  }
                />
                <SummaryItem
                  label="Fecha del cierre"
                  value={formatDate(selectedClosure.closure_date)}
                />
                <SummaryItem
                  label="Cuadre seleccionado"
                  value={
                    selectedCashSession
                      ? `${formatDate(selectedCashSession.session_date)} · #${selectedCashSession.id}`
                      : "Pendiente"
                  }
                />
                <SummaryItem
                  label="Estado de recepción"
                  value={
                    isCheckingClosure
                      ? "Consultando..."
                      : receiptCheck?.status === "received"
                        ? `Ya recibido: ${receiptCheck.active_receipt?.receipt_number}`
                        : "No registrado"
                  }
                />
              </div>
            ) : null}

            <div className="lg:col-span-2">
              <button
                className="h-11 rounded-md bg-water-700 px-5 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
                type="submit"
                disabled={
                  isSaving ||
                  isCheckingClosure ||
                  !selectedClosure ||
                  !selectedCashSession ||
                  receiptCheck?.status === "received"
                }
              >
                {isSaving ? "Registrando..." : "Registrar dinero en caja"}
              </button>
            </div>
          </form>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <h2 className="text-lg font-semibold text-slate-950">
              Registros de dinero de ruta
            </h2>
            <span className="text-sm text-slate-500">{receipts.length}</span>
          </div>
          <form
            className="grid gap-3 border-b border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 xl:grid-cols-5"
            onSubmit={(event) => {
              event.preventDefault();
              void applyFilters(filters);
            }}
          >
            <Field label="Buscar">
              <input
                className={fieldClassName}
                type="search"
                placeholder="Recibo, cierre, ruta o vehículo"
                value={filters.search}
                disabled={isFiltering}
                onChange={(event) =>
                  setFilters({ ...filters, search: event.target.value })
                }
              />
            </Field>
            <Field label="Desde">
              <input
                className={fieldClassName}
                type="date"
                value={filters.dateFrom}
                disabled={isFiltering}
                onChange={(event) =>
                  setFilters({ ...filters, dateFrom: event.target.value })
                }
              />
            </Field>
            <Field label="Hasta">
              <input
                className={fieldClassName}
                type="date"
                value={filters.dateTo}
                disabled={isFiltering}
                onChange={(event) =>
                  setFilters({ ...filters, dateTo: event.target.value })
                }
              />
            </Field>
            <Field label="Estado">
              <select
                className={fieldClassName}
                value={filters.status}
                disabled={isFiltering}
                onChange={(event) =>
                  setFilters({
                    ...filters,
                    status: event.target.value as RouteCashReceiptStatus | "",
                  })
                }
              >
                <option value="">Todos</option>
                <option value="active">Activos</option>
                <option value="voided">Anulados</option>
              </select>
            </Field>
            <div className="flex items-end gap-2">
              <button
                className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
                type="submit"
                disabled={isFiltering}
              >
                Consultar
              </button>
              <button
                className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                type="button"
                disabled={isFiltering}
                onClick={() => {
                  setFilters(emptyFilters);
                  void applyFilters(emptyFilters);
                }}
              >
                Limpiar
              </button>
            </div>
          </form>

          {isFiltering ? (
            <p className="px-4 py-8 text-sm text-slate-600">
              Actualizando registros...
            </p>
          ) : receipts.length === 0 ? (
            <p className="px-4 py-8 text-sm text-slate-600">
              Todavía no hay registros para los filtros seleccionados.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1200px] border-collapse text-left text-sm">
                <thead className="bg-white text-slate-600">
                  <tr>
                    <th className="px-4 py-3 font-medium">Recibo</th>
                    <th className="px-4 py-3 font-medium">Fecha</th>
                    <th className="px-4 py-3 font-medium">Cierre</th>
                    <th className="px-4 py-3 font-medium">Ruta</th>
                    <th className="px-4 py-3 font-medium">Vehículo</th>
                    <th className="px-4 py-3 text-right font-medium">
                      Entregado
                    </th>
                    <th className="px-4 py-3 text-right font-medium">
                      Recibido
                    </th>
                    <th className="px-4 py-3 text-right font-medium">
                      Diferencia
                    </th>
                    <th className="px-4 py-3 font-medium">Cuadre</th>
                    <th className="px-4 py-3 font-medium">Estado</th>
                    <th className="px-4 py-3 font-medium">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {receipts.map((receipt) => (
                    <tr key={receipt.id}>
                      <td className="px-4 py-3 align-top font-semibold text-slate-950">
                        {receipt.receipt_number}
                        {receipt.notes ? (
                          <p className="mt-1 max-w-52 text-xs font-normal text-slate-500">
                            {receipt.notes}
                          </p>
                        ) : null}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {formatDate(receipt.receipt_date)}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {receipt.closure_number_snapshot}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {receipt.route_name_snapshot}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {receipt.vehicle_name_snapshot}
                      </td>
                      <td className="px-4 py-3 text-right align-top text-slate-700">
                        {formatMoney(receipt.delivered_cash_total)}
                      </td>
                      <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
                        {formatMoney(receipt.received_amount)}
                      </td>
                      <td
                        className={`px-4 py-3 text-right align-top font-semibold ${differenceClassName(
                          receipt.difference_amount,
                        )}`}
                      >
                        {formatSignedMoney(receipt.difference_amount)}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {formatDate(receipt.cash_session.session_date)} · #
                        {receipt.cash_session_id}
                      </td>
                      <td className="px-4 py-3 align-top">
                        <span
                          className={
                            receipt.status === "active"
                              ? "inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800"
                              : "inline-flex rounded-full bg-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700"
                          }
                        >
                          {ROUTE_CASH_RECEIPT_STATUS_LABELS[receipt.status]}
                        </span>
                        {receipt.void_reason ? (
                          <p className="mt-1 max-w-48 text-xs text-slate-500">
                            {receipt.void_reason}
                          </p>
                        ) : null}
                      </td>
                      <td className="px-4 py-3 align-top">
                        {receipt.status === "active" ? (
                          <button
                            className="font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                            type="button"
                            disabled={voidingReceiptId === receipt.id}
                            onClick={() => void handleVoid(receipt)}
                          >
                            {voidingReceiptId === receipt.id
                              ? "Anulando..."
                              : "Anular"}
                          </button>
                        ) : (
                          <span className="text-slate-400">Sin acciones</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function Field({
  label,
  className = "",
  children,
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <label className={`grid gap-1.5 text-sm text-slate-700 ${className}`}>
      <span className="font-medium">{label}</span>
      {children}
    </label>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-sm font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function EmptyNotice({ text }: { text: string }) {
  return (
    <p className="mt-4 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
      {text}
    </p>
  );
}

function toApiFilters(
  filters: ReceiptFilterValues,
): RouteCashReceiptFilters {
  return {
    ...(filters.search ? { search: filters.search.trim() } : {}),
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.status ? { status: filters.status } : {}),
  };
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return `${day}/${month}/${year}`;
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

function formatSignedMoney(value: string): string {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "$0.00";
  }
  return `${amount > 0 ? "+" : ""}$${amount.toFixed(2)}`;
}

function formatSignedCents(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}$${formatCentsAsMoneyInput(Math.abs(value))}`;
}

function differenceClassName(value: string): string {
  const amount = Number(value);
  if (amount > 0) {
    return "text-emerald-700";
  }
  if (amount < 0) {
    return "text-red-700";
  }
  return "text-slate-700";
}

const fieldClassName =
  "h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500";

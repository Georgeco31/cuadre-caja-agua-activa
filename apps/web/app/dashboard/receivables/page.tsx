"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { CreditPaymentForm } from "@/components/CreditPaymentForm";
import { CreditPaymentList } from "@/components/CreditPaymentList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createCreditPayment,
  listCashSales,
  listCreditPayments,
  listCustomers,
  voidCreditPayment,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type {
  CreditPayment,
  CreditPaymentPayload,
} from "@/types/creditPayment";
import type { Customer } from "@/types/customer";
import type { Sale } from "@/types/sale";

export default function ReceivablesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [sales, setSales] = useState<Sale[]>([]);
  const [payments, setPayments] = useState<CreditPayment[]>([]);
  const [customerFilter, setCustomerFilter] = useState("");
  const [selectedSaleId, setSelectedSaleId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [voidingPaymentId, setVoidingPaymentId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const pendingSales = useMemo(
    () => sales.filter((sale) => Number(sale.balance_amount) > 0),
    [sales],
  );
  const totalPending = useMemo(
    () =>
      pendingSales.reduce(
        (total, sale) => total + Number(sale.balance_amount),
        0,
      ),
    [pendingSales],
  );

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadInitialData(storedToken);
  }, [router]);

  async function loadInitialData(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const [loadedCustomers, loadedSales, loadedPayments] = await Promise.all([
        listCustomers(activeToken),
        listCashSales(activeToken, {
          sale_type: "credit",
          status: "active",
        }),
        listCreditPayments(activeToken),
      ]);
      setCustomers(loadedCustomers);
      setSales(loadedSales);
      setPayments(loadedPayments);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadRecords(
    activeToken: string,
    activeCustomerFilter: string,
  ) {
    setIsRefreshing(true);
    setError("");
    try {
      const customerId = activeCustomerFilter
        ? Number(activeCustomerFilter)
        : undefined;
      const [loadedSales, loadedPayments] = await Promise.all([
        listCashSales(activeToken, {
          sale_type: "credit",
          status: "active",
          ...(customerId ? { customer_id: customerId } : {}),
        }),
        listCreditPayments(activeToken, {
          ...(customerId ? { customer_id: customerId } : {}),
        }),
      ]);
      const loadedPendingSales = loadedSales.filter(
        (sale) => Number(sale.balance_amount) > 0,
      );
      setSales(loadedSales);
      setPayments(loadedPayments);
      setSelectedSaleId((currentId) =>
        loadedPendingSales.some((sale) => sale.id === currentId)
          ? currentId
          : null,
      );
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsRefreshing(false);
    }
  }

  async function handleCreatePayment(
    saleId: number,
    payload: CreditPaymentPayload,
  ): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");
    try {
      const savedPayment = await createCreditPayment(token, saleId, payload);
      setMessage(
        `Abono registrado sobre ${savedPayment.sale_number}. Saldo actualizado: ${formatMoney(savedPayment.sale_balance_amount)}.`,
      );
      await loadRecords(token, customerFilter);
      return true;
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return false;
      }
      setError(getErrorMessage(saveError));
      return false;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleVoidPayment(payment: CreditPayment) {
    if (!token) {
      return;
    }
    const reason = window.prompt(
      `Motivo para anular el abono de ${formatMoney(payment.amount)} sobre ${payment.sale_number}:`,
    );
    if (reason === null) {
      return;
    }
    const normalizedReason = reason.trim();
    if (!normalizedReason) {
      setError("El motivo de anulación es obligatorio.");
      return;
    }

    setVoidingPaymentId(payment.id);
    setError("");
    setMessage("");
    try {
      const voidedPayment = await voidCreditPayment(
        token,
        payment.id,
        normalizedReason,
      );
      setMessage(
        `Abono anulado. El saldo de ${voidedPayment.sale_number} volvió a ${formatMoney(voidedPayment.sale_balance_amount)}.`,
      );
      await loadRecords(token, customerFilter);
    } catch (voidError) {
      if (redirectIfUnauthorized(voidError)) {
        return;
      }
      setError(getErrorMessage(voidError));
    } finally {
      setVoidingPaymentId(null);
    }
  }

  function handleSelectSale(saleId: number) {
    setSelectedSaleId(saleId);
    window.requestAnimationFrame(() => {
      document
        .getElementById("credit-payment-form")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function handleCustomerFilter(value: string) {
    setCustomerFilter(value);
    setSelectedSaleId(null);
    if (token) {
      loadRecords(token, value);
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
              Cobros y abonos
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra pagos sobre ventas a crédito. Estos abonos reducen la
              deuda del cliente, pero todavía no modifican el cuadre de caja
              automáticamente.
            </p>
          </div>
          <LogoutButton />
        </header>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando cartera..." />
        ) : (
          <>
            <section className="space-y-4 border-b border-slate-200 pb-6">
              <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                <label className="block w-full md:max-w-md">
                  <span className="text-sm font-medium text-slate-700">
                    Filtrar por cliente
                  </span>
                  <select
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
                    value={customerFilter}
                    disabled={isRefreshing}
                    onChange={(event) =>
                      handleCustomerFilter(event.target.value)
                    }
                  >
                    <option value="">Todos los clientes</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.name}
                        {!customer.is_active ? " - Inactivo" : ""}
                      </option>
                    ))}
                  </select>
                </label>
                {isRefreshing ? (
                  <p className="text-sm text-slate-500">Actualizando datos...</p>
                ) : null}
              </div>

              <dl className="grid gap-4 sm:grid-cols-3">
                <div>
                  <dt className="text-xs font-semibold uppercase text-slate-500">
                    Ventas pendientes
                  </dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-950">
                    {pendingSales.length}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-slate-500">
                    Saldo por cobrar
                  </dt>
                  <dd className="mt-1 text-2xl font-semibold text-amber-700">
                    {formatMoney(String(totalPending))}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-slate-500">
                    Abonos registrados
                  </dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-950">
                    {payments.length}
                  </dd>
                </div>
              </dl>
            </section>

            <PendingCreditSales
              sales={pendingSales}
              selectedSaleId={selectedSaleId}
              hasCustomerFilter={Boolean(customerFilter)}
              onSelect={handleSelectSale}
            />

            <CreditPaymentForm
              sales={pendingSales}
              selectedSaleId={selectedSaleId}
              isSubmitting={isSaving}
              onSaleChange={setSelectedSaleId}
              onSubmit={handleCreatePayment}
            />

            <CreditPaymentList
              payments={payments}
              isLoading={isRefreshing}
              hasCustomerFilter={Boolean(customerFilter)}
              voidingPaymentId={voidingPaymentId}
              onVoid={handleVoidPayment}
            />
          </>
        )}
      </div>
    </main>
  );
}

type PendingCreditSalesProps = {
  sales: Sale[];
  selectedSaleId: number | null;
  hasCustomerFilter: boolean;
  onSelect: (saleId: number) => void;
};

function PendingCreditSales({
  sales,
  selectedSaleId,
  hasCustomerFilter,
  onSelect,
}: PendingCreditSalesProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Ventas pendientes de cobro
        </h2>
        <span className="text-sm text-slate-500">{sales.length}</span>
      </div>

      {sales.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasCustomerFilter
            ? "El cliente seleccionado no tiene ventas pendientes."
            : "Todavía no hay ventas a crédito con saldo pendiente."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[920px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Venta</th>
                <th className="px-4 py-3 font-medium">Cliente</th>
                <th className="px-4 py-3 font-medium">Vencimiento</th>
                <th className="px-4 py-3 text-right font-medium">Total</th>
                <th className="px-4 py-3 text-right font-medium">Pagado</th>
                <th className="px-4 py-3 text-right font-medium">Saldo</th>
                <th className="px-4 py-3 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td className="px-4 py-3 align-top font-medium text-slate-950">
                    {sale.sale_number}
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {sale.customer_name_snapshot}
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {sale.due_date ? formatDate(sale.due_date) : "Sin fecha"}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-slate-700">
                    {formatMoney(sale.total_amount)}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-slate-700">
                    {formatMoney(sale.paid_amount)}
                  </td>
                  <td className="px-4 py-3 text-right align-top font-semibold text-amber-700">
                    {formatMoney(sale.balance_amount)}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <button
                      className="font-semibold text-water-700 hover:text-water-500"
                      type="button"
                      onClick={() => onSelect(sale.id)}
                    >
                      {selectedSaleId === sale.id
                        ? "Venta seleccionada"
                        : "Registrar abono"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
  );
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

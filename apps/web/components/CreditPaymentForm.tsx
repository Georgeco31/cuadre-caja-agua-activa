"use client";

import { FormEvent, useMemo, useState } from "react";

import {
  CREDIT_PAYMENT_METHOD_LABELS,
  type CreditPaymentMethod,
  type CreditPaymentPayload,
} from "@/types/creditPayment";
import type { Sale } from "@/types/sale";

type CreditPaymentFormProps = {
  sales: Sale[];
  selectedSaleId: number | null;
  isSubmitting: boolean;
  onSaleChange: (saleId: number | null) => void;
  onSubmit: (
    saleId: number,
    payload: CreditPaymentPayload,
  ) => Promise<boolean>;
};

const paymentMethods = Object.keys(
  CREDIT_PAYMENT_METHOD_LABELS,
) as CreditPaymentMethod[];

export function CreditPaymentForm({
  sales,
  selectedSaleId,
  isSubmitting,
  onSaleChange,
  onSubmit,
}: CreditPaymentFormProps) {
  const [paymentDate, setPaymentDate] = useState(currentDate());
  const [paymentMethod, setPaymentMethod] =
    useState<CreditPaymentMethod>("cash");
  const [amount, setAmount] = useState("");
  const [notes, setNotes] = useState("");
  const [formError, setFormError] = useState("");
  const selectedSale = useMemo(
    () => sales.find((sale) => sale.id === selectedSaleId) ?? null,
    [sales, selectedSaleId],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");

    if (!selectedSale) {
      setFormError("Selecciona una venta a crédito pendiente.");
      return;
    }
    const amountCents = parseMoneyToCents(amount);
    const balanceCents = parseMoneyToCents(selectedSale.balance_amount);
    if (amountCents === null || amountCents <= 0) {
      setFormError("El monto abonado debe ser mayor a 0.");
      return;
    }
    if (balanceCents === null || amountCents > balanceCents) {
      setFormError("El monto abonado no puede superar el saldo actual.");
      return;
    }

    const saved = await onSubmit(selectedSale.id, {
      payment_date: paymentDate,
      amount,
      payment_method: paymentMethod,
      notes: optionalText(notes),
    });
    if (saved) {
      setAmount("");
      setNotes("");
    }
  }

  return (
    <section
      id="credit-payment-form"
      className="rounded-lg border border-slate-200 bg-white shadow-sm"
    >
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar abono
        </h2>
      </div>

      <form className="space-y-5 p-4" onSubmit={handleSubmit}>
        {formError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        ) : null}

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Venta</span>
          <select
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={selectedSaleId ?? ""}
            disabled={isSubmitting || sales.length === 0}
            onChange={(event) => {
              setFormError("");
              onSaleChange(
                event.target.value ? Number(event.target.value) : null,
              );
            }}
          >
            <option value="">Seleccionar venta pendiente</option>
            {sales.map((sale) => (
              <option key={sale.id} value={sale.id}>
                {sale.sale_number} - {sale.customer_name_snapshot} - Saldo {" "}
                {formatMoney(sale.balance_amount)}
              </option>
            ))}
          </select>
        </label>

        {selectedSale ? (
          <dl className="grid gap-4 border-y border-slate-200 py-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs font-semibold uppercase text-slate-500">
                Cliente
              </dt>
              <dd className="mt-1 text-sm font-semibold text-slate-950">
                {selectedSale.customer_name_snapshot}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-slate-500">
                Total de venta
              </dt>
              <dd className="mt-1 text-sm font-semibold text-slate-950">
                {formatMoney(selectedSale.total_amount)}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase text-slate-500">
                Saldo actual
              </dt>
              <dd className="mt-1 text-lg font-semibold text-amber-700">
                {formatMoney(selectedSale.balance_amount)}
              </dd>
            </div>
          </dl>
        ) : (
          <p className="rounded-md bg-slate-50 px-3 py-4 text-sm text-slate-600">
            {sales.length === 0
              ? "No hay ventas a crédito con saldo pendiente."
              : "Selecciona una venta para registrar el abono."}
          </p>
        )}

        <div className="grid gap-4 md:grid-cols-3">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha de pago
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              type="date"
              value={paymentDate}
              disabled={isSubmitting}
              required
              onChange={(event) => setPaymentDate(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Método de pago
            </span>
            <select
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              value={paymentMethod}
              disabled={isSubmitting}
              onChange={(event) =>
                setPaymentMethod(event.target.value as CreditPaymentMethod)
              }
            >
              {paymentMethods.map((method) => (
                <option key={method} value={method}>
                  {CREDIT_PAYMENT_METHOD_LABELS[method]}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="flex items-center justify-between gap-3 text-sm font-medium text-slate-700">
              Monto abonado
              {selectedSale ? (
                <button
                  className="text-xs font-semibold text-water-700 hover:text-water-500 disabled:text-slate-400"
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => setAmount(selectedSale.balance_amount)}
                >
                  Usar saldo total
                </button>
              ) : null}
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              type="number"
              inputMode="decimal"
              min="0.01"
              step="0.01"
              value={amount}
              disabled={isSubmitting || !selectedSale}
              required
              onChange={(event) => setAmount(event.target.value)}
            />
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Observaciones
          </span>
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={notes}
            disabled={isSubmitting}
            onChange={(event) => setNotes(event.target.value)}
          />
        </label>

        <div className="flex justify-end border-t border-slate-200 pt-5">
          <button
            className="h-11 w-full rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
            type="submit"
            disabled={isSubmitting || !selectedSale}
          >
            {isSubmitting ? "Registrando abono..." : "Registrar abono"}
          </button>
        </div>
      </form>
    </section>
  );
}

function currentDate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

function parseMoneyToCents(value: string): number | null {
  const match = value.trim().match(/^(\d+)(?:\.(\d{1,2}))?$/);
  if (!match) {
    return null;
  }
  const units = Number(match[1]);
  const cents = Number((match[2] ?? "").padEnd(2, "0"));
  if (!Number.isSafeInteger(units)) {
    return null;
  }
  return units * 100 + cents;
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

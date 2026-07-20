"use client";

import { useState, type FormEvent } from "react";

import type { RouteCommercialActivity } from "@/types/routeActivity";
import type { RouteClosurePayload } from "@/types/routeClosure";
import type { RouteLoad } from "@/types/routeLoad";

type RouteClosureFormProps = {
  loads: RouteLoad[];
  selectedLoadId: string;
  activity: RouteCommercialActivity | null;
  isLoadingActivity: boolean;
  isSubmitting: boolean;
  onLoadChange: (loadId: string) => void;
  onSubmit: (payload: RouteClosurePayload) => Promise<boolean>;
};

export function RouteClosureForm({
  loads,
  selectedLoadId,
  activity,
  isLoadingActivity,
  isSubmitting,
  onLoadChange,
  onSubmit,
}: RouteClosureFormProps) {
  const [closureDate, setClosureDate] = useState(currentDate());
  const [deliveredCash, setDeliveredCash] = useState("");
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!closureDate) {
      setValidationError("La fecha de cierre es obligatoria.");
      return;
    }
    if (!selectedLoadId || !activity) {
      setValidationError("Selecciona una carga activa.");
      return;
    }
    if (parseMoneyToCents(deliveredCash) === null) {
      setValidationError(
        "El efectivo entregado debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    const saved = await onSubmit({
      closure_date: closureDate,
      route_load_id: Number(selectedLoadId),
      delivered_cash_total: deliveredCash,
      notes: optionalText(notes),
    });
    if (saved) {
      setDeliveredCash("");
      setNotes("");
    }
  }

  const deliveredCents = parseMoneyToCents(deliveredCash);
  const expectedCents = activity
    ? parseMoneyToCents(activity.expected_cash_total)
    : null;
  const estimatedDifference =
    deliveredCents !== null && expectedCents !== null
      ? deliveredCents - expectedCents
      : null;

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar cierre financiero
        </h2>
      </div>
      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 lg:grid-cols-3">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha de cierre
            </span>
            <input
              className={fieldClassName}
              type="date"
              value={closureDate}
              disabled={isSubmitting}
              required
              onChange={(event) => setClosureDate(event.target.value)}
            />
          </label>
          <label className="block lg:col-span-2">
            <span className="text-sm font-medium text-slate-700">
              Carga de ruta
            </span>
            <select
              className={fieldClassName}
              value={selectedLoadId}
              disabled={isSubmitting || isLoadingActivity || loads.length === 0}
              required
              onChange={(event) => {
                setValidationError("");
                setDeliveredCash("");
                onLoadChange(event.target.value);
              }}
            >
              <option value="">Seleccionar carga activa</option>
              {loads.map((load) => (
                <option key={load.id} value={load.id}>
                  {load.load_number} · {load.route_name} · {load.vehicle_name}
                </option>
              ))}
            </select>
          </label>
        </div>

        {isLoadingActivity ? (
          <p className="border-y border-slate-200 py-5 text-sm text-slate-600">
            Consultando actividad comercial...
          </p>
        ) : activity ? (
          <div className="grid gap-4 border-y border-slate-200 py-5 sm:grid-cols-2 lg:grid-cols-4">
            <Amount label="Ventas de contado" value={activity.cash_sales_total} />
            <Amount label="Ventas a crédito" value={activity.credit_sales_total} />
            <Amount label="Cobros y abonos" value={activity.payments_total} />
            <Amount label="Efectivo esperado" value={activity.expected_cash_total} />
          </div>
        ) : (
          <p className="border-y border-slate-200 py-5 text-sm text-slate-600">
            {loads.length === 0
              ? "No hay cargas activas disponibles para cerrar."
              : "Selecciona una carga para consultar sus totales oficiales."}
          </p>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Efectivo entregado
            </span>
            <input
              className={fieldClassName}
              type="number"
              inputMode="decimal"
              min="0"
              step="0.01"
              value={deliveredCash}
              disabled={isSubmitting || !activity}
              required
              onChange={(event) => setDeliveredCash(event.target.value)}
            />
          </label>
          <div>
            <p className="text-sm font-medium text-slate-700">
              Diferencia estimada
            </p>
            <p
              className={`mt-1 flex h-10 items-center text-xl font-semibold ${differenceClassName(estimatedDifference)}`}
            >
              {estimatedDifference === null
                ? "Pendiente"
                : formatCents(estimatedDifference)}
            </p>
          </div>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Observaciones
          </span>
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
            value={notes}
            disabled={isSubmitting}
            onChange={(event) => setNotes(event.target.value)}
          />
        </label>

        <div className="flex justify-end border-t border-slate-200 pt-5">
          <button
            className="h-11 w-full rounded-md bg-water-700 px-5 text-sm font-semibold text-white hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
            type="submit"
            disabled={isSubmitting || !activity || deliveredCents === null}
          >
            {isSubmitting ? "Registrando cierre..." : "Registrar cierre"}
          </button>
        </div>
      </form>
    </section>
  );
}

function Amount({ label, value }: { label: string; value: string }) {
  return (
    <dl>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-xl font-semibold text-slate-950">
        {formatMoney(value)}
      </dd>
    </dl>
  );
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

function formatCents(value: number): string {
  const sign = value < 0 ? "-" : value > 0 ? "+" : "";
  return `${sign}$${(Math.abs(value) / 100).toFixed(2)}`;
}

function differenceClassName(value: number | null): string {
  if (value === null || value === 0) {
    return "text-slate-700";
  }
  return value > 0 ? "text-emerald-700" : "text-red-700";
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
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

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";

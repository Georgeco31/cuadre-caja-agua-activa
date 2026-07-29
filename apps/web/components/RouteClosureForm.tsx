"use client";

import { useState, type FormEvent } from "react";

import {
  getRouteSettlementMessages,
  requiresDifferenceObservation,
  ROUTE_SETTLEMENT_STATUS_LABELS,
} from "@/lib/routeSettlement";
import type { RouteClosurePayload } from "@/types/routeClosure";
import type { RouteLoad } from "@/types/routeLoad";
import type {
  RouteSettlement,
  RouteSettlementStatus,
} from "@/types/routeSettlement";

type RouteClosureFormProps = {
  loads: RouteLoad[];
  selectedLoadId: string;
  settlement: RouteSettlement | null;
  canCreate: boolean;
  isLoadingSettlement: boolean;
  isSubmitting: boolean;
  onLoadChange: (loadId: string) => void;
  onSubmit: (payload: RouteClosurePayload) => Promise<boolean>;
};

export function RouteClosureForm({
  loads,
  selectedLoadId,
  settlement,
  canCreate,
  isLoadingSettlement,
  isSubmitting,
  onLoadChange,
  onSubmit,
}: RouteClosureFormProps) {
  const [closureDate, setClosureDate] = useState(currentDate());
  const [deliveredCash, setDeliveredCash] = useState("");
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState("");

  const deliveredCents = parseMoneyToCents(deliveredCash);
  const expectedCents = settlement
    ? parseMoneyToCents(settlement.expected_cash_amount)
    : null;
  const estimatedDifference =
    deliveredCents !== null && expectedCents !== null
      ? deliveredCents - expectedCents
      : null;
  const needsObservation = settlement
    ? requiresDifferenceObservation(
        settlement.items.map(
          (item) => item.physical_vs_registered_difference,
        ),
        estimatedDifference,
      )
    : false;
  const canRegisterClosure =
    canCreate && settlement !== null && settlement.route_closure_id === null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!closureDate) {
      setValidationError("La fecha de cierre es obligatoria.");
      return;
    }
    if (!selectedLoadId || !settlement) {
      setValidationError("Selecciona una carga activa.");
      return;
    }
    if (settlement.route_closure_id !== null) {
      setValidationError("La carga ya tiene un cierre financiero activo.");
      return;
    }
    if (deliveredCents === null) {
      setValidationError(
        "El efectivo entregado debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }
    if (needsObservation && !notes.trim()) {
      setValidationError(
        "Explica la diferencia de producto o dinero en las observaciones.",
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

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-950">
              Liquidación simple de ruta
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Compara lo cargado, retornado, vendido y entregado sin modificar
              ventas, cobros ni inventario.
            </p>
          </div>
          {settlement ? <StatusBadge status={settlement.status} /> : null}
        </div>
      </div>

      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Carga de ruta
          </span>
          <select
            className={fieldClassName}
            value={selectedLoadId}
            disabled={isSubmitting || isLoadingSettlement || loads.length === 0}
            onChange={(event) => {
              setValidationError("");
              setDeliveredCash("");
              setNotes("");
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

        {isLoadingSettlement ? (
          <p className="border-y border-slate-200 py-5 text-sm text-slate-600">
            Calculando liquidación...
          </p>
        ) : settlement ? (
          <SettlementSummary settlement={settlement} />
        ) : (
          <p className="border-y border-slate-200 py-5 text-sm text-slate-600">
            {loads.length === 0
              ? "No hay cargas activas para consultar."
              : "Selecciona una carga para ver su liquidación."}
          </p>
        )}

        {canRegisterClosure ? (
          <>
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
              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Dinero entregado
                </span>
                <input
                  className={fieldClassName}
                  type="number"
                  inputMode="decimal"
                  min="0"
                  step="0.01"
                  value={deliveredCash}
                  disabled={isSubmitting}
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
                {needsObservation
                  ? "Motivo u observación de la diferencia"
                  : "Observaciones"}
              </span>
              <textarea
                className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                value={notes}
                disabled={isSubmitting}
                required={needsObservation}
                onChange={(event) => setNotes(event.target.value)}
              />
            </label>

            <div className="flex justify-end border-t border-slate-200 pt-5">
              <button
                className="h-11 w-full rounded-md bg-water-700 px-5 text-sm font-semibold text-white hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
                type="submit"
                disabled={isSubmitting || deliveredCents === null}
              >
                {isSubmitting ? "Registrando cierre..." : "Registrar cierre"}
              </button>
            </div>
          </>
        ) : settlement !== null && settlement.route_closure_id !== null ? (
          <p className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
            Cierre financiero {settlement.closure_number} registrado. El dinero
            entregado y la diferencia mostrados son los valores oficiales
            congelados por ese cierre.
          </p>
        ) : !canCreate && settlement ? (
          <p className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
            Vista de consulta. Solo el administrador auditor puede registrar el
            cierre financiero.
          </p>
        ) : null}
      </form>
    </section>
  );
}

function SettlementSummary({ settlement }: { settlement: RouteSettlement }) {
  const messages = getRouteSettlementMessages(settlement);
  return (
    <div className="space-y-5 border-y border-slate-200 py-5">
      <div className="flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-600">
        <span>
          <strong className="text-slate-950">{settlement.load_number}</strong>
        </span>
        <span>{formatDate(settlement.load_date)}</span>
        <span>{settlement.route_name}</span>
        <span>{settlement.vehicle_name}</span>
        {settlement.responsible_name ? (
          <span>Responsable: {settlement.responsible_name}</span>
        ) : null}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric
          label="Cantidad cargada"
          value={formatQuantity(settlement.total_loaded_quantity)}
        />
        <Metric
          label="Cantidad retornada"
          value={formatOptionalQuantity(settlement.total_returned_quantity)}
        />
        <Metric
          label="Vendido físico"
          value={formatOptionalQuantity(settlement.physical_sold_quantity)}
        />
        <Metric
          label="Vendido registrado"
          value={formatQuantity(settlement.registered_sold_quantity)}
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Metric
          label="Diferencia de producto"
          value={formatOptionalSignedQuantity(
            settlement.physical_vs_registered_difference,
          )}
          tone={differenceTone(
            settlement.physical_vs_registered_difference,
          )}
        />
        <Metric
          label="Ventas registradas"
          value={formatMoney(settlement.registered_sales_amount)}
        />
        <Metric
          label="Cobros registrados"
          value={formatMoney(settlement.registered_payments_amount)}
        />
        <Metric
          label="Dinero esperado"
          value={formatMoney(settlement.expected_cash_amount)}
        />
        <Metric
          label="Dinero entregado"
          value={formatOptionalMoney(settlement.delivered_cash_amount)}
        />
      </div>

      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px]">
        <div className="space-y-2">
          {messages.map((message) => (
            <p
              key={message}
              className={messageClassName(settlement.status, message)}
            >
              {message}
            </p>
          ))}
        </div>
        <Metric
          label="Diferencia de dinero"
          value={formatOptionalSignedMoney(settlement.cash_difference)}
          tone={differenceTone(settlement.cash_difference)}
        />
      </div>

      <div className="overflow-x-auto rounded-md border border-slate-200">
        <table className="w-full min-w-[760px] border-collapse text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-3 py-2 font-medium">Producto</th>
              <th className="px-3 py-2 text-right font-medium">Cargado</th>
              <th className="px-3 py-2 text-right font-medium">Retornado</th>
              <th className="px-3 py-2 text-right font-medium">Físico vendido</th>
              <th className="px-3 py-2 text-right font-medium">Registrado</th>
              <th className="px-3 py-2 text-right font-medium">Diferencia</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {settlement.items.map((item) => (
              <tr key={item.product_id}>
                <td className="px-3 py-2 text-slate-950">
                  <span className="font-medium">
                    {item.product_name_snapshot}
                  </span>
                  {item.product_presentation_snapshot ? (
                    <span className="ml-1 text-xs text-slate-500">
                      · {item.product_presentation_snapshot}
                    </span>
                  ) : null}
                </td>
                <td className="px-3 py-2 text-right">
                  {formatQuantity(item.loaded_quantity)}
                </td>
                <td className="px-3 py-2 text-right">
                  {formatOptionalQuantity(item.returned_quantity)}
                </td>
                <td className="px-3 py-2 text-right">
                  {formatOptionalQuantity(item.physical_sold_quantity)}
                </td>
                <td className="px-3 py-2 text-right">
                  {formatQuantity(item.registered_sold_quantity)}
                </td>
                <td
                  className={`px-3 py-2 text-right font-semibold ${differenceTextClassName(item.physical_vs_registered_difference)}`}
                >
                  {formatOptionalSignedQuantity(
                    item.physical_vs_registered_difference,
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {settlement.return_observation ||
      settlement.settlement_observation ? (
        <div className="grid gap-2 text-sm sm:grid-cols-2">
          {settlement.return_observation ? (
            <p className="text-slate-700">
              <strong className="text-slate-950">
                Observación de retorno:{" "}
              </strong>
              {settlement.return_observation}
            </p>
          ) : null}
          {settlement.settlement_observation ? (
            <p className="text-slate-700">
              <strong className="text-slate-950">
                Observación de cierre:{" "}
              </strong>
              {settlement.settlement_observation}
            </p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function StatusBadge({ status }: { status: RouteSettlementStatus }) {
  const className =
    status === "balanced"
      ? "bg-emerald-50 text-emerald-700"
      : status === "with_difference"
        ? "bg-red-50 text-red-700"
        : "bg-amber-50 text-amber-800";
  return (
    <span
      className={`inline-flex w-fit rounded-md px-2.5 py-1 text-xs font-semibold ${className}`}
    >
      {ROUTE_SETTLEMENT_STATUS_LABELS[status]}
    </span>
  );
}

function Metric({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "difference";
}) {
  return (
    <dl className="rounded-md bg-slate-50 px-3 py-3">
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd
        className={`mt-1 text-xl font-semibold ${
          tone === "difference" ? "text-red-700" : "text-slate-950"
        }`}
      >
        {value}
      </dd>
    </dl>
  );
}

function messageClassName(
  status: RouteSettlementStatus,
  message: string,
): string {
  if (status === "balanced") {
    return noticeClassName("emerald");
  }
  if (message.includes("diferencia")) {
    return noticeClassName("red");
  }
  return noticeClassName("amber");
}

function noticeClassName(tone: "emerald" | "red" | "amber"): string {
  const colors = {
    emerald: "border-emerald-200 bg-emerald-50 text-emerald-700",
    red: "border-red-200 bg-red-50 text-red-700",
    amber: "border-amber-200 bg-amber-50 text-amber-900",
  };
  return `rounded-md border px-3 py-2 text-sm ${colors[tone]}`;
}

function differenceTone(value: string | null): "default" | "difference" {
  return isNonZero(value) ? "difference" : "default";
}

function differenceTextClassName(value: string | null): string {
  return isNonZero(value) ? "text-red-700" : "text-slate-700";
}

function isNonZero(value: string | null): boolean {
  const amount = value === null ? 0 : Number(value);
  return Number.isFinite(amount) && amount !== 0;
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
  return "text-red-700";
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

function formatOptionalMoney(value: string | null): string {
  return value === null ? "Pendiente" : formatMoney(value);
}

function formatOptionalSignedMoney(value: string | null): string {
  if (value === null) {
    return "Pendiente";
  }
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "$0.00";
  }
  return `${amount > 0 ? "+" : ""}$${amount.toFixed(2)}`;
}

function formatQuantity(value: string): string {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "0";
  }
  return amount.toLocaleString("es-EC", { maximumFractionDigits: 3 });
}

function formatOptionalQuantity(value: string | null): string {
  return value === null ? "Pendiente" : formatQuantity(value);
}

function formatOptionalSignedQuantity(value: string | null): string {
  if (value === null) {
    return "Pendiente";
  }
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "0";
  }
  const formatted = Math.abs(amount).toLocaleString("es-EC", {
    maximumFractionDigits: 3,
  });
  return `${amount > 0 ? "+" : amount < 0 ? "-" : ""}${formatted}`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
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

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";

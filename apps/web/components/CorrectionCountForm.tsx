"use client";

import { FormEvent, useState } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import type { CorrectionCountItemPayload } from "@/types/correction";
import type { Denomination } from "@/types/denomination";

type CorrectionCountFormProps = {
  denominations: Denomination[];
  disabled: boolean;
  isSubmitting: boolean;
  onSubmit: (payload: CorrectionCountItemPayload) => Promise<boolean>;
};

export function CorrectionCountForm({
  denominations,
  disabled,
  isSubmitting,
  onSubmit,
}: CorrectionCountFormProps) {
  const [denominationId, setDenominationId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [formError, setFormError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");

    const selectedDenominationId = Number(denominationId);
    const normalizedQuantity = quantity.trim();
    const normalizedReason = reason.trim();

    if (!Number.isInteger(selectedDenominationId) || selectedDenominationId <= 0) {
      setFormError("Selecciona una denominacion.");
      return;
    }

    if (!/^\d+$/.test(normalizedQuantity)) {
      setFormError("Ingresa una cantidad mayor o igual a cero.");
      return;
    }

    if (!normalizedReason) {
      setFormError("Ingresa el motivo de correccion.");
      return;
    }

    const wasSaved = await onSubmit({
      denomination_id: selectedDenominationId,
      quantity: Number(normalizedQuantity),
      reason: normalizedReason,
    });

    if (!wasSaved) {
      return;
    }

    setDenominationId("");
    setQuantity("");
    setReason("");
  }

  return (
    <section
      aria-labelledby="correction-count-form-title"
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="mb-4">
        <p className="text-sm font-medium text-water-700">Conteo</p>
        <h3
          id="correction-count-form-title"
          className="mt-1 text-lg font-semibold text-slate-950"
        >
          Corregir cantidad
        </h3>
      </div>

      {formError ? (
        <div className="mb-4">
          <ErrorMessage message={formError} />
        </div>
      ) : null}

      <form className="grid gap-4" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Denominacion
          </span>
          <select
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            value={denominationId}
            onChange={(event) => setDenominationId(event.target.value)}
            disabled={disabled || isSubmitting}
            required
          >
            <option value="">Selecciona una denominacion</option>
            {denominations.map((denomination) => (
              <option key={denomination.id} value={denomination.id}>
                {denomination.label} - {formatMoney(denomination.value)}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Nueva cantidad
          </span>
          <input
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            type="number"
            inputMode="numeric"
            min={0}
            step={1}
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
            disabled={disabled || isSubmitting}
            required
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Motivo de correccion
          </span>
          <textarea
            className="mt-1 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            disabled={disabled || isSubmitting}
            required
          />
        </label>

        <button
          className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
          type="submit"
          disabled={disabled || isSubmitting}
        >
          {disabled
            ? "Solo cuadres cerrados"
            : isSubmitting
              ? "Guardando..."
              : "Guardar correccion"}
        </button>
      </form>
    </section>
  );
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

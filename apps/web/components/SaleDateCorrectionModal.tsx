"use client";

import { useEffect, useState, type FormEvent } from "react";

import { validateSaleDateCorrectionForm } from "@/lib/saleDateCorrection";
import type {
  CashSale,
  SaleDateCorrectionPayload,
} from "@/types/sale";

type SaleDateCorrectionModalProps = {
  sale: CashSale;
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (payload: SaleDateCorrectionPayload) => Promise<boolean>;
};

export function SaleDateCorrectionModal({
  sale,
  isSubmitting,
  onCancel,
  onSubmit,
}: SaleDateCorrectionModalProps) {
  const [newSaleDate, setNewSaleDate] = useState(sale.sale_date);
  const [reason, setReason] = useState("");
  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    setNewSaleDate(sale.sale_date);
    setReason("");
    setValidationError("");
  }, [sale.id, sale.sale_date]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const error = validateSaleDateCorrectionForm(
      sale.sale_date,
      newSaleDate,
      reason,
    );
    if (error) {
      setValidationError(error);
      return;
    }

    setValidationError("");
    await onSubmit({
      new_sale_date: newSaleDate,
      reason: reason.trim(),
    });
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 px-4 py-6"
      role="presentation"
    >
      <section
        aria-labelledby="sale-date-correction-title"
        aria-modal="true"
        className="w-full max-w-lg rounded-lg border border-slate-200 bg-white p-5 shadow-xl"
        role="dialog"
      >
        <h2
          className="text-xl font-semibold text-slate-950"
          id="sale-date-correction-title"
        >
          Corregir fecha
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Venta <span className="font-semibold">{sale.sale_number}</span>. Solo
          cambiará la fecha de la venta; cliente, productos, montos y pagos se
          conservarán.
        </p>

        <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-700">
            Fecha actual
            <input
              className={`${fieldClassName} bg-slate-100 text-slate-500`}
              type="date"
              value={sale.sale_date}
              disabled
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Nueva fecha
            <input
              className={fieldClassName}
              type="date"
              value={newSaleDate}
              disabled={isSubmitting}
              required
              onChange={(event) => setNewSaleDate(event.target.value)}
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Motivo de corrección
            <textarea
              className={`${fieldClassName} min-h-24 resize-y`}
              value={reason}
              disabled={isSubmitting}
              maxLength={1000}
              required
              onChange={(event) => setReason(event.target.value)}
            />
          </label>

          {validationError ? (
            <p
              className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
              role="alert"
            >
              {validationError}
            </p>
          ) : null}

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:border-slate-400 disabled:cursor-not-allowed disabled:text-slate-400"
              type="button"
              disabled={isSubmitting}
              onClick={onCancel}
            >
              Cancelar
            </button>
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Corrigiendo..." : "Confirmar corrección"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

const fieldClassName =
  "mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed";

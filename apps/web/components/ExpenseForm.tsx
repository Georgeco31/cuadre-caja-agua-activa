"use client";

import { FormEvent, useState } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import {
  isValidMoneyInputDraft,
  parseMoneyInputToCents,
} from "@/lib/money";
import type { ExpensePayload, ExpenseTiming } from "@/types/expense";

type ExpenseFormProps = {
  title?: string;
  eyebrow?: string;
  helpText?: string;
  disabled: boolean;
  isSubmitting: boolean;
  expenseTiming?: ExpenseTiming;
  onSubmit: (payload: ExpensePayload) => Promise<boolean>;
};

export function ExpenseForm({
  title = "Registrar gasto",
  eyebrow = "Gastos del dia",
  helpText,
  disabled,
  isSubmitting,
  expenseTiming = "after_count",
  onSubmit,
}: ExpenseFormProps) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [expenseDate, setExpenseDate] = useState("");
  const [notes, setNotes] = useState("");
  const [formError, setFormError] = useState("");
  const titleId = `expense-form-${expenseTiming}-title`;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");

    const normalizedDescription = description.trim();
    const normalizedAmount = amount.trim();
    if (!normalizedDescription) {
      setFormError("Ingresa la descripción del gasto.");
      return;
    }

    const amountCents = parseMoneyInputToCents(normalizedAmount);
    if (amountCents === null || amountCents <= 0) {
      setFormError("Ingresa un monto mayor a cero.");
      return;
    }

    const wasSaved = await onSubmit({
      description: normalizedDescription,
      amount: normalizedAmount,
      expense_timing: expenseTiming,
      ...(category.trim() ? { category: category.trim() } : {}),
      ...(expenseDate ? { expense_date: expenseDate } : {}),
      ...(notes.trim() ? { notes: notes.trim() } : {}),
    });

    if (!wasSaved) {
      return;
    }

    setDescription("");
    setAmount("");
    setCategory("");
    setExpenseDate("");
    setNotes("");
  }

  return (
    <section
      aria-labelledby={titleId}
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="mb-4">
        <p className="text-sm font-medium text-water-700">{eyebrow}</p>
        <h2
          id={titleId}
          className="mt-1 text-lg font-semibold text-slate-950"
        >
          {title}
        </h2>
        {helpText ? (
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {helpText}
          </p>
        ) : null}
      </div>

      {formError ? (
        <div className="mb-4">
          <ErrorMessage message={formError} />
        </div>
      ) : null}

      <form className="grid gap-4" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Descripción
          </span>
          <input
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            disabled={disabled || isSubmitting}
            required
          />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Monto</span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
              type="text"
              inputMode="decimal"
              placeholder="0.00"
              value={amount}
              onChange={(event) => {
                if (isValidMoneyInputDraft(event.target.value)) {
                  setAmount(event.target.value);
                }
              }}
              disabled={disabled || isSubmitting}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Categoría opcional
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              disabled={disabled || isSubmitting}
            />
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Fecha del gasto opcional
          </span>
          <input
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            type="date"
            value={expenseDate}
            onChange={(event) => setExpenseDate(event.target.value)}
            disabled={disabled || isSubmitting}
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Observación opcional
          </span>
          <textarea
            className="mt-1 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            disabled={disabled || isSubmitting}
          />
        </label>

        <button
          className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
          type="submit"
          disabled={disabled || isSubmitting}
        >
          {disabled
            ? "Cuadre cerrado"
            : isSubmitting
              ? "Registrando..."
              : "Registrar gasto"}
        </button>
      </form>
    </section>
  );
}

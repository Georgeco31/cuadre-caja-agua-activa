"use client";

import { FormEvent } from "react";

import type {
  CashSummaryReportFilters,
  CashSummaryReportStatus,
} from "@/types/report";

type CashSummaryFiltersProps = {
  filters: CashSummaryReportFilters;
  disabled: boolean;
  onChange: (filters: CashSummaryReportFilters) => void;
  onSubmit: () => void;
  onClear: () => void;
};

export function CashSummaryFilters({
  filters,
  disabled,
  onChange,
  onSubmit,
  onClear,
}: CashSummaryFiltersProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form
      className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[180px_180px_180px_auto_auto] sm:items-end"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm font-medium text-slate-700">Desde</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
          type="date"
          value={filters.date_from ?? ""}
          onChange={(event) =>
            onChange({ ...filters, date_from: event.target.value })
          }
          disabled={disabled}
        />
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Hasta</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
          type="date"
          value={filters.date_to ?? ""}
          onChange={(event) =>
            onChange({ ...filters, date_to: event.target.value })
          }
          disabled={disabled}
        />
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Estado</span>
        <select
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
          value={filters.status ?? ""}
          onChange={(event) =>
            onChange({
              ...filters,
              status: event.target.value as CashSummaryReportStatus | "",
            })
          }
          disabled={disabled}
        >
          <option value="">Todos</option>
          <option value="open">open</option>
          <option value="closed">closed</option>
        </select>
      </label>

      <button
        className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
        type="submit"
        disabled={disabled}
      >
        Aplicar filtros
      </button>

      <button
        className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
        type="button"
        onClick={onClear}
        disabled={disabled}
      >
        Limpiar
      </button>
    </form>
  );
}

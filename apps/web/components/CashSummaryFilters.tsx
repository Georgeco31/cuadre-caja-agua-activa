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
      className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:p-5"
      onSubmit={handleSubmit}
    >
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
          Filtros
        </p>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">
          Acota los cuadres incluidos
        </h2>
      </div>

      <div className="mt-4 grid min-w-0 gap-4 md:grid-cols-3 xl:grid-cols-[minmax(170px,220px)_minmax(170px,220px)_minmax(170px,220px)_auto] xl:items-end">
        <label className="block min-w-0">
          <span className="text-sm font-semibold text-slate-800">Desde</span>
          <input
            className="mt-2 h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
            type="date"
            value={filters.date_from ?? ""}
            onChange={(event) =>
              onChange({ ...filters, date_from: event.target.value })
            }
            disabled={disabled}
          />
        </label>

        <label className="block min-w-0">
          <span className="text-sm font-semibold text-slate-800">Hasta</span>
          <input
            className="mt-2 h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
            type="date"
            value={filters.date_to ?? ""}
            onChange={(event) =>
              onChange({ ...filters, date_to: event.target.value })
            }
            disabled={disabled}
          />
        </label>

        <label className="block min-w-0">
          <span className="text-sm font-semibold text-slate-800">Estado</span>
          <select
            className="mt-2 h-11 w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
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
            <option value="open">Abiertos</option>
            <option value="closed">Cerrados</option>
          </select>
        </label>

        <div className="grid gap-3 sm:grid-cols-2 md:col-span-3 xl:col-span-1">
          <button
            className="min-h-11 rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
            type="submit"
            disabled={disabled}
          >
            Aplicar filtros
          </button>

          <button
            className="min-h-11 rounded-xl border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
            type="button"
            onClick={onClear}
            disabled={disabled}
          >
            Limpiar
          </button>
        </div>
      </div>
    </form>
  );
}

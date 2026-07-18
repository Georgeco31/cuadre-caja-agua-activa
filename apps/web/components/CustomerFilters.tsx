import type { FormEvent } from "react";

import {
  CUSTOMER_TYPE_LABELS,
  type CustomerType,
} from "@/types/customer";

export type CustomerFilterValues = {
  search: string;
  isActive: "" | "active" | "inactive";
  customerType: CustomerType | "";
  sector: string;
};

type CustomerFiltersProps = {
  filters: CustomerFilterValues;
  disabled?: boolean;
  onChange: (filters: CustomerFilterValues) => void;
  onSubmit: () => void;
  onClear: () => void;
};

const customerTypes = Object.keys(CUSTOMER_TYPE_LABELS) as CustomerType[];

export function CustomerFilters({
  filters,
  disabled = false,
  onChange,
  onSubmit,
  onClear,
}: CustomerFiltersProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form
      className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-2 lg:grid-cols-[minmax(220px,2fr)_150px_170px_minmax(150px,1fr)_auto_auto] lg:items-end"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm font-medium text-slate-700">Buscar</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          type="search"
          placeholder="Nombre, teléfono, sector o tipo"
          value={filters.search}
          disabled={disabled}
          onChange={(event) =>
            onChange({ ...filters, search: event.target.value })
          }
        />
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Estado</span>
        <select
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          value={filters.isActive}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              isActive: event.target.value as CustomerFilterValues["isActive"],
            })
          }
        >
          <option value="">Todos</option>
          <option value="active">Activos</option>
          <option value="inactive">Inactivos</option>
        </select>
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Tipo</span>
        <select
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          value={filters.customerType}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              customerType: event.target.value as CustomerType | "",
            })
          }
        >
          <option value="">Todos</option>
          {customerTypes.map((type) => (
            <option key={type} value={type}>
              {CUSTOMER_TYPE_LABELS[type]}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Sector</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          type="text"
          value={filters.sector}
          disabled={disabled}
          onChange={(event) =>
            onChange({ ...filters, sector: event.target.value })
          }
        />
      </label>

      <button
        className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
        type="submit"
        disabled={disabled}
      >
        Buscar
      </button>
      <button
        className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
        type="button"
        disabled={disabled}
        onClick={onClear}
      >
        Limpiar
      </button>
    </form>
  );
}

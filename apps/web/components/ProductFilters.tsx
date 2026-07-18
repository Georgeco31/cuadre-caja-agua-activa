import type { FormEvent } from "react";

import {
  PRODUCT_CATEGORY_LABELS,
  PRODUCT_UNIT_LABELS,
  type ProductCategory,
  type ProductUnit,
} from "@/types/product";

export type ProductFilterValues = {
  search: string;
  isActive: "" | "active" | "inactive";
  category: ProductCategory | "";
  unit: ProductUnit | "";
};

type ProductFiltersProps = {
  filters: ProductFilterValues;
  disabled?: boolean;
  onChange: (filters: ProductFilterValues) => void;
  onSubmit: () => void;
  onClear: () => void;
};

const categories = Object.keys(PRODUCT_CATEGORY_LABELS) as ProductCategory[];
const units = Object.keys(PRODUCT_UNIT_LABELS) as ProductUnit[];

export function ProductFilters({
  filters,
  disabled = false,
  onChange,
  onSubmit,
  onClear,
}: ProductFiltersProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form
      className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-2 lg:grid-cols-[minmax(220px,2fr)_150px_170px_150px_auto_auto] lg:items-end"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm font-medium text-slate-700">Buscar</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          type="search"
          placeholder="Nombre, SKU, categoría o presentación"
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
              isActive: event.target.value as ProductFilterValues["isActive"],
            })
          }
        >
          <option value="">Todos</option>
          <option value="active">Activos</option>
          <option value="inactive">Inactivos</option>
        </select>
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Categoría</span>
        <select
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          value={filters.category}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              category: event.target.value as ProductCategory | "",
            })
          }
        >
          <option value="">Todas</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {PRODUCT_CATEGORY_LABELS[category]}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Unidad</span>
        <select
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          value={filters.unit}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              unit: event.target.value as ProductUnit | "",
            })
          }
        >
          <option value="">Todas</option>
          {units.map((unit) => (
            <option key={unit} value={unit}>
              {PRODUCT_UNIT_LABELS[unit]}
            </option>
          ))}
        </select>
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

import type { FormEvent } from "react";

export type DeliveryRouteFilterValues = {
  search: string;
  isActive: "" | "active" | "inactive";
  zone: string;
  sector: string;
};

type DeliveryRouteFiltersProps = {
  filters: DeliveryRouteFilterValues;
  disabled?: boolean;
  onChange: (filters: DeliveryRouteFilterValues) => void;
  onSubmit: () => void;
  onClear: () => void;
};

export function DeliveryRouteFilters({
  filters,
  disabled = false,
  onChange,
  onSubmit,
  onClear,
}: DeliveryRouteFiltersProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form
      className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-2 lg:grid-cols-[minmax(220px,2fr)_150px_180px_180px_auto_auto] lg:items-end"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm font-medium text-slate-700">Buscar</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          type="search"
          placeholder="Nombre, código, zona, sector o días"
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
              isActive: event.target.value as DeliveryRouteFilterValues["isActive"],
            })
          }
        >
          <option value="">Todos</option>
          <option value="active">Activas</option>
          <option value="inactive">Inactivas</option>
        </select>
      </label>

      <FilterTextField
        label="Zona"
        value={filters.zone}
        disabled={disabled}
        onChange={(value) => onChange({ ...filters, zone: value })}
      />
      <FilterTextField
        label="Sector"
        value={filters.sector}
        disabled={disabled}
        onChange={(value) => onChange({ ...filters, sector: value })}
      />

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

type FilterTextFieldProps = {
  label: string;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
};

function FilterTextField({
  label,
  value,
  disabled,
  onChange,
}: FilterTextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        type="text"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

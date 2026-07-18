import type { FormEvent } from "react";

import {
  EMPLOYEE_TYPE_LABELS,
  type EmployeeType,
} from "@/types/employee";

export type EmployeeFilterValues = {
  search: string;
  isActive: "" | "active" | "inactive";
  employeeType: EmployeeType | "";
  jobPosition: string;
};

type EmployeeFiltersProps = {
  filters: EmployeeFilterValues;
  disabled?: boolean;
  onChange: (filters: EmployeeFilterValues) => void;
  onSubmit: () => void;
  onClear: () => void;
};

const employeeTypes = Object.keys(EMPLOYEE_TYPE_LABELS) as EmployeeType[];

export function EmployeeFilters({
  filters,
  disabled = false,
  onChange,
  onSubmit,
  onClear,
}: EmployeeFiltersProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form
      className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-2 lg:grid-cols-[minmax(220px,2fr)_150px_170px_180px_auto_auto] lg:items-end"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm font-medium text-slate-700">Buscar</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          type="search"
          placeholder="Nombre, identificación, teléfono, cargo o tipo"
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
              isActive: event.target.value as EmployeeFilterValues["isActive"],
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
          value={filters.employeeType}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              employeeType: event.target.value as EmployeeType | "",
            })
          }
        >
          <option value="">Todos</option>
          {employeeTypes.map((employeeType) => (
            <option key={employeeType} value={employeeType}>
              {EMPLOYEE_TYPE_LABELS[employeeType]}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Cargo</span>
        <input
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          type="text"
          value={filters.jobPosition}
          disabled={disabled}
          onChange={(event) =>
            onChange({ ...filters, jobPosition: event.target.value })
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

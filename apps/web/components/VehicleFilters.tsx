import type { FormEvent } from "react";

import {
  FUEL_TYPE_LABELS,
  VEHICLE_TYPE_LABELS,
  type FuelType,
  type VehicleType,
} from "@/types/vehicle";

export type VehicleFilterValues = {
  search: string;
  isActive: "" | "active" | "inactive";
  vehicleType: VehicleType | "";
  fuelType: FuelType | "";
};

type VehicleFiltersProps = {
  filters: VehicleFilterValues;
  disabled?: boolean;
  onChange: (filters: VehicleFilterValues) => void;
  onSubmit: () => void;
  onClear: () => void;
};

const vehicleTypes = Object.keys(VEHICLE_TYPE_LABELS) as VehicleType[];
const fuelTypes = Object.keys(FUEL_TYPE_LABELS) as FuelType[];

export function VehicleFilters({
  filters,
  disabled = false,
  onChange,
  onSubmit,
  onClear,
}: VehicleFiltersProps) {
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
          placeholder="Nombre, placa, código, tipo, marca o modelo"
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
              isActive: event.target.value as VehicleFilterValues["isActive"],
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
          value={filters.vehicleType}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              vehicleType: event.target.value as VehicleType | "",
            })
          }
        >
          <option value="">Todos</option>
          {vehicleTypes.map((vehicleType) => (
            <option key={vehicleType} value={vehicleType}>
              {VEHICLE_TYPE_LABELS[vehicleType]}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="text-sm font-medium text-slate-700">Combustible</span>
        <select
          className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          value={filters.fuelType}
          disabled={disabled}
          onChange={(event) =>
            onChange({
              ...filters,
              fuelType: event.target.value as FuelType | "",
            })
          }
        >
          <option value="">Todos</option>
          {fuelTypes.map((fuelType) => (
            <option key={fuelType} value={fuelType}>
              {FUEL_TYPE_LABELS[fuelType]}
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

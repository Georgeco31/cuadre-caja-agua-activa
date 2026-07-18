"use client";

import { useState, type FormEvent } from "react";

import {
  FUEL_TYPE_LABELS,
  VEHICLE_TYPE_LABELS,
  type FuelType,
  type Vehicle,
  type VehiclePayload,
  type VehicleType,
} from "@/types/vehicle";

type VehicleFormProps = {
  vehicle?: Vehicle | null;
  isSubmitting?: boolean;
  onSubmit: (payload: VehiclePayload) => Promise<boolean>;
  onCancel: () => void;
};

type VehicleFormValues = {
  code: string;
  name: string;
  plate: string;
  vehicleType: VehicleType;
  brand: string;
  model: string;
  year: string;
  color: string;
  fuelType: FuelType;
  capacityReference: string;
  referenceDriver: string;
  notes: string;
};

const vehicleTypes = Object.keys(VEHICLE_TYPE_LABELS) as VehicleType[];
const fuelTypes = Object.keys(FUEL_TYPE_LABELS) as FuelType[];

export function VehicleForm({
  vehicle = null,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: VehicleFormProps) {
  const [values, setValues] = useState<VehicleFormValues>(() =>
    buildInitialValues(vehicle),
  );
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    const name = values.name.trim();
    if (!name) {
      setValidationError("El nombre o alias del vehículo es obligatorio.");
      return;
    }

    const yearValue = values.year.trim();
    const year = yearValue ? Number(yearValue) : null;
    if (
      yearValue &&
      (!/^\d{4}$/.test(yearValue) || year === null || year < 1900 || year > 2100)
    ) {
      setValidationError("El año debe ser un entero entre 1900 y 2100.");
      return;
    }

    await onSubmit({
      code: optionalText(values.code),
      name,
      plate: optionalText(values.plate),
      vehicle_type: values.vehicleType,
      brand: optionalText(values.brand),
      model: optionalText(values.model),
      year,
      color: optionalText(values.color),
      fuel_type: values.fuelType,
      capacity_reference: optionalText(values.capacityReference),
      reference_driver: optionalText(values.referenceDriver),
      notes: optionalText(values.notes),
    });
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          {vehicle ? "Editar vehículo" : "Registrar vehículo"}
        </h2>
      </div>

      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          <TextField
            label="Código interno"
            value={values.code}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, code: value })}
          />
          <TextField
            label="Nombre o alias"
            value={values.name}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, name: value })}
          />
          <TextField
            label="Placa"
            value={values.plate}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, plate: value })}
          />
          <SelectField
            label="Tipo de vehículo"
            value={values.vehicleType}
            disabled={isSubmitting}
            options={vehicleTypes.map((vehicleType) => ({
              value: vehicleType,
              label: VEHICLE_TYPE_LABELS[vehicleType],
            }))}
            onChange={(value) =>
              setValues({ ...values, vehicleType: value as VehicleType })
            }
          />
          <TextField
            label="Marca"
            value={values.brand}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, brand: value })}
          />
          <TextField
            label="Modelo"
            value={values.model}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, model: value })}
          />
          <YearField
            label="Año"
            value={values.year}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, year: value })}
          />
          <TextField
            label="Color"
            value={values.color}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, color: value })}
          />
          <SelectField
            label="Tipo de combustible"
            value={values.fuelType}
            disabled={isSubmitting}
            options={fuelTypes.map((fuelType) => ({
              value: fuelType,
              label: FUEL_TYPE_LABELS[fuelType],
            }))}
            onChange={(value) =>
              setValues({ ...values, fuelType: value as FuelType })
            }
          />
          <TextField
            label="Capacidad referencial"
            value={values.capacityReference}
            disabled={isSubmitting}
            onChange={(value) =>
              setValues({ ...values, capacityReference: value })
            }
          />
          <TextField
            label="Chofer de referencia"
            value={values.referenceDriver}
            disabled={isSubmitting}
            onChange={(value) =>
              setValues({ ...values, referenceDriver: value })
            }
          />
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Observaciones</span>
          <textarea
            className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={values.notes}
            disabled={isSubmitting}
            onChange={(event) =>
              setValues({ ...values, notes: event.target.value })
            }
          />
        </label>

        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
            type="button"
            disabled={isSubmitting}
            onClick={onCancel}
          >
            Cancelar
          </button>
          <button
            className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Guardando..."
              : vehicle
                ? "Guardar cambios"
                : "Registrar vehículo"}
          </button>
        </div>
      </form>
    </section>
  );
}

type TextFieldProps = {
  label: string;
  value: string;
  required?: boolean;
  disabled?: boolean;
  onChange: (value: string) => void;
};

function TextField({
  label,
  value,
  required = false,
  disabled = false,
  onChange,
}: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        type="text"
        value={value}
        required={required}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function YearField(props: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{props.label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        type="number"
        inputMode="numeric"
        min="1900"
        max="2100"
        step="1"
        value={props.value}
        disabled={props.disabled}
        onChange={(event) => props.onChange(event.target.value)}
      />
    </label>
  );
}

type SelectFieldProps = {
  label: string;
  value: string;
  disabled?: boolean;
  options: Array<{ value: string; label: string }>;
  onChange: (value: string) => void;
};

function SelectField({
  label,
  value,
  disabled = false,
  options,
  onChange,
}: SelectFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <select
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function buildInitialValues(vehicle: Vehicle | null): VehicleFormValues {
  return {
    code: vehicle?.code ?? "",
    name: vehicle?.name ?? "",
    plate: vehicle?.plate ?? "",
    vehicleType: vehicle?.vehicle_type ?? "other",
    brand: vehicle?.brand ?? "",
    model: vehicle?.model ?? "",
    year: vehicle?.year ? String(vehicle.year) : "",
    color: vehicle?.color ?? "",
    fuelType: vehicle?.fuel_type ?? "other",
    capacityReference: vehicle?.capacity_reference ?? "",
    referenceDriver: vehicle?.reference_driver ?? "",
    notes: vehicle?.notes ?? "",
  };
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

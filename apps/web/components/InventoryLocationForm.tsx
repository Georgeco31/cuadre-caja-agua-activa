"use client";

import { useState, type FormEvent } from "react";

import {
  INVENTORY_LOCATION_TYPE_LABELS,
  type InventoryLocation,
  type InventoryLocationPayload,
  type InventoryLocationType,
} from "@/types/inventory";
import type { Vehicle } from "@/types/vehicle";

type InventoryLocationFormProps = {
  location?: InventoryLocation | null;
  vehicles: Vehicle[];
  isSubmitting?: boolean;
  onSubmit: (payload: InventoryLocationPayload) => Promise<boolean>;
  onCancel: () => void;
};

type FormValues = {
  code: string;
  name: string;
  locationType: InventoryLocationType;
  vehicleId: string;
  description: string;
  notes: string;
};

const locationTypes = Object.keys(
  INVENTORY_LOCATION_TYPE_LABELS,
) as InventoryLocationType[];

export function InventoryLocationForm({
  location = null,
  vehicles,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: InventoryLocationFormProps) {
  const [values, setValues] = useState<FormValues>(() =>
    buildInitialValues(location),
  );
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    const name = values.name.trim();
    if (!name) {
      setValidationError("El nombre de la ubicación es obligatorio.");
      return;
    }

    const saved = await onSubmit({
      code: optionalText(values.code),
      name,
      location_type: values.locationType,
      vehicle_id:
        values.locationType === "vehicle" && values.vehicleId
          ? Number(values.vehicleId)
          : null,
      description: optionalText(values.description),
      notes: optionalText(values.notes),
    });

    if (saved && !location) {
      setValues(buildInitialValues(null));
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          {location ? "Editar ubicación" : "Nueva ubicación"}
        </h2>
      </div>

      <form className="space-y-4 p-4" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          <TextField
            label="Código"
            value={values.code}
            disabled={isSubmitting}
            onChange={(code) => setValues({ ...values, code })}
          />
          <TextField
            label="Nombre"
            value={values.name}
            required
            disabled={isSubmitting}
            onChange={(name) => setValues({ ...values, name })}
          />
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Tipo de ubicación
            </span>
            <select
              className={fieldClassName}
              value={values.locationType}
              disabled={isSubmitting}
              onChange={(event) =>
                setValues({
                  ...values,
                  locationType: event.target.value as InventoryLocationType,
                  vehicleId:
                    event.target.value === "vehicle" ? values.vehicleId : "",
                })
              }
            >
              {locationTypes.map((locationType) => (
                <option key={locationType} value={locationType}>
                  {INVENTORY_LOCATION_TYPE_LABELS[locationType]}
                </option>
              ))}
            </select>
          </label>

          {values.locationType === "vehicle" ? (
            <label className="block">
              <span className="text-sm font-medium text-slate-700">
                Vehículo relacionado
              </span>
              <select
                className={fieldClassName}
                value={values.vehicleId}
                disabled={isSubmitting}
                onChange={(event) =>
                  setValues({ ...values, vehicleId: event.target.value })
                }
              >
                <option value="">Sin vehículo relacionado</option>
                {vehicles.map((vehicle) => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.name}
                    {vehicle.plate ? ` · ${vehicle.plate}` : ""}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
        </div>

        <TextAreaField
          label="Descripción"
          value={values.description}
          disabled={isSubmitting}
          onChange={(description) => setValues({ ...values, description })}
        />
        <TextAreaField
          label="Observaciones"
          value={values.notes}
          disabled={isSubmitting}
          onChange={(notes) => setValues({ ...values, notes })}
        />

        <div className="flex flex-col-reverse gap-2 border-t border-slate-200 pt-4 sm:flex-row sm:justify-end">
          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:text-slate-400"
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
              : location
                ? "Guardar cambios"
                : "Crear ubicación"}
          </button>
        </div>
      </form>
    </section>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";

type FieldProps = {
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
}: FieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className={fieldClassName}
        type="text"
        value={value}
        required={required}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function TextAreaField({
  label,
  value,
  disabled = false,
  onChange,
}: FieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <textarea
        className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function buildInitialValues(location: InventoryLocation | null): FormValues {
  return {
    code: location?.code ?? "",
    name: location?.name ?? "",
    locationType: location?.location_type ?? "warehouse",
    vehicleId: location?.vehicle_id ? String(location.vehicle_id) : "",
    description: location?.description ?? "",
    notes: location?.notes ?? "",
  };
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}


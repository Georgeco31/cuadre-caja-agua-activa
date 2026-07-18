"use client";

import { useState, type FormEvent } from "react";

import type {
  DeliveryRoute,
  DeliveryRoutePayload,
} from "@/types/deliveryRoute";

type DeliveryRouteFormProps = {
  deliveryRoute?: DeliveryRoute | null;
  isSubmitting?: boolean;
  onSubmit: (payload: DeliveryRoutePayload) => Promise<boolean>;
  onCancel: () => void;
};

type DeliveryRouteFormValues = {
  code: string;
  name: string;
  description: string;
  zone: string;
  sector: string;
  serviceDays: string;
  referenceDriver: string;
  referenceVehicle: string;
  expectedDailyCash: string;
  notes: string;
};

export function DeliveryRouteForm({
  deliveryRoute = null,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: DeliveryRouteFormProps) {
  const [values, setValues] = useState<DeliveryRouteFormValues>(() =>
    buildInitialValues(deliveryRoute),
  );
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    const name = values.name.trim();
    if (!name) {
      setValidationError("El nombre de la ruta es obligatorio.");
      return;
    }

    const expectedDailyCash = values.expectedDailyCash.trim() || "0.00";
    if (!isValidNonnegativeMoney(expectedDailyCash)) {
      setValidationError(
        "El efectivo diario esperado debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    await onSubmit({
      code: optionalText(values.code),
      name,
      description: optionalText(values.description),
      zone: optionalText(values.zone),
      sector: optionalText(values.sector),
      service_days: optionalText(values.serviceDays),
      reference_driver: optionalText(values.referenceDriver),
      reference_vehicle: optionalText(values.referenceVehicle),
      expected_daily_cash: expectedDailyCash,
      notes: optionalText(values.notes),
    });
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          {deliveryRoute ? "Editar ruta" : "Registrar ruta"}
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
            label="Nombre de la ruta"
            value={values.name}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, name: value })}
          />
          <TextField
            label="Zona"
            value={values.zone}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, zone: value })}
          />
          <TextField
            label="Sector"
            value={values.sector}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, sector: value })}
          />
          <TextField
            label="Días de atención"
            value={values.serviceDays}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, serviceDays: value })}
          />
          <MoneyField
            label="Efectivo diario esperado"
            value={values.expectedDailyCash}
            disabled={isSubmitting}
            onChange={(value) =>
              setValues({ ...values, expectedDailyCash: value })
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
          <TextField
            label="Vehículo de referencia"
            value={values.referenceVehicle}
            disabled={isSubmitting}
            onChange={(value) =>
              setValues({ ...values, referenceVehicle: value })
            }
          />
        </div>

        <TextAreaField
          label="Descripción"
          value={values.description}
          disabled={isSubmitting}
          onChange={(value) => setValues({ ...values, description: value })}
        />
        <TextAreaField
          label="Observaciones"
          value={values.notes}
          disabled={isSubmitting}
          onChange={(value) => setValues({ ...values, notes: value })}
        />

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
              : deliveryRoute
                ? "Guardar cambios"
                : "Registrar ruta"}
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

function MoneyField(props: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{props.label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        type="number"
        inputMode="decimal"
        min="0"
        step="0.01"
        value={props.value}
        disabled={props.disabled}
        onChange={(event) => props.onChange(event.target.value)}
      />
    </label>
  );
}

function TextAreaField(props: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{props.label}</span>
      <textarea
        className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        value={props.value}
        disabled={props.disabled}
        onChange={(event) => props.onChange(event.target.value)}
      />
    </label>
  );
}

function buildInitialValues(
  deliveryRoute: DeliveryRoute | null,
): DeliveryRouteFormValues {
  return {
    code: deliveryRoute?.code ?? "",
    name: deliveryRoute?.name ?? "",
    description: deliveryRoute?.description ?? "",
    zone: deliveryRoute?.zone ?? "",
    sector: deliveryRoute?.sector ?? "",
    serviceDays: deliveryRoute?.service_days ?? "",
    referenceDriver: deliveryRoute?.reference_driver ?? "",
    referenceVehicle: deliveryRoute?.reference_vehicle ?? "",
    expectedDailyCash: deliveryRoute?.expected_daily_cash ?? "0.00",
    notes: deliveryRoute?.notes ?? "",
  };
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

function isValidNonnegativeMoney(value: string): boolean {
  return /^\d+(?:\.\d{1,2})?$/.test(value);
}

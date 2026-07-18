"use client";

import { useState, type FormEvent } from "react";

import {
  CUSTOMER_TYPE_LABELS,
  type Customer,
  type CustomerPayload,
  type CustomerType,
} from "@/types/customer";

type CustomerFormProps = {
  customer?: Customer | null;
  isSubmitting?: boolean;
  onSubmit: (payload: CustomerPayload) => Promise<boolean>;
  onCancel: () => void;
};

type CustomerFormValues = {
  name: string;
  primaryPhone: string;
  secondaryPhone: string;
  address: string;
  sector: string;
  customerType: CustomerType;
  routeReference: string;
  creditAllowed: boolean;
  creditLimit: string;
  notes: string;
};

const customerTypes = Object.keys(CUSTOMER_TYPE_LABELS) as CustomerType[];

export function CustomerForm({
  customer = null,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: CustomerFormProps) {
  const [values, setValues] = useState<CustomerFormValues>(() =>
    buildInitialValues(customer),
  );
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    const name = values.name.trim();
    if (!name) {
      setValidationError("El nombre del cliente es obligatorio.");
      return;
    }

    const creditLimit = values.creditLimit.trim() || "0.00";
    if (!/^\d+(?:\.\d{1,2})?$/.test(creditLimit)) {
      setValidationError(
        "El límite de crédito debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    await onSubmit({
      name,
      primary_phone: optionalText(values.primaryPhone),
      secondary_phone: optionalText(values.secondaryPhone),
      address: optionalText(values.address),
      sector: optionalText(values.sector),
      customer_type: values.customerType,
      route_reference: optionalText(values.routeReference),
      credit_allowed: values.creditAllowed,
      credit_limit: values.creditAllowed ? creditLimit : "0.00",
      notes: optionalText(values.notes),
    });
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          {customer ? "Editar cliente" : "Registrar cliente"}
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
            label="Nombre"
            value={values.name}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, name: value })}
          />
          <SelectField
            label="Tipo de cliente"
            value={values.customerType}
            disabled={isSubmitting}
            onChange={(value) =>
              setValues({ ...values, customerType: value as CustomerType })
            }
            options={customerTypes.map((type) => ({
              value: type,
              label: CUSTOMER_TYPE_LABELS[type],
            }))}
          />
          <TextField
            label="Teléfono principal"
            value={values.primaryPhone}
            disabled={isSubmitting}
            inputMode="tel"
            onChange={(value) => setValues({ ...values, primaryPhone: value })}
          />
          <TextField
            label="Teléfono secundario"
            value={values.secondaryPhone}
            disabled={isSubmitting}
            inputMode="tel"
            onChange={(value) => setValues({ ...values, secondaryPhone: value })}
          />
          <TextField
            label="Dirección"
            value={values.address}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, address: value })}
          />
          <TextField
            label="Sector"
            value={values.sector}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, sector: value })}
          />
          <TextField
            label="Ruta/Zona de referencia"
            value={values.routeReference}
            disabled={isSubmitting}
            onChange={(value) =>
              setValues({ ...values, routeReference: value })
            }
          />
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Límite de crédito
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              type="number"
              inputMode="decimal"
              min="0"
              step="0.01"
              value={values.creditLimit}
              disabled={isSubmitting || !values.creditAllowed}
              onChange={(event) =>
                setValues({ ...values, creditLimit: event.target.value })
              }
            />
          </label>
        </div>

        <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
          <input
            className="h-4 w-4 accent-water-700"
            type="checkbox"
            checked={values.creditAllowed}
            disabled={isSubmitting}
            onChange={(event) =>
              setValues({
                ...values,
                creditAllowed: event.target.checked,
                creditLimit: event.target.checked ? values.creditLimit : "0.00",
              })
            }
          />
          Permite crédito
        </label>

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
              : customer
                ? "Guardar cambios"
                : "Registrar cliente"}
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
  inputMode?: "text" | "tel";
  onChange: (value: string) => void;
};

function TextField({
  label,
  value,
  required = false,
  disabled = false,
  inputMode = "text",
  onChange,
}: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        type="text"
        inputMode={inputMode}
        value={value}
        required={required}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
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

function buildInitialValues(customer: Customer | null): CustomerFormValues {
  return {
    name: customer?.name ?? "",
    primaryPhone: customer?.primary_phone ?? "",
    secondaryPhone: customer?.secondary_phone ?? "",
    address: customer?.address ?? "",
    sector: customer?.sector ?? "",
    customerType: customer?.customer_type ?? "household",
    routeReference: customer?.route_reference ?? "",
    creditAllowed: customer?.credit_allowed ?? false,
    creditLimit: customer?.credit_limit ?? "0.00",
    notes: customer?.notes ?? "",
  };
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

"use client";

import { useState, type FormEvent } from "react";

import {
  EMPLOYEE_TYPE_LABELS,
  PAYMENT_FREQUENCY_LABELS,
  type Employee,
  type EmployeePayload,
  type EmployeeType,
  type PaymentFrequency,
} from "@/types/employee";

type EmployeeFormProps = {
  employee?: Employee | null;
  isSubmitting?: boolean;
  onSubmit: (payload: EmployeePayload) => Promise<boolean>;
  onCancel: () => void;
};

type EmployeeFormValues = {
  firstName: string;
  lastName: string;
  identification: string;
  primaryPhone: string;
  secondaryPhone: string;
  address: string;
  jobPosition: string;
  employeeType: EmployeeType;
  baseSalary: string;
  paymentFrequency: PaymentFrequency;
  hireDate: string;
  notes: string;
};

const employeeTypes = Object.keys(EMPLOYEE_TYPE_LABELS) as EmployeeType[];
const paymentFrequencies = Object.keys(
  PAYMENT_FREQUENCY_LABELS,
) as PaymentFrequency[];

export function EmployeeForm({
  employee = null,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: EmployeeFormProps) {
  const [values, setValues] = useState<EmployeeFormValues>(() =>
    buildInitialValues(employee),
  );
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    const firstName = values.firstName.trim();
    if (!firstName) {
      setValidationError("Los nombres del empleado son obligatorios.");
      return;
    }

    const lastName = values.lastName.trim();
    if (!lastName) {
      setValidationError("Los apellidos del empleado son obligatorios.");
      return;
    }

    const baseSalary = values.baseSalary.trim() || "0.00";
    if (!isValidNonnegativeMoney(baseSalary)) {
      setValidationError(
        "El sueldo base debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    await onSubmit({
      first_name: firstName,
      last_name: lastName,
      identification: optionalText(values.identification),
      primary_phone: optionalText(values.primaryPhone),
      secondary_phone: optionalText(values.secondaryPhone),
      address: optionalText(values.address),
      job_position: optionalText(values.jobPosition),
      employee_type: values.employeeType,
      base_salary: baseSalary,
      payment_frequency: values.paymentFrequency,
      hire_date: optionalText(values.hireDate),
      notes: optionalText(values.notes),
    });
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          {employee ? "Editar empleado" : "Registrar empleado"}
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
            label="Nombres"
            value={values.firstName}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, firstName: value })}
          />
          <TextField
            label="Apellidos"
            value={values.lastName}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, lastName: value })}
          />
          <TextField
            label="Identificación"
            value={values.identification}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, identification: value })}
          />
          <TextField
            label="Teléfono principal"
            value={values.primaryPhone}
            inputType="tel"
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, primaryPhone: value })}
          />
          <TextField
            label="Teléfono secundario"
            value={values.secondaryPhone}
            inputType="tel"
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, secondaryPhone: value })}
          />
          <TextField
            label="Cargo"
            value={values.jobPosition}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, jobPosition: value })}
          />
          <SelectField
            label="Tipo de empleado"
            value={values.employeeType}
            disabled={isSubmitting}
            options={employeeTypes.map((employeeType) => ({
              value: employeeType,
              label: EMPLOYEE_TYPE_LABELS[employeeType],
            }))}
            onChange={(value) =>
              setValues({ ...values, employeeType: value as EmployeeType })
            }
          />
          <MoneyField
            label="Sueldo base"
            value={values.baseSalary}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, baseSalary: value })}
          />
          <SelectField
            label="Frecuencia de pago"
            value={values.paymentFrequency}
            disabled={isSubmitting}
            options={paymentFrequencies.map((frequency) => ({
              value: frequency,
              label: PAYMENT_FREQUENCY_LABELS[frequency],
            }))}
            onChange={(value) =>
              setValues({
                ...values,
                paymentFrequency: value as PaymentFrequency,
              })
            }
          />
          <TextField
            label="Fecha de ingreso"
            value={values.hireDate}
            inputType="date"
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, hireDate: value })}
          />
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Dirección</span>
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={values.address}
            disabled={isSubmitting}
            onChange={(event) =>
              setValues({ ...values, address: event.target.value })
            }
          />
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
              : employee
                ? "Guardar cambios"
                : "Registrar empleado"}
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
  inputType?: "text" | "tel" | "date";
  onChange: (value: string) => void;
};

function TextField({
  label,
  value,
  required = false,
  disabled = false,
  inputType = "text",
  onChange,
}: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        type={inputType}
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

function buildInitialValues(employee: Employee | null): EmployeeFormValues {
  return {
    firstName: employee?.first_name ?? "",
    lastName: employee?.last_name ?? "",
    identification: employee?.identification ?? "",
    primaryPhone: employee?.primary_phone ?? "",
    secondaryPhone: employee?.secondary_phone ?? "",
    address: employee?.address ?? "",
    jobPosition: employee?.job_position ?? "",
    employeeType: employee?.employee_type ?? "other",
    baseSalary: employee?.base_salary ?? "0.00",
    paymentFrequency: employee?.payment_frequency ?? "monthly",
    hireDate: employee?.hire_date ?? "",
    notes: employee?.notes ?? "",
  };
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

function isValidNonnegativeMoney(value: string): boolean {
  return /^\d+(?:\.\d{1,2})?$/.test(value);
}

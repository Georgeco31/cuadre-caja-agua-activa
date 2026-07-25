"use client";

import { useState, type FormEvent } from "react";

import {
  PRODUCT_CATEGORY_LABELS,
  PRODUCT_KIND_LABELS,
  PRODUCT_UNIT_LABELS,
  type Product,
  type ProductCategory,
  type ProductKind,
  type ProductPayload,
  type ProductUnit,
} from "@/types/product";

type ProductFormProps = {
  product?: Product | null;
  isSubmitting?: boolean;
  onSubmit: (payload: ProductPayload) => Promise<boolean>;
  onCancel: () => void;
};

type ProductFormValues = {
  sku: string;
  name: string;
  description: string;
  category: ProductCategory;
  unit: ProductUnit;
  presentation: string;
  defaultPrice: string;
  costEstimate: string;
  productKind: ProductKind;
  productionNotes: string;
  isReturnableContainer: boolean;
  notes: string;
};

const categories = Object.keys(PRODUCT_CATEGORY_LABELS) as ProductCategory[];
const units = Object.keys(PRODUCT_UNIT_LABELS) as ProductUnit[];
const productKinds = Object.keys(PRODUCT_KIND_LABELS) as ProductKind[];

export function ProductForm({
  product = null,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: ProductFormProps) {
  const [values, setValues] = useState<ProductFormValues>(() =>
    buildInitialValues(product),
  );
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    const name = values.name.trim();
    if (!name) {
      setValidationError("El nombre del producto es obligatorio.");
      return;
    }

    const defaultPrice = values.defaultPrice.trim();
    if (!isValidNonnegativeMoney(defaultPrice)) {
      setValidationError(
        "El precio base debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    const costEstimate = values.costEstimate.trim() || "0.00";
    if (!isValidNonnegativeMoney(costEstimate)) {
      setValidationError(
        "El costo estimado debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    await onSubmit({
      sku: optionalText(values.sku),
      name,
      description: optionalText(values.description),
      category: values.category,
      unit: values.unit,
      presentation: optionalText(values.presentation),
      default_price: defaultPrice,
      cost_estimate: costEstimate,
      product_kind: values.productKind,
      production_notes: optionalText(values.productionNotes),
      is_returnable_container: values.isReturnableContainer,
      notes: optionalText(values.notes),
    });
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          {product ? "Editar producto" : "Registrar producto"}
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
            label="Código interno/SKU"
            value={values.sku}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, sku: value })}
          />
          <TextField
            label="Nombre"
            value={values.name}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, name: value })}
          />
          <SelectField
            label="Categoría"
            value={values.category}
            disabled={isSubmitting}
            options={categories.map((category) => ({
              value: category,
              label: PRODUCT_CATEGORY_LABELS[category],
            }))}
            onChange={(value) =>
              setValues({ ...values, category: value as ProductCategory })
            }
          />
          <SelectField
            label="Unidad"
            value={values.unit}
            disabled={isSubmitting}
            options={units.map((unit) => ({
              value: unit,
              label: PRODUCT_UNIT_LABELS[unit],
            }))}
            onChange={(value) =>
              setValues({ ...values, unit: value as ProductUnit })
            }
          />
          <TextField
            label="Presentación"
            value={values.presentation}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, presentation: value })}
          />
          <MoneyField
            label="Precio base"
            value={values.defaultPrice}
            required
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, defaultPrice: value })}
          />
          <MoneyField
            label="Costo estimado"
            value={values.costEstimate}
            disabled={isSubmitting}
            onChange={(value) => setValues({ ...values, costEstimate: value })}
          />
          <SelectField
            label="Clasificación de producción"
            value={values.productKind}
            disabled={isSubmitting}
            options={productKinds.map((productKind) => ({
              value: productKind,
              label: PRODUCT_KIND_LABELS[productKind],
            }))}
            onChange={(value) =>
              setValues({ ...values, productKind: value as ProductKind })
            }
          />
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Descripción</span>
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={values.description}
            disabled={isSubmitting}
            onChange={(event) =>
              setValues({ ...values, description: event.target.value })
            }
          />
        </label>

        <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
          <input
            className="h-4 w-4 accent-water-700"
            type="checkbox"
            checked={values.isReturnableContainer}
            disabled={isSubmitting}
            onChange={(event) =>
              setValues({
                ...values,
                isReturnableContainer: event.target.checked,
              })
            }
          />
          Envase retornable
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Notas de producción
          </span>
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={values.productionNotes}
            disabled={isSubmitting}
            onChange={(event) =>
              setValues({ ...values, productionNotes: event.target.value })
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
              : product
                ? "Guardar cambios"
                : "Registrar producto"}
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
        required={props.required}
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

function buildInitialValues(product: Product | null): ProductFormValues {
  return {
    sku: product?.sku ?? "",
    name: product?.name ?? "",
    description: product?.description ?? "",
    category: product?.category ?? "water",
    unit: product?.unit ?? "unit",
    presentation: product?.presentation ?? "",
    defaultPrice: product?.default_price ?? "0.00",
    costEstimate: product?.cost_estimate ?? "0.00",
    productKind: product?.product_kind ?? "finished_good",
    productionNotes: product?.production_notes ?? "",
    isReturnableContainer: product?.is_returnable_container ?? false,
    notes: product?.notes ?? "",
  };
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

function isValidNonnegativeMoney(value: string): boolean {
  return /^\d+(?:\.\d{1,2})?$/.test(value);
}

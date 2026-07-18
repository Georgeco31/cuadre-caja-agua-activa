"use client";

import { useState, type FormEvent } from "react";

import {
  INVENTORY_MOVEMENT_TYPE_LABELS,
  type InventoryLocation,
  type InventoryMovementPayload,
  type InventoryMovementType,
} from "@/types/inventory";
import type { Product } from "@/types/product";

type InventoryMovementFormProps = {
  products: Product[];
  locations: InventoryLocation[];
  isSubmitting?: boolean;
  onSubmit: (payload: InventoryMovementPayload) => Promise<boolean>;
};

type FormValues = {
  movementDate: string;
  movementType: InventoryMovementType;
  productId: string;
  locationId: string;
  quantity: string;
  unitCost: string;
  reason: string;
};

const movementTypes = Object.keys(
  INVENTORY_MOVEMENT_TYPE_LABELS,
) as InventoryMovementType[];

export function InventoryMovementForm({
  products,
  locations,
  isSubmitting = false,
  onSubmit,
}: InventoryMovementFormProps) {
  const [values, setValues] = useState<FormValues>(buildInitialValues);
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    if (!values.productId) {
      setValidationError("Selecciona un producto activo.");
      return;
    }
    if (!values.locationId) {
      setValidationError("Selecciona una ubicación activa.");
      return;
    }
    if (!isValidDecimal(values.quantity, 3, true)) {
      setValidationError(
        "La cantidad debe ser mayor a cero y tener máximo tres decimales.",
      );
      return;
    }
    const unitCost = values.unitCost.trim();
    if (unitCost && !isValidDecimal(unitCost, 2)) {
      setValidationError(
        "El costo unitario debe ser mayor o igual a cero y tener máximo dos decimales.",
      );
      return;
    }

    const saved = await onSubmit({
      movement_date: values.movementDate,
      movement_type: values.movementType,
      product_id: Number(values.productId),
      location_id: Number(values.locationId),
      quantity: values.quantity.trim(),
      unit_cost: unitCost || null,
      reason: optionalText(values.reason),
    });
    if (saved) {
      setValues(buildInitialValues());
    }
  }

  const cannotRegister = products.length === 0 || locations.length === 0;

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar movimiento manual
        </h2>
      </div>

      <form className="space-y-4 p-4" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}
        {cannotRegister ? (
          <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            Se necesita al menos un producto activo y una ubicación activa.
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Fecha</span>
            <input
              className={fieldClassName}
              type="date"
              value={values.movementDate}
              required
              disabled={isSubmitting}
              onChange={(event) =>
                setValues({ ...values, movementDate: event.target.value })
              }
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Tipo</span>
            <select
              className={fieldClassName}
              value={values.movementType}
              disabled={isSubmitting}
              onChange={(event) =>
                setValues({
                  ...values,
                  movementType: event.target.value as InventoryMovementType,
                })
              }
            >
              {movementTypes.map((movementType) => (
                <option key={movementType} value={movementType}>
                  {INVENTORY_MOVEMENT_TYPE_LABELS[movementType]}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Producto</span>
            <select
              className={fieldClassName}
              value={values.productId}
              required
              disabled={isSubmitting || products.length === 0}
              onChange={(event) =>
                setValues({ ...values, productId: event.target.value })
              }
            >
              <option value="">Seleccionar producto</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                  {product.presentation ? ` · ${product.presentation}` : ""}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Ubicación</span>
            <select
              className={fieldClassName}
              value={values.locationId}
              required
              disabled={isSubmitting || locations.length === 0}
              onChange={(event) =>
                setValues({ ...values, locationId: event.target.value })
              }
            >
              <option value="">Seleccionar ubicación</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Cantidad</span>
            <input
              className={fieldClassName}
              type="number"
              inputMode="decimal"
              min="0.001"
              step="0.001"
              value={values.quantity}
              required
              disabled={isSubmitting}
              onChange={(event) =>
                setValues({ ...values, quantity: event.target.value })
              }
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Costo unitario
            </span>
            <input
              className={fieldClassName}
              type="number"
              inputMode="decimal"
              min="0"
              step="0.01"
              value={values.unitCost}
              disabled={isSubmitting}
              onChange={(event) =>
                setValues({ ...values, unitCost: event.target.value })
              }
            />
          </label>
          <label className="block md:col-span-2">
            <span className="text-sm font-medium text-slate-700">
              Motivo u observación
            </span>
            <input
              className={fieldClassName}
              type="text"
              value={values.reason}
              disabled={isSubmitting}
              onChange={(event) =>
                setValues({ ...values, reason: event.target.value })
              }
            />
          </label>
        </div>

        <div className="flex justify-end border-t border-slate-200 pt-4">
          <button
            className="h-10 w-full rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
            type="submit"
            disabled={isSubmitting || cannotRegister}
          >
            {isSubmitting ? "Registrando..." : "Registrar movimiento"}
          </button>
        </div>
      </form>
    </section>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";

function buildInitialValues(): FormValues {
  return {
    movementDate: currentDate(),
    movementType: "entry",
    productId: "",
    locationId: "",
    quantity: "",
    unitCost: "",
    reason: "",
  };
}

function currentDate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function isValidDecimal(
  value: string,
  decimalPlaces: number,
  requirePositive = false,
): boolean {
  const normalizedValue = value.trim();
  const pattern = new RegExp(`^\\d+(?:\\.\\d{1,${decimalPlaces}})?$`);
  if (!pattern.test(normalizedValue)) {
    return false;
  }
  return !requirePositive || /[1-9]/.test(normalizedValue);
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

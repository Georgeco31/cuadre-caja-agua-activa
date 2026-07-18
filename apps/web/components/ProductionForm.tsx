"use client";

import Link from "next/link";
import { useMemo, useState, type FormEvent } from "react";

import type { Product } from "@/types/product";
import type { ProductionBatchPayload } from "@/types/production";

type ProductionFormProps = {
  products: Product[];
  isSubmitting?: boolean;
  onSubmit: (payload: ProductionBatchPayload) => Promise<boolean>;
};

type ProductionLine = {
  productId: number;
  quantityProduced: string;
  quantityWaste: string;
  notes: string;
};

export function ProductionForm({
  products,
  isSubmitting = false,
  onSubmit,
}: ProductionFormProps) {
  const [productionDate, setProductionDate] = useState(currentDate());
  const [notes, setNotes] = useState("");
  const [selectedProductId, setSelectedProductId] = useState("");
  const [lines, setLines] = useState<ProductionLine[]>([]);
  const [validationError, setValidationError] = useState("");

  const productsById = useMemo(
    () => new Map(products.map((product) => [product.id, product])),
    [products],
  );

  function handleAddProduct() {
    setValidationError("");
    const productId = Number(selectedProductId);
    const product = productsById.get(productId);
    if (!product) {
      setValidationError("Selecciona un producto activo.");
      return;
    }
    if (lines.some((line) => line.productId === productId)) {
      setValidationError("El producto seleccionado ya está en la producción.");
      return;
    }

    setLines([
      ...lines,
      {
        productId,
        quantityProduced: "",
        quantityWaste: "0",
        notes: "",
      },
    ]);
    setSelectedProductId("");
  }

  function updateLine(productId: number, values: Partial<ProductionLine>) {
    setLines(
      lines.map((line) =>
        line.productId === productId ? { ...line, ...values } : line,
      ),
    );
  }

  function removeLine(productId: number) {
    setLines(lines.filter((line) => line.productId !== productId));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");

    if (!productionDate) {
      setValidationError("La fecha de producción es obligatoria.");
      return;
    }
    if (lines.length === 0) {
      setValidationError("Agrega al menos un producto a la producción.");
      return;
    }
    for (const line of lines) {
      if (!isValidDecimal(line.quantityProduced, true)) {
        setValidationError(
          "Todas las cantidades producidas deben ser mayores a cero y tener máximo tres decimales.",
        );
        return;
      }
      if (!isValidDecimal(line.quantityWaste)) {
        setValidationError(
          "La merma debe ser mayor o igual a cero y tener máximo tres decimales.",
        );
        return;
      }
    }

    const saved = await onSubmit({
      production_date: productionDate,
      notes: optionalText(notes),
      items: lines.map((line) => ({
        product_id: line.productId,
        quantity_produced: line.quantityProduced.trim(),
        quantity_waste: line.quantityWaste.trim(),
        notes: optionalText(line.notes),
      })),
    });
    if (saved) {
      setNotes("");
      setSelectedProductId("");
      setLines([]);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar producción y envasado
        </h2>
      </div>

      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-[minmax(220px,0.35fr)_minmax(0,1fr)]">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha de producción
            </span>
            <input
              className={fieldClassName}
              type="date"
              value={productionDate}
              required
              disabled={isSubmitting}
              onChange={(event) => setProductionDate(event.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Observación general
            </span>
            <input
              className={fieldClassName}
              type="text"
              value={notes}
              disabled={isSubmitting}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>
        </div>

        <div className="space-y-3 border-t border-slate-200 pt-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="block flex-1">
              <span className="text-sm font-medium text-slate-700">
                Producto activo
              </span>
              <select
                className={fieldClassName}
                value={selectedProductId}
                disabled={isSubmitting || products.length === 0}
                onChange={(event) => setSelectedProductId(event.target.value)}
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
            <button
              className="h-10 rounded-md border border-water-700 bg-white px-4 text-sm font-semibold text-water-700 transition hover:bg-water-50 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
              type="button"
              disabled={isSubmitting || products.length === 0}
              onClick={handleAddProduct}
            >
              Agregar producto
            </button>
          </div>

          {products.length === 0 ? (
            <p className="text-sm text-slate-600">
              No hay productos activos disponibles. Registra o reactiva uno en{" "}
              <Link
                className="font-semibold text-water-700 hover:text-water-500"
                href="/dashboard/products"
              >
                Productos
              </Link>
              .
            </p>
          ) : null}

          {lines.length > 0 ? (
            <div className="overflow-x-auto rounded-md border border-slate-200">
              <table className="w-full min-w-[980px] border-collapse text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-3 py-2 font-medium">Producto</th>
                    <th className="w-40 px-3 py-2 font-medium">Producido</th>
                    <th className="w-40 px-3 py-2 font-medium">
                      Merma / dañados
                    </th>
                    <th className="w-72 px-3 py-2 font-medium">
                      Observación
                    </th>
                    <th className="w-24 px-3 py-2 font-medium">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {lines.map((line) => {
                    const product = productsById.get(line.productId);
                    return (
                      <tr key={line.productId}>
                        <td className="px-3 py-3">
                          <p className="font-medium text-slate-950">
                            {product?.name}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            {product?.sku ?? "Sin SKU"}
                            {product?.presentation
                              ? ` · ${product.presentation}`
                              : ""}
                          </p>
                        </td>
                        <td className="px-3 py-3">
                          <input
                            className={lineFieldClassName}
                            aria-label={`Cantidad producida de ${product?.name ?? "producto"}`}
                            type="number"
                            inputMode="decimal"
                            min="0.001"
                            step="0.001"
                            value={line.quantityProduced}
                            required
                            disabled={isSubmitting}
                            onChange={(event) =>
                              updateLine(line.productId, {
                                quantityProduced: event.target.value,
                              })
                            }
                          />
                        </td>
                        <td className="px-3 py-3">
                          <input
                            className={lineFieldClassName}
                            aria-label={`Merma de ${product?.name ?? "producto"}`}
                            type="number"
                            inputMode="decimal"
                            min="0"
                            step="0.001"
                            value={line.quantityWaste}
                            required
                            disabled={isSubmitting}
                            onChange={(event) =>
                              updateLine(line.productId, {
                                quantityWaste: event.target.value,
                              })
                            }
                          />
                        </td>
                        <td className="px-3 py-3">
                          <input
                            className={lineFieldClassName}
                            aria-label={`Observación de ${product?.name ?? "producto"}`}
                            type="text"
                            value={line.notes}
                            disabled={isSubmitting}
                            onChange={(event) =>
                              updateLine(line.productId, {
                                notes: event.target.value,
                              })
                            }
                          />
                        </td>
                        <td className="px-3 py-3">
                          <button
                            className="font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                            type="button"
                            disabled={isSubmitting}
                            onClick={() => removeLine(line.productId)}
                          >
                            Quitar
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="rounded-md bg-slate-50 px-3 py-4 text-sm text-slate-600">
              Agrega los productos envasados durante la jornada.
            </p>
          )}
        </div>

        <div className="flex justify-end border-t border-slate-200 pt-5">
          <button
            className="h-11 w-full rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
            type="submit"
            disabled={isSubmitting || products.length === 0}
          >
            {isSubmitting ? "Guardando producción..." : "Registrar producción"}
          </button>
        </div>
      </form>
    </section>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";
const lineFieldClassName =
  "h-9 w-full rounded-md border border-slate-300 px-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";

function currentDate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function isValidDecimal(value: string, requirePositive = false): boolean {
  const normalizedValue = value.trim();
  if (!/^\d+(?:\.\d{1,3})?$/.test(normalizedValue)) {
    return false;
  }
  return !requirePositive || /[1-9]/.test(normalizedValue);
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

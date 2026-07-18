"use client";

import Link from "next/link";
import { useMemo, useState, type FormEvent } from "react";

import type { Customer } from "@/types/customer";
import type { Product } from "@/types/product";
import {
  SALE_PAYMENT_METHOD_LABELS,
  type CashSalePayload,
  type SalePaymentMethod,
} from "@/types/sale";

type CashSaleFormProps = {
  customers: Customer[];
  products: Product[];
  isSubmitting?: boolean;
  onSubmit: (payload: CashSalePayload) => Promise<boolean>;
};

type SaleLine = {
  productId: number;
  quantity: string;
  unitPrice: string;
};

const paymentMethods = Object.keys(
  SALE_PAYMENT_METHOD_LABELS,
) as SalePaymentMethod[];

export function CashSaleForm({
  customers,
  products,
  isSubmitting = false,
  onSubmit,
}: CashSaleFormProps) {
  const [saleDate, setSaleDate] = useState(currentDate());
  const [customerId, setCustomerId] = useState("");
  const [paymentMethod, setPaymentMethod] =
    useState<SalePaymentMethod>("cash");
  const [notes, setNotes] = useState("");
  const [selectedProductId, setSelectedProductId] = useState("");
  const [lines, setLines] = useState<SaleLine[]>([]);
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
      setValidationError("El producto seleccionado ya está en la venta.");
      return;
    }

    setLines([
      ...lines,
      {
        productId,
        quantity: "1",
        unitPrice: product.default_price,
      },
    ]);
    setSelectedProductId("");
  }

  function updateLine(productId: number, values: Partial<SaleLine>) {
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

    if (!saleDate) {
      setValidationError("La fecha de venta es obligatoria.");
      return;
    }
    if (lines.length === 0) {
      setValidationError("Agrega al menos un producto a la venta.");
      return;
    }
    for (const line of lines) {
      if (!isPositiveNumber(line.quantity)) {
        setValidationError("Todas las cantidades deben ser mayores a cero.");
        return;
      }
      if (!isNonnegativeMoney(line.unitPrice)) {
        setValidationError(
          "Todos los precios deben ser mayores o iguales a cero y tener máximo dos decimales.",
        );
        return;
      }
    }

    const saved = await onSubmit({
      sale_date: saleDate,
      ...(customerId ? { customer_id: Number(customerId) } : {}),
      payment_method: paymentMethod,
      notes: optionalText(notes),
      items: lines.map((line) => ({
        product_id: line.productId,
        quantity: line.quantity,
        unit_price: line.unitPrice,
      })),
    });

    if (saved) {
      setCustomerId("");
      setPaymentMethod("cash");
      setNotes("");
      setSelectedProductId("");
      setLines([]);
    }
  }

  const total = lines.reduce(
    (sum, line) => sum + calculateSubtotal(line.quantity, line.unitPrice),
    0,
  );

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar venta
        </h2>
      </div>

      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-3">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Fecha de venta
            </span>
            <input
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              type="date"
              value={saleDate}
              required
              disabled={isSubmitting}
              onChange={(event) => setSaleDate(event.target.value)}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Cliente opcional
            </span>
            <select
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              value={customerId}
              disabled={isSubmitting}
              onChange={(event) => setCustomerId(event.target.value)}
            >
              <option value="">Consumidor final</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">
              Método de pago
            </span>
            <select
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              value={paymentMethod}
              disabled={isSubmitting}
              onChange={(event) =>
                setPaymentMethod(event.target.value as SalePaymentMethod)
              }
            >
              {paymentMethods.map((method) => (
                <option key={method} value={method}>
                  {SALE_PAYMENT_METHOD_LABELS[method]}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Notas</span>
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            value={notes}
            disabled={isSubmitting}
            onChange={(event) => setNotes(event.target.value)}
          />
        </label>

        <div className="space-y-3 border-t border-slate-200 pt-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="block flex-1">
              <span className="text-sm font-medium text-slate-700">
                Producto
              </span>
              <select
                className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
                value={selectedProductId}
                disabled={isSubmitting || products.length === 0}
                onChange={(event) => setSelectedProductId(event.target.value)}
              >
                <option value="">Seleccionar producto</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                    {product.presentation ? ` - ${product.presentation}` : ""}
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
                Productos y precios
              </Link>
              .
            </p>
          ) : null}

          {lines.length > 0 ? (
            <div className="overflow-x-auto rounded-md border border-slate-200">
              <table className="w-full min-w-[760px] border-collapse text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-3 py-2 font-medium">Producto</th>
                    <th className="w-36 px-3 py-2 font-medium">Cantidad</th>
                    <th className="w-40 px-3 py-2 font-medium">Precio unitario</th>
                    <th className="w-32 px-3 py-2 text-right font-medium">
                      Subtotal
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
                            {product?.presentation ?? product?.sku ?? "Sin referencia"}
                          </p>
                        </td>
                        <td className="px-3 py-3">
                          <input
                            className="h-9 w-full rounded-md border border-slate-300 px-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                            type="number"
                            inputMode="decimal"
                            min="0.001"
                            step="0.001"
                            value={line.quantity}
                            disabled={isSubmitting}
                            onChange={(event) =>
                              updateLine(line.productId, {
                                quantity: event.target.value,
                              })
                            }
                          />
                        </td>
                        <td className="px-3 py-3">
                          <input
                            className="h-9 w-full rounded-md border border-slate-300 px-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                            type="number"
                            inputMode="decimal"
                            min="0"
                            step="0.01"
                            value={line.unitPrice}
                            disabled={isSubmitting}
                            onChange={(event) =>
                              updateLine(line.productId, {
                                unitPrice: event.target.value,
                              })
                            }
                          />
                        </td>
                        <td className="px-3 py-3 text-right font-semibold text-slate-950">
                          {formatMoney(
                            calculateSubtotal(line.quantity, line.unitPrice),
                          )}
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
              Agrega productos para preparar la venta.
            </p>
          )}
        </div>

        <div className="flex flex-col gap-4 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">
              Total estimado
            </p>
            <p className="mt-1 text-2xl font-semibold text-slate-950">
              {formatMoney(total)}
            </p>
          </div>
          <button
            className="h-11 rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
            type="submit"
            disabled={isSubmitting || products.length === 0}
          >
            {isSubmitting ? "Guardando venta..." : "Guardar venta"}
          </button>
        </div>
      </form>
    </section>
  );
}

function currentDate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function optionalText(value: string): string | null {
  const normalizedValue = value.trim();
  return normalizedValue || null;
}

function isPositiveNumber(value: string): boolean {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) && numberValue > 0;
}

function isNonnegativeMoney(value: string): boolean {
  return /^(?:0|[1-9]\d*)(?:\.\d{1,2})?$/.test(value);
}

function calculateSubtotal(quantity: string, unitPrice: string): number {
  const quantityValue = Number(quantity);
  const priceValue = Number(unitPrice);
  if (!Number.isFinite(quantityValue) || !Number.isFinite(priceValue)) {
    return 0;
  }
  return quantityValue * priceValue;
}

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

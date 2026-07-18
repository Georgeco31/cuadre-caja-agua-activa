"use client";

import type { FormEvent } from "react";

import type { InventoryLocation, InventoryStock } from "@/types/inventory";
import type { Product } from "@/types/product";

export type InventoryStockFilterValues = {
  productId: string;
  locationId: string;
  onlyPositive: boolean;
};

type InventoryStockTableProps = {
  stocks: InventoryStock[];
  products: Product[];
  locations: InventoryLocation[];
  filters: InventoryStockFilterValues;
  isLoading?: boolean;
  onFiltersChange: (filters: InventoryStockFilterValues) => void;
  onFilter: () => void;
  onClear: () => void;
};

export function InventoryStockTable({
  stocks,
  products,
  locations,
  filters,
  isLoading = false,
  onFiltersChange,
  onFilter,
  onClear,
}: InventoryStockTableProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onFilter();
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">Stock actual</h2>
        <span className="text-sm text-slate-500">{stocks.length}</span>
      </div>

      <form
        className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-2 xl:grid-cols-[1fr_1fr_auto_auto] xl:items-end"
        onSubmit={handleSubmit}
      >
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Producto</span>
          <select
            className={fieldClassName}
            value={filters.productId}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, productId: event.target.value })
            }
          >
            <option value="">Todos</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Ubicación</span>
          <select
            className={fieldClassName}
            value={filters.locationId}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, locationId: event.target.value })
            }
          >
            <option value="">Todas</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex h-10 items-center gap-2 text-sm font-medium text-slate-700">
          <input
            className="h-4 w-4 rounded border-slate-300 text-water-700 focus:ring-water-500"
            type="checkbox"
            checked={filters.onlyPositive}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, onlyPositive: event.target.checked })
            }
          />
          Solo stock positivo
        </label>
        <div className="flex gap-2">
          <button
            className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
            type="submit"
            disabled={isLoading}
          >
            Consultar
          </button>
          <button
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
            type="button"
            disabled={isLoading}
            onClick={onClear}
          >
            Limpiar
          </button>
        </div>
      </form>

      {isLoading ? (
        <p className="px-4 py-8 text-sm text-slate-600">Actualizando stock...</p>
      ) : stocks.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Todavía no hay stock registrado para los filtros seleccionados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Producto</th>
                <th className="px-4 py-3 font-medium">Presentación</th>
                <th className="px-4 py-3 font-medium">Ubicación</th>
                <th className="px-4 py-3 text-right font-medium">
                  Cantidad disponible
                </th>
                <th className="px-4 py-3 font-medium">Actualizado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stocks.map((stock) => (
                <tr key={stock.id}>
                  <td className="px-4 py-3 align-top">
                    <p className="font-medium text-slate-950">
                      {stock.product_name}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {stock.product_sku ?? "Sin SKU"}
                    </p>
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {stock.product_presentation ?? "Sin presentación"}
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {stock.location_name}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-lg font-semibold text-slate-950">
                    {formatQuantity(stock.quantity_on_hand)}
                  </td>
                  <td className="px-4 py-3 align-top text-slate-600">
                    {formatDateTime(stock.updated_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";

function formatQuantity(value: string): string {
  const [units, decimals = ""] = value.split(".");
  const trimmedDecimals = decimals.padEnd(3, "0").slice(0, 3).replace(/0+$/, "");
  return trimmedDecimals ? `${units}.${trimmedDecimals}` : units;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}


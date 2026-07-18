"use client";

import { useState, type FormEvent, type ReactNode } from "react";

import type { Product } from "@/types/product";
import {
  PRODUCTION_STATUS_LABELS,
  type ProductionBatch,
  type ProductionStatus,
} from "@/types/production";

export type ProductionFilterValues = {
  search: string;
  dateFrom: string;
  dateTo: string;
  status: ProductionStatus | "";
  productId: string;
};

type ProductionListProps = {
  batches: ProductionBatch[];
  products: Product[];
  filters: ProductionFilterValues;
  isLoading?: boolean;
  voidingBatchId?: number | null;
  onFiltersChange: (filters: ProductionFilterValues) => void;
  onFilter: () => void;
  onClear: () => void;
  onVoid: (batch: ProductionBatch) => void;
};

const statuses: ProductionStatus[] = ["active", "voided"];

export function ProductionList({
  batches,
  products,
  filters,
  isLoading = false,
  voidingBatchId = null,
  onFiltersChange,
  onFilter,
  onClear,
  onVoid,
}: ProductionListProps) {
  const [expandedBatchId, setExpandedBatchId] = useState<number | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onFilter();
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Producciones recientes
        </h2>
        <span className="text-sm text-slate-500">{batches.length}</span>
      </div>

      <form
        className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-2 xl:grid-cols-5"
        onSubmit={handleSubmit}
      >
        <FilterField label="Buscar">
          <input
            className={fieldClassName}
            type="search"
            placeholder="Número o producto"
            value={filters.search}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, search: event.target.value })
            }
          />
        </FilterField>
        <FilterField label="Desde">
          <input
            className={fieldClassName}
            type="date"
            value={filters.dateFrom}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, dateFrom: event.target.value })
            }
          />
        </FilterField>
        <FilterField label="Hasta">
          <input
            className={fieldClassName}
            type="date"
            value={filters.dateTo}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, dateTo: event.target.value })
            }
          />
        </FilterField>
        <FilterField label="Estado">
          <select
            className={fieldClassName}
            value={filters.status}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({
                ...filters,
                status: event.target.value as ProductionStatus | "",
              })
            }
          >
            <option value="">Todos</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {PRODUCTION_STATUS_LABELS[status]}
              </option>
            ))}
          </select>
        </FilterField>
        <FilterField label="Producto">
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
        </FilterField>
        <div className="flex gap-2 md:col-span-2 xl:col-span-5 xl:justify-end">
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
        <p className="px-4 py-8 text-sm text-slate-600">
          Actualizando producciones...
        </p>
      ) : batches.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Todavía no hay producciones para los filtros seleccionados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Número</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Productos</th>
                <th className="px-4 py-3 text-right font-medium">Producido</th>
                <th className="px-4 py-3 text-right font-medium">Merma</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {batches.map((batch) => {
                const isExpanded = batch.id === expandedBatchId;
                return (
                  <FragmentRows key={batch.id}>
                    <tr>
                      <td className="px-4 py-3 align-top font-semibold text-slate-950">
                        {batch.production_number}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {formatDate(batch.production_date)}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {batch.items.length}
                      </td>
                      <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
                        {formatQuantity(sumQuantities(batch, "quantity_produced"))}
                      </td>
                      <td className="px-4 py-3 text-right align-top text-slate-700">
                        {formatQuantity(sumQuantities(batch, "quantity_waste"))}
                      </td>
                      <td className="px-4 py-3 align-top">
                        <span
                          className={
                            batch.status === "active"
                              ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                              : "inline-flex rounded-md bg-red-50 px-2 py-1 text-xs font-semibold text-red-700"
                          }
                        >
                          {PRODUCTION_STATUS_LABELS[batch.status]}
                        </span>
                      </td>
                      <td className="px-4 py-3 align-top">
                        <div className="flex items-center gap-3">
                          <button
                            className="font-semibold text-water-700 hover:text-water-500"
                            type="button"
                            onClick={() =>
                              setExpandedBatchId(isExpanded ? null : batch.id)
                            }
                          >
                            {isExpanded ? "Ocultar" : "Detalle"}
                          </button>
                          {batch.status === "active" ? (
                            <button
                              className="font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                              type="button"
                              disabled={voidingBatchId === batch.id}
                              onClick={() => onVoid(batch)}
                            >
                              {voidingBatchId === batch.id
                                ? "Anulando..."
                                : "Anular"}
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                    {isExpanded ? (
                      <tr>
                        <td className="bg-slate-50 px-4 py-4" colSpan={7}>
                          <ProductionDetail batch={batch} />
                        </td>
                      </tr>
                    ) : null}
                  </FragmentRows>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function ProductionDetail({ batch }: { batch: ProductionBatch }) {
  return (
    <div className="space-y-3">
      <div className="grid gap-2 text-sm sm:grid-cols-2">
        <p className="text-slate-700">
          <span className="font-semibold text-slate-950">Observación: </span>
          {batch.notes ?? "Sin observación general"}
        </p>
        {batch.void_reason ? (
          <p className="text-red-700">
            <span className="font-semibold">Motivo de anulación: </span>
            {batch.void_reason}
          </p>
        ) : null}
      </div>
      <div className="overflow-x-auto rounded-md border border-slate-200 bg-white">
        <table className="w-full min-w-[680px] border-collapse text-left text-sm">
          <thead className="bg-white text-slate-600">
            <tr>
              <th className="px-3 py-2 font-medium">Producto</th>
              <th className="px-3 py-2 text-right font-medium">Producido</th>
              <th className="px-3 py-2 text-right font-medium">Merma</th>
              <th className="px-3 py-2 font-medium">Observación</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {batch.items.map((item) => (
              <tr key={item.id}>
                <td className="px-3 py-2">
                  <p className="font-medium text-slate-950">
                    {item.product_name_snapshot}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {item.product_sku_snapshot ?? "Sin SKU"}
                    {item.product_presentation_snapshot
                      ? ` · ${item.product_presentation_snapshot}`
                      : ""}
                  </p>
                </td>
                <td className="px-3 py-2 text-right font-semibold text-slate-950">
                  {formatQuantity(item.quantity_produced)}
                </td>
                <td className="px-3 py-2 text-right text-slate-700">
                  {formatQuantity(item.quantity_waste)}
                </td>
                <td className="px-3 py-2 text-slate-700">
                  {item.notes ?? "Sin observación"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FragmentRows({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

function FilterField({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";

function sumQuantities(
  batch: ProductionBatch,
  field: "quantity_produced" | "quantity_waste",
): string {
  const totalThousandths = batch.items.reduce(
    (total, item) => total + toThousandths(item[field]),
    0,
  );
  const units = Math.floor(totalThousandths / 1000);
  const decimals = String(totalThousandths % 1000).padStart(3, "0");
  return `${units}.${decimals}`;
}

function toThousandths(value: string): number {
  const [units, decimals = ""] = value.split(".");
  return Number(units) * 1000 + Number(decimals.padEnd(3, "0").slice(0, 3));
}

function formatQuantity(value: string): string {
  const [units, decimals = ""] = value.split(".");
  const visibleDecimals = decimals
    .padEnd(3, "0")
    .slice(0, 3)
    .replace(/0+$/, "");
  return visibleDecimals ? `${units}.${visibleDecimals}` : units;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
  );
}

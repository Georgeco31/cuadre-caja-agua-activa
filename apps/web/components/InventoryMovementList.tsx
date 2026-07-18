"use client";

import type { FormEvent, ReactNode } from "react";

import {
  INVENTORY_MOVEMENT_STATUS_LABELS,
  INVENTORY_MOVEMENT_TYPE_LABELS,
  type InventoryLocation,
  type InventoryMovement,
  type InventoryMovementStatus,
  type InventoryMovementType,
} from "@/types/inventory";
import type { Product } from "@/types/product";

export type InventoryMovementFilterValues = {
  dateFrom: string;
  dateTo: string;
  productId: string;
  locationId: string;
  movementType: InventoryMovementType | "";
  status: InventoryMovementStatus | "";
};

type InventoryMovementListProps = {
  movements: InventoryMovement[];
  products: Product[];
  locations: InventoryLocation[];
  filters: InventoryMovementFilterValues;
  isLoading?: boolean;
  onFiltersChange: (filters: InventoryMovementFilterValues) => void;
  onFilter: () => void;
  onClear: () => void;
  onVoid: (movement: InventoryMovement) => void;
};

const movementTypes = Object.keys(
  INVENTORY_MOVEMENT_TYPE_LABELS,
) as InventoryMovementType[];
const movementStatuses = Object.keys(
  INVENTORY_MOVEMENT_STATUS_LABELS,
) as InventoryMovementStatus[];

export function InventoryMovementList({
  movements,
  products,
  locations,
  filters,
  isLoading = false,
  onFiltersChange,
  onFilter,
  onClear,
  onVoid,
}: InventoryMovementListProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onFilter();
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Historial de movimientos
        </h2>
        <span className="text-sm text-slate-500">{movements.length}</span>
      </div>

      <form
        className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-2 xl:grid-cols-6"
        onSubmit={handleSubmit}
      >
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
        <FilterField label="Ubicación">
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
        </FilterField>
        <FilterField label="Tipo">
          <select
            className={fieldClassName}
            value={filters.movementType}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({
                ...filters,
                movementType: event.target.value as InventoryMovementType | "",
              })
            }
          >
            <option value="">Todos</option>
            {movementTypes.map((movementType) => (
              <option key={movementType} value={movementType}>
                {INVENTORY_MOVEMENT_TYPE_LABELS[movementType]}
              </option>
            ))}
          </select>
        </FilterField>
        <FilterField label="Estado">
          <select
            className={fieldClassName}
            value={filters.status}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({
                ...filters,
                status: event.target.value as InventoryMovementStatus | "",
              })
            }
          >
            <option value="">Todos</option>
            {movementStatuses.map((movementStatus) => (
              <option key={movementStatus} value={movementStatus}>
                {INVENTORY_MOVEMENT_STATUS_LABELS[movementStatus]}
              </option>
            ))}
          </select>
        </FilterField>
        <div className="flex gap-2 md:col-span-2 xl:col-span-6 xl:justify-end">
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
          Actualizando movimientos...
        </p>
      ) : movements.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Todavía no hay movimientos para los filtros seleccionados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1220px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Producto</th>
                <th className="px-4 py-3 font-medium">Ubicación</th>
                <th className="px-4 py-3 text-right font-medium">Cantidad</th>
                <th className="px-4 py-3 text-right font-medium">
                  Costo unitario
                </th>
                <th className="px-4 py-3 text-right font-medium">Costo total</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Motivo</th>
                <th className="px-4 py-3 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {movements.map((movement) => (
                <tr key={movement.id}>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {formatDate(movement.movement_date)}
                  </td>
                  <td className="px-4 py-3 align-top font-medium text-slate-950">
                    {INVENTORY_MOVEMENT_TYPE_LABELS[movement.movement_type]}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <p className="font-medium text-slate-950">
                      {movement.product_name_snapshot}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {movement.product_sku_snapshot ?? "Sin SKU"}
                      {movement.product_presentation_snapshot
                        ? ` · ${movement.product_presentation_snapshot}`
                        : ""}
                    </p>
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {movement.location_name}
                  </td>
                  <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
                    {formatQuantity(movement.quantity)}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-slate-700">
                    {movement.unit_cost
                      ? formatMoney(movement.unit_cost)
                      : "Sin costo"}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-slate-700">
                    {movement.total_cost
                      ? formatMoney(movement.total_cost)
                      : "Sin costo"}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <span
                      className={
                        movement.status === "active"
                          ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                          : "inline-flex rounded-md bg-red-50 px-2 py-1 text-xs font-semibold text-red-700"
                      }
                    >
                      {INVENTORY_MOVEMENT_STATUS_LABELS[movement.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    <p className="max-w-56">
                      {movement.reason ?? "Sin observación"}
                    </p>
                    {movement.void_reason ? (
                      <p className="mt-1 max-w-56 text-xs text-red-700">
                        Anulación: {movement.void_reason}
                      </p>
                    ) : null}
                  </td>
                  <td className="px-4 py-3 align-top">
                    {movement.status === "active" ? (
                      <button
                        className="font-semibold text-red-700 hover:text-red-600"
                        type="button"
                        onClick={() => onVoid(movement)}
                      >
                        Anular
                      </button>
                    ) : (
                      <span className="text-slate-400">Sin acciones</span>
                    )}
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

function formatQuantity(value: string): string {
  const [units, decimals = ""] = value.split(".");
  const trimmedDecimals = decimals.padEnd(3, "0").slice(0, 3).replace(/0+$/, "");
  return trimmedDecimals ? `${units}.${trimmedDecimals}` : units;
}

function formatMoney(value: string): string {
  const [units, decimals = ""] = value.split(".");
  return `$${units}.${decimals.padEnd(2, "0").slice(0, 2)}`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
  );
}

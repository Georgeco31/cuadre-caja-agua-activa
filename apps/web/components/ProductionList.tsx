"use client";

import { useState, type FormEvent, type ReactNode } from "react";

import type { InventoryLocation } from "@/types/inventory";
import type { Product } from "@/types/product";
import {
  PRODUCTION_STATUS_LABELS,
  type ProductionBatch,
  type ProductionInventoryApplication,
  type ProductionInventoryApplyPayload,
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
  locations: InventoryLocation[];
  inventoryApplications: Record<
    number,
    ProductionInventoryApplication | undefined
  >;
  filters: ProductionFilterValues;
  isLoading?: boolean;
  canVoid?: boolean;
  voidingBatchId?: number | null;
  applyingBatchId?: number | null;
  voidingApplicationId?: number | null;
  onFiltersChange: (filters: ProductionFilterValues) => void;
  onFilter: () => void;
  onClear: () => void;
  onVoid: (batch: ProductionBatch) => void;
  onApplyInventory: (
    batch: ProductionBatch,
    payload: ProductionInventoryApplyPayload,
  ) => Promise<boolean>;
  onVoidInventoryApplication: (
    batch: ProductionBatch,
    application: ProductionInventoryApplication,
  ) => void;
};

const statuses: ProductionStatus[] = ["active", "voided"];

export function ProductionList({
  batches,
  products,
  locations,
  inventoryApplications,
  filters,
  isLoading = false,
  canVoid = false,
  voidingBatchId = null,
  applyingBatchId = null,
  voidingApplicationId = null,
  onFiltersChange,
  onFilter,
  onClear,
  onVoid,
  onApplyInventory,
  onVoidInventoryApplication,
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
          <table className="w-full min-w-[1020px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Número</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Productos</th>
                <th className="px-4 py-3 text-right font-medium">Producido</th>
                <th className="px-4 py-3 text-right font-medium">Merma</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Inventario</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {batches.map((batch) => {
                const isExpanded = batch.id === expandedBatchId;
                const inventoryApplication = inventoryApplications[batch.id];
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
                        <InventoryApplicationBadge
                          application={inventoryApplication}
                        />
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
                          {canVoid && batch.status === "active" ? (
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
                        <td className="bg-slate-50 px-4 py-4" colSpan={8}>
                          <ProductionDetail
                            batch={batch}
                            locations={locations}
                            inventoryApplication={inventoryApplication}
                            isApplying={applyingBatchId === batch.id}
                            isVoidingApplication={
                              inventoryApplication?.application_id ===
                              voidingApplicationId
                            }
                            canVoid={canVoid}
                            onApplyInventory={onApplyInventory}
                            onVoidInventoryApplication={
                              onVoidInventoryApplication
                            }
                          />
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

function ProductionDetail({
  batch,
  locations,
  inventoryApplication,
  isApplying,
  isVoidingApplication,
  canVoid,
  onApplyInventory,
  onVoidInventoryApplication,
}: {
  batch: ProductionBatch;
  locations: InventoryLocation[];
  inventoryApplication: ProductionInventoryApplication | undefined;
  isApplying: boolean;
  isVoidingApplication: boolean;
  canVoid: boolean;
  onApplyInventory: (
    batch: ProductionBatch,
    payload: ProductionInventoryApplyPayload,
  ) => Promise<boolean>;
  onVoidInventoryApplication: (
    batch: ProductionBatch,
    application: ProductionInventoryApplication,
  ) => void;
}) {
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
              <th className="px-3 py-2 text-right font-medium">Neto</th>
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
                <td className="px-3 py-2 text-right font-semibold text-emerald-700">
                  {formatQuantity(netQuantity(item))}
                </td>
                <td className="px-3 py-2 text-slate-700">
                  {item.notes ?? "Sin observación"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ProductionInventoryPanel
        batch={batch}
        locations={locations}
        application={inventoryApplication}
        isApplying={isApplying}
        isVoiding={isVoidingApplication}
        canVoid={canVoid}
        onApply={onApplyInventory}
        onVoid={onVoidInventoryApplication}
      />
    </div>
  );
}

function ProductionInventoryPanel({
  batch,
  locations,
  application,
  isApplying,
  isVoiding,
  canVoid,
  onApply,
  onVoid,
}: {
  batch: ProductionBatch;
  locations: InventoryLocation[];
  application: ProductionInventoryApplication | undefined;
  isApplying: boolean;
  isVoiding: boolean;
  canVoid: boolean;
  onApply: (
    batch: ProductionBatch,
    payload: ProductionInventoryApplyPayload,
  ) => Promise<boolean>;
  onVoid: (
    batch: ProductionBatch,
    application: ProductionInventoryApplication,
  ) => void;
}) {
  const [locationId, setLocationId] = useState("");
  const [movementDate, setMovementDate] = useState(batch.production_date);
  const [notes, setNotes] = useState("");
  const hasNetQuantity = batch.items.some(
    (item) => toThousandths(netQuantity(item)) > 0,
  );

  async function handleApply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const selectedLocation = locations.find(
      (location) => location.id === Number(locationId),
    );
    if (!selectedLocation || !movementDate) {
      return;
    }
    const confirmed = window.confirm(
      `Aplicar la producción ${batch.production_number} a ${selectedLocation.name}?`,
    );
    if (!confirmed) {
      return;
    }
    const saved = await onApply(batch, {
      location_id: selectedLocation.id,
      movement_date: movementDate,
      notes: notes.trim() || null,
    });
    if (saved) {
      setNotes("");
    }
  }

  return (
    <div className="border-t border-slate-200 pt-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-950">
            Aplicación a inventario
          </h3>
          <p className="mt-1 text-sm text-slate-600">
            Solo las cantidades netas positivas generan entradas de inventario.
          </p>
        </div>
        <InventoryApplicationBadge application={application} />
      </div>

      {!application ? (
        <p className="mt-4 text-sm text-slate-600">Cargando estado...</p>
      ) : application.state === "applied" ? (
        <div className="mt-4 space-y-3">
          <dl className="grid gap-3 text-sm sm:grid-cols-3">
            <ApplicationValue
              label="Ubicación"
              value={application.location_name ?? "Sin ubicación"}
            />
            <ApplicationValue
              label="Fecha de movimiento"
              value={
                application.items[0]
                  ? formatDate(application.items[0].movement_date)
                  : "Sin fecha"
              }
            />
            <ApplicationValue
              label="Aplicado"
              value={
                application.applied_at
                  ? formatDateTime(application.applied_at)
                  : "Sin fecha"
              }
            />
          </dl>
          <div className="overflow-x-auto border-y border-slate-200 bg-white">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-3 py-2 font-medium">Producto</th>
                  <th className="px-3 py-2 text-right font-medium">Cantidad</th>
                  <th className="px-3 py-2 text-right font-medium">Movimiento</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {application.items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-3 py-2 text-slate-950">
                      {productName(batch, item.product_id)}
                    </td>
                    <td className="px-3 py-2 text-right font-semibold text-slate-950">
                      {formatQuantity(item.quantity_applied)}
                    </td>
                    <td className="px-3 py-2 text-right text-slate-700">
                      #{item.inventory_movement_id}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {canVoid ? <div className="flex justify-end">
            <button
              className="h-10 rounded-md border border-red-300 bg-white px-4 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:border-slate-200 disabled:text-slate-400"
              type="button"
              disabled={isVoiding}
              onClick={() => onVoid(batch, application)}
            >
              {isVoiding ? "Anulando aplicación..." : "Anular aplicación"}
            </button>
          </div> : null}
        </div>
      ) : (
        <>
          {application.state === "voided" ? (
            <p className="mt-4 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
              La aplicación anterior a {application.location_name ?? "inventario"}
              {application.void_reason
                ? ` fue anulada: ${application.void_reason}`
                : " fue anulada."}
            </p>
          ) : null}
          {batch.status === "active" ? (
            <form
              className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4"
              onSubmit={handleApply}
            >
              <FilterField label="Ubicación de destino">
                <select
                  className={fieldClassName}
                  value={locationId}
                  required
                  disabled={isApplying || locations.length === 0}
                  onChange={(event) => setLocationId(event.target.value)}
                >
                  <option value="">Seleccionar ubicación</option>
                  {locations.map((location) => (
                    <option key={location.id} value={location.id}>
                      {location.name}
                    </option>
                  ))}
                </select>
              </FilterField>
              <FilterField label="Fecha de movimiento">
                <input
                  className={fieldClassName}
                  type="date"
                  value={movementDate}
                  required
                  disabled={isApplying}
                  onChange={(event) => setMovementDate(event.target.value)}
                />
              </FilterField>
              <FilterField label="Nota opcional">
                <input
                  className={fieldClassName}
                  value={notes}
                  maxLength={300}
                  disabled={isApplying}
                  onChange={(event) => setNotes(event.target.value)}
                />
              </FilterField>
              <div className="flex items-end">
                <button
                  className="h-10 w-full rounded-md bg-emerald-700 px-4 text-sm font-semibold text-white hover:bg-emerald-600 disabled:bg-slate-300"
                  type="submit"
                  disabled={
                    isApplying ||
                    !locationId ||
                    !movementDate ||
                    !hasNetQuantity
                  }
                >
                  {isApplying ? "Aplicando..." : "Aplicar a inventario"}
                </button>
              </div>
              {locations.length === 0 ? (
                <p className="text-sm text-amber-800 md:col-span-2 xl:col-span-4">
                  No hay ubicaciones activas disponibles.
                </p>
              ) : null}
              {!hasNetQuantity ? (
                <p className="text-sm text-amber-800 md:col-span-2 xl:col-span-4">
                  Esta producción no tiene una cantidad neta positiva para aplicar.
                </p>
              ) : null}
            </form>
          ) : null}
        </>
      )}
    </div>
  );
}

function InventoryApplicationBadge({
  application,
}: {
  application: ProductionInventoryApplication | undefined;
}) {
  if (!application) {
    return <span className="text-xs text-slate-500">Consultando...</span>;
  }
  const styles = {
    not_applied: "bg-amber-50 text-amber-800",
    applied: "bg-emerald-50 text-emerald-700",
    voided: "bg-slate-200 text-slate-700",
  }[application.state];
  const label = {
    not_applied: "Pendiente",
    applied: "Aplicada",
    voided: "Aplicación anulada",
  }[application.state];
  return (
    <span className={`inline-flex rounded-md px-2 py-1 text-xs font-semibold ${styles}`}>
      {label}
    </span>
  );
}

function ApplicationValue({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-medium text-slate-500">{label}</dt>
      <dd className="mt-1 font-semibold text-slate-950">{value}</dd>
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

function netQuantity(item: ProductionBatch["items"][number]): string {
  const totalThousandths =
    toThousandths(item.quantity_produced) -
    toThousandths(item.quantity_waste);
  const units = Math.floor(totalThousandths / 1000);
  const decimals = String(totalThousandths % 1000).padStart(3, "0");
  return `${units}.${decimals}`;
}

function productName(batch: ProductionBatch, productId: number): string {
  return (
    batch.items.find((item) => item.product_id === productId)
      ?.product_name_snapshot ?? `Producto #${productId}`
  );
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

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

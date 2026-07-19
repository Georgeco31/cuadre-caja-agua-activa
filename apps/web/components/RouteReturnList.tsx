"use client";

import { useState, type FormEvent, type ReactNode } from "react";

import type { DeliveryRoute } from "@/types/deliveryRoute";
import {
  ROUTE_RETURN_STATUS_LABELS,
  type RouteReturn,
  type RouteReturnStatus,
} from "@/types/routeReturn";
import type { Vehicle } from "@/types/vehicle";

export type RouteReturnFilterValues = {
  search: string;
  dateFrom: string;
  dateTo: string;
  status: RouteReturnStatus | "";
  routeId: string;
  vehicleId: string;
};

type RouteReturnListProps = {
  returns: RouteReturn[];
  routes: DeliveryRoute[];
  vehicles: Vehicle[];
  filters: RouteReturnFilterValues;
  isLoading?: boolean;
  voidingReturnId?: number | null;
  onFiltersChange: (filters: RouteReturnFilterValues) => void;
  onFilter: () => void;
  onClear: () => void;
  onVoid: (routeReturn: RouteReturn) => void;
};

const statuses: RouteReturnStatus[] = ["active", "voided"];

export function RouteReturnList({
  returns,
  routes,
  vehicles,
  filters,
  isLoading = false,
  voidingReturnId = null,
  onFiltersChange,
  onFilter,
  onClear,
  onVoid,
}: RouteReturnListProps) {
  const [expandedReturnId, setExpandedReturnId] = useState<number | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onFilter();
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Retornos recientes
        </h2>
        <span className="text-sm text-slate-500">{returns.length}</span>
      </div>

      <form
        className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-2 xl:grid-cols-6"
        onSubmit={handleSubmit}
      >
        <FilterField label="Buscar">
          <input
            className={fieldClassName}
            type="search"
            placeholder="Número, carga o producto"
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
                status: event.target.value as RouteReturnStatus | "",
              })
            }
          >
            <option value="">Todos</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {ROUTE_RETURN_STATUS_LABELS[status]}
              </option>
            ))}
          </select>
        </FilterField>
        <FilterField label="Ruta">
          <select
            className={fieldClassName}
            value={filters.routeId}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, routeId: event.target.value })
            }
          >
            <option value="">Todas</option>
            {routes.map((route) => (
              <option key={route.id} value={route.id}>
                {route.name}
              </option>
            ))}
          </select>
        </FilterField>
        <FilterField label="Vehículo">
          <select
            className={fieldClassName}
            value={filters.vehicleId}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, vehicleId: event.target.value })
            }
          >
            <option value="">Todos</option>
            {vehicles.map((vehicle) => (
              <option key={vehicle.id} value={vehicle.id}>
                {vehicle.name}
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
          Actualizando retornos...
        </p>
      ) : returns.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Todavía no hay retornos para los filtros seleccionados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1160px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Número</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Carga</th>
                <th className="px-4 py-3 font-medium">Ruta</th>
                <th className="px-4 py-3 font-medium">Vehículo</th>
                <th className="px-4 py-3 font-medium">Retorno</th>
                <th className="px-4 py-3 text-right font-medium">Productos</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {returns.map((routeReturn) => {
                const isExpanded = expandedReturnId === routeReturn.id;
                return (
                  <FragmentRows key={routeReturn.id}>
                    <tr>
                      <td className="px-4 py-3 align-top font-semibold text-slate-950">
                        {routeReturn.return_number}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {formatDate(routeReturn.return_date)}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {routeReturn.route_load_number}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {routeReturn.route_name}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {routeReturn.vehicle_name}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        <p>{routeReturn.source_location_name}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          Hacia {routeReturn.destination_location_name}
                        </p>
                      </td>
                      <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
                        {routeReturn.items.length}
                      </td>
                      <td className="px-4 py-3 align-top">
                        <StatusBadge status={routeReturn.status} />
                      </td>
                      <td className="px-4 py-3 align-top">
                        <div className="flex items-center gap-3">
                          <button
                            className="font-semibold text-water-700 hover:text-water-500"
                            type="button"
                            onClick={() =>
                              setExpandedReturnId(
                                isExpanded ? null : routeReturn.id,
                              )
                            }
                          >
                            {isExpanded ? "Ocultar" : "Detalle"}
                          </button>
                          {routeReturn.status === "active" ? (
                            <button
                              className="font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                              type="button"
                              disabled={voidingReturnId === routeReturn.id}
                              onClick={() => onVoid(routeReturn)}
                            >
                              {voidingReturnId === routeReturn.id
                                ? "Anulando..."
                                : "Anular"}
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                    {isExpanded ? (
                      <tr>
                        <td className="bg-slate-50 px-4 py-4" colSpan={9}>
                          <RouteReturnDetail routeReturn={routeReturn} />
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

function RouteReturnDetail({ routeReturn }: { routeReturn: RouteReturn }) {
  return (
    <div className="space-y-3">
      <div className="grid gap-2 text-sm sm:grid-cols-2">
        <p className="text-slate-700">
          <span className="font-semibold text-slate-950">Observación: </span>
          {routeReturn.notes ?? "Sin observación"}
        </p>
        {routeReturn.void_reason ? (
          <p className="text-red-700">
            <span className="font-semibold">Motivo de anulación: </span>
            {routeReturn.void_reason}
          </p>
        ) : null}
      </div>
      <div className="overflow-x-auto rounded-md border border-slate-200 bg-white">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="bg-white text-slate-600">
            <tr>
              <th className="px-3 py-2 font-medium">Producto</th>
              <th className="px-3 py-2 text-right font-medium">Cargado</th>
              <th className="px-3 py-2 text-right font-medium">Devuelto</th>
              <th className="px-3 py-2 text-right font-medium">Salida vehículo</th>
              <th className="px-3 py-2 text-right font-medium">Entrada destino</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {routeReturn.items.map((item) => (
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
                <td className="px-3 py-2 text-right text-slate-700">
                  {formatQuantity(item.quantity_loaded)}
                </td>
                <td className="px-3 py-2 text-right font-semibold text-slate-950">
                  {formatQuantity(item.quantity_returned)}
                </td>
                <td className="px-3 py-2 text-right text-slate-700">
                  #{item.source_exit_movement_id} · {" "}
                  {movementStatus(item.source_exit_movement_status)}
                </td>
                <td className="px-3 py-2 text-right text-slate-700">
                  #{item.destination_entry_movement_id} · {" "}
                  {movementStatus(item.destination_entry_movement_status)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: RouteReturnStatus }) {
  return (
    <span
      className={
        status === "active"
          ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
          : "inline-flex rounded-md bg-red-50 px-2 py-1 text-xs font-semibold text-red-700"
      }
    >
      {ROUTE_RETURN_STATUS_LABELS[status]}
    </span>
  );
}

function movementStatus(status: "active" | "voided"): string {
  return status === "active" ? "Activo" : "Anulado";
}

function FilterField({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function FragmentRows({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
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

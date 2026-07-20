"use client";

import { useState, type FormEvent, type ReactNode } from "react";

import type { DeliveryRoute } from "@/types/deliveryRoute";
import {
  ROUTE_CLOSURE_STATUS_LABELS,
  type RouteClosure,
  type RouteClosureStatus,
} from "@/types/routeClosure";
import type { Vehicle } from "@/types/vehicle";

export type RouteClosureFilterValues = {
  search: string;
  dateFrom: string;
  dateTo: string;
  status: RouteClosureStatus | "";
  routeId: string;
  vehicleId: string;
};

type RouteClosureListProps = {
  closures: RouteClosure[];
  routes: DeliveryRoute[];
  vehicles: Vehicle[];
  filters: RouteClosureFilterValues;
  isLoading: boolean;
  voidingClosureId: number | null;
  onFiltersChange: (filters: RouteClosureFilterValues) => void;
  onFilter: () => void;
  onClear: () => void;
  onVoid: (closure: RouteClosure) => void;
};

export function RouteClosureList({
  closures,
  routes,
  vehicles,
  filters,
  isLoading,
  voidingClosureId,
  onFiltersChange,
  onFilter,
  onClear,
  onVoid,
}: RouteClosureListProps) {
  const [expandedClosureId, setExpandedClosureId] = useState<number | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onFilter();
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Cierres financieros
        </h2>
        <span className="text-sm text-slate-500">{closures.length}</span>
      </div>

      <form
        className="grid gap-3 border-b border-slate-200 bg-slate-50 p-4 md:grid-cols-2 xl:grid-cols-6"
        onSubmit={handleSubmit}
      >
        <FilterField label="Buscar">
          <input
            className={fieldClassName}
            type="search"
            placeholder="Cierre, carga, ruta o vehículo"
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
                status: event.target.value as RouteClosureStatus | "",
              })
            }
          >
            <option value="">Todos</option>
            <option value="active">Activos</option>
            <option value="voided">Anulados</option>
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
          Actualizando cierres...
        </p>
      ) : closures.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Todavía no hay cierres para los filtros seleccionados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1220px] border-collapse text-left text-sm">
            <thead className="bg-white text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Cierre</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Ruta</th>
                <th className="px-4 py-3 font-medium">Vehículo</th>
                <th className="px-4 py-3 text-right font-medium">Esperado</th>
                <th className="px-4 py-3 text-right font-medium">Entregado</th>
                <th className="px-4 py-3 text-right font-medium">Diferencia</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {closures.map((closure) => {
                const isExpanded = expandedClosureId === closure.id;
                const isVoiding = voidingClosureId === closure.id;
                return (
                  <FragmentRows key={closure.id}>
                    <tr>
                      <td className="px-4 py-3 align-top">
                        <p className="font-semibold text-slate-950">
                          {closure.closure_number}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {closure.load_number_snapshot}
                        </p>
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {formatDate(closure.closure_date)}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {closure.route_name_snapshot}
                      </td>
                      <td className="px-4 py-3 align-top text-slate-700">
                        {closure.vehicle_name_snapshot}
                      </td>
                      <td className="px-4 py-3 text-right align-top text-slate-700">
                        {formatMoney(closure.expected_cash_total)}
                      </td>
                      <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
                        {formatMoney(closure.delivered_cash_total)}
                      </td>
                      <td
                        className={`px-4 py-3 text-right align-top font-semibold ${differenceClassName(closure.difference_amount)}`}
                      >
                        {formatSignedMoney(closure.difference_amount)}
                      </td>
                      <td className="px-4 py-3 align-top">
                        <StatusBadge status={closure.status} />
                      </td>
                      <td className="px-4 py-3 align-top">
                        <div className="flex items-center gap-3">
                          <button
                            className="font-semibold text-water-700 hover:text-water-500"
                            type="button"
                            onClick={() =>
                              setExpandedClosureId(isExpanded ? null : closure.id)
                            }
                          >
                            {isExpanded ? "Ocultar" : "Detalle"}
                          </button>
                          {closure.status === "active" ? (
                            <button
                              className="font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                              type="button"
                              disabled={isVoiding}
                              onClick={() => onVoid(closure)}
                            >
                              {isVoiding ? "Anulando..." : "Anular"}
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                    {isExpanded ? (
                      <tr>
                        <td className="bg-slate-50 px-4 py-4" colSpan={9}>
                          <ClosureDetail closure={closure} />
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

function ClosureDetail({ closure }: { closure: RouteClosure }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <Detail label="Ventas contado" value={formatMoney(closure.cash_sales_total)} />
        <Detail label="Ventas crédito" value={formatMoney(closure.credit_sales_total)} />
        <Detail label="Cobros" value={formatMoney(closure.payments_total)} />
        <Detail label="Efectivo esperado" value={formatMoney(closure.expected_cash_total)} />
        <Detail label="Efectivo entregado" value={formatMoney(closure.delivered_cash_total)} />
      </div>
      <div className="grid gap-2 text-sm sm:grid-cols-2">
        <p className="text-slate-700">
          <span className="font-semibold text-slate-950">Observaciones: </span>
          {closure.notes ?? "Sin observaciones"}
        </p>
        {closure.void_reason ? (
          <p className="text-red-700">
            <span className="font-semibold">Motivo de anulación: </span>
            {closure.void_reason}
          </p>
        ) : null}
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <dl>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 font-semibold text-slate-950">{value}</dd>
    </dl>
  );
}

function StatusBadge({ status }: { status: RouteClosureStatus }) {
  return (
    <span
      className={
        status === "active"
          ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
          : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
      }
    >
      {ROUTE_CLOSURE_STATUS_LABELS[status]}
    </span>
  );
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

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
  );
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

function formatSignedMoney(value: string): string {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "$0.00";
  }
  const sign = amount > 0 ? "+" : "";
  return `${sign}$${amount.toFixed(2)}`;
}

function differenceClassName(value: string): string {
  const amount = Number(value);
  if (amount > 0) {
    return "text-emerald-700";
  }
  if (amount < 0) {
    return "text-red-700";
  }
  return "text-slate-700";
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";

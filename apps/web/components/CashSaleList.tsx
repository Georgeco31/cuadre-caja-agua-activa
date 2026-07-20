"use client";

import { useState, type FormEvent, type ReactNode } from "react";

import type { Customer } from "@/types/customer";
import {
  CREDIT_STATUS_LABELS,
  SALE_PAYMENT_METHOD_LABELS,
  SALE_STATUS_LABELS,
  type CashSale,
  type SalePaymentMethod,
  type SaleStatus,
} from "@/types/sale";

export type CashSaleFilterValues = {
  search: string;
  dateFrom: string;
  dateTo: string;
  status: SaleStatus | "";
  customerId: string;
  paymentMethod: SalePaymentMethod | "";
};

export type CashSaleListProps = {
  mode?: "cash" | "credit";
  sales: CashSale[];
  customers: Customer[];
  filters: CashSaleFilterValues;
  hasActiveFilters?: boolean;
  isLoading?: boolean;
  voidingSaleId?: number | null;
  onFiltersChange: (filters: CashSaleFilterValues) => void;
  onFilter: () => void;
  onClearFilters: () => void;
  onVoid: (sale: CashSale) => void;
};

const paymentMethods = Object.keys(
  SALE_PAYMENT_METHOD_LABELS,
) as SalePaymentMethod[];

export function CashSaleList({
  mode = "cash",
  sales,
  customers,
  filters,
  hasActiveFilters = false,
  isLoading = false,
  voidingSaleId = null,
  onFiltersChange,
  onFilter,
  onClearFilters,
  onVoid,
}: CashSaleListProps) {
  const isCredit = mode === "credit";
  const [expandedSaleId, setExpandedSaleId] = useState<number | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onFilter();
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-2 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-lg font-semibold text-slate-950">
          {isCredit ? "Ventas a crédito recientes" : "Ventas recientes"}
        </h2>
        <span className="text-sm text-slate-500">{sales.length}</span>
      </div>

      <form
        className={
          isCredit
            ? "grid gap-3 border-b border-slate-200 bg-slate-50 p-4 md:grid-cols-2 xl:grid-cols-[minmax(220px,2fr)_145px_145px_135px_minmax(180px,1fr)_auto_auto] xl:items-end"
            : "grid gap-3 border-b border-slate-200 bg-slate-50 p-4 md:grid-cols-2 xl:grid-cols-[minmax(180px,2fr)_145px_145px_135px_minmax(170px,1fr)_145px_auto_auto] xl:items-end"
        }
        onSubmit={handleSubmit}
      >
        <FilterField label="Buscar">
          <input
            className={fieldClassName}
            type="search"
            placeholder="Número o cliente"
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
                status: event.target.value as SaleStatus | "",
              })
            }
          >
            <option value="">Todos</option>
            <option value="active">Activas</option>
            <option value="voided">Anuladas</option>
          </select>
        </FilterField>
        <FilterField label="Cliente">
          <select
            className={fieldClassName}
            value={filters.customerId}
            disabled={isLoading}
            onChange={(event) =>
              onFiltersChange({ ...filters, customerId: event.target.value })
            }
          >
            <option value="">Todos</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.name}
              </option>
            ))}
          </select>
        </FilterField>
        {!isCredit ? (
          <FilterField label="Pago">
            <select
              className={fieldClassName}
              value={filters.paymentMethod}
              disabled={isLoading}
              onChange={(event) =>
                onFiltersChange({
                  ...filters,
                  paymentMethod: event.target.value as SalePaymentMethod | "",
                })
              }
            >
              <option value="">Todos</option>
              {paymentMethods.map((method) => (
                <option key={method} value={method}>
                  {SALE_PAYMENT_METHOD_LABELS[method]}
                </option>
              ))}
            </select>
          </FilterField>
        ) : null}
        <button
          className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
          type="submit"
          disabled={isLoading}
        >
          Buscar
        </button>
        <button
          className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
          type="button"
          disabled={isLoading}
          onClick={onClearFilters}
        >
          Limpiar
        </button>
      </form>

      {isLoading ? (
        <p className="px-4 py-8 text-sm text-slate-600">Cargando ventas...</p>
      ) : sales.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron ventas con los filtros seleccionados."
            : "Todavía no hay ventas registradas."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table
            className={
              isCredit
                ? "w-full min-w-[1240px] border-collapse text-left text-sm"
                : "w-full min-w-[1020px] border-collapse text-left text-sm"
            }
          >
            <thead className="bg-white text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Venta</th>
                <th className="px-4 py-3 font-medium">Cliente</th>
                {isCredit ? (
                  <th className="px-4 py-3 font-medium">Vencimiento</th>
                ) : (
                  <th className="px-4 py-3 font-medium">Pago</th>
                )}
                <th className="px-4 py-3 text-right font-medium">Total</th>
                {isCredit ? (
                  <>
                    <th className="px-4 py-3 text-right font-medium">Pagado</th>
                    <th className="px-4 py-3 text-right font-medium">Saldo</th>
                  </>
                ) : null}
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sales.map((sale) => {
                const isExpanded = expandedSaleId === sale.id;
                const isVoiding = voidingSaleId === sale.id;
                return (
                  <SaleRows
                    key={sale.id}
                    sale={sale}
                    mode={mode}
                    isExpanded={isExpanded}
                    isVoiding={isVoiding}
                    onToggle={() =>
                      setExpandedSaleId(isExpanded ? null : sale.id)
                    }
                    onVoid={() => onVoid(sale)}
                  />
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

type SaleRowsProps = {
  sale: CashSale;
  mode: "cash" | "credit";
  isExpanded: boolean;
  isVoiding: boolean;
  onToggle: () => void;
  onVoid: () => void;
};

function SaleRows({
  sale,
  mode,
  isExpanded,
  isVoiding,
  onToggle,
  onVoid,
}: SaleRowsProps) {
  const isCredit = mode === "credit";
  return (
    <>
      <tr>
        <td className="px-4 py-3 align-top">
          <p className="font-medium text-slate-950">{sale.sale_number}</p>
          <p className="mt-1 text-xs text-slate-500">
            {formatSaleDate(sale.sale_date)} · {sale.items.length} producto
            {sale.items.length === 1 ? "" : "s"}
          </p>
          <p className="mt-1 text-xs text-slate-600">
            {sale.route_load_number
              ? `${sale.route_load_number} · ${sale.route_name} · ${sale.route_vehicle_name}`
              : "Sin carga de ruta"}
          </p>
        </td>
        <td className="px-4 py-3 align-top text-slate-700">
          {sale.customer_name_snapshot}
        </td>
        {isCredit ? (
          <td className="px-4 py-3 align-top text-slate-700">
            {sale.due_date ? formatSaleDate(sale.due_date) : "Sin fecha"}
          </td>
        ) : (
          <td className="px-4 py-3 align-top text-slate-700">
            {SALE_PAYMENT_METHOD_LABELS[sale.payment_method]}
          </td>
        )}
        <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
          {formatMoney(sale.total_amount)}
        </td>
        {isCredit ? (
          <>
            <td className="px-4 py-3 text-right align-top text-slate-700">
              {formatMoney(sale.paid_amount)}
            </td>
            <td className="px-4 py-3 text-right align-top font-semibold text-amber-700">
              {formatMoney(sale.balance_amount)}
            </td>
          </>
        ) : null}
        <td className="px-4 py-3 align-top">
          <span
            className={
              isCredit && sale.credit_status === "pending"
                ? "inline-flex rounded-md bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700"
                : sale.status === "active"
                  ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                  : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
            }
          >
            {isCredit
              ? CREDIT_STATUS_LABELS[sale.credit_status]
              : SALE_STATUS_LABELS[sale.status]}
          </span>
        </td>
        <td className="px-4 py-3 align-top">
          <div className="flex items-center gap-3">
            <button
              className="font-semibold text-water-700 hover:text-water-500"
              type="button"
              onClick={onToggle}
            >
              {isExpanded ? "Ocultar" : "Ver detalle"}
            </button>
            {sale.status === "active" ? (
              <button
                className="font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                type="button"
                disabled={isVoiding}
                onClick={onVoid}
              >
                {isVoiding ? "Anulando..." : "Anular"}
              </button>
            ) : null}
          </div>
        </td>
      </tr>
      {isExpanded ? (
        <tr>
          <td className="bg-slate-50 px-4 py-4" colSpan={isCredit ? 8 : 6}>
            <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(220px,1fr)]">
              <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
                <table className="w-full border-collapse text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600">
                    <tr>
                      <th className="px-3 py-2 font-medium">Producto</th>
                      <th className="px-3 py-2 text-right font-medium">
                        Cantidad
                      </th>
                      <th className="px-3 py-2 text-right font-medium">
                        Precio
                      </th>
                      <th className="px-3 py-2 text-right font-medium">
                        Subtotal
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sale.items.map((item) => (
                      <tr key={item.id}>
                        <td className="px-3 py-2 text-slate-700">
                          <p className="font-medium text-slate-950">
                            {item.product_name_snapshot}
                          </p>
                          <p className="mt-1 text-slate-500">
                            {item.product_presentation_snapshot ??
                              item.product_sku_snapshot ??
                              "Sin referencia"}
                          </p>
                        </td>
                        <td className="px-3 py-2 text-right text-slate-700">
                          {formatQuantity(item.quantity)}
                        </td>
                        <td className="px-3 py-2 text-right text-slate-700">
                          {formatMoney(item.unit_price)}
                        </td>
                        <td className="px-3 py-2 text-right font-semibold text-slate-950">
                          {formatMoney(item.subtotal)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="text-sm text-slate-600">
                {isCredit ? (
                  <div className="mb-3 grid grid-cols-3 gap-3">
                    <DetailAmount label="Total" value={sale.total_amount} />
                    <DetailAmount label="Pagado" value={sale.paid_amount} />
                    <DetailAmount label="Saldo" value={sale.balance_amount} />
                  </div>
                ) : null}
                <p className="mb-3">
                  <span className="font-medium text-slate-950">
                    Carga de ruta:
                  </span>{" "}
                  {sale.route_load_number
                    ? `${sale.route_load_number} · ${sale.route_name} · ${sale.route_vehicle_name}`
                    : "No asociada"}
                </p>
                <p>
                  <span className="font-medium text-slate-950">Notas:</span>{" "}
                  {sale.notes ?? "Sin observaciones"}
                </p>
                {sale.void_reason ? (
                  <p className="mt-2">
                    <span className="font-medium text-slate-950">
                      Motivo de anulación:
                    </span>{" "}
                    {sale.void_reason}
                  </p>
                ) : null}
              </div>
            </div>
          </td>
        </tr>
      ) : null}
    </>
  );
}

function DetailAmount({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-950">{formatMoney(value)}</p>
    </div>
  );
}

type FilterFieldProps = {
  label: string;
  children: ReactNode;
};

function FilterField({ label, children }: FilterFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

function formatQuantity(value: string): string {
  return value.replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1");
}

function formatSaleDate(value: string): string {
  const [year, month, day] = value.split("-");
  return `${day}/${month}/${year}`;
}

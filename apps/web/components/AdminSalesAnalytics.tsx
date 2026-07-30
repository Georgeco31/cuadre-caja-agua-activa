"use client";

import type { FormEvent } from "react";

import {
  getAnalyticsViewState,
  getAnalyticsPreset,
  type AnalyticsPreset,
} from "@/lib/adminAnalytics";
import type {
  AdminDashboardAnalytics,
  AdminDashboardAnalyticsFilters,
} from "@/types/adminDashboardAnalytics";

type AdminSalesAnalyticsProps = {
  data: AdminDashboardAnalytics | null;
  error?: string;
  filters: AdminDashboardAnalyticsFilters;
  isLoading?: boolean;
  onFiltersChange: (filters: AdminDashboardAnalyticsFilters) => void;
  onLoad: (filters: AdminDashboardAnalyticsFilters) => void;
};

export function AdminSalesAnalytics({
  data,
  error = "",
  filters,
  isLoading = false,
  onFiltersChange,
  onLoad,
}: AdminSalesAnalyticsProps) {
  const viewState = getAnalyticsViewState({
    error,
    hasData: data !== null,
    isLoading,
  });
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onLoad(filters);
  }

  function applyPreset(preset: AnalyticsPreset) {
    const nextFilters = getAnalyticsPreset(preset);
    onFiltersChange(nextFilters);
    onLoad(nextFilters);
  }

  return (
    <section
      aria-labelledby="admin-analytics-title"
      className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card"
    >
      <div className="border-b border-slate-200 bg-gradient-to-br from-water-50 to-white p-5 sm:p-6">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
              Lectura gerencial · solo administrador
            </p>
            <h2
              className="mt-1.5 text-2xl font-semibold tracking-tight text-slate-950"
              id="admin-analytics-title"
            >
              Cómo vamos este mes
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Ventas registradas, cobros y gastos se muestran por separado para
              no confundirlos con el efectivo contado en caja.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <PresetButton label="Hoy" onClick={() => applyPreset("today")} />
            <PresetButton
              label="Últimos 7 días"
              onClick={() => applyPreset("last7")}
            />
            <PresetButton
              label="Mes actual"
              onClick={() => applyPreset("month")}
            />
          </div>
        </div>
        <form
          className="mt-5 grid gap-3 sm:grid-cols-[minmax(150px,220px)_minmax(150px,220px)_auto] sm:items-end"
          onSubmit={handleSubmit}
        >
          <DateInput
            label="Desde"
            onChange={(value) =>
              onFiltersChange({ ...filters, start_date: value })
            }
            value={filters.start_date ?? ""}
          />
          <DateInput
            label="Hasta"
            onChange={(value) =>
              onFiltersChange({ ...filters, end_date: value })
            }
            value={filters.end_date ?? ""}
          />
          <button
            className="h-11 rounded-xl bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={isLoading}
            type="submit"
          >
            {isLoading ? "Actualizando..." : "Aplicar rango"}
          </button>
        </form>
      </div>

      <div className="p-5 sm:p-6">
        {viewState === "loading" ? (
          <p className="rounded-2xl border border-water-100 bg-water-50 px-4 py-8 text-center text-sm text-water-900">
            Calculando métricas del negocio...
          </p>
        ) : viewState === "error" ? (
          <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">
            {error}
          </p>
        ) : viewState === "ready" && data ? (
          <AnalyticsContent data={data} />
        ) : (
          <p className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-600">
            No hay métricas disponibles para mostrar.
          </p>
        )}
      </div>
    </section>
  );
}

function AnalyticsContent({ data }: { data: AdminDashboardAnalytics }) {
  const maxDailySales = Math.max(
    ...data.daily_sales.map((item) => Number(item.total_sales_amount)),
    0,
  );
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold text-slate-700">
          {formatDate(data.period_start)} al {formatDate(data.period_end)}
        </p>
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          Ventas anuladas excluidas
        </span>
      </div>

      <div className="grid gap-3 min-[360px]:grid-cols-2 lg:grid-cols-4">
        <Metric label="Total vendido" value={formatMoney(data.total_sales_amount)} />
        <Metric label="Ventas contado" value={formatMoney(data.cash_sales_amount)} />
        <Metric label="Ventas crédito" value={formatMoney(data.credit_sales_amount)} />
        <Metric
          label="Cobros de crédito recibidos"
          value={formatMoney(data.collections_amount)}
        />
        <Metric
          tone="warning"
          label="Saldo de crédito pendiente"
          value={formatMoney(data.pending_credit_amount)}
        />
        <Metric
          label="Gastos operativos registrados"
          value={formatMoney(data.expenses_amount)}
        />
        <Metric
          label="Promedio diario vendido"
          value={formatMoney(data.average_daily_sales)}
        />
        <Metric
          label="Clientes atendidos"
          value={String(data.customers_served_count)}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(280px,0.7fr)]">
        <div className="rounded-2xl border border-slate-200 p-4 sm:p-5">
          <h3 className="font-semibold text-slate-950">Tendencia diaria de ventas</h3>
          {data.daily_sales.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">
              Sin ventas activas en el período.
            </p>
          ) : (
            <div className="mt-5 space-y-4">
              {data.daily_sales.map((item) => {
                const width =
                  maxDailySales > 0
                    ? Math.max(
                        (Number(item.total_sales_amount) / maxDailySales) * 100,
                        3,
                      )
                    : 0;
                return (
                  <div key={item.date}>
                    <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
                      <span className="font-medium text-slate-600">
                        {formatDate(item.date)}
                      </span>
                      <span className="font-semibold text-slate-950">
                        {formatMoney(item.total_sales_amount)}
                      </span>
                    </div>
                    <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                      <div
                        aria-label={`${formatDate(item.date)} ${formatMoney(item.total_sales_amount)}`}
                        className="h-full rounded-full bg-water-600"
                        style={{ width: `${width}%` }}
                      />
                    </div>
                    <p className="mt-1 text-[11px] text-slate-500">
                      Contado {formatMoney(item.cash_sales_amount)} · Crédito{" "}
                      {formatMoney(item.credit_sales_amount)}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="space-y-5">
          <div className="rounded-2xl border border-slate-200 p-4 sm:p-5">
            <p className="text-xs font-bold uppercase tracking-[0.15em] text-water-700">
              Día con más ventas
            </p>
            {data.best_sales_day ? (
              <>
                <p className="mt-2 text-xl font-bold text-slate-950">
                  {formatDate(data.best_sales_day.date)}
                </p>
                <p className="mt-1 text-2xl font-black text-water-700">
                  {formatMoney(data.best_sales_day.amount)}
                </p>
              </>
            ) : (
              <p className="mt-3 text-sm text-slate-500">Sin ventas en el período.</p>
            )}
          </div>
          <div className="rounded-2xl border border-slate-200 p-4 sm:p-5">
            <h3 className="font-semibold text-slate-950">Contado vs. crédito</h3>
            <div className="mt-4 space-y-4">
              {data.sales_mix.map((item) => (
                <div key={item.sale_type}>
                  <div className="flex justify-between gap-3 text-xs">
                    <span className="font-medium text-slate-600">
                      {item.sale_type === "cash" ? "Contado" : "Crédito"}
                    </span>
                    <span className="font-semibold text-slate-950">
                      {item.percentage}% · {formatMoney(item.amount)}
                    </span>
                  </div>
                  <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={
                        item.sale_type === "cash"
                          ? "h-full rounded-full bg-emerald-500"
                          : "h-full rounded-full bg-amber-500"
                      }
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 p-4 sm:p-5">
        <h3 className="font-semibold text-slate-950">Top clientes por ventas</h3>
        {data.top_customers.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">
            No hay ventas asociadas a clientes en el período.
          </p>
        ) : (
          <ol className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {data.top_customers.map((customer, index) => (
              <li
                className="rounded-xl border border-slate-200 bg-slate-50 p-3"
                key={customer.customer_id}
              >
                <p className="text-xs font-bold text-water-700">#{index + 1}</p>
                <p className="mt-1 truncate font-semibold text-slate-950">
                  {customer.customer_name}
                </p>
                <p className="mt-2 text-lg font-bold text-slate-950">
                  {formatMoney(customer.total_amount)}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {customer.sales_count} venta(s)
                </p>
              </li>
            ))}
          </ol>
        )}
      </div>

      <p className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs leading-5 text-slate-600">
        {data.net_amount_note}
      </p>
    </div>
  );
}

function Metric({
  label,
  tone = "neutral",
  value,
}: {
  label: string;
  tone?: "neutral" | "warning";
  value: string;
}) {
  return (
    <div
      className={`rounded-2xl border p-4 ${
        tone === "warning"
          ? "border-amber-200 bg-amber-50"
          : "border-slate-200 bg-white"
      }`}
    >
      <p className="text-xs font-medium leading-5 text-slate-500">{label}</p>
      <p
        className={`mt-1 text-xl font-bold ${
          tone === "warning" ? "text-amber-800" : "text-slate-950"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function PresetButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      className="min-h-10 rounded-xl border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700"
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}

function DateInput({
  label,
  onChange,
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <label>
      <span className="text-xs font-semibold text-slate-700">{label}</span>
      <input
        className="mt-1 h-11 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
        onChange={(event) => onChange(event.target.value)}
        type="date"
        value={value}
      />
    </label>
  );
}

function formatMoney(value: string): string {
  const numberValue = Number(value);
  return Number.isFinite(numberValue)
    ? new Intl.NumberFormat("es-EC", {
        style: "currency",
        currency: "USD",
      }).format(numberValue)
    : "$0.00";
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return `${day}/${month}/${year}`;
}

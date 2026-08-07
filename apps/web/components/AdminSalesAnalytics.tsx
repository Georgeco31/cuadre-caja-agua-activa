"use client";

import type { FormEvent } from "react";

import {
  ADMIN_ANALYTICS_TEXT,
  getAnalyticsPreset,
  getAnalyticsViewState,
  getSalesComparison,
  type AnalyticsPreset,
} from "@/lib/adminAnalytics";
import type {
  AdminDashboardAnalytics,
  AdminDashboardAnalyticsFilters,
  AdminSimpleRouteRanking,
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
              Ventas oficiales y operación de rutas se presentan como dominios
              separados, con un total combinado únicamente informativo.
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
  const maxOfficialDailySales = Math.max(
    ...data.daily_sales.map((item) => Number(item.total_sales_amount)),
    0,
  );
  const maxRouteDailySales = Math.max(
    ...data.simple_route_daily_sales.map((item) => Number(item.amount)),
    0,
  );
  const salesComparison = getSalesComparison(
    data.official_sales_amount,
    data.simple_route_sales_amount,
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold text-slate-700">
          {formatDate(data.period_start)} al {formatDate(data.period_end)}
        </p>
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          Ventas anuladas y rutas canceladas excluidas
        </span>
      </div>

      <OfficialSalesSection
        data={data}
        maxDailySales={maxOfficialDailySales}
      />
      <SimpleRoutesSection data={data} maxDailySales={maxRouteDailySales} />

      <section className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 sm:p-5">
        <p className="text-xs font-bold uppercase tracking-[0.15em] text-emerald-700">
          Sección 3
        </p>
        <h3 className="mt-1 text-xl font-bold text-slate-950">
          {ADMIN_ANALYTICS_TEXT.totalWithRoutes}
        </h3>
        <p className="mt-3 text-3xl font-black tracking-tight text-emerald-800">
          {formatMoney(data.total_sales_with_routes_amount)}
        </p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Suma informativa de ventas oficiales y ventas de ruta. Cada dominio
          conserva sus propios cobros, saldos y movimientos.
        </p>
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {salesComparison.map((item) => (
            <div
              className="rounded-xl border border-emerald-200 bg-white p-4"
              key={item.key}
            >
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-semibold text-slate-700">
                  {item.label}
                </span>
                <span className="font-bold text-slate-950">
                  {formatMoney(String(item.amount))}
                </span>
              </div>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-100">
                <div
                  className={`h-full rounded-full ${
                    item.key === "official" ? "bg-water-600" : "bg-sky-500"
                  }`}
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
              <p className="mt-1.5 text-right text-xs font-medium text-slate-500">
                {item.percentage.toFixed(1)}% del total combinado
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function OfficialSalesSection({
  data,
  maxDailySales,
}: {
  data: AdminDashboardAnalytics;
  maxDailySales: number;
}) {
  return (
    <section className="space-y-5 rounded-2xl border border-slate-200 bg-slate-50/60 p-4 sm:p-5">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.15em] text-water-700">
          Sección 1
        </p>
        <h3 className="mt-1 text-xl font-bold text-slate-950">
          {ADMIN_ANALYTICS_TEXT.officialSales}
        </h3>
        <p className="mt-1 text-sm leading-6 text-slate-600">
          Ventas contado y crédito del sistema oficial. No incluyen ventas,
          fiados ni abonos de Rutas Simples.
        </p>
      </div>

      <div className="grid gap-3 min-[360px]:grid-cols-2 lg:grid-cols-4">
        <Metric
          label={ADMIN_ANALYTICS_TEXT.officialSales}
          value={formatMoney(data.official_sales_amount)}
        />
        <Metric
          label={ADMIN_ANALYTICS_TEXT.officialCashSales}
          value={formatMoney(data.official_cash_sales_amount)}
        />
        <Metric
          label={ADMIN_ANALYTICS_TEXT.officialCreditSales}
          value={formatMoney(data.official_credit_sales_amount)}
        />
        <Metric
          label={ADMIN_ANALYTICS_TEXT.officialCollections}
          value={formatMoney(data.official_credit_collections_amount)}
        />
        <Metric
          label={ADMIN_ANALYTICS_TEXT.officialPending}
          tone="warning"
          value={formatMoney(data.official_credit_pending_amount)}
        />
        <Metric
          label="Gastos operativos oficiales"
          value={formatMoney(data.expenses_amount)}
        />
        <Metric
          label="Promedio diario de ventas oficiales"
          value={formatMoney(data.average_daily_sales)}
        />
        <Metric
          label="Clientes atendidos en ventas oficiales"
          value={String(data.customers_served_count)}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(280px,0.7fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
          <h4 className="font-semibold text-slate-950">
            Tendencia diaria de ventas oficiales
          </h4>
          {data.daily_sales.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">
              Sin ventas oficiales activas en el período.
            </p>
          ) : (
            <div className="mt-5 space-y-4">
              {data.daily_sales.map((item) => {
                const width = getBarWidth(
                  Number(item.total_sales_amount),
                  maxDailySales,
                );
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
                      Contado oficial {formatMoney(item.cash_sales_amount)} ·
                      Crédito oficial {formatMoney(item.credit_sales_amount)}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="space-y-5">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
            <p className="text-xs font-bold uppercase tracking-[0.15em] text-water-700">
              Día con más ventas oficiales
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
              <p className="mt-3 text-sm text-slate-500">
                Sin ventas oficiales en el período.
              </p>
            )}
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
            <h4 className="font-semibold text-slate-950">
              Contado vs. crédito oficiales
            </h4>
            <div className="mt-4 space-y-4">
              {data.sales_mix.map((item) => (
                <div key={item.sale_type}>
                  <div className="flex justify-between gap-3 text-xs">
                    <span className="font-medium text-slate-600">
                      {item.sale_type === "cash"
                        ? "Contado oficial"
                        : "Crédito oficial"}
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

      <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
        <h4 className="font-semibold text-slate-950">
          Top clientes por ventas oficiales
        </h4>
        {data.top_customers.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">
            No hay ventas oficiales asociadas a clientes en el período.
          </p>
        ) : (
          <ol className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {data.top_customers.map((customer, index) => (
              <li
                className="rounded-xl border border-slate-200 bg-slate-50 p-3"
                key={customer.customer_id}
              >
                <p className="text-xs font-bold text-water-700">
                  #{index + 1}
                </p>
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

      <p className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs leading-5 text-slate-600">
        {data.net_amount_note}
      </p>
    </section>
  );
}

function SimpleRoutesSection({
  data,
  maxDailySales,
}: {
  data: AdminDashboardAnalytics;
  maxDailySales: number;
}) {
  return (
    <section className="space-y-5 rounded-2xl border border-sky-200 bg-sky-50/60 p-4 sm:p-5">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.15em] text-sky-700">
          Sección 2
        </p>
        <h3 className="mt-1 text-xl font-bold text-slate-950">
          {ADMIN_ANALYTICS_TEXT.routeSection}
        </h3>
        <p className="mt-2 rounded-xl border border-sky-200 bg-white px-4 py-3 text-sm font-medium leading-6 text-sky-950">
          {ADMIN_ANALYTICS_TEXT.separationNote}
        </p>
      </div>

      <div className="grid gap-3 min-[360px]:grid-cols-2 lg:grid-cols-4">
        <Metric
          label={ADMIN_ANALYTICS_TEXT.routeSales}
          value={formatMoney(data.simple_route_sales_amount)}
        />
        <Metric
          label="Ventas de ruta contado"
          value={formatMoney(data.simple_route_cash_sales_amount)}
        />
        <Metric
          label="Ventas de ruta parciales"
          value={formatMoney(data.simple_route_partial_sales_amount)}
        />
        <Metric
          label="Cobrado al vender en ruta"
          value={formatMoney(data.simple_route_paid_amount)}
        />
        <Metric
          label={ADMIN_ANALYTICS_TEXT.routePending}
          tone="warning"
          value={formatMoney(data.simple_route_pending_amount)}
        />
        <Metric
          label={ADMIN_ANALYTICS_TEXT.routeCollections}
          value={formatMoney(data.simple_route_collections_amount)}
        />
        <Metric
          label="Gastos de ruta"
          value={formatMoney(data.simple_route_expenses_amount)}
        />
        <Metric
          label="Efectivo esperado de rutas"
          value={formatMoney(data.simple_route_expected_cash_amount)}
        />
        <Metric
          label="Efectivo entregado de rutas"
          value={formatMoney(data.simple_route_cash_delivered_amount)}
        />
        <Metric
          label="Diferencia de rutas"
          tone={
            Number(data.simple_route_cash_difference_amount) === 0
              ? "neutral"
              : "warning"
          }
          value={formatMoney(data.simple_route_cash_difference_amount)}
        />
        <Metric
          label="Hojas operativas"
          value={String(data.simple_route_sheets_count)}
        />
        <Metric
          label="Hojas con diferencia"
          tone={
            data.simple_route_sheets_with_difference === 0
              ? "neutral"
              : "warning"
          }
          value={String(data.simple_route_sheets_with_difference)}
        />
      </div>

      {data.simple_route_sheets_count === 0 ? (
        <p className="rounded-xl border border-sky-200 bg-white px-4 py-6 text-center text-sm text-slate-600">
          No hay Rutas Simples en el período. Sus métricas se muestran en cero
          y no alteran las ventas oficiales.
        </p>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(280px,0.7fr)]">
          <div className="rounded-2xl border border-sky-200 bg-white p-4 sm:p-5">
            <h4 className="font-semibold text-slate-950">
              Tendencia diaria de ventas de ruta
            </h4>
            <div className="mt-5 space-y-4">
              {data.simple_route_daily_sales.map((item) => {
                const width = getBarWidth(Number(item.amount), maxDailySales);
                return (
                  <div key={item.date}>
                    <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
                      <span className="font-medium text-slate-600">
                        {formatDate(item.date)}
                      </span>
                      <span className="font-semibold text-slate-950">
                        {formatMoney(item.amount)}
                      </span>
                    </div>
                    <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                      <div
                        aria-label={`${formatDate(item.date)} ${formatMoney(item.amount)}`}
                        className="h-full rounded-full bg-sky-500"
                        style={{ width: `${width}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="space-y-5">
            <div className="rounded-2xl border border-sky-200 bg-white p-4 sm:p-5">
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-sky-700">
                Día con más ventas de ruta
              </p>
              {data.simple_route_best_day ? (
                <>
                  <p className="mt-2 text-xl font-bold text-slate-950">
                    {formatDate(data.simple_route_best_day.date)}
                  </p>
                  <p className="mt-1 text-2xl font-black text-sky-700">
                    {formatMoney(data.simple_route_best_day.amount)}
                  </p>
                </>
              ) : (
                <p className="mt-3 text-sm text-slate-500">
                  Sin ventas de ruta en el período.
                </p>
              )}
            </div>
            <RankingList
              emptyText="Sin rutas o zonas para clasificar."
              items={data.simple_route_top_routes}
              title="Top rutas / zonas"
            />
            <RankingList
              emptyText="Sin vendedores para clasificar."
              items={data.simple_route_top_sellers}
              title="Top vendedores"
            />
          </div>
        </div>
      )}
    </section>
  );
}

function RankingList({
  emptyText,
  items,
  title,
}: {
  emptyText: string;
  items: AdminSimpleRouteRanking[];
  title: string;
}) {
  return (
    <div className="rounded-2xl border border-sky-200 bg-white p-4 sm:p-5">
      <h4 className="font-semibold text-slate-950">{title}</h4>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">{emptyText}</p>
      ) : (
        <ol className="mt-3 space-y-2">
          {items.slice(0, 5).map((item, index) => (
            <li
              className="flex items-center justify-between gap-3 text-sm"
              key={item.label}
            >
              <span className="min-w-0 truncate text-slate-600">
                {index + 1}. {item.label}
              </span>
              <span className="shrink-0 font-semibold text-slate-950">
                {formatMoney(item.amount)}
              </span>
            </li>
          ))}
        </ol>
      )}
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
      className={`min-w-0 rounded-2xl border p-4 ${
        tone === "warning"
          ? "border-amber-200 bg-amber-50"
          : "border-slate-200 bg-white"
      }`}
    >
      <p className="text-xs font-medium leading-5 text-slate-500">{label}</p>
      <p
        className={`mt-1 break-words text-xl font-bold ${
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

function getBarWidth(value: number, maximum: number): number {
  return maximum > 0 ? Math.max((value / maximum) * 100, 3) : 0;
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

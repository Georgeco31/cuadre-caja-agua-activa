"use client";

import Link from "next/link";
import { FormEvent, ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { ApiError, getManagementDashboard } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type {
  ManagementAlert,
  ManagementDashboard,
  ManagementDashboardFilters,
  ManagementExpenseCategory,
  ManagementLowStockItem,
  ManagementSupplierTotal,
} from "@/types/managementDashboard";

const moneyFormatter = new Intl.NumberFormat("es-EC", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
});

const quantityFormatter = new Intl.NumberFormat("es-EC", {
  maximumFractionDigits: 3,
});

export default function ManagementDashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [filters, setFilters] = useState<ManagementDashboardFilters>({});
  const [report, setReport] = useState<ManagementDashboard | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadReport(storedToken, {});
  }, [router]);

  async function loadReport(
    activeToken: string,
    activeFilters: ManagementDashboardFilters,
  ) {
    if (
      activeFilters.date_from &&
      activeFilters.date_to &&
      activeFilters.date_to < activeFilters.date_from
    ) {
      setError("La fecha hasta no puede ser menor que la fecha desde.");
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      setReport(await getManagementDashboard(activeToken, activeFilters));
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setReport(null);
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (token) {
      loadReport(token, filters);
    }
  }

  function handleCurrentMonth() {
    if (!token) {
      return;
    }
    const monthFilters = getCurrentMonthFilters();
    setFilters(monthFilters);
    loadReport(token, monthFilters);
  }

  function redirectIfUnauthorized(possibleError: unknown): boolean {
    if (
      possibleError instanceof ApiError &&
      (possibleError.status === 401 || possibleError.status === 403)
    ) {
      removeToken();
      router.replace("/login");
      return true;
    }
    return false;
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-7 px-4 py-6 sm:px-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <p className="mt-4 text-sm font-medium text-water-700">
              Agua Activa
            </p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-950">
              Panel gerencial
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Indicadores generales de Agua Activa por período. Este panel es
              solo lectura.
            </p>
          </div>
          <LogoutButton />
        </header>

        <ManagementFilters
          disabled={isLoading}
          filters={filters}
          onChange={setFilters}
          onCurrentMonth={handleCurrentMonth}
          onSubmit={handleSubmit}
        />

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando indicadores gerenciales..." />
        ) : report ? (
          <ManagementDashboardContent report={report} />
        ) : null}

        <p className="rounded-lg border border-water-100 bg-water-50 px-4 py-3 text-sm leading-6 text-water-900">
          Este panel no modifica información. Los valores son informativos y
          dependen de los registros ingresados en cada módulo.
        </p>
      </div>
    </main>
  );
}

type ManagementFiltersProps = {
  filters: ManagementDashboardFilters;
  disabled: boolean;
  onChange: (filters: ManagementDashboardFilters) => void;
  onCurrentMonth: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function ManagementFilters({
  filters,
  disabled,
  onChange,
  onCurrentMonth,
  onSubmit,
}: ManagementFiltersProps) {
  return (
    <form
      className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-2 lg:grid-cols-[minmax(180px,1fr)_minmax(180px,1fr)_auto_auto] lg:items-end"
      onSubmit={onSubmit}
    >
      <DateInput
        disabled={disabled}
        label="Fecha desde"
        onChange={(value) => onChange({ ...filters, date_from: value })}
        value={filters.date_from ?? ""}
      />
      <DateInput
        disabled={disabled}
        label="Fecha hasta"
        onChange={(value) => onChange({ ...filters, date_to: value })}
        value={filters.date_to ?? ""}
      />
      <button
        className="h-10 rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
        disabled={disabled}
        type="submit"
      >
        Consultar
      </button>
      <button
        className="h-10 rounded-md border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
        disabled={disabled}
        onClick={onCurrentMonth}
        type="button"
      >
        Mes actual
      </button>
    </form>
  );
}

function DateInput({
  disabled,
  label,
  onChange,
  value,
}: {
  disabled: boolean;
  label: string;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        type="date"
        value={value}
      />
    </label>
  );
}

function ManagementDashboardContent({
  report,
}: {
  report: ManagementDashboard;
}) {
  const hasPeriodActivity =
    report.cash.cash_sessions_count > 0 ||
    report.sales.active_sales_count > 0 ||
    report.operating_expenses.operating_expenses_total !== "0.00" ||
    report.purchases.active_purchases_count > 0 ||
    report.production.production_batches_count > 0 ||
    report.routes.route_loads_count > 0 ||
    report.payroll.payroll_runs_count > 0;

  const primaryCards = [
    {
      label: "Total ventas",
      value: formatMoney(report.sales.sales_total),
      note: `${report.sales.active_sales_count} venta(s) activa(s)`,
      tone: "water",
    },
    {
      label: "Cobros recibidos",
      value: formatMoney(report.receivables.payments_total),
      note: "Cobros activos del período",
      tone: "emerald",
    },
    {
      label: "Cartera pendiente",
      value: formatMoney(report.receivables.pending_balance_total),
      note: `${report.receivables.customers_with_balance_count} cliente(s) con saldo`,
      tone: "amber",
    },
    {
      label: "Caja final",
      value: formatMoney(report.cash.cash_final_total),
      note: `${report.cash.cash_sessions_count} cuadre(s)`,
      tone: "slate",
    },
    {
      label: "Gastos operativos",
      value: formatMoney(report.operating_expenses.operating_expenses_total),
      note: `${report.operating_expenses.voided_expenses_count} anulado(s) excluido(s)`,
      tone: "rose",
    },
    {
      label: "Compras",
      value: formatMoney(report.purchases.purchases_total),
      note: `${report.purchases.active_purchases_count} compra(s) activa(s)`,
      tone: "indigo",
    },
    {
      label: "Producción total",
      value: formatQuantity(
        report.production.production_items_total_quantity,
      ),
      note: `${report.production.production_batches_count} producción(es) activa(s)`,
      tone: "cyan",
    },
    {
      label: "Nómina neta calculada",
      value: formatMoney(report.payroll.net_pay_total),
      note: `${report.payroll.payroll_runs_count} rol(es) activo(s)`,
      tone: "violet",
    },
  ] as const;

  return (
    <div className="space-y-9">
      <div className="flex flex-col gap-1 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">
        <span>
          Período:{" "}
          <strong className="font-semibold text-slate-900">
            {formatDate(report.period.date_from)} —{" "}
            {formatDate(report.period.date_to)}
          </strong>
        </span>
        <span className="text-xs text-slate-500">
          Montos informativos en dólares
        </span>
      </div>

      {!hasPeriodActivity ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white px-5 py-8 text-center">
          <p className="font-semibold text-slate-900">
            No hay movimientos en el período seleccionado
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Los indicadores permanecen en cero. El inventario muestra su estado
            actual porque no es un dato histórico por fecha.
          </p>
        </div>
      ) : null}

      <section aria-labelledby="management-summary-title" className="space-y-4">
        <SectionHeading
          eyebrow="Resumen ejecutivo"
          id="management-summary-title"
          title="Indicadores principales"
        />
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {primaryCards.map((card) => (
            <PrimaryMetricCard key={card.label} {...card} />
          ))}
        </div>
      </section>

      <ManagementAlerts alerts={report.alerts} />
      <ManagementChartsSection report={report} />
      <ManagementDetails report={report} />
    </div>
  );
}

function PrimaryMetricCard({
  label,
  value,
  note,
  tone,
}: {
  label: string;
  value: string;
  note: string;
  tone:
    | "water"
    | "emerald"
    | "amber"
    | "slate"
    | "rose"
    | "indigo"
    | "cyan"
    | "violet";
}) {
  const toneClasses = {
    water: "border-water-100 bg-water-50 text-water-900",
    emerald: "border-emerald-100 bg-emerald-50 text-emerald-950",
    amber: "border-amber-100 bg-amber-50 text-amber-950",
    slate: "border-slate-200 bg-white text-slate-950",
    rose: "border-rose-100 bg-rose-50 text-rose-950",
    indigo: "border-indigo-100 bg-indigo-50 text-indigo-950",
    cyan: "border-cyan-100 bg-cyan-50 text-cyan-950",
    violet: "border-violet-100 bg-violet-50 text-violet-950",
  };
  return (
    <article
      className={`rounded-xl border p-4 shadow-sm ${toneClasses[tone]}`}
    >
      <p className="text-sm font-medium opacity-75">{label}</p>
      <p className="mt-2 break-words text-2xl font-semibold tracking-tight">
        {value}
      </p>
      <p className="mt-2 text-xs leading-5 opacity-70">{note}</p>
    </article>
  );
}

function ManagementAlerts({ alerts }: { alerts: ManagementAlert[] }) {
  return (
    <section aria-labelledby="management-alerts-title" className="space-y-4">
      <SectionHeading
        eyebrow="Atención"
        id="management-alerts-title"
        title="Alertas gerenciales"
      />
      {alerts.length ? (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {alerts.map((alert) => (
            <article
              className={
                alert.type === "warning"
                  ? "rounded-xl border border-amber-200 bg-amber-50 p-4"
                  : "rounded-xl border border-sky-200 bg-sky-50 p-4"
              }
              key={alert.title}
            >
              <div className="flex items-start justify-between gap-4">
                <h3
                  className={
                    alert.type === "warning"
                      ? "font-semibold text-amber-950"
                      : "font-semibold text-sky-950"
                  }
                >
                  {alert.title}
                </h3>
                <span
                  className={
                    alert.type === "warning"
                      ? "rounded-full bg-amber-200 px-2.5 py-1 text-xs font-bold text-amber-950"
                      : "rounded-full bg-sky-200 px-2.5 py-1 text-xs font-bold text-sky-950"
                  }
                >
                  {alert.count}
                </span>
              </div>
              <p
                className={
                  alert.type === "warning"
                    ? "mt-2 text-sm leading-6 text-amber-900"
                    : "mt-2 text-sm leading-6 text-sky-900"
                }
              >
                {alert.message}
              </p>
            </article>
          ))}
        </div>
      ) : (
        <p className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-5 text-sm text-emerald-900">
          No se detectaron alertas gerenciales para los datos consultados.
        </p>
      )}
    </section>
  );
}

function ManagementChartsSection({
  report,
}: {
  report: ManagementDashboard;
}) {
  return (
    <section aria-labelledby="management-charts-title" className="space-y-4">
      <SectionHeading
        eyebrow="Tendencias"
        id="management-charts-title"
        title="Gráficos del período"
      />
      <div className="grid gap-5 xl:grid-cols-2">
        <GroupedBarChart
          labels={[
            ["cash_sales_total", "Contado", "bg-water-700"],
            ["credit_sales_total", "Crédito", "bg-indigo-500"],
            ["payments_total", "Cobros", "bg-emerald-500"],
          ]}
          points={report.charts.daily_sales}
          title="Ventas y cobros por día"
        />
        <GroupedBarChart
          labels={[
            ["cash_total_counted", "Contado", "bg-water-700"],
            ["cash_final_total", "Caja final", "bg-sky-400"],
          ]}
          points={report.charts.daily_cash}
          title="Caja por día"
        />
        <GroupedBarChart
          labels={[
            [
              "operating_expenses_total",
              "Gastos operativos",
              "bg-rose-500",
            ],
            ["cash_expenses_total", "Gastos de caja", "bg-amber-500"],
          ]}
          points={report.charts.daily_expenses}
          title="Gastos por día"
        />
        <HorizontalBarChart
          items={report.charts.production_by_product.map((item) => ({
            id: item.product_id,
            label: item.product_name,
            value: item.quantity_produced,
          }))}
          title="Producción por producto"
          valueFormatter={formatQuantity}
        />
        <div className="xl:col-span-2">
          <HorizontalBarChart
            items={report.charts.purchases_by_supplier.map((item) => ({
              id: item.supplier_id,
              label: item.supplier_name,
              value: item.total_amount,
            }))}
            title="Compras por proveedor"
            valueFormatter={formatMoney}
          />
        </div>
      </div>
    </section>
  );
}

type ChartPoint = { date: string } & Record<string, string>;

function GroupedBarChart({
  labels,
  points,
  title,
}: {
  labels: readonly (readonly [string, string, string])[];
  points: ChartPoint[];
  title: string;
}) {
  const values = points.flatMap((point) =>
    labels.map(([key]) => toChartNumber(point[key])),
  );
  const maximum = Math.max(...values, 0);
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="font-semibold text-slate-950">{title}</h3>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2">
        {labels.map(([, label, color]) => (
          <span
            className="inline-flex items-center gap-1.5 text-xs text-slate-600"
            key={label}
          >
            <span className={`h-2.5 w-2.5 rounded-sm ${color}`} />
            {label}
          </span>
        ))}
      </div>
      {points.length ? (
        <div className="mt-5 max-h-80 space-y-4 overflow-y-auto pr-1">
          {points.map((point) => (
            <div className="grid grid-cols-[78px_1fr] gap-3" key={point.date}>
              <span className="pt-1 text-xs font-medium text-slate-600">
                {formatShortDate(point.date)}
              </span>
              <div className="space-y-1.5">
                {labels.map(([key, label, color]) => {
                  const value = point[key] ?? "0.00";
                  return (
                    <div className="group relative" key={key}>
                      <div className="h-5 overflow-hidden rounded bg-slate-100">
                        <div
                          aria-label={`${label}: ${formatMoney(value)}`}
                          className={`h-full min-w-px rounded ${color}`}
                          role="img"
                          style={{
                            width: `${getBarPercentage(value, maximum)}%`,
                          }}
                          title={`${label}: ${formatMoney(value)}`}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <ChartEmptyState />
      )}
    </article>
  );
}

function HorizontalBarChart({
  items,
  title,
  valueFormatter,
}: {
  items: { id: number; label: string; value: string }[];
  title: string;
  valueFormatter: (value: string) => string;
}) {
  const maximum = Math.max(...items.map((item) => toChartNumber(item.value)), 0);
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="font-semibold text-slate-950">{title}</h3>
      {items.length ? (
        <div className="mt-5 space-y-4">
          {items.map((item) => (
            <div key={item.id}>
              <div className="mb-1.5 flex items-baseline justify-between gap-4 text-sm">
                <span className="truncate font-medium text-slate-700">
                  {item.label}
                </span>
                <span className="whitespace-nowrap text-xs font-semibold text-slate-900">
                  {valueFormatter(item.value)}
                </span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <div
                  aria-label={`${item.label}: ${valueFormatter(item.value)}`}
                  className="h-full min-w-px rounded-full bg-water-700"
                  role="img"
                  style={{
                    width: `${getBarPercentage(item.value, maximum)}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <ChartEmptyState />
      )}
    </article>
  );
}

function ChartEmptyState() {
  return (
    <p className="mt-5 rounded-lg bg-slate-50 px-4 py-7 text-center text-sm text-slate-500">
      No hay datos para mostrar en este gráfico.
    </p>
  );
}

function ManagementDetails({ report }: { report: ManagementDashboard }) {
  return (
    <section aria-labelledby="management-details-title" className="space-y-4">
      <SectionHeading
        eyebrow="Detalle"
        id="management-details-title"
        title="Indicadores por módulo"
      />
      <div className="grid gap-5 xl:grid-cols-2">
        <DetailPanel title="Caja">
          <DetailGrid>
            <DetailMetric
              label="Total contado"
              value={formatMoney(report.cash.cash_total_counted)}
            />
            <DetailMetric
              label="Gastos después del conteo"
              value={formatMoney(
                report.cash.cash_total_expenses_after_count,
              )}
            />
            <DetailMetric
              label="Cuadres abiertos"
              value={String(report.cash.open_cash_sessions_count)}
            />
            <DetailMetric
              label="Cuadres cerrados"
              value={String(report.cash.closed_cash_sessions_count)}
            />
          </DetailGrid>
        </DetailPanel>

        <DetailPanel title="Ventas y cartera">
          <DetailGrid>
            <DetailMetric
              label="Ventas de contado"
              value={formatMoney(report.sales.cash_sales_total)}
            />
            <DetailMetric
              label="Ventas a crédito"
              value={formatMoney(report.sales.credit_sales_total)}
            />
            <DetailMetric
              label="Venta promedio"
              value={formatMoney(report.sales.average_sale_amount)}
            />
            <DetailMetric
              label="Cartera vencida"
              value={formatMoney(report.receivables.overdue_balance_total)}
            />
          </DetailGrid>
        </DetailPanel>

        <DetailPanel title="Gastos y compras">
          <DetailGrid>
            <DetailMetric
              label="Gastos pagados"
              value={formatMoney(
                report.operating_expenses.paid_expenses_total,
              )}
            />
            <DetailMetric
              label="Gastos pendientes"
              value={formatMoney(
                report.operating_expenses.unpaid_expenses_total,
              )}
            />
            <DetailMetric
              label="Compras pagadas"
              value={formatMoney(report.purchases.paid_purchases_total)}
            />
            <DetailMetric
              label="Compras pendientes"
              value={formatMoney(report.purchases.unpaid_purchases_total)}
            />
          </DetailGrid>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <RankingList
              emptyMessage="Sin categorías en el período."
              items={report.operating_expenses.top_categories}
              title="Principales categorías"
            />
            <RankingList
              emptyMessage="Sin proveedores en el período."
              items={report.purchases.top_suppliers}
              title="Principales proveedores"
            />
          </div>
        </DetailPanel>

        <DetailPanel title="Producción e inventario">
          <DetailGrid>
            <DetailMetric
              label="Merma registrada"
              value={formatQuantity(
                report.production.production_waste_total_quantity,
              )}
            />
            <DetailMetric
              label="Aplicaciones a inventario"
              value={String(
                report.production.production_applied_to_inventory_count,
              )}
            />
            <DetailMetric
              label="Costo de insumos"
              value={formatMoney(
                report.production.material_consumptions_total_cost,
              )}
            />
            <DetailMetric
              label="Stock total actual"
              value={formatQuantity(report.inventory.total_stock_quantity)}
            />
          </DetailGrid>
          <LowStockList items={report.inventory.low_stock_items} />
        </DetailPanel>

        <DetailPanel title="Rutas y cierres">
          <DetailGrid>
            <DetailMetric
              label="Cargas activas"
              value={String(report.routes.route_loads_count)}
            />
            <DetailMetric
              label="Retornos activos"
              value={String(report.routes.route_returns_count)}
            />
            <DetailMetric
              label="Efectivo esperado"
              value={formatMoney(report.routes.route_expected_cash_total)}
            />
            <DetailMetric
              label="Efectivo entregado"
              value={formatMoney(report.routes.route_delivered_cash_total)}
            />
            <DetailMetric
              label="Diferencia"
              value={formatMoney(report.routes.route_difference_total)}
            />
            <DetailMetric
              label="Registrado en caja"
              value={formatMoney(report.routes.route_cash_receipts_total)}
            />
          </DetailGrid>
        </DetailPanel>

        <DetailPanel title="Nómina calculada">
          <DetailGrid>
            <DetailMetric
              label="Roles activos"
              value={String(report.payroll.payroll_runs_count)}
            />
            <DetailMetric
              label="Total bruto"
              value={formatMoney(report.payroll.gross_pay_total)}
            />
            <DetailMetric
              label="Deducciones"
              value={formatMoney(report.payroll.deductions_total)}
            />
            <DetailMetric
              label="Roles anulados"
              value={String(report.payroll.voided_payroll_runs_count)}
            />
          </DetailGrid>
        </DetailPanel>
      </div>
    </section>
  );
}

function DetailPanel({
  children,
  title,
}: {
  children: ReactNode;
  title: string;
}) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-950">{title}</h3>
      <div className="mt-4">{children}</div>
    </article>
  );
}

function DetailGrid({ children }: { children: ReactNode }) {
  return <dl className="grid grid-cols-2 gap-4">{children}</dl>;
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs leading-5 text-slate-500">{label}</dt>
      <dd className="mt-1 break-words font-semibold text-slate-900">{value}</dd>
    </div>
  );
}

function RankingList({
  emptyMessage,
  items,
  title,
}: {
  emptyMessage: string;
  items: (ManagementExpenseCategory | ManagementSupplierTotal)[];
  title: string;
}) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
      {items.length ? (
        <ol className="mt-2 divide-y divide-slate-100 text-sm">
          {items.map((item) => {
            const id =
              "category_id" in item ? item.category_id : item.supplier_id;
            const name =
              "category_name" in item
                ? item.category_name
                : item.supplier_name;
            return (
              <li
                className="flex items-center justify-between gap-3 py-2"
                key={id}
              >
                <span className="truncate text-slate-600">{name}</span>
                <span className="whitespace-nowrap font-medium text-slate-900">
                  {formatMoney(item.total_amount)}
                </span>
              </li>
            );
          })}
        </ol>
      ) : (
        <p className="mt-2 text-xs leading-5 text-slate-500">{emptyMessage}</p>
      )}
    </div>
  );
}

function LowStockList({ items }: { items: ManagementLowStockItem[] }) {
  return (
    <div className="mt-5 border-t border-slate-100 pt-4">
      <div className="flex items-baseline justify-between gap-3">
        <h4 className="text-sm font-semibold text-slate-800">Stock bajo</h4>
        <span className="text-xs text-slate-500">Regla informativa: ≤ 5</span>
      </div>
      {items.length ? (
        <ul className="mt-2 divide-y divide-slate-100 text-sm">
          {items.slice(0, 8).map((item) => (
            <li
              className="flex items-center justify-between gap-3 py-2"
              key={item.product_id}
            >
              <span className="min-w-0 truncate text-slate-600">
                {item.product_name}
                {item.product_sku ? ` · ${item.product_sku}` : ""}
              </span>
              <span className="whitespace-nowrap font-semibold text-amber-700">
                {formatQuantity(item.total_stock_quantity)}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-xs leading-5 text-emerald-700">
          No hay productos bajo el umbral informativo.
        </p>
      )}
    </div>
  );
}

function SectionHeading({
  eyebrow,
  id,
  title,
}: {
  eyebrow: string;
  id: string;
  title: string;
}) {
  return (
    <div>
      <p className="text-sm font-medium text-water-700">{eyebrow}</p>
      <h2 className="mt-1 text-xl font-semibold text-slate-950" id={id}>
        {title}
      </h2>
    </div>
  );
}

function getCurrentMonthFilters(): ManagementDashboardFilters {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const dateFrom = toLocalISODate(new Date(year, month, 1));
  const dateTo = toLocalISODate(new Date(year, month + 1, 0));
  return { date_from: dateFrom, date_to: dateTo };
}

function toLocalISODate(value: Date): string {
  const localDate = new Date(
    value.getTime() - value.getTimezoneOffset() * 60_000,
  );
  return localDate.toISOString().slice(0, 10);
}

function getBarPercentage(value: string, maximum: number): number {
  if (maximum <= 0) {
    return 0;
  }
  return Math.max(0, Math.min(100, (toChartNumber(value) / maximum) * 100));
}

function toChartNumber(value: string | undefined): number {
  const parsed = Number(value ?? "0");
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatMoney(value: string): string {
  return moneyFormatter.format(toChartNumber(value));
}

function formatQuantity(value: string): string {
  return quantityFormatter.format(toChartNumber(value));
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return year && month && day ? `${day}/${month}/${year}` : value;
}

function formatShortDate(value: string): string {
  const [, month, day] = value.split("-");
  return month && day ? `${day}/${month}` : value;
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo cargar el panel gerencial.";
}

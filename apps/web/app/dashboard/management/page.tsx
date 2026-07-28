"use client";

import Link from "next/link";
import { FormEvent, ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { DashboardShell } from "@/components/ui/DashboardShell";
import { MetricGrid } from "@/components/ui/MetricGrid";
import { PageHeader } from "@/components/ui/PageHeader";
import { ReportSection } from "@/components/ui/ReportSection";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  ApiError,
  downloadFile,
  getCurrentUser,
  getManagementDashboard,
} from "@/lib/api";
import { getToken, removeToken, saveUser } from "@/lib/auth";
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
  const [exportingFormat, setExportingFormat] = useState<
    "xlsx" | "pdf" | null
  >(null);
  const [forbidden, setForbidden] = useState(false);
  const [accountName, setAccountName] = useState("Agua Activa");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    void authorizePage(storedToken);
  }, [router]);

  async function authorizePage(activeToken: string) {
    try {
      const currentUser = await getCurrentUser(activeToken);
      saveUser(currentUser);
      setAccountName(currentUser.username);
      if (currentUser.role !== "admin_auditor") {
        setForbidden(true);
        setIsLoading(false);
        return;
      }
      setToken(activeToken);
      await loadReport(activeToken, {});
    } catch (loadError) {
      if (!redirectIfUnauthorized(loadError)) {
        setError(getErrorMessage(loadError));
        setIsLoading(false);
      }
    }
  }

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

  async function handleExport(format: "xlsx" | "pdf") {
    if (!token) {
      return;
    }
    if (
      filters.date_from &&
      filters.date_to &&
      filters.date_to < filters.date_from
    ) {
      setError("La fecha hasta no puede ser menor que la fecha desde.");
      return;
    }

    const searchParams = new URLSearchParams();
    if (filters.date_from) {
      searchParams.set("date_from", filters.date_from);
    }
    if (filters.date_to) {
      searchParams.set("date_to", filters.date_to);
    }

    setExportingFormat(format);
    setError("");
    try {
      const query = searchParams.toString();
      await downloadFile(
        token,
        `/reports/exports/management-dashboard.${format}${
          query ? `?${query}` : ""
        }`,
        `panel-gerencial.${format}`,
      );
    } catch (exportError) {
      if (redirectIfUnauthorized(exportError)) {
        return;
      }
      setError(getErrorMessage(exportError));
    } finally {
      setExportingFormat(null);
    }
  }

  function redirectIfUnauthorized(possibleError: unknown): boolean {
    if (
      possibleError instanceof ApiError &&
      possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return true;
    }
    return false;
  }

  return (
    <DashboardShell
      activeHref="/dashboard/reports"
      dateLabel={formatTopbarDate(new Date())}
      roleLabel={forbidden ? "Operador" : "Administrador / auditor"}
      userName={accountName}
    >
      <div className="mx-auto flex w-full min-w-0 max-w-screen-2xl flex-col gap-7 px-4 py-7 sm:px-6 sm:py-9 xl:gap-9 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description="Indicadores, alertas y tendencias generales de Agua Activa por período. Este panel es solo lectura."
          eyebrow="Reportes y control"
          meta={
            <div className="flex flex-wrap items-center gap-3">
              <StatusBadge label="Acceso restringido" tone="info" />
              <Link
                className="inline-flex min-h-10 items-center text-sm font-semibold text-water-700 hover:text-water-600"
                href="/dashboard"
              >
                ← Volver al dashboard
              </Link>
            </div>
          }
          title="Panel gerencial"
        />

        {forbidden ? (
          <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
            <h2 className="text-lg font-semibold text-amber-950">
              No tienes permisos
            </h2>
            <p className="mt-2 text-sm text-amber-900">
              El panel gerencial está reservado al administrador/auditor.
            </p>
          </section>
        ) : null}

        {!forbidden ? (
          <>
            <ManagementFilters
              disabled={isLoading || exportingFormat !== null}
              exportingFormat={exportingFormat}
              filters={filters}
              onChange={setFilters}
              onCurrentMonth={handleCurrentMonth}
              onExport={handleExport}
              onSubmit={handleSubmit}
            />

            {error ? <ErrorMessage message={error} /> : null}

            {isLoading ? (
              <LoadingState label="Cargando indicadores gerenciales..." />
            ) : report ? (
              <ManagementDashboardContent report={report} />
            ) : null}

            <p className="rounded-2xl border border-water-100 bg-water-50 px-5 py-4 text-sm leading-6 text-water-900">
              Este panel no modifica información. Los valores son informativos
              y dependen de los registros ingresados en cada módulo.
            </p>
          </>
        ) : null}
      </div>
    </DashboardShell>
  );
}

type ManagementFiltersProps = {
  filters: ManagementDashboardFilters;
  disabled: boolean;
  exportingFormat: "xlsx" | "pdf" | null;
  onChange: (filters: ManagementDashboardFilters) => void;
  onCurrentMonth: () => void;
  onExport: (format: "xlsx" | "pdf") => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function ManagementFilters({
  filters,
  disabled,
  exportingFormat,
  onChange,
  onCurrentMonth,
  onExport,
  onSubmit,
}: ManagementFiltersProps) {
  return (
    <form
      className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:p-5"
      onSubmit={onSubmit}
    >
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
          Período y exportación
        </p>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">
          Ajusta el rango del panel
        </h2>
      </div>
      <div className="mt-4 grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(180px,1fr)_minmax(180px,1fr)_auto_auto_auto_auto] xl:items-end">
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
          className="min-h-11 rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          disabled={disabled}
          type="submit"
        >
          Consultar
        </button>
        <button
          className="min-h-11 rounded-xl border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
          disabled={disabled}
          onClick={onCurrentMonth}
          type="button"
        >
          Mes actual
        </button>
        <button
          className="min-h-11 rounded-xl border border-water-200 bg-water-50 px-5 text-sm font-semibold text-water-800 transition hover:border-water-500 hover:bg-water-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-100 disabled:text-slate-400"
          disabled={disabled}
          onClick={() => onExport("xlsx")}
          type="button"
        >
          {exportingFormat === "xlsx" ? "Exportando..." : "Exportar Excel"}
        </button>
        <button
          className="min-h-11 rounded-xl border border-slate-300 bg-slate-50 px-5 text-sm font-semibold text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
          disabled={disabled}
          onClick={() => onExport("pdf")}
          type="button"
        >
          {exportingFormat === "pdf" ? "Exportando..." : "Exportar PDF"}
        </button>
      </div>
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
    <label className="block min-w-0">
      <span className="text-sm font-semibold text-slate-800">{label}</span>
      <input
        className="mt-2 h-11 w-full min-w-0 rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
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
      tone: "neutral",
    },
    {
      label: "Cartera pendiente",
      value: formatMoney(report.receivables.pending_balance_total),
      note: `${report.receivables.customers_with_balance_count} cliente(s) con saldo`,
      tone: "warning",
    },
    {
      label: "Caja final",
      value: formatMoney(report.cash.cash_final_total),
      note: `${report.cash.cash_sessions_count} cuadre(s)`,
      tone: "neutral",
    },
    {
      label: "Gastos operativos",
      value: formatMoney(report.operating_expenses.operating_expenses_total),
      note: `${report.operating_expenses.voided_expenses_count} anulado(s) excluido(s)`,
      tone: "neutral",
    },
    {
      label: "Compras",
      value: formatMoney(report.purchases.purchases_total),
      note: `${report.purchases.active_purchases_count} compra(s) activa(s)`,
      tone: "neutral",
    },
    {
      label: "Producción total",
      value: formatQuantity(
        report.production.production_items_total_quantity,
      ),
      note: `${report.production.production_batches_count} producción(es) activa(s)`,
      tone: "neutral",
    },
    {
      label: "Nómina neta calculada",
      value: formatMoney(report.payroll.net_pay_total),
      note: `${report.payroll.payroll_runs_count} rol(es) activo(s)`,
      tone: "neutral",
    },
  ] as const;

  return (
    <div className="min-w-0 space-y-9">
      <div className="flex flex-col gap-2 rounded-2xl border border-water-100 bg-water-50 px-4 py-3 text-sm text-water-900 sm:flex-row sm:items-center sm:justify-between sm:px-5">
        <span>
          Período:{" "}
          <strong className="font-semibold">
            {formatDate(report.period.date_from)} —{" "}
            {formatDate(report.period.date_to)}
          </strong>
        </span>
        <span className="text-xs font-medium text-water-700">
          Montos informativos en dólares
        </span>
      </div>

      {!hasPeriodActivity ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-9 text-center">
          <p className="font-semibold text-slate-900">
            No hay movimientos en el período seleccionado
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Los indicadores permanecen en cero. El inventario muestra su estado
            actual porque no es un dato histórico por fecha.
          </p>
        </div>
      ) : null}

      <ReportSection
        description="Valores consolidados de las áreas incluidas en el panel."
        eyebrow="Resumen ejecutivo"
        id="management-summary-title"
        title="Indicadores principales"
      >
        <MetricGrid>
          {primaryCards.map((card) => (
            <StatCard
              hint={card.note}
              key={card.label}
              label={card.label}
              tone={card.tone}
              value={card.value}
            />
          ))}
        </MetricGrid>
      </ReportSection>

      <ManagementAlerts alerts={report.alerts} />
      <ManagementChartsSection report={report} />
      <ManagementDetails report={report} />
    </div>
  );
}

function ManagementAlerts({ alerts }: { alerts: ManagementAlert[] }) {
  return (
    <ReportSection
      description="Indicadores reales que requieren seguimiento en los datos consultados."
      eyebrow="Atención"
      id="management-alerts-title"
      title="Alertas gerenciales"
    >
      {alerts.length ? (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {alerts.map((alert) => (
            <article
              className={
                alert.type === "warning"
                  ? "rounded-2xl border border-amber-200 bg-amber-50 p-5"
                  : "rounded-2xl border border-water-100 bg-water-50 p-5"
              }
              key={alert.title}
            >
              <div className="flex items-start justify-between gap-4">
                <h3
                  className={
                    alert.type === "warning"
                      ? "font-semibold text-amber-950"
                      : "font-semibold text-water-900"
                  }
                >
                  {alert.title}
                </h3>
                <span
                  className={
                    alert.type === "warning"
                      ? "rounded-full bg-amber-200 px-2.5 py-1 text-xs font-bold text-amber-950"
                      : "rounded-full bg-water-100 px-2.5 py-1 text-xs font-bold text-water-900"
                  }
                >
                  {alert.count}
                </span>
              </div>
              <p
                className={
                  alert.type === "warning"
                    ? "mt-2 text-sm leading-6 text-amber-900"
                    : "mt-2 text-sm leading-6 text-water-800"
                }
              >
                {alert.message}
              </p>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-900">
          <p className="font-semibold">Sin alertas gerenciales</p>
          <p className="mt-1 leading-6 text-emerald-800">
            No se detectaron alertas para los datos consultados.
          </p>
        </div>
      )}
    </ReportSection>
  );
}

function ManagementChartsSection({
  report,
}: {
  report: ManagementDashboard;
}) {
  return (
    <ReportSection
      description="Series del período y distribuciones disponibles en el reporte gerencial."
      eyebrow="Tendencias"
      id="management-charts-title"
      title="Gráficos del período"
    >
      <div className="grid min-w-0 gap-5 xl:grid-cols-2">
        <GroupedBarChart
          labels={[
            ["cash_sales_total", "Contado", "bg-water-800"],
            ["credit_sales_total", "Crédito", "bg-water-500"],
            ["payments_total", "Cobros", "bg-slate-400"],
          ]}
          points={report.charts.daily_sales}
          title="Ventas y cobros por día"
        />
        <GroupedBarChart
          labels={[
            ["cash_total_counted", "Contado", "bg-water-800"],
            ["cash_final_total", "Caja final", "bg-water-500"],
          ]}
          points={report.charts.daily_cash}
          title="Caja por día"
        />
        <GroupedBarChart
          labels={[
            [
              "operating_expenses_total",
              "Gastos operativos",
              "bg-water-700",
            ],
            ["cash_expenses_total", "Gastos de caja", "bg-slate-400"],
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
        <div className="min-w-0 xl:col-span-2">
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
    </ReportSection>
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
    <article className="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:p-5">
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
    <article className="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:p-5">
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
    <ReportSection
      description="Desglose de los mismos datos consolidados, organizado por área del ERP."
      eyebrow="Detalle"
      id="management-details-title"
      title="Indicadores por módulo"
    >
      <div className="grid min-w-0 gap-5 xl:grid-cols-2">
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
    </ReportSection>
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
    <article className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
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
      <dd className="mt-1 break-words font-semibold tabular-nums text-slate-900">
        {value}
      </dd>
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

function formatTopbarDate(value: Date): string {
  return new Intl.DateTimeFormat("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(value);
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo cargar el panel gerencial.";
}

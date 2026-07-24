import type { ReactNode } from "react";

import {
  formatMoney,
  formatQuantity,
} from "@/components/DailySummaryCards";
import type { MonthlyOperationalSummary } from "@/types/monthlyOperationalSummary";

type MonthlySummaryCardsProps = {
  report: MonthlyOperationalSummary;
};

export function MonthlySummaryCards({ report }: MonthlySummaryCardsProps) {
  const cash = report.cash_summary;
  const production = report.production_summary;
  const sales = report.sales_summary;
  const receivables = report.receivables_summary;
  const routes = report.route_operations_summary;
  const closures = report.route_financial_summary;
  const receipts = report.route_cash_receipts_summary;

  return (
    <div className="space-y-8">
      <section
        aria-labelledby="monthly-reference-title"
        className="rounded-xl border border-water-100 bg-water-50 p-5 shadow-sm"
      >
        <p className="text-sm font-medium text-water-700">
          Referencia operativa del mes
        </p>
        <h2
          className="mt-1 text-sm font-medium text-water-900"
          id="monthly-reference-title"
        >
          Flujo de efectivo de referencia
        </h2>
        <p className="mt-2 text-3xl font-semibold text-water-900">
          {formatMoney(
            report.totals.total_business_cash_inflow_reference,
          )}
        </p>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-water-800">
          Suma ventas de contado, cobros y dinero de rutas registrado en caja.
          Es una referencia operativa y no reemplaza el cuadre oficial.
        </p>
      </section>

      <SummarySection eyebrow="Comercial" title="Ventas y cobros">
        <MetricCard
          label="Ventas de contado"
          note={`${sales.cash_sales_count} venta(s) activa(s)`}
          value={formatMoney(sales.cash_sales_total)}
        />
        <MetricCard
          label="Ventas a crédito"
          note={`${sales.credit_sales_count} venta(s) activa(s)`}
          value={formatMoney(sales.credit_sales_total)}
        />
        <MetricCard
          label="Total vendido"
          note={`${sales.voided_sales_count} venta(s) anulada(s)`}
          value={formatMoney(sales.total_sales_amount)}
        />
        <MetricCard
          label="Cobros recibidos"
          note={`${receivables.payments_count} cobro(s) activo(s)`}
          value={formatMoney(receivables.payments_total)}
        />
        <MetricCard
          label="Crédito pendiente"
          note={`${receivables.customers_with_credit_sales_count} cliente(s)`}
          value={formatMoney(receivables.pending_credit_total)}
        />
      </SummarySection>

      <SummarySection eyebrow="Caja" title="Cuadres del mes">
        <MetricCard
          label="Total contado"
          value={formatMoney(cash.total_counted)}
        />
        <MetricCard
          label="Gastos"
          value={formatMoney(cash.total_expenses)}
        />
        <MetricCard
          label="Total final"
          value={formatMoney(cash.total_final)}
        />
        <MetricCard
          label="Promedio diario contado"
          note="Sobre días con cuadre"
          value={formatMoney(cash.average_daily_counted)}
        />
        <MetricCard
          label="Días con cuadre"
          note={`${cash.days_without_cash_session} día(s) sin cuadre`}
          value={String(cash.days_with_cash_session)}
        />
        <MetricCard
          label="Cuadres registrados"
          note={`${cash.open_cash_sessions_count} abierto(s) · ${cash.closed_cash_sessions_count} cerrado(s)`}
          value={String(cash.cash_sessions_count)}
        />
      </SummarySection>

      <SummarySection eyebrow="Producción" title="Producción y merma">
        <MetricCard
          label="Neto producido"
          value={formatQuantity(production.total_quantity_net)}
        />
        <MetricCard
          label="Cantidad producida"
          value={formatQuantity(production.total_quantity_produced)}
        />
        <MetricCard
          label="Merma"
          value={formatQuantity(production.total_quantity_waste)}
        />
        <MetricCard
          label="Producciones activas"
          note={`${production.voided_production_batches_count} anulada(s)`}
          value={String(production.active_production_batches_count)}
        />
      </SummarySection>

      <SummarySection eyebrow="Rutas" title="Operación y efectivo de rutas">
        <MetricCard
          label="Cargas activas"
          note={`${routes.voided_route_loads_count} anulada(s)`}
          value={String(routes.active_route_loads_count)}
        />
        <MetricCard
          label="Cantidad cargada"
          value={formatQuantity(routes.total_quantity_loaded)}
        />
        <MetricCard
          label="Retornos activos"
          note={`${routes.voided_route_returns_count} anulado(s)`}
          value={String(routes.active_route_returns_count)}
        />
        <MetricCard
          label="Cantidad retornada"
          value={formatQuantity(routes.total_quantity_returned)}
        />
        <MetricCard
          label="Efectivo esperado"
          note={`${closures.active_route_closures_count} cierre(s) activo(s)`}
          value={formatMoney(closures.expected_cash_total)}
        />
        <MetricCard
          label="Efectivo entregado"
          value={formatMoney(closures.delivered_cash_total)}
        />
        <MetricCard
          label="Diferencia de cierres"
          note={`${closures.closures_with_shortage_count} faltante(s) · ${closures.closures_with_surplus_count} sobrante(s)`}
          value={formatMoney(closures.difference_total)}
        />
        <MetricCard
          label="Registrado en caja"
          note={`${receipts.active_receipts_count} registro(s) activo(s)`}
          value={formatMoney(receipts.received_amount_total)}
        />
        <MetricCard
          label="Diferencia de registros"
          value={formatMoney(receipts.difference_total)}
        />
      </SummarySection>
    </div>
  );
}

type SummarySectionProps = {
  eyebrow: string;
  title: string;
  children: ReactNode;
};

function SummarySection({
  eyebrow,
  title,
  children,
}: SummarySectionProps) {
  return (
    <section className="space-y-3">
      <div>
        <p className="text-sm font-medium text-water-700">{eyebrow}</p>
        <h2 className="mt-1 text-xl font-semibold text-slate-950">{title}</h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        {children}
      </div>
    </section>
  );
}

type MetricCardProps = {
  label: string;
  value: string;
  note?: string;
};

function MetricCard({ label, value, note }: MetricCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-600">{label}</p>
      <p className="mt-2 break-words text-lg font-semibold text-slate-950">
        {value}
      </p>
      {note ? (
        <p className="mt-1 text-xs leading-5 text-slate-500">{note}</p>
      ) : null}
    </div>
  );
}

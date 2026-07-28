import {
  formatMoney,
  formatQuantity,
} from "@/components/DailySummaryCards";
import { MetricGrid } from "@/components/ui/MetricGrid";
import { ReportSection } from "@/components/ui/ReportSection";
import { StatCard } from "@/components/ui/StatCard";
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
    <div className="min-w-0 space-y-8">
      <section
        aria-labelledby="monthly-reference-title"
        className="rounded-2xl border border-water-100 bg-water-50 p-5 shadow-card sm:p-6"
      >
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
          Referencia operativa del mes
        </p>
        <h2
          className="mt-2 text-sm font-semibold text-water-900"
          id="monthly-reference-title"
        >
          Flujo de efectivo de referencia
        </h2>
        <p className="mt-2 break-words text-3xl font-semibold tabular-nums tracking-tight text-water-900">
          {formatMoney(
            report.totals.total_business_cash_inflow_reference,
          )}
        </p>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-water-800">
          Suma ventas de contado, cobros y dinero de rutas registrado en caja.
          Es una referencia operativa y no reemplaza el cuadre oficial.
        </p>
      </section>

      <ReportSection
        eyebrow="Comercial"
        id="monthly-commercial-summary-title"
        title="Ventas y cobros"
      >
        <MetricGrid columns="five">
        <StatCard
          label="Ventas de contado"
          hint={`${sales.cash_sales_count} venta(s) activa(s)`}
          value={formatMoney(sales.cash_sales_total)}
        />
        <StatCard
          label="Ventas a crédito"
          hint={`${sales.credit_sales_count} venta(s) activa(s)`}
          value={formatMoney(sales.credit_sales_total)}
        />
        <StatCard
          label="Total vendido"
          hint={`${sales.voided_sales_count} venta(s) anulada(s)`}
          tone="water"
          value={formatMoney(sales.total_sales_amount)}
        />
        <StatCard
          label="Cobros recibidos"
          hint={`${receivables.payments_count} cobro(s) activo(s)`}
          value={formatMoney(receivables.payments_total)}
        />
        <StatCard
          label="Crédito pendiente"
          hint={`${receivables.customers_with_credit_sales_count} cliente(s)`}
          value={formatMoney(receivables.pending_credit_total)}
        />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        eyebrow="Caja"
        id="monthly-cash-summary-title"
        title="Cuadres del mes"
      >
        <MetricGrid>
        <StatCard
          label="Total contado"
          value={formatMoney(cash.total_counted)}
        />
        <StatCard
          label="Gastos"
          value={formatMoney(cash.total_expenses)}
        />
        <StatCard
          label="Total final"
          tone="water"
          value={formatMoney(cash.total_final)}
        />
        <StatCard
          label="Promedio diario contado"
          hint="Sobre días con cuadre"
          value={formatMoney(cash.average_daily_counted)}
        />
        <StatCard
          label="Días con cuadre"
          hint={`${cash.days_without_cash_session} día(s) sin cuadre`}
          value={String(cash.days_with_cash_session)}
        />
        <StatCard
          label="Cuadres registrados"
          hint={`${cash.open_cash_sessions_count} abierto(s) · ${cash.closed_cash_sessions_count} cerrado(s)`}
          value={String(cash.cash_sessions_count)}
        />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        eyebrow="Producción"
        id="monthly-production-summary-title"
        title="Producción y merma"
      >
        <MetricGrid>
        <StatCard
          label="Neto producido"
          tone="water"
          value={formatQuantity(production.total_quantity_net)}
        />
        <StatCard
          label="Cantidad producida"
          value={formatQuantity(production.total_quantity_produced)}
        />
        <StatCard
          label="Merma"
          value={formatQuantity(production.total_quantity_waste)}
        />
        <StatCard
          label="Producciones activas"
          hint={`${production.voided_production_batches_count} anulada(s)`}
          value={String(production.active_production_batches_count)}
        />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        eyebrow="Rutas"
        id="monthly-routes-summary-title"
        title="Operación y efectivo de rutas"
      >
        <MetricGrid>
        <StatCard
          label="Cargas activas"
          hint={`${routes.voided_route_loads_count} anulada(s)`}
          value={String(routes.active_route_loads_count)}
        />
        <StatCard
          label="Cantidad cargada"
          value={formatQuantity(routes.total_quantity_loaded)}
        />
        <StatCard
          label="Retornos activos"
          hint={`${routes.voided_route_returns_count} anulado(s)`}
          value={String(routes.active_route_returns_count)}
        />
        <StatCard
          label="Cantidad retornada"
          value={formatQuantity(routes.total_quantity_returned)}
        />
        <StatCard
          label="Efectivo esperado"
          hint={`${closures.active_route_closures_count} cierre(s) activo(s)`}
          value={formatMoney(closures.expected_cash_total)}
        />
        <StatCard
          label="Efectivo entregado"
          value={formatMoney(closures.delivered_cash_total)}
        />
        <StatCard
          label="Diferencia de cierres"
          hint={`${closures.closures_with_shortage_count} faltante(s) · ${closures.closures_with_surplus_count} sobrante(s)`}
          value={formatMoney(closures.difference_total)}
        />
        <StatCard
          label="Registrado en caja"
          hint={`${receipts.active_receipts_count} registro(s) activo(s)`}
          tone="water"
          value={formatMoney(receipts.received_amount_total)}
        />
        <StatCard
          label="Diferencia de registros"
          value={formatMoney(receipts.difference_total)}
        />
        </MetricGrid>
      </ReportSection>
    </div>
  );
}

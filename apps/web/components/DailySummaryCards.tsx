import { MetricGrid } from "@/components/ui/MetricGrid";
import { ReportSection } from "@/components/ui/ReportSection";
import { StatCard } from "@/components/ui/StatCard";
import type { DailyOperationalSummary } from "@/types/dailyOperationalSummary";

type DailySummaryCardsProps = {
  report: DailyOperationalSummary;
};

export function DailySummaryCards({ report }: DailySummaryCardsProps) {
  const { cash_summary: cash } = report;
  const { production_summary: production } = report;
  const { route_closures_summary: closures } = report;
  const { route_cash_receipts_summary: receipts } = report;
  const { route_loads_summary: loads } = report;
  const { route_returns_summary: returns } = report;
  const { sales_summary: sales } = report;
  const { receivables_summary: receivables } = report;

  return (
    <div className="min-w-0 space-y-8">
      <ReportSection
        description="Estado y resultado del cuadre registrado para la fecha."
        eyebrow="Caja"
        id="daily-cash-summary-title"
        title="Estado del cuadre"
      >
        <MetricGrid columns="five">
        <StatCard
          label="Estado del cuadre"
          value={formatCashStatus(
            cash.cash_session_exists,
            cash.cash_session_status,
          )}
        />
        <StatCard
          label="Total contado"
          value={formatMoney(cash.total_counted)}
        />
        <StatCard label="Gastos" value={formatMoney(cash.total_expenses)} />
        <StatCard
          label="Total final"
          tone="water"
          value={formatMoney(cash.total_final)}
        />
        <StatCard
          label="Dinero de rutas en caja"
          hint={`${cash.route_cash_receipts_count} registro(s) activo(s)`}
          value={formatMoney(cash.route_cash_receipts_total)}
        />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        eyebrow="Producción"
        id="daily-production-summary-title"
        title="Producción y merma"
      >
        <MetricGrid>
        <StatCard
          label="Producciones activas"
          hint={`${production.voided_production_batches_count} anulada(s)`}
          value={String(production.active_production_batches_count)}
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
          label="Neto producido"
          tone="water"
          value={formatQuantity(production.total_quantity_net)}
        />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        eyebrow="Rutas"
        id="daily-routes-summary-title"
        title="Movimiento y cierre de rutas"
      >
        <MetricGrid columns="four">
        <StatCard
          label="Cargas activas"
          value={String(loads.active_route_loads_count)}
        />
        <StatCard
          label="Retornos activos"
          value={String(returns.active_route_returns_count)}
        />
        <StatCard
          label="Cierres activos"
          value={String(closures.active_route_closures_count)}
        />
        <StatCard
          label="Efectivo esperado"
          value={formatMoney(closures.expected_cash_total)}
        />
        <StatCard
          label="Efectivo entregado"
          value={formatMoney(closures.delivered_cash_total)}
        />
        <StatCard
          label="Diferencia rutas"
          value={formatMoney(closures.difference_total)}
        />
        <StatCard
          label="Dinero registrado en caja"
          hint={`${receipts.active_receipts_count} registro(s) activo(s)`}
          tone="water"
          value={formatMoney(receipts.received_amount_total)}
        />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        eyebrow="Comercial"
        id="daily-commercial-summary-title"
        title="Ventas y cobros"
      >
        <MetricGrid>
        <StatCard
          label="Ventas contado"
          hint={`${sales.cash_sales_count} venta(s)`}
          value={formatMoney(sales.cash_sales_total)}
        />
        <StatCard
          label="Ventas crédito"
          hint={`${sales.credit_sales_count} venta(s)`}
          value={formatMoney(sales.credit_sales_total)}
        />
        <StatCard
          label="Cobros"
          hint={`${receivables.payments_count} cobro(s)`}
          value={formatMoney(receivables.payments_total)}
        />
        <StatCard
          label="Total ventas"
          tone="water"
          value={formatMoney(sales.total_sales_amount)}
        />
        </MetricGrid>
      </ReportSection>

      <div className="rounded-2xl border border-water-100 bg-water-50 px-5 py-5 text-water-900 shadow-card sm:px-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
          Referencia operativa
        </p>
        <p className="mt-2 text-sm font-semibold">
          Flujo de efectivo de referencia
        </p>
        <p className="mt-2 break-words text-3xl font-semibold tabular-nums tracking-tight">
          {formatMoney(report.totals.total_business_cash_inflow_reference)}
        </p>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-water-800">
          Suma ventas de contado, cobros y dinero de rutas registrado. Es una
          referencia operativa y no reemplaza el total oficial del cuadre.
        </p>
      </div>
    </div>
  );
}

export function formatMoney(value: string): string {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return `$${value}`;
  }
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(numericValue);
}

export function formatQuantity(value: string): string {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return value;
  }
  return new Intl.NumberFormat("es-EC", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 3,
  }).format(numericValue);
}

export function formatStatus(status: string): string {
  if (status === "active") {
    return "Activo";
  }
  if (status === "voided") {
    return "Anulado";
  }
  if (status === "open") {
    return "Abierto";
  }
  if (status === "closed") {
    return "Cerrado";
  }
  if (status === "corrected") {
    return "Corregido";
  }
  return status;
}

function formatCashStatus(exists: boolean, status: string | null): string {
  if (!exists) {
    return "Sin cuadre";
  }
  return status ? formatStatus(status) : "Sin estado";
}

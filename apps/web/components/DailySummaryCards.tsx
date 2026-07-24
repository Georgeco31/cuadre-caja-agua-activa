import type { ReactNode } from "react";

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
    <div className="space-y-8">
      <SummarySection eyebrow="Caja" title="Estado del cuadre">
        <MetricCard
          label="Estado del cuadre"
          value={formatCashStatus(
            cash.cash_session_exists,
            cash.cash_session_status,
          )}
        />
        <MetricCard
          label="Total contado"
          value={formatMoney(cash.total_counted)}
        />
        <MetricCard label="Gastos" value={formatMoney(cash.total_expenses)} />
        <MetricCard
          label="Total final"
          value={formatMoney(cash.total_final)}
        />
        <MetricCard
          label="Dinero de rutas en caja"
          note={`${cash.route_cash_receipts_count} registro(s) activo(s)`}
          value={formatMoney(cash.route_cash_receipts_total)}
        />
      </SummarySection>

      <SummarySection eyebrow="Producción" title="Producción y merma">
        <MetricCard
          label="Producciones activas"
          note={`${production.voided_production_batches_count} anulada(s)`}
          value={String(production.active_production_batches_count)}
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
          label="Neto producido"
          value={formatQuantity(production.total_quantity_net)}
        />
      </SummarySection>

      <SummarySection eyebrow="Rutas" title="Movimiento y cierre de rutas">
        <MetricCard
          label="Cargas activas"
          value={String(loads.active_route_loads_count)}
        />
        <MetricCard
          label="Retornos activos"
          value={String(returns.active_route_returns_count)}
        />
        <MetricCard
          label="Cierres activos"
          value={String(closures.active_route_closures_count)}
        />
        <MetricCard
          label="Efectivo esperado"
          value={formatMoney(closures.expected_cash_total)}
        />
        <MetricCard
          label="Efectivo entregado"
          value={formatMoney(closures.delivered_cash_total)}
        />
        <MetricCard
          label="Diferencia rutas"
          value={formatMoney(closures.difference_total)}
        />
        <MetricCard
          label="Dinero registrado en caja"
          note={`${receipts.active_receipts_count} registro(s) activo(s)`}
          value={formatMoney(receipts.received_amount_total)}
        />
      </SummarySection>

      <SummarySection eyebrow="Comercial" title="Ventas y cobros">
        <MetricCard
          label="Ventas contado"
          note={`${sales.cash_sales_count} venta(s)`}
          value={formatMoney(sales.cash_sales_total)}
        />
        <MetricCard
          label="Ventas crédito"
          note={`${sales.credit_sales_count} venta(s)`}
          value={formatMoney(sales.credit_sales_total)}
        />
        <MetricCard
          label="Cobros"
          note={`${receivables.payments_count} cobro(s)`}
          value={formatMoney(receivables.payments_total)}
        />
        <MetricCard
          label="Total ventas"
          value={formatMoney(sales.total_sales_amount)}
        />
      </SummarySection>

      <div className="rounded-lg border border-water-100 bg-water-50 px-4 py-4 text-water-900">
        <p className="text-sm font-medium">Flujo de efectivo de referencia</p>
        <p className="mt-1 text-2xl font-semibold">
          {formatMoney(report.totals.total_business_cash_inflow_reference)}
        </p>
        <p className="mt-2 text-sm leading-6 text-water-800">
          Suma ventas de contado, cobros y dinero de rutas registrado. Es una
          referencia operativa y no reemplaza el total oficial del cuadre.
        </p>
      </div>
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
      {note ? <p className="mt-1 text-xs text-slate-500">{note}</p> : null}
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

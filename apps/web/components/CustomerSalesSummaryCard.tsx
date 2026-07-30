import { getCustomerSalesSummaryMetrics } from "@/lib/customerSalesReporting";
import type { CustomerSalesSummary } from "@/types/customer";

type CustomerSalesSummaryCardProps = {
  error?: string;
  isLoading?: boolean;
  summary: CustomerSalesSummary | null;
};

export function CustomerSalesSummaryCard({
  error = "",
  isLoading = false,
  summary,
}: CustomerSalesSummaryCardProps) {
  if (isLoading) {
    return (
      <div className="border-b border-slate-200 bg-water-50 px-4 py-5 text-sm text-water-900">
        Calculando totales del cliente...
      </div>
    );
  }
  if (error) {
    return (
      <div className="border-b border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">
        {error}
      </div>
    );
  }
  if (!summary) {
    return (
      <div className="border-b border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">
        Selecciona un cliente y aplica el filtro para ver sus totales de contado,
        crédito y saldo pendiente.
      </div>
    );
  }

  const periodLabel =
    summary.period_start && summary.period_end
      ? `${formatDate(summary.period_start)} al ${formatDate(summary.period_end)}`
      : "Todo el historial";
  const metrics = getCustomerSalesSummaryMetrics(summary);
  return (
    <section
      aria-label={`Resumen de ventas de ${summary.customer_name}`}
      className="border-b border-water-100 bg-water-50/70 px-4 py-5"
    >
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
            Totales calculados por el sistema
          </p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">
            {summary.customer_name}
          </h3>
        </div>
        <p className="text-xs text-slate-500">{periodLabel}</p>
      </div>
      <div className="mt-4 grid gap-3 min-[360px]:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <Metric
            emphasized={metric.label === "Total vendido"}
            key={metric.label}
            label={metric.label}
            value={metric.value}
            warning={metric.label === "Saldo pendiente"}
          />
        ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-600">
        <span>{summary.total_sales_count} ventas activas</span>
        <span>
          Cobrado sobre crédito: {formatMoney(summary.total_collected_amount)}
        </span>
        <span>
          Última venta:{" "}
          {summary.last_sale_date
            ? formatDate(summary.last_sale_date)
            : "Sin ventas"}
        </span>
        {summary.cancelled_sales_count > 0 ? (
          <span>
            Referencia: {summary.cancelled_sales_count} anulada(s) por{" "}
            {formatMoney(summary.cancelled_sales_total)} (no suman)
          </span>
        ) : null}
      </div>
    </section>
  );
}

function Metric({
  emphasized = false,
  label,
  value,
  warning = false,
}: {
  emphasized?: boolean;
  label: string;
  value: string;
  warning?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border bg-white p-3 ${
        warning
          ? "border-amber-200"
          : emphasized
            ? "border-water-300"
            : "border-slate-200"
      }`}
    >
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p
        className={`mt-1 text-lg font-bold ${
          warning ? "text-amber-700" : "text-slate-950"
        }`}
      >
        {formatMoney(value)}
      </p>
    </div>
  );
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount)
    ? new Intl.NumberFormat("es-EC", {
        style: "currency",
        currency: "USD",
      }).format(amount)
    : "$0.00";
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return `${day}/${month}/${year}`;
}

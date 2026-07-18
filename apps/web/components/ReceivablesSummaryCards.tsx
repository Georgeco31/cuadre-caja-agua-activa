import type { ReceivablesSummary } from "@/types/receivable";

type ReceivablesSummaryCardsProps = {
  summary: ReceivablesSummary;
};

export function ReceivablesSummaryCards({
  summary,
}: ReceivablesSummaryCardsProps) {
  const metrics = [
    {
      label: "Clientes con saldo",
      value: String(summary.total_customers_with_balance),
      valueClass: "text-slate-950",
    },
    {
      label: "Total vendido a crédito",
      value: formatMoney(summary.total_credit_sales),
      valueClass: "text-slate-950",
    },
    {
      label: "Total pagado",
      value: formatMoney(summary.total_paid),
      valueClass: "text-emerald-700",
    },
    {
      label: "Saldo pendiente",
      value: formatMoney(summary.total_balance),
      valueClass: "text-amber-700",
    },
  ];

  return (
    <section
      aria-label="Resumen general de cartera"
      className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"
    >
      {metrics.map((metric) => (
        <article
          className="rounded-lg border border-slate-200 bg-white px-4 py-4 shadow-sm"
          key={metric.label}
        >
          <p className="text-xs font-semibold uppercase text-slate-500">
            {metric.label}
          </p>
          <p className={`mt-2 text-2xl font-semibold ${metric.valueClass}`}>
            {metric.value}
          </p>
        </article>
      ))}
    </section>
  );
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

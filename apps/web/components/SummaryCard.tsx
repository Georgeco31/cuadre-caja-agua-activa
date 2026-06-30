import type { CashSessionSummary } from "@/types/summary";

type SummaryCardProps = {
  summary: CashSessionSummary;
};

const summaryItems = [
  ["Total monedas", "total_coins"],
  ["Total billetes", "total_bills"],
  ["Total contado", "total_counted"],
  ["Total gastos", "total_expenses"],
  ["Total final", "final_total"],
] as const;

export function SummaryCard({ summary }: SummaryCardProps) {
  return (
    <section aria-labelledby="cash-summary-title" className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-water-700">Resumen</p>
          <h2
            id="cash-summary-title"
            className="mt-1 text-xl font-semibold text-slate-950"
          >
            Totales calculados
          </h2>
        </div>
        <span className="w-fit rounded-md border border-slate-200 bg-white px-3 py-1 text-sm font-medium text-slate-700">
          {summary.status}
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {summaryItems.map(([label, key]) => (
          <div
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
            key={key}
          >
            <p className="text-sm text-slate-600">{label}</p>
            <p className="mt-2 text-lg font-semibold text-slate-950">
              {formatMoney(summary[key])}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatMoney(value: string): string {
  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) {
    return `$${value}`;
  }

  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(numberValue);
}

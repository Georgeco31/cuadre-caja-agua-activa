import type { CashSessionSummary } from "@/types/summary";

type SummaryCardProps = {
  summary: CashSessionSummary;
};

const summaryItems = [
  ["Total monedas", "total_coins"],
  ["Total billetes", "total_bills"],
  ["Total contado", "total_counted"],
  ["Gastos antes del conteo", "total_pre_count_expenses"],
  ["Gastos después del conteo", "total_post_count_expenses"],
  ["Total final", "final_total"],
] as const;

export function SummaryCard({ summary }: SummaryCardProps) {
  const isClosed = summary.status === "closed";
  const statusStyles = isClosed
    ? "border-slate-200 bg-slate-100 text-slate-700"
    : "border-water-100 bg-water-50 text-water-700";

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
        <span
          className={`w-fit rounded-md border px-3 py-1 text-sm font-medium ${statusStyles}`}
        >
          {summary.status}
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
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

      <p className="rounded-md border border-water-100 bg-water-50 px-4 py-3 text-sm leading-6 text-water-800">
        Los gastos antes del conteo no se restan porque ya están reflejados en
        el dinero contado. El total final solo resta los gastos después del
        conteo.
      </p>
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

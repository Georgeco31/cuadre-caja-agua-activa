import type { CashSummaryReport } from "@/types/report";

type CashSummaryReportCardsProps = {
  report: CashSummaryReport;
};

const cardItems = [
  ["Cuadres registrados", "total_sessions", "count"],
  ["Cuadres abiertos", "open_sessions", "count"],
  ["Cuadres cerrados", "closed_sessions", "count"],
  ["Total en monedas", "total_coins", "money"],
  ["Total en billetes", "total_bills", "money"],
  ["Total contado", "total_counted", "money"],
  ["Gastos antes del conteo", "total_pre_count_expenses", "money"],
  ["Gastos después del conteo", "total_post_count_expenses", "money"],
  ["Total final", "final_total", "money"],
] as const;

export function CashSummaryReportCards({
  report,
}: CashSummaryReportCardsProps) {
  return (
    <section
      aria-labelledby="cash-summary-report-cards-title"
      className="space-y-4"
    >
      <div>
        <p className="text-sm font-medium text-water-700">Reporte</p>
        <h2
          id="cash-summary-report-cards-title"
          className="mt-1 text-xl font-semibold text-slate-950"
        >
          Totales acumulados
        </h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cardItems.map(([label, key, format]) => (
          <div
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
            key={key}
          >
            <p className="text-sm text-slate-600">{label}</p>
            <p className="mt-2 text-xl font-semibold text-slate-950">
              {format === "money"
                ? formatMoney(String(report[key]))
                : report[key]}
            </p>
          </div>
        ))}
      </div>

      {report.total_sessions === 0 ? (
        <p className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          No hay cuadres registrados para los filtros seleccionados.
        </p>
      ) : null}
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

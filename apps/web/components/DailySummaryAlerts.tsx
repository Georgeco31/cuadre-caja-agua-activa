import type { DailyOperationalAlert } from "@/types/dailyOperationalSummary";

type DailySummaryAlertsProps = {
  alerts: DailyOperationalAlert[];
};

const alertStyles = {
  warning: "border-amber-200 bg-amber-50 text-amber-900",
  info: "border-sky-200 bg-sky-50 text-sky-900",
  success: "border-emerald-200 bg-emerald-50 text-emerald-900",
} as const;

const alertLabels = {
  warning: "Atención",
  info: "Información",
  success: "Correcto",
} as const;

export function DailySummaryAlerts({ alerts }: DailySummaryAlertsProps) {
  return (
    <section aria-labelledby="daily-alerts-title" className="space-y-3">
      <div>
        <p className="text-sm font-medium text-water-700">Seguimiento</p>
        <h2
          className="mt-1 text-xl font-semibold text-slate-950"
          id="daily-alerts-title"
        >
          Alertas del día
        </h2>
      </div>

      {alerts.length === 0 ? (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          No hay alertas operativas para esta fecha.
        </div>
      ) : (
        <div className="grid gap-3 lg:grid-cols-2">
          {alerts.map((alert) => (
            <div
              className={`rounded-lg border px-4 py-3 ${alertStyles[alert.type]}`}
              key={alert.code}
            >
              <p className="text-xs font-semibold uppercase tracking-wide">
                {alertLabels[alert.type]}
              </p>
              <p className="mt-1 text-sm leading-6">{alert.message}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

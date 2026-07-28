import { ReportSection } from "@/components/ui/ReportSection";
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
    <ReportSection
      description="Avisos derivados de los registros disponibles para la fecha consultada."
      eyebrow="Seguimiento"
      id="daily-alerts-title"
      title="Alertas del día"
    >
      {alerts.length === 0 ? (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-900">
          <p className="font-semibold">Sin alertas operativas</p>
          <p className="mt-1 leading-6 text-emerald-800">
            No hay alertas operativas para esta fecha.
          </p>
        </div>
      ) : (
        <div className="grid gap-3 lg:grid-cols-2">
          {alerts.map((alert) => (
            <div
              className={`rounded-2xl border px-5 py-4 ${alertStyles[alert.type]}`}
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
    </ReportSection>
  );
}

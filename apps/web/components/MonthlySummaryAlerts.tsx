import type { MonthlyOperationalAlertsSummary } from "@/types/monthlyOperationalSummary";

type MonthlySummaryAlertsProps = {
  summary: MonthlyOperationalAlertsSummary;
};

const alertLabels: Record<string, string> = {
  cash_session_missing: "Cuadre faltante",
  cash_session_open: "Cuadre abierto",
  route_shortage: "Faltante de ruta",
  route_closure_without_cash_receipt: "Cierre sin registro en caja",
  route_cash_receipt_difference: "Diferencia al registrar ruta",
  no_production: "Sin producción",
  no_sales: "Sin ventas",
  routes_loaded_without_closure: "Carga sin cierre",
};

export function MonthlySummaryAlerts({
  summary,
}: MonthlySummaryAlertsProps) {
  if (summary.total_alerts === 0) {
    return (
      <section
        aria-labelledby="monthly-alerts-title"
        className="rounded-lg border border-emerald-200 bg-emerald-50 p-4"
      >
        <p className="text-sm font-semibold text-emerald-900">
          Sin alertas operativas
        </p>
        <h2 className="sr-only" id="monthly-alerts-title">
          Alertas del mes
        </h2>
        <p className="mt-1 text-sm text-emerald-800">
          No se detectaron alertas para el mes seleccionado.
        </p>
      </section>
    );
  }

  return (
    <section aria-labelledby="monthly-alerts-title" className="space-y-3">
      <div>
        <p className="text-sm font-medium text-amber-700">
          {summary.total_alerts} alerta(s) en{" "}
          {summary.days_with_alerts_count} día(s)
        </p>
        <h2
          className="mt-1 text-xl font-semibold text-slate-950"
          id="monthly-alerts-title"
        >
          Alertas importantes
        </h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {summary.alerts_by_code.map((alert) => (
          <article
            className="rounded-lg border border-amber-200 bg-amber-50 p-4"
            key={alert.code}
          >
            <div className="flex items-start justify-between gap-3">
              <h3 className="text-sm font-semibold text-amber-950">
                {alertLabels[alert.code] ?? alert.code}
              </h3>
              <span className="rounded-full bg-amber-200 px-2.5 py-1 text-xs font-bold text-amber-950">
                {alert.count}
              </span>
            </div>
            <p className="mt-2 text-sm leading-6 text-amber-900">
              {alert.message}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

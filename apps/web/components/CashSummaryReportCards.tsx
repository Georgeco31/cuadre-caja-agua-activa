import type { CashSummaryReport } from "@/types/report";

import { MetricGrid } from "@/components/ui/MetricGrid";
import { ReportSection } from "@/components/ui/ReportSection";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/StatusBadge";

type CashSummaryReportCardsProps = {
  report: CashSummaryReport;
};

export function CashSummaryReportCards({
  report,
}: CashSummaryReportCardsProps) {
  return (
    <div className="min-w-0 space-y-8">
      <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-card sm:flex-row sm:items-center sm:justify-between sm:px-5">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
            Consulta aplicada
          </p>
          <p className="mt-1 text-sm font-medium text-slate-900">
            {formatPeriod(report.date_from, report.date_to)}
          </p>
        </div>
        <StatusBadge
          label={formatStatusFilter(report.status)}
          tone="info"
        />
      </div>

      {report.total_sessions === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-9 text-center">
          <p className="font-semibold text-slate-900">
            No hay cuadres para esta consulta
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Ajusta el período o el estado para revisar otros registros.
          </p>
        </div>
      ) : null}

      <ReportSection
        description="Cantidad y estado de los cuadres incluidos en el acumulado."
        eyebrow="Sesiones"
        id="cash-summary-sessions-title"
        title="Cuadres registrados"
      >
        <MetricGrid columns="three">
          <StatCard
            label="Cuadres registrados"
            value={report.total_sessions}
          />
          <StatCard
            hint="Sesiones todavía en proceso"
            label="Cuadres abiertos"
            value={report.open_sessions}
          />
          <StatCard
            hint="Sesiones finalizadas"
            label="Cuadres cerrados"
            value={report.closed_sessions}
          />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        description="Desglose del efectivo contado en los cuadres seleccionados."
        eyebrow="Efectivo"
        id="cash-summary-cash-title"
        title="Monedas, billetes y contado"
      >
        <MetricGrid columns="three">
          <StatCard
            label="Total en monedas"
            value={formatMoney(report.total_coins)}
          />
          <StatCard
            label="Total en billetes"
            value={formatMoney(report.total_bills)}
          />
          <StatCard
            label="Total contado"
            tone="water"
            value={formatMoney(report.total_counted)}
          />
        </MetricGrid>
      </ReportSection>

      <ReportSection
        description="Los valores conservan la fórmula y la clasificación registradas en cada cuadre."
        eyebrow="Resultado"
        id="cash-summary-result-title"
        title="Gastos y total final"
      >
        <MetricGrid>
          <StatCard
            label="Gastos antes del conteo"
            value={formatMoney(report.total_pre_count_expenses)}
          />
          <StatCard
            label="Gastos después del conteo"
            value={formatMoney(report.total_post_count_expenses)}
          />
          <StatCard
            label="Gastos acumulados"
            value={formatMoney(report.total_expenses)}
          />
          <StatCard
            hint="Resultado acumulado del reporte"
            label="Total final"
            tone="water"
            value={formatMoney(report.final_total)}
          />
        </MetricGrid>
      </ReportSection>
    </div>
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

function formatPeriod(
  dateFrom: string | null,
  dateTo: string | null,
): string {
  if (!dateFrom && !dateTo) {
    return "Todos los períodos disponibles";
  }
  if (dateFrom && dateTo) {
    return `${formatDate(dateFrom)} — ${formatDate(dateTo)}`;
  }
  return dateFrom
    ? `Desde ${formatDate(dateFrom)}`
    : `Hasta ${formatDate(dateTo ?? "")}`;
}

function formatStatusFilter(status: string | null): string {
  if (status === "open") {
    return "Solo abiertos";
  }
  if (status === "closed") {
    return "Solo cerrados";
  }
  if (status === "corrected") {
    return "Solo corregidos";
  }
  return "Todos los estados";
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return year && month && day ? `${day}/${month}/${year}` : value;
}

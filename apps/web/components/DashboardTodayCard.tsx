import Link from "next/link";

import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { CashSession } from "@/types/cashSession";
import type { CashSessionSummary } from "@/types/summary";

type DashboardTodayCardProps = {
  cashSession: CashSession | null;
  summary: CashSessionSummary | null;
};

const summaryItems = [
  ["Total contado", "total_counted"],
  ["Gastos antes", "total_pre_count_expenses"],
  ["Gastos después", "total_post_count_expenses"],
  ["Total final", "final_total"],
] as const;

export function DashboardTodayCard({
  cashSession,
  summary,
}: DashboardTodayCardProps) {
  const status = cashSession?.status ?? "missing";
  const statusLabel = getStatusLabel(status);
  const message = getStatusMessage(status);

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card sm:p-6">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
            Estado del cuadre de hoy
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
            {message}
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {cashSession
              ? `Fecha registrada: ${formatDate(cashSession.session_date)}.`
            : "Todavía no se ha creado el cuadre de hoy."}
          </p>
        </div>

        <StatusBadge label={statusLabel} tone={getStatusTone(status)} />
      </div>

      {summary ? (
        <dl className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {summaryItems.map(([label, key]) => (
            <StatCard
              hint={key === "final_total" ? "Resultado oficial" : undefined}
              key={key}
              label={label}
              tone={key === "final_total" ? "water" : "neutral"}
              value={formatMoney(summary[key])}
            />
          ))}
        </dl>
      ) : (
        <p className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4 text-sm leading-6 text-amber-900">
          Cuando se registre el cuadre diario, aquí aparecerán los totales
          oficiales calculados por el backend.
        </p>
      )}

      <div className="mt-6">
        <Link
          className="inline-flex min-h-11 w-full items-center justify-center rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-water-500 focus-visible:ring-offset-2 sm:w-auto"
          href="/dashboard/cash-session"
        >
          Registrar o consultar cuadre
        </Link>
      </div>
    </section>
  );
}

function getStatusLabel(status: CashSession["status"] | "missing"): string {
  if (status === "open") {
    return "Abierto";
  }
  if (status === "closed") {
    return "Cerrado";
  }

  return "No creado";
}

function getStatusMessage(status: CashSession["status"] | "missing"): string {
  if (status === "open") {
    return "Cuadre de hoy abierto.";
  }
  if (status === "closed") {
    return "Cuadre de hoy cerrado.";
  }

  return "Todavía no se ha creado el cuadre de hoy.";
}

function getStatusTone(
  status: CashSession["status"] | "missing",
): "success" | "neutral" | "warning" {
  if (status === "open") {
    return "success";
  }
  if (status === "closed") {
    return "neutral";
  }

  return "warning";
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "long",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
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

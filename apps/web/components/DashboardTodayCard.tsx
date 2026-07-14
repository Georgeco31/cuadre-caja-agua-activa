import Link from "next/link";

import type { CashSession } from "@/types/cashSession";
import type { CashSessionSummary } from "@/types/summary";

type DashboardTodayCardProps = {
  cashSession: CashSession | null;
  summary: CashSessionSummary | null;
};

const summaryItems = [
  ["Total contado", "total_counted", "money"],
  ["Gastos antes", "total_pre_count_expenses", "money"],
  ["Gastos después", "total_post_count_expenses", "money"],
  ["Total final", "final_total", "money"],
  ["Estado", "status", "status"],
] as const;

export function DashboardTodayCard({
  cashSession,
  summary,
}: DashboardTodayCardProps) {
  const status = cashSession?.status ?? "missing";
  const statusLabel = getStatusLabel(status);
  const statusStyles = getStatusStyles(status);
  const message = getStatusMessage(status);

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-water-700">
            Estado del cuadre de hoy
          </p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            {message}
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {cashSession
              ? `Fecha registrada: ${formatDate(cashSession.session_date)}.`
              : "Todavía no se ha creado el cuadre de hoy."}
          </p>
        </div>

        <span
          className={`w-fit rounded-md border px-3 py-1 text-sm font-semibold ${statusStyles}`}
        >
          {statusLabel}
        </span>
      </div>

      {summary ? (
        <dl className="mt-5 grid overflow-hidden rounded-md border border-slate-200 sm:grid-cols-2 lg:grid-cols-5">
          {summaryItems.map(([label, key, format]) => (
            <div
              className="border-b border-slate-200 px-3 py-3 last:border-b-0 sm:border-b-0 sm:border-r sm:last:border-r-0"
              key={key}
            >
              <dt className="text-sm text-slate-600">{label}</dt>
              <dd className="mt-1 text-base font-semibold text-slate-950">
                {format === "money"
                  ? formatMoney(summary[key])
                  : getStatusLabel(summary[key])}
              </dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="mt-5 rounded-md border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-600">
          Cuando se registre el cuadre diario, aquí aparecerán los totales
          oficiales calculados por el backend.
        </p>
      )}

      <div className="mt-5">
        <Link
          className="inline-flex h-10 items-center justify-center rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500"
          href="/dashboard/cash-session"
        >
          Registrar cuadre diario
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

function getStatusStyles(status: CashSession["status"] | "missing"): string {
  if (status === "open") {
    return "border-water-100 bg-water-50 text-water-700";
  }
  if (status === "closed") {
    return "border-slate-200 bg-slate-100 text-slate-700";
  }

  return "border-amber-200 bg-amber-50 text-amber-800";
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

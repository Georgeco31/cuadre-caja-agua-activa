import Link from "next/link";

import { StatusBadge } from "@/components/ui/StatusBadge";
import type { CashSession } from "@/types/cashSession";
import type { CashSessionSummary } from "@/types/summary";

export type DashboardRecentSessionItem = {
  cashSession: CashSession;
  summary: CashSessionSummary | null;
};

type DashboardRecentSessionsProps = {
  items: DashboardRecentSessionItem[];
};

export function DashboardRecentSessions({
  items,
}: DashboardRecentSessionsProps) {
  return (
    <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-end sm:justify-between sm:px-6">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
            Actividad reciente
          </p>
          <h2 className="mt-2 text-xl font-semibold text-slate-950">
          Últimos cuadres registrados
          </h2>
        </div>
        <Link
          className="text-sm font-semibold text-water-700 hover:text-water-600"
          href="/dashboard/history"
        >
          Ver historial completo →
        </Link>
      </div>

      {items.length === 0 ? (
        <p className="px-5 py-8 text-sm text-slate-600 sm:px-6">
          Todavía no hay cuadres registrados.
        </p>
      ) : (
        <>
          <div className="divide-y divide-slate-100 md:hidden">
            {items.map(({ cashSession, summary }) => (
              <article className="space-y-3 px-5 py-5" key={cashSession.id}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Fecha
                    </p>
                    <p className="mt-1 font-semibold text-slate-950">
                      {formatDate(cashSession.session_date)}
                    </p>
                  </div>
                  <StatusBadge
                    label={getStatusLabel(cashSession.status)}
                    tone={
                      cashSession.status === "open" ? "success" : "neutral"
                    }
                  />
                </div>
                <div className="flex items-end justify-between gap-3">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                      Total final
                    </p>
                    <p className="mt-1 text-lg font-semibold text-slate-950">
                      {summary
                        ? formatMoney(summary.final_total)
                        : "No disponible"}
                    </p>
                  </div>
                  <Link
                    className="inline-flex min-h-11 items-center rounded-xl border border-slate-200 px-4 text-sm font-semibold text-water-700"
                    href={`/dashboard/history/${cashSession.id}`}
                  >
                    Ver detalle
                  </Link>
                </div>
              </article>
            ))}
          </div>
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                  <th className="px-6 py-3 font-medium">Fecha</th>
                  <th className="px-6 py-3 font-medium">Estado</th>
                  <th className="px-6 py-3 font-medium">Total final</th>
                  <th className="px-6 py-3 text-right font-medium">Detalle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map(({ cashSession, summary }) => (
                  <tr className="transition hover:bg-slate-50/80" key={cashSession.id}>
                    <td className="px-6 py-4 font-medium text-slate-950">
                    {formatDate(cashSession.session_date)}
                  </td>
                    <td className="px-6 py-4 text-slate-700">
                      <StatusBadge
                        label={getStatusLabel(cashSession.status)}
                        tone={
                          cashSession.status === "open" ? "success" : "neutral"
                        }
                      />
                  </td>
                    <td className="px-6 py-4 font-semibold text-slate-800">
                    {summary
                      ? formatMoney(summary.final_total)
                      : "No disponible"}
                  </td>
                    <td className="px-6 py-4 text-right">
                    <Link
                        className="font-semibold text-water-700 hover:text-water-600"
                      href={`/dashboard/history/${cashSession.id}`}
                    >
                        Ver detalle →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </>
      )}
    </section>
  );
}

function getStatusLabel(status: CashSession["status"]): string {
  if (status === "open") {
    return "Abierto";
  }

  return "Cerrado";
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
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

import Link from "next/link";

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
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <p className="text-sm font-medium text-water-700">Historial</p>
        <h2 className="mt-1 text-xl font-semibold text-slate-950">
          Últimos cuadres registrados
        </h2>
      </div>

      {items.length === 0 ? (
        <p className="px-4 py-6 text-sm text-slate-600">
          Todavía no hay cuadres registrados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Total final</th>
                <th className="px-4 py-3 font-medium">Detalle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map(({ cashSession, summary }) => (
                <tr key={cashSession.id}>
                  <td className="px-4 py-3 font-medium text-slate-950">
                    {formatDate(cashSession.session_date)}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {getStatusLabel(cashSession.status)}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {summary
                      ? formatMoney(summary.final_total)
                      : "No disponible"}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      className="font-semibold text-water-700 hover:text-water-500"
                      href={`/dashboard/history/${cashSession.id}`}
                    >
                      Ver detalle
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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

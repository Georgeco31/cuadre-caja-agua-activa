import Link from "next/link";

import type { CashSession } from "@/types/cashSession";

type CashSessionHistoryTableProps = {
  cashSessions: CashSession[];
};

export function CashSessionHistoryTable({
  cashSessions,
}: CashSessionHistoryTableProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Cuadres registrados
        </h2>
      </div>

      {cashSessions.length === 0 ? (
        <p className="px-4 py-6 text-sm text-slate-600">
          Todavía no hay cuadres registrados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Notas</th>
                <th className="px-4 py-3 font-medium">Creación</th>
                <th className="px-4 py-3 font-medium">Cierre</th>
                <th className="px-4 py-3 font-medium">Detalle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {cashSessions.map((cashSession) => (
                <tr key={cashSession.id}>
                  <td className="px-4 py-3 text-slate-950">
                    {formatDate(cashSession.session_date)}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {cashSession.status}
                  </td>
                  <td className="max-w-xs px-4 py-3 text-slate-600">
                    {cashSession.notes ?? "Sin notas"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {formatDateTime(cashSession.created_at)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {cashSession.closed_at
                      ? formatDateTime(cashSession.closed_at)
                      : "Sin cierre"}
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

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

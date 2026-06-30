import type { CorrectionLog } from "@/types/correction";

type CorrectionLogsListProps = {
  correctionLogs: CorrectionLog[];
};

export function CorrectionLogsList({
  correctionLogs,
}: CorrectionLogsListProps) {
  return (
    <section
      aria-labelledby="correction-logs-title"
      className="rounded-lg border border-slate-200 bg-white shadow-sm"
    >
      <div className="border-b border-slate-200 px-4 py-3">
        <h3
          id="correction-logs-title"
          className="text-lg font-semibold text-slate-950"
        >
          Historial de correcciones
        </h3>
      </div>

      {correctionLogs.length === 0 ? (
        <p className="px-4 py-6 text-sm text-slate-600">
          Todavia no hay correcciones registradas para este cuadre.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Motivo</th>
                <th className="px-4 py-3 font-medium">Total anterior</th>
                <th className="px-4 py-3 font-medium">Total nuevo</th>
                <th className="px-4 py-3 font-medium">Usuario</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {correctionLogs.map((correctionLog) => (
                <tr key={correctionLog.id}>
                  <td className="max-w-sm px-4 py-3 text-slate-950">
                    {correctionLog.reason}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {formatMoney(correctionLog.previous_total)}
                  </td>
                  <td className="px-4 py-3 font-semibold text-slate-950">
                    {formatMoney(correctionLog.new_total)}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {correctionLog.created_by
                      ? `Usuario ${correctionLog.created_by}`
                      : "Sin usuario"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {formatDateTime(correctionLog.created_at)}
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

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

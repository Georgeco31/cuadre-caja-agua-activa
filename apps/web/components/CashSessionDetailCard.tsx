import type { CashSession } from "@/types/cashSession";

type CashSessionDetailCardProps = {
  cashSession: CashSession;
};

export function CashSessionDetailCard({
  cashSession,
}: CashSessionDetailCardProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <p className="text-sm text-slate-600">Fecha</p>
          <p className="mt-1 font-semibold text-slate-950">
            {formatDate(cashSession.session_date)}
          </p>
        </div>
        <div>
          <p className="text-sm text-slate-600">Estado</p>
          <p className="mt-1 font-semibold text-slate-950">
            {cashSession.status}
          </p>
        </div>
        <div>
          <p className="text-sm text-slate-600">Creación</p>
          <p className="mt-1 font-semibold text-slate-950">
            {formatDateTime(cashSession.created_at)}
          </p>
        </div>
        <div>
          <p className="text-sm text-slate-600">Cierre</p>
          <p className="mt-1 font-semibold text-slate-950">
            {cashSession.closed_at
              ? formatDateTime(cashSession.closed_at)
              : "Sin cierre"}
          </p>
        </div>
      </div>

      <div className="mt-4 border-t border-slate-100 pt-4">
        <p className="text-sm text-slate-600">Notas</p>
        <p className="mt-1 text-sm leading-6 text-slate-700">
          {cashSession.notes ?? "Sin notas"}
        </p>
      </div>
    </section>
  );
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "long",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

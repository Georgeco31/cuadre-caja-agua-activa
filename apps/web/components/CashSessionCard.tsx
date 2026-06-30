import type { CashSession } from "@/types/cashSession";

type CashSessionCardProps = {
  cashSession: CashSession;
  isClosing: boolean;
  onClose: () => void;
};

export function CashSessionCard({
  cashSession,
  isClosing,
  onClose,
}: CashSessionCardProps) {
  const isClosed = cashSession.status === "closed";

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-water-700">
            Cuadre del día
          </p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            {formatDate(cashSession.session_date)}
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Estado: {cashSession.status}
          </p>
        </div>

        <button
          className="h-10 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          type="button"
          onClick={onClose}
          disabled={isClosed || isClosing}
        >
          {isClosed ? "Cuadre cerrado" : isClosing ? "Cerrando..." : "Cerrar cuadre"}
        </button>
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

import Link from "next/link";

import { StatusBadge } from "@/components/ui/StatusBadge";
import type { CashSession } from "@/types/cashSession";
import type { CashSessionSummary } from "@/types/summary";

type DashboardTodayCardProps = {
  cashSession: CashSession | null;
  summary: CashSessionSummary | null;
};

export function DashboardTodayCard({
  cashSession,
  summary,
}: DashboardTodayCardProps) {
  const status = cashSession?.status ?? "missing";

  return (
    <section
      aria-labelledby="today-cash-session-title"
      className="relative min-w-0 overflow-hidden rounded-3xl bg-water-900 p-5 text-white shadow-water sm:p-7 lg:p-8"
    >
      <span
        aria-hidden="true"
        className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-water-500/20 blur-2xl"
      />
      <span
        aria-hidden="true"
        className="absolute -bottom-28 left-1/3 h-52 w-52 rounded-full bg-white/10 blur-3xl"
      />

      <div className="relative">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-water-100">
              Operación principal
            </p>
            <h2
              className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl"
              id="today-cash-session-title"
            >
              Cuadre de caja de hoy
            </h2>
          </div>
          <StatusBadge
            label={getStatusLabel(status)}
            tone={getStatusTone(status)}
          />
        </div>

        <p className="mt-5 max-w-2xl text-base font-medium leading-7 text-white sm:text-lg">
          {getStatusMessage(status)}
        </p>
        <p className="mt-1.5 text-sm leading-6 text-water-100">
          {cashSession
            ? `Fecha registrada: ${formatDate(cashSession.session_date)}.`
            : "La consulta de hoy no devolvió una sesión de caja registrada."}
        </p>

        {summary ? (
          <div className="mt-7 grid gap-3 rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-sm min-[430px]:grid-cols-2 sm:max-w-xl sm:p-5">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-water-100">
                Total contado
              </p>
              <p className="mt-2 break-words text-xl font-semibold tabular-nums text-white sm:text-2xl">
                {formatMoney(summary.total_counted)}
              </p>
            </div>
            <div className="border-white/15 min-[430px]:border-l min-[430px]:pl-5">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-water-100">
                Total final
              </p>
              <p className="mt-2 break-words text-xl font-semibold tabular-nums text-white sm:text-2xl">
                {formatMoney(summary.final_total)}
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-7 max-w-2xl rounded-2xl border border-white/15 bg-white/10 px-4 py-4 text-sm leading-6 text-water-50">
            Cuando se registre el cuadre diario, aquí aparecerán los totales
            oficiales calculados por el backend.
          </div>
        )}

        <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
          <Link
            className="inline-flex min-h-12 w-full items-center justify-center rounded-xl bg-white px-5 text-sm font-semibold text-water-900 shadow-sm transition hover:bg-water-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-water-900 sm:w-auto"
            href="/dashboard/cash-session"
          >
            Registrar o consultar cuadre
            <span aria-hidden="true" className="ml-2">
              →
            </span>
          </Link>
          <Link
            className="inline-flex min-h-12 w-full items-center justify-center rounded-xl border border-white/20 px-5 text-sm font-semibold text-white transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white sm:w-auto"
            href="/dashboard/history"
          >
            Ver historial de caja
          </Link>
        </div>
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
    return "El cuadre está abierto y listo para continuar.";
  }
  if (status === "closed") {
    return "El cuadre de hoy está cerrado.";
  }

  return "El cuadre de hoy está pendiente.";
}

function getStatusTone(
  status: CashSession["status"] | "missing",
): "success" | "info" | "warning" {
  if (status === "open") {
    return "success";
  }
  if (status === "closed") {
    return "info";
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

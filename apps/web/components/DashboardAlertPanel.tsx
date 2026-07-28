import type { ReactNode } from "react";

import { StatusBadge } from "@/components/ui/StatusBadge";

export type DashboardAlertItem = {
  description: string;
  id: string;
  title: string;
  tone: "info" | "warning" | "danger";
};

type DashboardAlertPanelProps = {
  alerts: DashboardAlertItem[];
  children?: ReactNode;
};

const alertStyles = {
  info: {
    article: "border-water-100 bg-water-50/70",
    icon: "bg-water-100 text-water-800",
  },
  warning: {
    article: "border-amber-200 bg-amber-50",
    icon: "bg-amber-100 text-amber-800",
  },
  danger: {
    article: "border-red-200 bg-red-50",
    icon: "bg-red-100 text-red-800",
  },
} as const;

export function DashboardAlertPanel({
  alerts,
  children,
}: DashboardAlertPanelProps) {
  const noticeCount = alerts.length + (children ? 1 : 0);

  return (
    <section
      aria-labelledby="dashboard-alerts-title"
      className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card sm:p-6"
      id="alertas"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
            Alertas reales
          </p>
          <h2
            className="mt-2 text-xl font-semibold tracking-tight text-slate-950"
            id="dashboard-alerts-title"
          >
            Atención operativa
          </h2>
        </div>
        <StatusBadge
          label={`${noticeCount} ${noticeCount === 1 ? "aviso" : "avisos"}`}
          tone={alerts.length > 0 ? "warning" : "info"}
        />
      </div>

      <div className="mt-5 space-y-3">
        {alerts.map((alert) => {
          const styles = alertStyles[alert.tone];

          return (
            <article
              className={`rounded-2xl border p-4 ${styles.article}`}
              key={alert.id}
            >
              <div className="flex items-start gap-3">
                <span
                  aria-hidden="true"
                  className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${styles.icon}`}
                >
                  !
                </span>
                <div className="min-w-0">
                  <h3 className="font-semibold text-slate-950">
                    {alert.title}
                  </h3>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    {alert.description}
                  </p>
                </div>
              </div>
            </article>
          );
        })}

        {children}

        {noticeCount === 0 ? (
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
            <p className="font-semibold text-emerald-900">
              Sin alertas con los datos disponibles
            </p>
            <p className="mt-1 text-sm leading-6 text-emerald-800">
              El panel no detecta tareas pendientes en la información que
              recibe actualmente.
            </p>
          </div>
        ) : null}
      </div>
    </section>
  );
}

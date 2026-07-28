import type { ReactNode } from "react";

import { ActionCard } from "@/components/ui/ActionCard";

export type DashboardModuleAction = {
  badge?: ReactNode;
  description: string;
  href: string;
  icon: string;
  title: string;
  variant?: "primary" | "secondary";
};

type DashboardModuleGroupProps = {
  actions: DashboardModuleAction[];
  description: string;
  id: string;
  index: number;
  title: string;
};

export function DashboardModuleGroup({
  actions,
  description,
  id,
  index,
  title,
}: DashboardModuleGroupProps) {
  return (
    <section
      aria-labelledby={`dashboard-group-${id}`}
      className="min-w-0 rounded-3xl border border-slate-200 bg-white p-4 shadow-card sm:p-6"
    >
      <div className="mb-5 flex items-start gap-3">
        <span
          aria-hidden="true"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-water-50 text-sm font-bold text-water-700"
        >
          {String(index).padStart(2, "0")}
        </span>
        <div className="min-w-0">
          <h3
            className="text-lg font-semibold text-slate-950"
            id={`dashboard-group-${id}`}
          >
            {title}
          </h3>
          <p className="mt-1 text-sm leading-5 text-slate-600">
            {description}
          </p>
        </div>
      </div>

      <div className="grid min-w-0 gap-3 sm:grid-cols-2">
        {actions.map((action) => (
          <ActionCard
            badge={action.badge}
            description={action.description}
            href={action.href}
            icon={action.icon}
            key={action.href}
            size="compact"
            title={action.title}
            variant={action.variant}
          />
        ))}
      </div>
    </section>
  );
}

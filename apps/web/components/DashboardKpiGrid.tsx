import { StatCard } from "@/components/ui/StatCard";

export type DashboardKpiItem = {
  hint?: string;
  icon?: string;
  label: string;
  tone?: "neutral" | "water" | "success" | "warning" | "danger";
  value: string;
};

type DashboardKpiGridProps = {
  items: DashboardKpiItem[];
};

export function DashboardKpiGrid({ items }: DashboardKpiGridProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section aria-labelledby="dashboard-kpis-title">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
            Lectura rápida
          </p>
          <h2
            className="mt-1.5 text-xl font-semibold tracking-tight text-slate-950"
            id="dashboard-kpis-title"
          >
            Totales del cuadre de hoy
          </h2>
        </div>
        <p className="text-sm text-slate-500">Valores oficiales del resumen</p>
      </div>

      <div className="grid min-w-0 grid-cols-1 gap-3 min-[360px]:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => (
          <StatCard
            hint={item.hint}
            icon={item.icon}
            key={item.label}
            label={item.label}
            tone={item.tone}
            value={item.value}
          />
        ))}
      </div>
    </section>
  );
}

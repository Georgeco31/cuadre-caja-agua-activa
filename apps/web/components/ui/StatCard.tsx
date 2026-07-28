import type { ReactNode } from "react";

const toneStyles = {
  neutral: "border-slate-200 bg-white",
  water: "border-water-100 bg-water-50/70",
  success: "border-emerald-200 bg-emerald-50",
  warning: "border-amber-200 bg-amber-50",
  danger: "border-red-200 bg-red-50",
} as const;

type StatCardProps = {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: keyof typeof toneStyles;
  icon?: ReactNode;
};

export function StatCard({
  label,
  value,
  hint,
  tone = "neutral",
  icon,
}: StatCardProps) {
  return (
    <div className={`rounded-2xl border p-4 ${toneStyles[tone]}`}>
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          {label}
        </p>
        {icon ? (
          <span
            aria-hidden="true"
            className="text-sm font-semibold text-water-700"
          >
            {icon}
          </span>
        ) : null}
      </div>
      <div className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
        {value}
      </div>
      {hint ? (
        <div className="mt-2 text-xs leading-5 text-slate-600">{hint}</div>
      ) : null}
    </div>
  );
}

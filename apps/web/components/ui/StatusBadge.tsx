import type { ReactNode } from "react";

const toneStyles = {
  neutral: "border-slate-200 bg-slate-100 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-red-200 bg-red-50 text-red-800",
  info: "border-water-100 bg-water-50 text-water-800",
} as const;

type StatusBadgeProps = {
  label: ReactNode;
  tone?: keyof typeof toneStyles;
};

export function StatusBadge({
  label,
  tone = "neutral",
}: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex w-fit items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${toneStyles[tone]}`}
    >
      {label}
    </span>
  );
}

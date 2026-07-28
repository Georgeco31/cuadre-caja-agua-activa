import Link from "next/link";
import type { ReactNode } from "react";

type ActionCardProps = {
  title: string;
  description: string;
  href: string;
  variant?: "primary" | "secondary";
  badge?: ReactNode;
  disabled?: boolean;
  icon?: ReactNode;
};

export function ActionCard({
  title,
  description,
  href,
  variant = "secondary",
  badge,
  disabled = false,
  icon,
}: ActionCardProps) {
  const className =
    variant === "primary"
      ? "group flex min-h-36 flex-col rounded-2xl border border-water-700 bg-water-700 p-5 text-white shadow-water transition hover:-translate-y-0.5 hover:bg-water-600 hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-water-500 focus-visible:ring-offset-2"
      : "group flex min-h-36 flex-col rounded-2xl border border-slate-200 bg-white p-5 text-slate-950 shadow-card transition hover:-translate-y-0.5 hover:border-water-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-water-500 focus-visible:ring-offset-2";

  const content = (
    <>
      <span className="flex items-start justify-between gap-3">
        <span
          aria-hidden="true"
          className={
            variant === "primary"
              ? "inline-flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 text-sm font-bold text-white"
              : "inline-flex h-10 w-10 items-center justify-center rounded-xl bg-water-50 text-sm font-bold text-water-700"
          }
        >
          {icon ?? "AA"}
        </span>
        {badge ? <span className="shrink-0">{badge}</span> : null}
      </span>
      <span className="mt-5 block text-base font-semibold">{title}</span>
      <span
        className={
          variant === "primary"
            ? "mt-2 block text-sm leading-5 text-water-50"
            : "mt-2 block text-sm leading-5 text-slate-600"
        }
      >
        {description}
      </span>
      <span
        aria-hidden="true"
        className={
          variant === "primary"
            ? "mt-auto pt-4 text-lg text-white/80 transition group-hover:translate-x-1"
            : "mt-auto pt-4 text-lg text-water-700 transition group-hover:translate-x-1"
        }
      >
        →
      </span>
    </>
  );

  if (disabled) {
    return (
      <div
        aria-disabled="true"
        className={`${className} cursor-not-allowed opacity-55`}
      >
        {content}
      </div>
    );
  }

  return (
    <Link className={className} href={href}>
      {content}
    </Link>
  );
}

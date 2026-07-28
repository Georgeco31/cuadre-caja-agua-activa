import Link from "next/link";
import type { ReactNode } from "react";

type ActionCardProps = {
  title: string;
  description: string;
  href: string;
  variant?: "primary" | "secondary";
  size?: "regular" | "compact";
  badge?: ReactNode;
  disabled?: boolean;
  icon?: ReactNode;
};

export function ActionCard({
  title,
  description,
  href,
  variant = "secondary",
  size = "regular",
  badge,
  disabled = false,
  icon,
}: ActionCardProps) {
  const isPrimary = variant === "primary";
  const className = [
    "group flex rounded-2xl border transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-water-500 focus-visible:ring-offset-2",
    size === "compact" ? "min-h-28 p-4" : "min-h-40 flex-col p-5",
    isPrimary
      ? "border-water-700 bg-water-700 text-white shadow-water hover:-translate-y-0.5 hover:bg-water-600 hover:shadow-lg"
      : "border-slate-200 bg-white text-slate-950 shadow-card hover:-translate-y-0.5 hover:border-water-200 hover:shadow-md",
  ].join(" ");

  const iconClassName = isPrimary
    ? "inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/15 text-sm font-bold text-white"
    : "inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-water-50 text-sm font-bold text-water-700";

  if (size === "compact") {
    const compactContent = (
      <>
        <span aria-hidden="true" className={iconClassName}>
          {icon ?? "AA"}
        </span>
        <span className="ml-3 min-w-0 flex-1">
          <span className="flex items-start justify-between gap-2">
            <span className="block text-sm font-semibold leading-5">
              {title}
            </span>
            {badge ? <span className="shrink-0">{badge}</span> : null}
          </span>
          <span
            className={
              isPrimary
                ? "mt-1.5 block text-xs leading-5 text-water-50"
                : "mt-1.5 block text-xs leading-5 text-slate-600"
            }
          >
            {description}
          </span>
        </span>
        <span
          aria-hidden="true"
          className={
            isPrimary
              ? "ml-2 self-center text-lg text-white/80 transition group-hover:translate-x-1"
              : "ml-2 self-center text-lg text-water-700 transition group-hover:translate-x-1"
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
          {compactContent}
        </div>
      );
    }

    return (
      <Link className={className} href={href}>
        {compactContent}
      </Link>
    );
  }

  const content = (
    <>
      <span className="flex items-start justify-between gap-3">
        <span aria-hidden="true" className={iconClassName}>
          {icon ?? "AA"}
        </span>
        {badge ? <span className="shrink-0">{badge}</span> : null}
      </span>
      <span className="mt-5 block text-base font-semibold">{title}</span>
      <span
        className={
          isPrimary
            ? "mt-2 block text-sm leading-5 text-water-50"
            : "mt-2 block text-sm leading-5 text-slate-600"
        }
      >
        {description}
      </span>
      <span
        aria-hidden="true"
        className={
          isPrimary
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

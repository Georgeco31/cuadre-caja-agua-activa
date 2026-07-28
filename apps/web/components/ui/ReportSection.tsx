import type { ReactNode } from "react";

type ReportSectionProps = {
  children: ReactNode;
  description?: string;
  eyebrow: string;
  id: string;
  title: string;
};

export function ReportSection({
  children,
  description,
  eyebrow,
  id,
  title,
}: ReportSectionProps) {
  return (
    <section aria-labelledby={id} className="min-w-0 space-y-4">
      <div className="max-w-3xl">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
          {eyebrow}
        </p>
        <h2
          className="mt-1.5 text-xl font-semibold tracking-tight text-slate-950 sm:text-2xl"
          id={id}
        >
          {title}
        </h2>
        {description ? (
          <p className="mt-2 text-sm leading-6 text-slate-600">
            {description}
          </p>
        ) : null}
      </div>
      {children}
    </section>
  );
}

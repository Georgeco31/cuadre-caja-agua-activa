import type { ReactNode } from "react";

type ResponsiveToolbarProps = {
  children?: ReactNode;
  actions?: ReactNode;
};

export function ResponsiveToolbar({
  children,
  actions,
}: ResponsiveToolbarProps) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-card sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">{children}</div>
      {actions ? (
        <div className="flex shrink-0 flex-wrap items-center gap-3">
          {actions}
        </div>
      ) : null}
    </div>
  );
}

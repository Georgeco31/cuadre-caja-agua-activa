import type { ReactNode } from "react";

const columnStyles = {
  three: "lg:grid-cols-3",
  four: "lg:grid-cols-4",
  five: "lg:grid-cols-4 xl:grid-cols-5",
} as const;

type MetricGridProps = {
  children: ReactNode;
  columns?: keyof typeof columnStyles;
};

export function MetricGrid({
  children,
  columns = "four",
}: MetricGridProps) {
  return (
    <div
      className={`grid min-w-0 gap-3 min-[360px]:grid-cols-2 ${columnStyles[columns]}`}
    >
      {children}
    </div>
  );
}

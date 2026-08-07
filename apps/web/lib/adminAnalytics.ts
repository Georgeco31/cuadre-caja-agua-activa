import type { UserRole } from "@/types/auth";

export type AnalyticsPreset = "today" | "last7" | "month";
export type AnalyticsViewState = "loading" | "error" | "ready" | "empty";

export const ADMIN_ANALYTICS_TEXT = {
  officialSales: "Ventas oficiales",
  officialCashSales: "Ventas contado oficiales",
  officialCreditSales: "Ventas crédito oficiales",
  officialCollections: "Cobros crédito recibidos",
  officialPending: "Saldo crédito formal",
  routeSection: "Rutas simples / operativo",
  routeSales: "Ventas de ruta",
  routePending: "Fiado de rutas",
  routeCollections: "Abonos de ruta",
  totalWithRoutes: "Total vendido con rutas",
  separationNote:
    "Las rutas simples son control operativo separado. No afectan cartera formal, inventario ni ventas oficiales.",
} as const;

export type SalesComparisonItem = {
  key: "official" | "routes";
  label: string;
  amount: number;
  percentage: number;
};

export function canShowAdminAnalytics(
  role: UserRole | null | undefined,
): boolean {
  return role === "admin_auditor";
}

export function getAnalyticsViewState({
  error,
  hasData,
  isLoading,
}: {
  error: string;
  hasData: boolean;
  isLoading: boolean;
}): AnalyticsViewState {
  if (isLoading) {
    return "loading";
  }
  if (error) {
    return "error";
  }
  return hasData ? "ready" : "empty";
}

export function getAnalyticsPreset(
  preset: AnalyticsPreset,
  today = new Date(),
): { start_date: string; end_date: string } {
  const end = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  let start = new Date(end);
  if (preset === "last7") {
    start.setDate(start.getDate() - 6);
  }
  if (preset === "month") {
    start = new Date(end.getFullYear(), end.getMonth(), 1);
  }
  return {
    start_date: toLocalISODate(start),
    end_date: toLocalISODate(end),
  };
}

export function getSalesComparison(
  officialSales: string,
  routeSales: string,
): SalesComparisonItem[] {
  const officialAmount = toNonNegativeNumber(officialSales);
  const routeAmount = toNonNegativeNumber(routeSales);
  const total = officialAmount + routeAmount;
  const percentage = (amount: number) =>
    total === 0 ? 0 : (amount / total) * 100;
  return [
    {
      key: "official",
      label: ADMIN_ANALYTICS_TEXT.officialSales,
      amount: officialAmount,
      percentage: percentage(officialAmount),
    },
    {
      key: "routes",
      label: ADMIN_ANALYTICS_TEXT.routeSales,
      amount: routeAmount,
      percentage: percentage(routeAmount),
    },
  ];
}

function toNonNegativeNumber(value: string): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

function toLocalISODate(value: Date): string {
  const localDate = new Date(
    value.getTime() - value.getTimezoneOffset() * 60_000,
  );
  return localDate.toISOString().slice(0, 10);
}

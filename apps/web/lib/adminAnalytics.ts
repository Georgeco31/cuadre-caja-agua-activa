import type { UserRole } from "@/types/auth";

export type AnalyticsPreset = "today" | "last7" | "month";
export type AnalyticsViewState = "loading" | "error" | "ready" | "empty";

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

function toLocalISODate(value: Date): string {
  const localDate = new Date(
    value.getTime() - value.getTimezoneOffset() * 60_000,
  );
  return localDate.toISOString().slice(0, 10);
}

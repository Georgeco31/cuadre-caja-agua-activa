import type { UserRole } from "@/types/auth";

const ADMIN_ONLY_DASHBOARD_PATHS = [
  "/dashboard/employees",
  "/dashboard/exports",
  "/dashboard/management",
  "/dashboard/monthly-summary",
  "/dashboard/payroll",
  "/dashboard/pricing",
  "/dashboard/production/material-consumption",
  "/dashboard/production/recipes",
  "/dashboard/reports",
  "/dashboard/users",
] as const;

export function canUseAdminActions(role: UserRole | null | undefined): boolean {
  return role === "admin_auditor";
}

export function canAccessDashboardPath(
  role: UserRole | null | undefined,
  pathname: string,
): boolean {
  if (role !== "operator") {
    return true;
  }

  return !ADMIN_ONLY_DASHBOARD_PATHS.some(
    (restrictedPath) =>
      pathname === restrictedPath || pathname.startsWith(`${restrictedPath}/`),
  );
}


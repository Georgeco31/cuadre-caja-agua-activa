"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";

import { AccessRestricted } from "@/components/AccessRestricted";
import { LoadingState } from "@/components/LoadingState";
import { canAccessDashboardPath } from "@/lib/frontendPermissions";
import { PAYROLL_PERMISSION_MESSAGE } from "@/lib/payrollWorkflow";
import { useCurrentRole } from "@/lib/useCurrentRole";

export default function DashboardLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  const pathname = usePathname();
  const { isResolved, role } = useCurrentRole();

  if (!isResolved) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-8">
        <div className="mx-auto w-full max-w-6xl">
          <LoadingState label="Validando acceso..." />
        </div>
      </main>
    );
  }

  if (!canAccessDashboardPath(role, pathname)) {
    return (
      <AccessRestricted
        message={
          pathname === "/dashboard/payroll" ||
          pathname.startsWith("/dashboard/payroll/")
            ? PAYROLL_PERMISSION_MESSAGE
            : undefined
        }
      />
    );
  }

  return children;
}

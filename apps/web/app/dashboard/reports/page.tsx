"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CashSummaryFilters } from "@/components/CashSummaryFilters";
import { CashSummaryReportCards } from "@/components/CashSummaryReportCards";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { DashboardShell } from "@/components/ui/DashboardShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { ResponsiveToolbar } from "@/components/ui/ResponsiveToolbar";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ApiError, getCashSummaryReport } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type {
  CashSummaryReport,
  CashSummaryReportFilters,
} from "@/types/report";

export default function ReportsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [filters, setFilters] = useState<CashSummaryReportFilters>({});
  const [report, setReport] = useState<CashSummaryReport | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadReport(storedToken, {});
  }, [router]);

  async function loadReport(
    activeToken: string,
    activeFilters: CashSummaryReportFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedReport = await getCashSummaryReport(
        activeToken,
        activeFilters,
      );
      setReport(loadedReport);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }

      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmitFilters() {
    if (!token) {
      return;
    }

    loadReport(token, filters);
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }

    const emptyFilters: CashSummaryReportFilters = {};
    setFilters(emptyFilters);
    loadReport(token, emptyFilters);
  }

  function redirectIfUnauthorized(possibleError: unknown): boolean {
    if (
      possibleError instanceof ApiError &&
      possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return true;
    }

    return false;
  }

  return (
    <DashboardShell
      activeHref="/dashboard/reports"
      dateLabel={formatTopbarDate(new Date())}
    >
      <div className="mx-auto flex w-full min-w-0 max-w-screen-2xl flex-col gap-7 px-4 py-7 sm:px-6 sm:py-9 xl:gap-9 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description="Consulta el acumulado de los cuadres registrados por período y estado, con la composición del efectivo, los gastos y el total final."
          eyebrow="Reportes y control"
          meta={
            <Link
              className="inline-flex min-h-10 items-center text-sm font-semibold text-water-700 hover:text-water-600"
              href="/dashboard"
            >
              ← Volver al dashboard
            </Link>
          }
          title="Resumen acumulado de caja"
        />

        <ResponsiveToolbar>
          <div className="flex items-start gap-3">
            <StatusBadge label="Solo lectura" tone="success" />
            <p className="max-w-3xl text-sm leading-6 text-slate-600">
              Este reporte resume los cuadres registrados. No representa ventas
              reales si el dinero de caja se arrastra entre días.
            </p>
          </div>
        </ResponsiveToolbar>

        <CashSummaryFilters
          filters={filters}
          disabled={isLoading}
          onChange={setFilters}
          onSubmit={handleSubmitFilters}
          onClear={handleClearFilters}
        />

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando reporte..." />
        ) : report ? (
          <CashSummaryReportCards report={report} />
        ) : null}
      </div>
    </DashboardShell>
  );
}

function formatTopbarDate(value: Date): string {
  return new Intl.DateTimeFormat("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(value);
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }

  return "No se pudo completar la solicitud.";
}

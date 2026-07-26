"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CashSummaryFilters } from "@/components/CashSummaryFilters";
import { CashSummaryReportCards } from "@/components/CashSummaryReportCards";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
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
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Resumen acumulado de caja
            </h1>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-water-100 bg-water-50 px-4 py-3 text-sm leading-6 text-water-800">
          Este reporte resume los cuadres registrados. No representa ventas
          reales si el dinero de caja se arrastra entre dias.
        </p>

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
    </main>
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }

  return "No se pudo completar la solicitud.";
}

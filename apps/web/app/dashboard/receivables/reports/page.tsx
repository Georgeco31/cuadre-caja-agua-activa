"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { ReceivablesCustomerList } from "@/components/ReceivablesCustomerList";
import { ReceivablesSummaryCards } from "@/components/ReceivablesSummaryCards";
import {
  ApiError,
  getReceivablesSummary,
  listReceivableCustomers,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type {
  ReceivableCustomer,
  ReceivablesSummary,
} from "@/types/receivable";

type ReportFilters = {
  search: string;
  onlyWithBalance: boolean;
  isActive: "" | "true" | "false";
  dateFrom: string;
  dateTo: string;
};

const initialFilters: ReportFilters = {
  search: "",
  onlyWithBalance: true,
  isActive: "",
  dateFrom: "",
  dateTo: "",
};

export default function ReceivablesReportsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [summary, setSummary] = useState<ReceivablesSummary | null>(null);
  const [customers, setCustomers] = useState<ReceivableCustomer[]>([]);
  const [filters, setFilters] = useState<ReportFilters>(initialFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<ReportFilters>(initialFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadInitialData(storedToken);
  }, [router]);

  async function loadInitialData(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const [loadedSummary, loadedCustomers] = await Promise.all([
        getReceivablesSummary(activeToken),
        listReceivableCustomers(activeToken, { only_with_balance: true }),
      ]);
      setSummary(loadedSummary);
      setCustomers(loadedCustomers);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadReport(
    activeToken: string,
    activeFilters: ReportFilters,
  ) {
    setIsFiltering(true);
    setError("");
    try {
      const dateFilters = {
        ...(activeFilters.dateFrom
          ? { date_from: activeFilters.dateFrom }
          : {}),
        ...(activeFilters.dateTo ? { date_to: activeFilters.dateTo } : {}),
      };
      const [loadedSummary, loadedCustomers] = await Promise.all([
        getReceivablesSummary(activeToken, dateFilters),
        listReceivableCustomers(activeToken, {
          ...dateFilters,
          only_with_balance: activeFilters.onlyWithBalance,
          ...(activeFilters.search ? { search: activeFilters.search } : {}),
          ...(activeFilters.isActive
            ? { is_active: activeFilters.isActive === "true" }
            : {}),
        }),
      ]);
      setSummary(loadedSummary);
      setCustomers(loadedCustomers);
      setAppliedFilters({ ...activeFilters });
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsFiltering(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (token) {
      loadReport(token, filters);
    }
  }

  function handleClear() {
    setFilters(initialFilters);
    if (token) {
      loadReport(token, initialFilters);
    }
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
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard/receivables"
            >
              Volver a cobros y abonos
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Cuentas por cobrar
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Consulta clientes con saldo pendiente, ventas a crédito y abonos
              registrados. Este reporte no modifica caja automáticamente.
            </p>
          </div>
          <LogoutButton />
        </header>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando cuentas por cobrar..." />
        ) : summary ? (
          <>
            <ReceivablesSummaryCards summary={summary} />

            <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 px-4 py-3">
                <h2 className="text-lg font-semibold text-slate-950">
                  Filtros de cartera
                </h2>
              </div>
              <form
                className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-6"
                onSubmit={handleSubmit}
              >
                <label className="block xl:col-span-2">
                  <span className="text-sm font-medium text-slate-700">
                    Buscar cliente
                  </span>
                  <input
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                    type="search"
                    placeholder="Nombre o teléfono"
                    value={filters.search}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        search: event.target.value,
                      }))
                    }
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Desde
                  </span>
                  <input
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                    type="date"
                    value={filters.dateFrom}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        dateFrom: event.target.value,
                      }))
                    }
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Hasta
                  </span>
                  <input
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                    type="date"
                    value={filters.dateTo}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        dateTo: event.target.value,
                      }))
                    }
                  />
                </label>

                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Estado del cliente
                  </span>
                  <select
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                    value={filters.isActive}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        isActive: event.target.value as ReportFilters["isActive"],
                      }))
                    }
                  >
                    <option value="">Todos</option>
                    <option value="true">Activos</option>
                    <option value="false">Inactivos</option>
                  </select>
                </label>

                <label className="flex h-10 items-center gap-2 self-end text-sm font-medium text-slate-700">
                  <input
                    className="h-4 w-4 rounded border-slate-300 text-water-700 focus:ring-water-500"
                    type="checkbox"
                    checked={filters.onlyWithBalance}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        onlyWithBalance: event.target.checked,
                      }))
                    }
                  />
                  Solo con saldo
                </label>

                <div className="flex flex-col gap-2 md:flex-row xl:col-span-6 xl:justify-end">
                  <button
                    className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
                    type="submit"
                    disabled={isFiltering}
                  >
                    {isFiltering ? "Consultando..." : "Consultar"}
                  </button>
                  <button
                    className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:text-slate-400"
                    type="button"
                    disabled={isFiltering}
                    onClick={handleClear}
                  >
                    Limpiar
                  </button>
                </div>
              </form>
            </section>

            <ReceivablesCustomerList
              customers={customers}
              hasActiveFilters={hasActiveFilters(appliedFilters)}
              isLoading={isFiltering}
            />
          </>
        ) : null}
      </div>
    </main>
  );
}

function hasActiveFilters(filters: ReportFilters): boolean {
  return Boolean(
    filters.search ||
      filters.dateFrom ||
      filters.dateTo ||
      filters.isActive ||
      !filters.onlyWithBalance,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

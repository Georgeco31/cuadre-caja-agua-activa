"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { CustomerStatementView } from "@/components/CustomerStatementView";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { ApiError, getCustomerStatement } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { CustomerStatement } from "@/types/receivable";

type StatementFilters = {
  dateFrom: string;
  dateTo: string;
  includePaid: boolean;
};

const initialFilters: StatementFilters = {
  dateFrom: "",
  dateTo: "",
  includePaid: false,
};

export default function CustomerStatementPage() {
  const params = useParams<{ customerId: string }>();
  const router = useRouter();
  const customerId = Number(params.customerId);
  const [token, setToken] = useState<string | null>(null);
  const [statement, setStatement] = useState<CustomerStatement | null>(null);
  const [filters, setFilters] = useState<StatementFilters>(initialFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<StatementFilters>(initialFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);

    if (!Number.isInteger(customerId) || customerId <= 0) {
      setError("El cliente solicitado no es válido.");
      setIsLoading(false);
      return;
    }
    loadStatement(storedToken, initialFilters);
  }, [customerId, router]);

  async function loadStatement(
    activeToken: string,
    activeFilters: StatementFilters,
  ) {
    setIsLoading(true);
    setError("");
    try {
      const loadedStatement = await getCustomerStatement(
        activeToken,
        customerId,
        {
          ...(activeFilters.dateFrom
            ? { date_from: activeFilters.dateFrom }
            : {}),
          ...(activeFilters.dateTo ? { date_to: activeFilters.dateTo } : {}),
          include_paid: activeFilters.includePaid,
        },
      );
      setStatement(loadedStatement);
      setAppliedFilters({ ...activeFilters });
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (token) {
      loadStatement(token, filters);
    }
  }

  function handleClear() {
    setFilters(initialFilters);
    if (token) {
      loadStatement(token, initialFilters);
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
              href="/dashboard/receivables/reports"
            >
              Volver a cuentas por cobrar
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Estado de cuenta
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Consulta ventas a crédito y abonos del cliente. Esta pantalla es
              informativa y no registra movimientos.
            </p>
          </div>
          <LogoutButton />
        </header>

        {error ? <ErrorMessage message={error} /> : null}

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-4 py-3">
            <h2 className="text-lg font-semibold text-slate-950">
              Periodo y contenido
            </h2>
          </div>
          <form
            className="grid gap-4 p-4 md:grid-cols-2 lg:grid-cols-4"
            onSubmit={handleSubmit}
          >
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Desde</span>
              <input
                className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                type="date"
                value={filters.dateFrom}
                disabled={isLoading}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    dateFrom: event.target.value,
                  }))
                }
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Hasta</span>
              <input
                className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                type="date"
                value={filters.dateTo}
                disabled={isLoading}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    dateTo: event.target.value,
                  }))
                }
              />
            </label>
            <label className="flex h-10 items-center gap-2 self-end text-sm font-medium text-slate-700">
              <input
                className="h-4 w-4 rounded border-slate-300 text-water-700 focus:ring-water-500"
                type="checkbox"
                checked={filters.includePaid}
                disabled={isLoading}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    includePaid: event.target.checked,
                  }))
                }
              />
              Incluir ventas pagadas
            </label>
            <div className="flex flex-col gap-2 self-end sm:flex-row">
              <button
                className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:bg-slate-300"
                type="submit"
                disabled={isLoading}
              >
                Consultar
              </button>
              <button
                className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:text-slate-400"
                type="button"
                disabled={isLoading}
                onClick={handleClear}
              >
                Limpiar
              </button>
            </div>
          </form>
        </section>

        {isLoading ? (
          <LoadingState label="Cargando estado de cuenta..." />
        ) : statement ? (
          <CustomerStatementView
            statement={statement}
            includePaid={appliedFilters.includePaid}
          />
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

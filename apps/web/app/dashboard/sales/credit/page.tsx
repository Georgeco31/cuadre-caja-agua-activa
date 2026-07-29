"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CreditSaleForm } from "@/components/CreditSaleForm";
import { CreditSaleList } from "@/components/CreditSaleList";
import type { CashSaleFilterValues } from "@/components/CashSaleList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { SaleDateCorrectionModal } from "@/components/SaleDateCorrectionModal";
import {
  ApiError,
  correctSaleDate,
  createCreditSale,
  listCashSales,
  listCustomers,
  listProducts,
  listRouteLoads,
  voidCashSale,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { getSaleDateCorrectionErrorMessage } from "@/lib/saleDateCorrection";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { Customer } from "@/types/customer";
import type { Product } from "@/types/product";
import type { RouteLoad } from "@/types/routeLoad";
import type {
  CashSale,
  CreditSalePayload,
  SaleDateCorrectionPayload,
} from "@/types/sale";

const emptyFilters: CashSaleFilterValues = {
  search: "",
  dateFrom: "",
  dateTo: "",
  status: "",
  customerId: "",
  paymentMethod: "",
};

export default function CreditSalesPage() {
  const canUseAdminSaleActions = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [routeLoads, setRouteLoads] = useState<RouteLoad[]>([]);
  const [sales, setSales] = useState<CashSale[]>([]);
  const [filters, setFilters] = useState<CashSaleFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<CashSaleFilterValues>(emptyFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingSales, setIsLoadingSales] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [voidingSaleId, setVoidingSaleId] = useState<number | null>(null);
  const [saleToCorrect, setSaleToCorrect] = useState<CashSale | null>(null);
  const [isCorrectingDate, setIsCorrectingDate] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

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
      const [loadedCustomers, loadedProducts, loadedRouteLoads, loadedSales] =
        await Promise.all([
        listCustomers(activeToken, { is_active: true }),
        listProducts(activeToken, { is_active: true }),
        listRouteLoads(activeToken, { status: "active" }),
        listCashSales(activeToken, { sale_type: "credit" }),
      ]);
      setCustomers(loadedCustomers);
      setProducts(loadedProducts);
      setRouteLoads(loadedRouteLoads);
      setSales(loadedSales);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadSales(
    activeToken: string,
    activeFilters: CashSaleFilterValues,
  ) {
    setIsLoadingSales(true);
    setError("");
    try {
      const loadedSales = await listCashSales(activeToken, {
        sale_type: "credit",
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.dateFrom ? { date_from: activeFilters.dateFrom } : {}),
        ...(activeFilters.dateTo ? { date_to: activeFilters.dateTo } : {}),
        ...(activeFilters.status ? { status: activeFilters.status } : {}),
        ...(activeFilters.customerId
          ? { customer_id: Number(activeFilters.customerId) }
          : {}),
      });
      setSales(loadedSales);
      setAppliedFilters({ ...activeFilters });
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoadingSales(false);
    }
  }

  async function handleCreateSale(payload: CreditSalePayload): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");
    try {
      const savedSale = await createCreditSale(token, payload);
      setMessage(
        `Venta ${savedSale.sale_number} registrada. Total oficial: ${formatMoney(savedSale.total_amount)}. Saldo pendiente: ${formatMoney(savedSale.balance_amount)}.`,
      );
      await loadSales(token, appliedFilters);
      return true;
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return false;
      }
      setError(getErrorMessage(saveError));
      return false;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleVoidSale(sale: CashSale) {
    if (!token) {
      return;
    }
    const reason = window.prompt(
      `Motivo para anular la venta ${sale.sale_number}:`,
    );
    if (reason === null) {
      return;
    }
    const normalizedReason = reason.trim();
    if (!normalizedReason) {
      setError("El motivo de anulación es obligatorio.");
      return;
    }

    setVoidingSaleId(sale.id);
    setError("");
    setMessage("");
    try {
      const voidedSale = await voidCashSale(token, sale.id, normalizedReason);
      setMessage(`Venta ${voidedSale.sale_number} anulada.`);
      await loadSales(token, appliedFilters);
    } catch (voidError) {
      if (redirectIfUnauthorized(voidError)) {
        return;
      }
      setError(getSaleVoidErrorMessage(voidError));
    } finally {
      setVoidingSaleId(null);
    }
  }

  async function handleCorrectSaleDate(
    payload: SaleDateCorrectionPayload,
  ): Promise<boolean> {
    if (!token || !saleToCorrect) {
      return false;
    }

    setIsCorrectingDate(true);
    setError("");
    setMessage("");
    try {
      const correction = await correctSaleDate(
        token,
        saleToCorrect.id,
        payload,
      );
      setMessage(
        `Fecha de venta corregida correctamente. ${correction.sale.sale_number}: ${formatDate(correction.previous_sale_date)} → ${formatDate(correction.new_sale_date)}.`,
      );
      setSaleToCorrect(null);
      await loadSales(token, appliedFilters);
      return true;
    } catch (correctionError) {
      if (redirectIfUnauthorized(correctionError)) {
        return false;
      }
      setError(getSaleDateCorrectionErrorMessage(correctionError));
      return false;
    } finally {
      setIsCorrectingDate(false);
    }
  }

  function handleFilter() {
    if (token) {
      loadSales(token, filters);
    }
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    loadSales(token, emptyFilters);
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
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Ventas a crédito
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra ventas pendientes de cobro. Este módulo crea la deuda del
              cliente; sus pagos se administran desde Cobros y abonos.
            </p>
          </div>
          <LogoutButton />
        </header>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando ventas a crédito..." />
        ) : (
          <>
            <CreditSaleForm
              token={token!}
              customers={customers}
              products={products}
              routeLoads={routeLoads}
              isSubmitting={isSaving}
              onSubmit={handleCreateSale}
            />
            <CreditSaleList
              canVoid={canUseAdminSaleActions}
              canCorrectDate={canUseAdminSaleActions}
              sales={sales}
              customers={customers}
              filters={filters}
              hasActiveFilters={hasActiveFilters(appliedFilters)}
              isLoading={isLoadingSales}
              voidingSaleId={voidingSaleId}
              onFiltersChange={setFilters}
              onFilter={handleFilter}
              onClearFilters={handleClearFilters}
              onVoid={handleVoidSale}
              onCorrectDate={setSaleToCorrect}
            />
          </>
        )}
      </div>
      {saleToCorrect ? (
        <SaleDateCorrectionModal
          sale={saleToCorrect}
          isSubmitting={isCorrectingDate}
          onCancel={() => setSaleToCorrect(null)}
          onSubmit={handleCorrectSaleDate}
        />
      ) : null}
    </main>
  );
}

function hasActiveFilters(filters: CashSaleFilterValues): boolean {
  return Boolean(
    filters.search ||
      filters.dateFrom ||
      filters.dateTo ||
      filters.status ||
      filters.customerId,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

function getSaleVoidErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof ApiError && possibleError.status === 403) {
    return "No tienes permiso para anular ventas. Solicita autorización a George.";
  }
  return getErrorMessage(possibleError);
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return `${day}/${month}/${year}`;
}

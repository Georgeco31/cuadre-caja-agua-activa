"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { ProductionForm } from "@/components/ProductionForm";
import {
  ProductionList,
  type ProductionFilterValues,
} from "@/components/ProductionList";
import {
  ApiError,
  applyProductionToInventory,
  createProductionBatch,
  getProductionInventoryApplication,
  listInventoryLocations,
  listProductionBatches,
  listProducts,
  voidProductionBatch,
  voidProductionInventoryApplication,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { InventoryLocation } from "@/types/inventory";
import type { Product } from "@/types/product";
import type {
  ProductionBatch,
  ProductionBatchFilters,
  ProductionBatchPayload,
  ProductionInventoryApplication,
  ProductionInventoryApplyPayload,
} from "@/types/production";

const emptyFilters: ProductionFilterValues = {
  search: "",
  dateFrom: "",
  dateTo: "",
  status: "",
  productId: "",
};

export default function ProductionPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [locations, setLocations] = useState<InventoryLocation[]>([]);
  const [batches, setBatches] = useState<ProductionBatch[]>([]);
  const [inventoryApplications, setInventoryApplications] = useState<
    Record<number, ProductionInventoryApplication | undefined>
  >({});
  const [filters, setFilters] =
    useState<ProductionFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<ProductionFilterValues>(emptyFilters);
  const [voidingBatch, setVoidingBatch] = useState<ProductionBatch | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidValidationError, setVoidValidationError] = useState("");
  const [voidingInventory, setVoidingInventory] = useState<{
    batch: ProductionBatch;
    application: ProductionInventoryApplication;
  } | null>(null);
  const [inventoryVoidReason, setInventoryVoidReason] = useState("");
  const [inventoryVoidError, setInventoryVoidError] = useState("");
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isVoiding, setIsVoiding] = useState(false);
  const [applyingBatchId, setApplyingBatchId] = useState<number | null>(null);
  const [isVoidingInventory, setIsVoidingInventory] = useState(false);
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
    setIsInitialLoading(true);
    setError("");
    try {
      const [loadedProducts, loadedLocations, loadedBatches] = await Promise.all([
        listProducts(activeToken, { is_active: true }),
        listInventoryLocations(activeToken, { is_active: true }),
        listProductionBatches(activeToken),
      ]);
      const loadedApplications = await loadInventoryApplications(
        activeToken,
        loadedBatches,
      );
      setProducts(loadedProducts);
      setLocations(loadedLocations);
      setBatches(loadedBatches);
      setInventoryApplications(loadedApplications);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsInitialLoading(false);
    }
  }

  async function loadBatches(
    activeToken: string,
    activeFilters: ProductionFilterValues,
  ) {
    setIsFiltering(true);
    setError("");
    try {
      const loadedBatches = await listProductionBatches(
        activeToken,
        toApiFilters(activeFilters),
      );
      const loadedApplications = await loadInventoryApplications(
        activeToken,
        loadedBatches,
      );
      setBatches(loadedBatches);
      setInventoryApplications(loadedApplications);
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

  async function handleCreateProduction(
    payload: ProductionBatchPayload,
  ): Promise<boolean> {
    if (!token) {
      return false;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const savedBatch = await createProductionBatch(token, payload);
      setMessage(`Producción ${savedBatch.production_number} registrada.`);
      await loadBatches(token, appliedFilters);
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

  function handleOpenVoid(batch: ProductionBatch) {
    setVoidingBatch(batch);
    setVoidReason("");
    setVoidValidationError("");
    clearNotices();
  }

  async function handleApplyInventory(
    batch: ProductionBatch,
    payload: ProductionInventoryApplyPayload,
  ): Promise<boolean> {
    if (!token) {
      return false;
    }
    setApplyingBatchId(batch.id);
    clearNotices();
    try {
      const application = await applyProductionToInventory(
        token,
        batch.id,
        payload,
      );
      setMessage(
        `Producción ${batch.production_number} aplicada a ${application.location_name}.`,
      );
      await loadBatches(token, appliedFilters);
      return true;
    } catch (applyError) {
      if (redirectIfUnauthorized(applyError)) {
        return false;
      }
      setError(getErrorMessage(applyError));
      return false;
    } finally {
      setApplyingBatchId(null);
    }
  }

  function handleOpenInventoryVoid(
    batch: ProductionBatch,
    application: ProductionInventoryApplication,
  ) {
    setVoidingInventory({ batch, application });
    setInventoryVoidReason("");
    setInventoryVoidError("");
    clearNotices();
  }

  async function handleVoidInventoryApplication(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    if (!token || !voidingInventory?.application.application_id) {
      return;
    }
    const reason = inventoryVoidReason.trim();
    if (!reason) {
      setInventoryVoidError("El motivo de anulación es obligatorio.");
      return;
    }
    setIsVoidingInventory(true);
    setInventoryVoidError("");
    try {
      await voidProductionInventoryApplication(
        token,
        voidingInventory.application.application_id,
        reason,
      );
      setMessage(
        `Aplicación de ${voidingInventory.batch.production_number} anulada.`,
      );
      setVoidingInventory(null);
      setInventoryVoidReason("");
      await loadBatches(token, appliedFilters);
    } catch (voidError) {
      if (redirectIfUnauthorized(voidError)) {
        return;
      }
      setInventoryVoidError(getErrorMessage(voidError));
    } finally {
      setIsVoidingInventory(false);
    }
  }

  async function handleVoidProduction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !voidingBatch) {
      return;
    }
    const reason = voidReason.trim();
    if (!reason) {
      setVoidValidationError("El motivo de anulación es obligatorio.");
      return;
    }
    setIsVoiding(true);
    setVoidValidationError("");
    try {
      const voidedBatch = await voidProductionBatch(
        token,
        voidingBatch.id,
        reason,
      );
      setMessage(`Producción ${voidedBatch.production_number} anulada.`);
      setVoidingBatch(null);
      setVoidReason("");
      await loadBatches(token, appliedFilters);
    } catch (voidError) {
      if (redirectIfUnauthorized(voidError)) {
        return;
      }
      setVoidValidationError(getErrorMessage(voidError));
    } finally {
      setIsVoiding(false);
    }
  }

  function clearNotices() {
    setError("");
    setMessage("");
  }

  function redirectIfUnauthorized(possibleError: unknown): boolean {
    if (
      possibleError instanceof ApiError &&
      (possibleError.status === 401 || possibleError.status === 403)
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
              Producción
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra la producción y el envasado diario por producto, con las
              cantidades producidas y la merma reportada.
            </p>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          La producción no aumenta inventario automáticamente hasta que se
          aplique a una ubicación. Tampoco consume materia prima
          automáticamente.{" "}
          <Link
            className="font-semibold underline hover:text-amber-700"
            href="/dashboard/production/material-consumption"
          >
            Ir a consumo de insumos
          </Link>
          .
        </p>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isInitialLoading ? (
          <LoadingState label="Cargando producción..." />
        ) : (
          <>
            <ProductionForm
              products={products}
              isSubmitting={isSaving}
              onSubmit={handleCreateProduction}
            />
            <ProductionList
              batches={batches}
              products={products}
              locations={locations}
              inventoryApplications={inventoryApplications}
              filters={filters}
              isLoading={isFiltering}
              voidingBatchId={isVoiding ? voidingBatch?.id : null}
              applyingBatchId={applyingBatchId}
              voidingApplicationId={
                isVoidingInventory
                  ? voidingInventory?.application.application_id
                  : null
              }
              onFiltersChange={setFilters}
              onFilter={() => token && loadBatches(token, filters)}
              onClear={() => {
                setFilters(emptyFilters);
                if (token) {
                  loadBatches(token, emptyFilters);
                }
              }}
              onVoid={handleOpenVoid}
              onApplyInventory={handleApplyInventory}
              onVoidInventoryApplication={handleOpenInventoryVoid}
            />
          </>
        )}
      </div>

      {voidingBatch ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="void-production-title"
        >
          <form
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl"
            onSubmit={handleVoidProduction}
          >
            <div className="border-b border-slate-200 px-5 py-4">
              <h2
                className="text-lg font-semibold text-slate-950"
                id="void-production-title"
              >
                Anular producción
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {voidingBatch.production_number}
              </p>
            </div>
            <div className="space-y-4 p-5">
              {voidValidationError ? (
                <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {voidValidationError}
                </p>
              ) : null}
              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Motivo de anulación
                </span>
                <textarea
                  className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                  value={voidReason}
                  required
                  disabled={isVoiding}
                  onChange={(event) => setVoidReason(event.target.value)}
                />
              </label>
              <p className="text-sm text-slate-600">
                El registro y sus productos se conservarán como anulados. El
                inventario no cambiará.
              </p>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
                  type="button"
                  disabled={isVoiding}
                  onClick={() => setVoidingBatch(null)}
                >
                  Cancelar
                </button>
                <button
                  className="h-10 rounded-md bg-red-700 px-4 text-sm font-semibold text-white hover:bg-red-600 disabled:bg-slate-300"
                  type="submit"
                  disabled={isVoiding}
                >
                  {isVoiding ? "Anulando..." : "Confirmar anulación"}
                </button>
              </div>
            </div>
          </form>
        </div>
      ) : null}

      {voidingInventory ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="void-production-inventory-title"
        >
          <form
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl"
            onSubmit={handleVoidInventoryApplication}
          >
            <div className="border-b border-slate-200 px-5 py-4">
              <h2
                className="text-lg font-semibold text-slate-950"
                id="void-production-inventory-title"
              >
                Anular aplicación a inventario
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {voidingInventory.batch.production_number} · {" "}
                {voidingInventory.application.location_name}
              </p>
            </div>
            <div className="space-y-4 p-5">
              {inventoryVoidError ? (
                <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {inventoryVoidError}
                </p>
              ) : null}
              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Motivo de anulación
                </span>
                <textarea
                  className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                  value={inventoryVoidReason}
                  required
                  disabled={isVoidingInventory}
                  onChange={(event) =>
                    setInventoryVoidReason(event.target.value)
                  }
                />
              </label>
              <p className="text-sm text-slate-600">
                Los movimientos se conservarán anulados y el stock se revertirá.
                La operación fallará si el stock actual resultaría negativo.
              </p>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
                  type="button"
                  disabled={isVoidingInventory}
                  onClick={() => setVoidingInventory(null)}
                >
                  Cancelar
                </button>
                <button
                  className="h-10 rounded-md bg-red-700 px-4 text-sm font-semibold text-white hover:bg-red-600 disabled:bg-slate-300"
                  type="submit"
                  disabled={isVoidingInventory}
                >
                  {isVoidingInventory
                    ? "Anulando..."
                    : "Confirmar anulación"}
                </button>
              </div>
            </div>
          </form>
        </div>
      ) : null}
    </main>
  );
}

async function loadInventoryApplications(
  token: string,
  batches: ProductionBatch[],
): Promise<Record<number, ProductionInventoryApplication>> {
  const applications = await Promise.all(
    batches.map((batch) =>
      getProductionInventoryApplication(token, batch.id),
    ),
  );
  return Object.fromEntries(
    applications.map((application) => [
      application.production_batch_id,
      application,
    ]),
  );
}

function toApiFilters(
  filters: ProductionFilterValues,
): ProductionBatchFilters {
  return {
    ...(filters.search ? { search: filters.search } : {}),
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.productId
      ? { product_id: Number(filters.productId) }
      : {}),
  };
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

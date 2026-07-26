"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { InventoryLocationForm } from "@/components/InventoryLocationForm";
import { InventoryLocationList } from "@/components/InventoryLocationList";
import { InventoryMovementForm } from "@/components/InventoryMovementForm";
import {
  InventoryMovementList,
  type InventoryMovementFilterValues,
} from "@/components/InventoryMovementList";
import {
  InventoryStockTable,
  type InventoryStockFilterValues,
} from "@/components/InventoryStockTable";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  activateInventoryLocation,
  ApiError,
  createInventoryLocation,
  createInventoryMovement,
  deactivateInventoryLocation,
  listInventoryLocations,
  listInventoryMovements,
  listInventoryStocks,
  listProducts,
  listVehicles,
  updateInventoryLocation,
  voidInventoryMovement,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type {
  InventoryLocation,
  InventoryLocationPayload,
  InventoryMovement,
  InventoryMovementFilters,
  InventoryMovementPayload,
  InventoryStock,
  InventoryStockFilters,
} from "@/types/inventory";
import type { Product } from "@/types/product";
import type { Vehicle } from "@/types/vehicle";

const emptyStockFilters: InventoryStockFilterValues = {
  productId: "",
  locationId: "",
  onlyPositive: false,
};

const emptyMovementFilters: InventoryMovementFilterValues = {
  dateFrom: "",
  dateTo: "",
  productId: "",
  locationId: "",
  movementType: "",
  status: "",
};

export default function InventoryPage() {
  const canManageCriticalActions = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [locations, setLocations] = useState<InventoryLocation[]>([]);
  const [stocks, setStocks] = useState<InventoryStock[]>([]);
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [stockFilters, setStockFilters] =
    useState<InventoryStockFilterValues>(emptyStockFilters);
  const [appliedStockFilters, setAppliedStockFilters] =
    useState<InventoryStockFilterValues>(emptyStockFilters);
  const [movementFilters, setMovementFilters] =
    useState<InventoryMovementFilterValues>(emptyMovementFilters);
  const [appliedMovementFilters, setAppliedMovementFilters] =
    useState<InventoryMovementFilterValues>(emptyMovementFilters);
  const [editingLocation, setEditingLocation] =
    useState<InventoryLocation | null>(null);
  const [isLocationFormVisible, setIsLocationFormVisible] = useState(false);
  const [voidingMovement, setVoidingMovement] =
    useState<InventoryMovement | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidValidationError, setVoidValidationError] = useState("");
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isFilteringStocks, setIsFilteringStocks] = useState(false);
  const [isFilteringMovements, setIsFilteringMovements] = useState(false);
  const [isSavingLocation, setIsSavingLocation] = useState(false);
  const [changingLocationId, setChangingLocationId] = useState<number | null>(
    null,
  );
  const [isSavingMovement, setIsSavingMovement] = useState(false);
  const [isVoidingMovement, setIsVoidingMovement] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const activeProducts = useMemo(
    () => products.filter((product) => product.is_active),
    [products],
  );
  const activeLocations = useMemo(
    () => locations.filter((location) => location.is_active),
    [locations],
  );

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
      const [
        loadedLocations,
        loadedStocks,
        loadedMovements,
        loadedProducts,
        loadedVehicles,
      ] = await Promise.all([
        listInventoryLocations(activeToken),
        listInventoryStocks(activeToken),
        listInventoryMovements(activeToken),
        listProducts(activeToken),
        listVehicles(activeToken, { is_active: true }),
      ]);
      setLocations(loadedLocations);
      setStocks(loadedStocks);
      setMovements(loadedMovements);
      setProducts(loadedProducts);
      setVehicles(loadedVehicles);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsInitialLoading(false);
    }
  }

  async function loadStocks(
    activeToken: string,
    activeFilters: InventoryStockFilterValues,
  ) {
    setIsFilteringStocks(true);
    setError("");
    try {
      const loadedStocks = await listInventoryStocks(
        activeToken,
        toStockApiFilters(activeFilters),
      );
      setStocks(loadedStocks);
      setAppliedStockFilters({ ...activeFilters });
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsFilteringStocks(false);
    }
  }

  async function loadMovements(
    activeToken: string,
    activeFilters: InventoryMovementFilterValues,
  ) {
    setIsFilteringMovements(true);
    setError("");
    try {
      const loadedMovements = await listInventoryMovements(
        activeToken,
        toMovementApiFilters(activeFilters),
      );
      setMovements(loadedMovements);
      setAppliedMovementFilters({ ...activeFilters });
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsFilteringMovements(false);
    }
  }

  async function refreshInventoryData(activeToken: string) {
    const [loadedLocations, loadedStocks, loadedMovements] = await Promise.all([
      listInventoryLocations(activeToken),
      listInventoryStocks(activeToken, toStockApiFilters(appliedStockFilters)),
      listInventoryMovements(
        activeToken,
        toMovementApiFilters(appliedMovementFilters),
      ),
    ]);
    setLocations(loadedLocations);
    setStocks(loadedStocks);
    setMovements(loadedMovements);
  }

  function handleShowLocationForm() {
    setEditingLocation(null);
    setIsLocationFormVisible(true);
    clearNotices();
  }

  function handleEditLocation(location: InventoryLocation) {
    setEditingLocation(location);
    setIsLocationFormVisible(true);
    clearNotices();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelLocationForm() {
    setEditingLocation(null);
    setIsLocationFormVisible(false);
  }

  async function handleSaveLocation(
    payload: InventoryLocationPayload,
  ): Promise<boolean> {
    if (!token) {
      return false;
    }
    setIsSavingLocation(true);
    clearNotices();
    try {
      const savedLocation = editingLocation
        ? await updateInventoryLocation(token, editingLocation.id, payload)
        : await createInventoryLocation(token, payload);
      setMessage(
        editingLocation
          ? `Ubicación actualizada: ${savedLocation.name}.`
          : `Ubicación creada: ${savedLocation.name}.`,
      );
      setEditingLocation(null);
      setIsLocationFormVisible(false);
      await refreshInventoryData(token);
      return true;
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return false;
      }
      setError(getErrorMessage(saveError));
      return false;
    } finally {
      setIsSavingLocation(false);
    }
  }

  async function handleToggleLocation(location: InventoryLocation) {
    if (!token) {
      return;
    }
    if (
      location.is_active &&
      !window.confirm(`¿Inactivar la ubicación ${location.name}?`)
    ) {
      return;
    }
    setChangingLocationId(location.id);
    clearNotices();
    try {
      const updatedLocation = location.is_active
        ? await deactivateInventoryLocation(token, location.id)
        : await activateInventoryLocation(token, location.id);
      setMessage(
        updatedLocation.is_active
          ? `Ubicación reactivada: ${updatedLocation.name}.`
          : `Ubicación inactivada: ${updatedLocation.name}.`,
      );
      await refreshInventoryData(token);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingLocationId(null);
    }
  }

  async function handleCreateMovement(
    payload: InventoryMovementPayload,
  ): Promise<boolean> {
    if (!token) {
      return false;
    }
    setIsSavingMovement(true);
    clearNotices();
    try {
      const movement = await createInventoryMovement(token, payload);
      setMessage(
        `Movimiento registrado: ${movement.product_name_snapshot} en ${movement.location_name}.`,
      );
      await refreshInventoryData(token);
      return true;
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return false;
      }
      setError(getErrorMessage(saveError));
      return false;
    } finally {
      setIsSavingMovement(false);
    }
  }

  function handleOpenVoid(movement: InventoryMovement) {
    setVoidingMovement(movement);
    setVoidReason("");
    setVoidValidationError("");
    clearNotices();
  }

  async function handleVoidMovement(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !voidingMovement) {
      return;
    }
    const reason = voidReason.trim();
    if (!reason) {
      setVoidValidationError("El motivo de anulación es obligatorio.");
      return;
    }
    setIsVoidingMovement(true);
    setVoidValidationError("");
    try {
      await voidInventoryMovement(token, voidingMovement.id, reason);
      setMessage("Movimiento anulado y stock actualizado.");
      setVoidingMovement(null);
      setVoidReason("");
      await refreshInventoryData(token);
    } catch (voidError) {
      if (redirectIfUnauthorized(voidError)) {
        return;
      }
      setVoidValidationError(getErrorMessage(voidError));
    } finally {
      setIsVoidingMovement(false);
    }
  }

  function clearNotices() {
    setError("");
    setMessage("");
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
              Inventario
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Controla el stock de productos por ubicación mediante entradas,
              salidas y ajustes manuales. Este módulo todavía no descuenta
              inventario automáticamente por ventas.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:bg-slate-300"
              type="button"
              disabled={isSavingLocation}
              onClick={handleShowLocationForm}
            >
              Nueva ubicación
            </button>
            <LogoutButton />
          </div>
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Las ventas, la caja, los cobros, las rutas y la producción no modifican
          este inventario automáticamente.
        </p>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isInitialLoading ? (
          <LoadingState label="Cargando inventario..." />
        ) : (
          <>
            <InventoryStockTable
              stocks={stocks}
              products={products}
              locations={locations}
              filters={stockFilters}
              isLoading={isFilteringStocks}
              onFiltersChange={setStockFilters}
              onFilter={() => token && loadStocks(token, stockFilters)}
              onClear={() => {
                setStockFilters(emptyStockFilters);
                if (token) {
                  loadStocks(token, emptyStockFilters);
                }
              }}
            />

            <div
              className={
                isLocationFormVisible
                  ? "grid gap-6 xl:grid-cols-[minmax(360px,0.8fr)_minmax(0,1.2fr)]"
                  : "grid gap-6"
              }
            >
              {isLocationFormVisible ? (
                <InventoryLocationForm
                  key={editingLocation?.id ?? "new"}
                  location={editingLocation}
                  vehicles={vehicles}
                  isSubmitting={isSavingLocation}
                  onSubmit={handleSaveLocation}
                  onCancel={handleCancelLocationForm}
                />
              ) : null}
              <InventoryLocationList
                locations={locations}
                vehicles={vehicles}
                changingLocationId={changingLocationId}
                onEdit={handleEditLocation}
                onToggleActive={handleToggleLocation}
              />
            </div>

            <InventoryMovementForm
              canAdjust={canManageCriticalActions}
              products={activeProducts}
              locations={activeLocations}
              isSubmitting={isSavingMovement}
              onSubmit={handleCreateMovement}
            />

            <InventoryMovementList
              canVoid={canManageCriticalActions}
              movements={movements}
              products={products}
              locations={locations}
              filters={movementFilters}
              isLoading={isFilteringMovements}
              onFiltersChange={setMovementFilters}
              onFilter={() => token && loadMovements(token, movementFilters)}
              onClear={() => {
                setMovementFilters(emptyMovementFilters);
                if (token) {
                  loadMovements(token, emptyMovementFilters);
                }
              }}
              onVoid={handleOpenVoid}
            />
          </>
        )}
      </div>

      {canManageCriticalActions && voidingMovement ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="void-inventory-title"
        >
          <form
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl"
            onSubmit={handleVoidMovement}
          >
            <div className="border-b border-slate-200 px-5 py-4">
              <h2
                className="text-lg font-semibold text-slate-950"
                id="void-inventory-title"
              >
                Anular movimiento
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {voidingMovement.product_name_snapshot} · {voidingMovement.location_name}
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
                  disabled={isVoidingMovement}
                  onChange={(event) => setVoidReason(event.target.value)}
                />
              </label>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
                  type="button"
                  disabled={isVoidingMovement}
                  onClick={() => setVoidingMovement(null)}
                >
                  Cancelar
                </button>
                <button
                  className="h-10 rounded-md bg-red-700 px-4 text-sm font-semibold text-white hover:bg-red-600 disabled:bg-slate-300"
                  type="submit"
                  disabled={isVoidingMovement}
                >
                  {isVoidingMovement ? "Anulando..." : "Confirmar anulación"}
                </button>
              </div>
            </div>
          </form>
        </div>
      ) : null}
    </main>
  );
}

function toStockApiFilters(
  filters: InventoryStockFilterValues,
): InventoryStockFilters {
  return {
    ...(filters.productId ? { product_id: Number(filters.productId) } : {}),
    ...(filters.locationId ? { location_id: Number(filters.locationId) } : {}),
    only_positive: filters.onlyPositive,
  };
}

function toMovementApiFilters(
  filters: InventoryMovementFilterValues,
): InventoryMovementFilters {
  return {
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.productId ? { product_id: Number(filters.productId) } : {}),
    ...(filters.locationId ? { location_id: Number(filters.locationId) } : {}),
    ...(filters.movementType ? { movement_type: filters.movementType } : {}),
    ...(filters.status ? { status: filters.status } : {}),
  };
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

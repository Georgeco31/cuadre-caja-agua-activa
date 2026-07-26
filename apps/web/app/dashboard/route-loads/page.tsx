"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { RouteLoadForm } from "@/components/RouteLoadForm";
import {
  RouteLoadList,
  type RouteLoadFilterValues,
} from "@/components/RouteLoadList";
import {
  ApiError,
  createRouteLoad,
  listDeliveryRoutes,
  listInventoryLocations,
  listInventoryStocks,
  listProducts,
  listRouteLoads,
  listVehicles,
  voidRouteLoad,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { DeliveryRoute } from "@/types/deliveryRoute";
import type {
  InventoryLocation,
  InventoryStock,
} from "@/types/inventory";
import type { Product } from "@/types/product";
import type {
  RouteLoad,
  RouteLoadFilters,
  RouteLoadPayload,
} from "@/types/routeLoad";
import type { Vehicle } from "@/types/vehicle";

const emptyFilters: RouteLoadFilterValues = {
  search: "",
  dateFrom: "",
  dateTo: "",
  status: "",
  routeId: "",
  vehicleId: "",
};

export default function RouteLoadsPage() {
  const canVoid = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [routes, setRoutes] = useState<DeliveryRoute[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [locations, setLocations] = useState<InventoryLocation[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [stocks, setStocks] = useState<InventoryStock[]>([]);
  const [loads, setLoads] = useState<RouteLoad[]>([]);
  const [filters, setFilters] = useState<RouteLoadFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<RouteLoadFilterValues>(emptyFilters);
  const [voidingLoad, setVoidingLoad] = useState<RouteLoad | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidValidationError, setVoidValidationError] = useState("");
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isVoiding, setIsVoiding] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const activeRoutes = useMemo(
    () => routes.filter((route) => route.is_active),
    [routes],
  );
  const activeVehicles = useMemo(
    () => vehicles.filter((vehicle) => vehicle.is_active),
    [vehicles],
  );
  const activeLocations = useMemo(
    () => locations.filter((location) => location.is_active),
    [locations],
  );
  const activeProducts = useMemo(
    () => products.filter((product) => product.is_active),
    [products],
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
        loadedRoutes,
        loadedVehicles,
        loadedLocations,
        loadedProducts,
        loadedStocks,
        loadedLoads,
      ] = await Promise.all([
        listDeliveryRoutes(activeToken),
        listVehicles(activeToken),
        listInventoryLocations(activeToken),
        listProducts(activeToken),
        listInventoryStocks(activeToken),
        listRouteLoads(activeToken),
      ]);
      setRoutes(loadedRoutes);
      setVehicles(loadedVehicles);
      setLocations(loadedLocations);
      setProducts(loadedProducts);
      setStocks(loadedStocks);
      setLoads(loadedLoads);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsInitialLoading(false);
    }
  }

  async function loadFilteredLoads(
    activeToken: string,
    activeFilters: RouteLoadFilterValues,
  ) {
    setIsFiltering(true);
    setError("");
    try {
      const loadedLoads = await listRouteLoads(
        activeToken,
        toApiFilters(activeFilters),
      );
      setLoads(loadedLoads);
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

  async function refreshOperationalData(activeToken: string) {
    const [loadedStocks, loadedLoads] = await Promise.all([
      listInventoryStocks(activeToken),
      listRouteLoads(activeToken, toApiFilters(appliedFilters)),
    ]);
    setStocks(loadedStocks);
    setLoads(loadedLoads);
  }

  async function handleCreate(payload: RouteLoadPayload): Promise<boolean> {
    if (!token) {
      return false;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const savedLoad = await createRouteLoad(token, payload);
      setMessage(`Carga ${savedLoad.load_number} registrada y stock actualizado.`);
      await refreshOperationalData(token);
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

  function handleOpenVoid(routeLoad: RouteLoad) {
    setVoidingLoad(routeLoad);
    setVoidReason("");
    setVoidValidationError("");
    clearNotices();
  }

  async function handleVoid(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !voidingLoad) {
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
      const voidedLoad = await voidRouteLoad(token, voidingLoad.id, reason);
      setMessage(`Carga ${voidedLoad.load_number} anulada y stock revertido.`);
      setVoidingLoad(null);
      setVoidReason("");
      await refreshOperationalData(token);
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
              Carga de camión
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra la salida de productos desde bodega hacia un vehículo para
              una ruta. Este módulo mueve inventario, pero todavía no cierra rutas
              ni registra ventas por ruta.
            </p>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          La carga solo traslada inventario entre ubicaciones. No registra ventas,
          cobros, dinero entregado ni cierres de ruta.
        </p>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isInitialLoading ? (
          <LoadingState label="Cargando módulo de cargas..." />
        ) : (
          <>
            <RouteLoadForm
              routes={activeRoutes}
              vehicles={activeVehicles}
              locations={activeLocations}
              products={activeProducts}
              stocks={stocks}
              isSubmitting={isSaving}
              onSubmit={handleCreate}
            />
            <RouteLoadList
              canVoid={canVoid}
              loads={loads}
              routes={routes}
              vehicles={vehicles}
              filters={filters}
              isLoading={isFiltering}
              voidingLoadId={isVoiding ? voidingLoad?.id : null}
              onFiltersChange={setFilters}
              onFilter={() => token && loadFilteredLoads(token, filters)}
              onClear={() => {
                setFilters(emptyFilters);
                if (token) {
                  loadFilteredLoads(token, emptyFilters);
                }
              }}
              onVoid={handleOpenVoid}
            />
          </>
        )}
      </div>

      {canVoid && voidingLoad ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="void-route-load-title"
        >
          <form
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl"
            onSubmit={handleVoid}
          >
            <div className="border-b border-slate-200 px-5 py-4">
              <h2
                className="text-lg font-semibold text-slate-950"
                id="void-route-load-title"
              >
                Anular carga de camión
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {voidingLoad.load_number} · {voidingLoad.vehicle_name}
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
                Los movimientos se conservarán anulados y el stock volverá a su
                ubicación de origen. La operación fallará si el vehículo ya no
                tiene cantidad suficiente para revertirla.
              </p>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
                  type="button"
                  disabled={isVoiding}
                  onClick={() => setVoidingLoad(null)}
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
    </main>
  );
}

function toApiFilters(filters: RouteLoadFilterValues): RouteLoadFilters {
  return {
    ...(filters.search ? { search: filters.search } : {}),
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.routeId ? { route_id: Number(filters.routeId) } : {}),
    ...(filters.vehicleId ? { vehicle_id: Number(filters.vehicleId) } : {}),
  };
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

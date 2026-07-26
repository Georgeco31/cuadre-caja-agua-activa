"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import { RouteClosureForm } from "@/components/RouteClosureForm";
import {
  RouteClosureList,
  type RouteClosureFilterValues,
} from "@/components/RouteClosureList";
import {
  ApiError,
  createRouteClosure,
  getRouteCommercialActivity,
  listDeliveryRoutes,
  listRouteClosures,
  listRouteLoads,
  listVehicles,
  voidRouteClosure,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { DeliveryRoute } from "@/types/deliveryRoute";
import type { RouteCommercialActivity } from "@/types/routeActivity";
import type {
  RouteClosure,
  RouteClosureFilters,
  RouteClosurePayload,
} from "@/types/routeClosure";
import type { RouteLoad } from "@/types/routeLoad";
import type { Vehicle } from "@/types/vehicle";

const emptyFilters: RouteClosureFilterValues = {
  search: "",
  dateFrom: "",
  dateTo: "",
  status: "",
  routeId: "",
  vehicleId: "",
};

export default function RouteClosuresPage() {
  const canVoid = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [loads, setLoads] = useState<RouteLoad[]>([]);
  const [closures, setClosures] = useState<RouteClosure[]>([]);
  const [allClosures, setAllClosures] = useState<RouteClosure[]>([]);
  const [routes, setRoutes] = useState<DeliveryRoute[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedLoadId, setSelectedLoadId] = useState("");
  const [activity, setActivity] = useState<RouteCommercialActivity | null>(null);
  const [filters, setFilters] = useState<RouteClosureFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<RouteClosureFilterValues>(emptyFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingActivity, setIsLoadingActivity] = useState(false);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [voidingClosureId, setVoidingClosureId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const availableLoads = useMemo(() => {
    const closedLoadIds = new Set(
      allClosures
        .filter((closure) => closure.status === "active")
        .map((closure) => closure.route_load_id),
    );
    return loads.filter((load) => !closedLoadIds.has(load.id));
  }, [allClosures, loads]);

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
      const [loadedLoads, loadedClosures, loadedRoutes, loadedVehicles] =
        await Promise.all([
          listRouteLoads(activeToken, { status: "active" }),
          listRouteClosures(activeToken),
          listDeliveryRoutes(activeToken),
          listVehicles(activeToken),
        ]);
      setLoads(loadedLoads);
      setClosures(loadedClosures);
      setAllClosures(loadedClosures);
      setRoutes(loadedRoutes);
      setVehicles(loadedVehicles);
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleLoadChange(loadId: string) {
    setSelectedLoadId(loadId);
    setActivity(null);
    setError("");
    setMessage("");
    if (!token || !loadId) {
      return;
    }
    setIsLoadingActivity(true);
    try {
      setActivity(await getRouteCommercialActivity(token, Number(loadId)));
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setIsLoadingActivity(false);
    }
  }

  async function handleCreate(payload: RouteClosurePayload): Promise<boolean> {
    if (!token) {
      return false;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const saved = await createRouteClosure(token, payload);
      setMessage(
        `Cierre ${saved.closure_number} registrado. Diferencia oficial: ${formatSignedMoney(saved.difference_amount)}.`,
      );
      setSelectedLoadId("");
      setActivity(null);
      await refreshData(token, appliedFilters);
      return true;
    } catch (saveError) {
      handleError(saveError);
      return false;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleVoid(closure: RouteClosure) {
    if (!token) {
      return;
    }
    const reason = window.prompt(
      `Motivo para anular el cierre ${closure.closure_number}:`,
    );
    if (reason === null) {
      return;
    }
    const normalizedReason = reason.trim();
    if (!normalizedReason) {
      setError("El motivo de anulación es obligatorio.");
      return;
    }
    setVoidingClosureId(closure.id);
    clearNotices();
    try {
      const voided = await voidRouteClosure(token, closure.id, normalizedReason);
      setMessage(`Cierre ${voided.closure_number} anulado.`);
      await refreshData(token, appliedFilters);
    } catch (voidError) {
      handleError(voidError);
    } finally {
      setVoidingClosureId(null);
    }
  }

  async function refreshData(
    activeToken: string,
    activeFilters: RouteClosureFilterValues,
  ) {
    const [loadedLoads, loadedClosures, loadedAllClosures] = await Promise.all([
      listRouteLoads(activeToken, { status: "active" }),
      listRouteClosures(activeToken, toApiFilters(activeFilters)),
      listRouteClosures(activeToken),
    ]);
    setLoads(loadedLoads);
    setClosures(loadedClosures);
    setAllClosures(loadedAllClosures);
  }

  async function loadFilteredClosures(
    activeToken: string,
    activeFilters: RouteClosureFilterValues,
  ) {
    setIsFiltering(true);
    setError("");
    try {
      setClosures(
        await listRouteClosures(activeToken, toApiFilters(activeFilters)),
      );
      setAppliedFilters({ ...activeFilters });
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setIsFiltering(false);
    }
  }

  function clearNotices() {
    setError("");
    setMessage("");
  }

  function handleError(possibleError: unknown) {
    if (
      possibleError instanceof ApiError &&
      possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(
      possibleError instanceof Error
        ? possibleError.message
        : "No se pudo completar la solicitud.",
    );
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
              Cierre financiero de ruta
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Compara el efectivo esperado de una ruta contra el efectivo
              realmente entregado. Este módulo no modifica caja general todavía.
            </p>
          </div>
          <LogoutButton />
        </header>

        <div className="flex flex-col gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 sm:flex-row sm:items-center sm:justify-between">
          <p>
            El cierre congela los totales comerciales de la carga. No mueve
            caja, inventario ni el estado físico de la ruta.
          </p>
          <Link
            className="shrink-0 font-semibold text-water-700 hover:text-water-500"
            href="/dashboard/route-cash-receipts"
          >
            Registrar dinero en caja
          </Link>
        </div>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando cierres financieros..." />
        ) : (
          <>
            <RouteClosureForm
              loads={availableLoads}
              selectedLoadId={selectedLoadId}
              activity={activity}
              isLoadingActivity={isLoadingActivity}
              isSubmitting={isSaving}
              onLoadChange={handleLoadChange}
              onSubmit={handleCreate}
            />
            <RouteClosureList
              canVoid={canVoid}
              closures={closures}
              routes={routes}
              vehicles={vehicles}
              filters={filters}
              isLoading={isFiltering}
              voidingClosureId={voidingClosureId}
              onFiltersChange={setFilters}
              onFilter={() => token && loadFilteredClosures(token, filters)}
              onClear={() => {
                setFilters(emptyFilters);
                if (token) {
                  loadFilteredClosures(token, emptyFilters);
                }
              }}
              onVoid={handleVoid}
            />
          </>
        )}
      </div>
    </main>
  );
}

function toApiFilters(filters: RouteClosureFilterValues): RouteClosureFilters {
  return {
    ...(filters.search ? { search: filters.search } : {}),
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.routeId ? { route_id: Number(filters.routeId) } : {}),
    ...(filters.vehicleId ? { vehicle_id: Number(filters.vehicleId) } : {}),
  };
}

function formatSignedMoney(value: string): string {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "$0.00";
  }
  return `${amount > 0 ? "+" : ""}$${amount.toFixed(2)}`;
}

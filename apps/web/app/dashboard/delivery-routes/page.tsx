"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  DeliveryRouteFilters,
  type DeliveryRouteFilterValues,
} from "@/components/DeliveryRouteFilters";
import { DeliveryRouteForm } from "@/components/DeliveryRouteForm";
import { DeliveryRouteList } from "@/components/DeliveryRouteList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  activateDeliveryRoute,
  ApiError,
  createDeliveryRoute,
  deactivateDeliveryRoute,
  listDeliveryRoutes,
  updateDeliveryRoute,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type {
  DeliveryRoute,
  DeliveryRoutePayload,
} from "@/types/deliveryRoute";

const emptyFilters: DeliveryRouteFilterValues = {
  search: "",
  isActive: "",
  zone: "",
  sector: "",
};

export default function DeliveryRoutesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [deliveryRoutes, setDeliveryRoutes] = useState<DeliveryRoute[]>([]);
  const [filters, setFilters] = useState<DeliveryRouteFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<DeliveryRouteFilterValues>(emptyFilters);
  const [editingRoute, setEditingRoute] = useState<DeliveryRoute | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingRouteId, setChangingRouteId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadDeliveryRoutes(storedToken);
  }, [router]);

  async function loadDeliveryRoutes(
    activeToken: string,
    activeFilters: DeliveryRouteFilterValues = emptyFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedRoutes = await listDeliveryRoutes(activeToken, {
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.isActive
          ? { is_active: activeFilters.isActive === "active" }
          : {}),
        ...(activeFilters.zone ? { zone: activeFilters.zone } : {}),
        ...(activeFilters.sector ? { sector: activeFilters.sector } : {}),
      });
      setDeliveryRoutes(loadedRoutes);
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

  function handleShowCreateForm() {
    setEditingRoute(null);
    setIsFormVisible(true);
    setError("");
    setMessage("");
  }

  function handleEdit(deliveryRoute: DeliveryRoute) {
    setEditingRoute(deliveryRoute);
    setIsFormVisible(true);
    setError("");
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelForm() {
    setEditingRoute(null);
    setIsFormVisible(false);
  }

  async function handleSaveRoute(
    payload: DeliveryRoutePayload,
  ): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const savedRoute = editingRoute
        ? await updateDeliveryRoute(token, editingRoute.id, payload)
        : await createDeliveryRoute(token, payload);
      const action = editingRoute ? "actualizada" : "registrada";

      setEditingRoute(null);
      setIsFormVisible(false);
      setMessage(`Ruta ${action}: ${savedRoute.name}.`);
      await loadDeliveryRoutes(token, appliedFilters);
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

  async function handleToggleActive(deliveryRoute: DeliveryRoute) {
    if (!token) {
      return;
    }
    if (
      deliveryRoute.is_active &&
      !window.confirm(`¿Inactivar la ruta ${deliveryRoute.name}?`)
    ) {
      return;
    }

    setChangingRouteId(deliveryRoute.id);
    setError("");
    setMessage("");

    try {
      const updatedRoute = deliveryRoute.is_active
        ? await deactivateDeliveryRoute(token, deliveryRoute.id)
        : await activateDeliveryRoute(token, deliveryRoute.id);
      setMessage(
        updatedRoute.is_active
          ? `Ruta reactivada: ${updatedRoute.name}.`
          : `Ruta inactivada: ${updatedRoute.name}.`,
      );
      await loadDeliveryRoutes(token, appliedFilters);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingRouteId(null);
    }
  }

  function handleFilterSubmit() {
    if (token) {
      loadDeliveryRoutes(token, filters);
    }
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    loadDeliveryRoutes(token, emptyFilters);
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
              Rutas de entrega
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Administra las rutas y zonas de entrega de Agua Activa. Este módulo
              será la base para ventas por ruta, cobros, carga de camión y cierre
              de ruta.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
              type="button"
              disabled={isSaving}
              onClick={handleShowCreateForm}
            >
              Nueva ruta
            </button>
            <LogoutButton />
          </div>
        </header>

        {isFormVisible ? (
          <DeliveryRouteForm
            key={editingRoute?.id ?? "new"}
            deliveryRoute={editingRoute}
            isSubmitting={isSaving}
            onSubmit={handleSaveRoute}
            onCancel={handleCancelForm}
          />
        ) : null}

        <DeliveryRouteFilters
          filters={filters}
          disabled={isLoading}
          onChange={setFilters}
          onSubmit={handleFilterSubmit}
          onClear={handleClearFilters}
        />

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando rutas..." />
        ) : (
          <DeliveryRouteList
            deliveryRoutes={deliveryRoutes}
            hasActiveFilters={hasActiveFilters(appliedFilters)}
            changingRouteId={changingRouteId}
            onEdit={handleEdit}
            onToggleActive={handleToggleActive}
          />
        )}
      </div>
    </main>
  );
}

function hasActiveFilters(filters: DeliveryRouteFilterValues): boolean {
  return Boolean(
    filters.search || filters.isActive || filters.zone || filters.sector,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AccessRestricted } from "@/components/AccessRestricted";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  VehicleFilters,
  type VehicleFilterValues,
} from "@/components/VehicleFilters";
import { VehicleForm } from "@/components/VehicleForm";
import { VehicleList } from "@/components/VehicleList";
import {
  activateVehicle,
  ApiError,
  createVehicle,
  deactivateVehicle,
  listVehicles,
  updateVehicle,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { Vehicle, VehiclePayload } from "@/types/vehicle";

const emptyFilters: VehicleFilterValues = {
  search: "",
  isActive: "",
  vehicleType: "",
  fuelType: "",
};

export default function VehiclesPage() {
  const canManage = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filters, setFilters] = useState<VehicleFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<VehicleFilterValues>(emptyFilters);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingVehicleId, setChangingVehicleId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadVehicles(storedToken);
  }, [router]);

  async function loadVehicles(
    activeToken: string,
    activeFilters: VehicleFilterValues = emptyFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedVehicles = await listVehicles(activeToken, {
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.isActive
          ? { is_active: activeFilters.isActive === "active" }
          : {}),
        ...(activeFilters.vehicleType
          ? { vehicle_type: activeFilters.vehicleType }
          : {}),
        ...(activeFilters.fuelType
          ? { fuel_type: activeFilters.fuelType }
          : {}),
      });
      setVehicles(loadedVehicles);
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
    setEditingVehicle(null);
    setIsFormVisible(true);
    setError("");
    setMessage("");
  }

  function handleEdit(vehicle: Vehicle) {
    setEditingVehicle(vehicle);
    setIsFormVisible(true);
    setError("");
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelForm() {
    setEditingVehicle(null);
    setIsFormVisible(false);
  }

  async function handleSaveVehicle(payload: VehiclePayload): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const savedVehicle = editingVehicle
        ? await updateVehicle(token, editingVehicle.id, payload)
        : await createVehicle(token, payload);
      const action = editingVehicle ? "actualizado" : "registrado";

      setEditingVehicle(null);
      setIsFormVisible(false);
      setMessage(`Vehículo ${action}: ${savedVehicle.name}.`);
      await loadVehicles(token, appliedFilters);
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

  async function handleToggleActive(vehicle: Vehicle) {
    if (!token) {
      return;
    }
    if (
      vehicle.is_active &&
      !window.confirm(`¿Inactivar el vehículo ${vehicle.name}?`)
    ) {
      return;
    }

    setChangingVehicleId(vehicle.id);
    setError("");
    setMessage("");

    try {
      const updatedVehicle = vehicle.is_active
        ? await deactivateVehicle(token, vehicle.id)
        : await activateVehicle(token, vehicle.id);
      setMessage(
        updatedVehicle.is_active
          ? `Vehículo reactivado: ${updatedVehicle.name}.`
          : `Vehículo inactivado: ${updatedVehicle.name}.`,
      );
      await loadVehicles(token, appliedFilters);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingVehicleId(null);
    }
  }

  function handleFilterSubmit() {
    if (token) {
      loadVehicles(token, filters);
    }
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    loadVehicles(token, emptyFilters);
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
              Vehículos
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Administra los vehículos y camiones de Agua Activa. Este módulo será
              la base para rutas, mantenimiento, combustible, carga de camión y
              rentabilidad por vehículo.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            {canManage ? (
              <button
                className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
                type="button"
                disabled={isSaving}
                onClick={handleShowCreateForm}
              >
                Nuevo vehículo
              </button>
            ) : null}
            <LogoutButton />
          </div>
        </header>

        {!canManage ? <AccessRestricted compact /> : null}

        {canManage && isFormVisible ? (
          <VehicleForm
            key={editingVehicle?.id ?? "new"}
            vehicle={editingVehicle}
            isSubmitting={isSaving}
            onSubmit={handleSaveVehicle}
            onCancel={handleCancelForm}
          />
        ) : null}

        <VehicleFilters
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
          <LoadingState label="Cargando vehículos..." />
        ) : (
          <VehicleList
            vehicles={vehicles}
            canManage={canManage}
            hasActiveFilters={hasActiveFilters(appliedFilters)}
            changingVehicleId={changingVehicleId}
            onEdit={handleEdit}
            onToggleActive={handleToggleActive}
          />
        )}
      </div>
    </main>
  );
}

function hasActiveFilters(filters: VehicleFilterValues): boolean {
  return Boolean(
    filters.search ||
      filters.isActive ||
      filters.vehicleType ||
      filters.fuelType,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

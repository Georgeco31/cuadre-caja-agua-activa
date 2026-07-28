"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AccessRestricted } from "@/components/AccessRestricted";
import {
  CustomerFilters,
  type CustomerFilterValues,
} from "@/components/CustomerFilters";
import { CustomerForm } from "@/components/CustomerForm";
import { CustomerList } from "@/components/CustomerList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  activateCustomer,
  ApiError,
  createCustomer,
  deactivateCustomer,
  listCustomers,
  updateCustomer,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { Customer, CustomerPayload } from "@/types/customer";

const emptyFilters: CustomerFilterValues = {
  search: "",
  isActive: "",
  customerType: "",
  sector: "",
};

export default function CustomersPage() {
  const canManageExistingCustomers = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filters, setFilters] =
    useState<CustomerFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<CustomerFilterValues>(emptyFilters);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingCustomerId, setChangingCustomerId] = useState<number | null>(
    null,
  );
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadCustomers(storedToken);
  }, [router]);

  async function loadCustomers(
    activeToken: string,
    activeFilters: CustomerFilterValues = emptyFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedCustomers = await listCustomers(activeToken, {
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.isActive
          ? { is_active: activeFilters.isActive === "active" }
          : {}),
        ...(activeFilters.customerType
          ? { customer_type: activeFilters.customerType }
          : {}),
        ...(activeFilters.sector ? { sector: activeFilters.sector } : {}),
      });
      setCustomers(loadedCustomers);
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
    setEditingCustomer(null);
    setIsFormVisible(true);
    setError("");
    setMessage("");
  }

  function handleEdit(customer: Customer) {
    setEditingCustomer(customer);
    setIsFormVisible(true);
    setError("");
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelForm() {
    setEditingCustomer(null);
    setIsFormVisible(false);
  }

  async function handleSaveCustomer(payload: CustomerPayload): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const savedCustomer = editingCustomer
        ? await updateCustomer(token, editingCustomer.id, payload)
        : await createCustomer(token, payload);
      const action = editingCustomer ? "actualizado" : "registrado";

      setEditingCustomer(null);
      setIsFormVisible(false);
      setMessage(`Cliente ${action}: ${savedCustomer.name}.`);
      await loadCustomers(token, appliedFilters);
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

  async function handleToggleActive(customer: Customer) {
    if (!token) {
      return;
    }
    if (
      customer.is_active &&
      !window.confirm(`¿Inactivar al cliente ${customer.name}?`)
    ) {
      return;
    }

    setChangingCustomerId(customer.id);
    setError("");
    setMessage("");

    try {
      const updatedCustomer = customer.is_active
        ? await deactivateCustomer(token, customer.id)
        : await activateCustomer(token, customer.id);
      setMessage(
        updatedCustomer.is_active
          ? `Cliente reactivado: ${updatedCustomer.name}.`
          : `Cliente inactivado: ${updatedCustomer.name}.`,
      );
      await loadCustomers(token, appliedFilters);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingCustomerId(null);
    }
  }

  function handleFilterSubmit() {
    if (token) {
      loadCustomers(token, filters);
    }
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    loadCustomers(token, emptyFilters);
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
              Clientes
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Administra los clientes de Agua Activa. Este módulo será la base
              para ventas, créditos, cobros y rutas.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
              type="button"
              disabled={isSaving}
              onClick={handleShowCreateForm}
            >
              Nuevo cliente
            </button>
            <LogoutButton />
          </div>
        </header>

        {!canManageExistingCustomers ? (
          <AccessRestricted
            compact
            message="Puedes consultar y registrar clientes nuevos. La edición, activación e inactivación de clientes existentes está disponible solo para el administrador/auditor."
          />
        ) : null}

        {isFormVisible ? (
          <CustomerForm
            key={editingCustomer?.id ?? "new"}
            customer={editingCustomer}
            isSubmitting={isSaving}
            onSubmit={handleSaveCustomer}
            onCancel={handleCancelForm}
          />
        ) : null}

        <CustomerFilters
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
          <LoadingState label="Cargando clientes..." />
        ) : (
          <CustomerList
            customers={customers}
            canManage={canManageExistingCustomers}
            hasActiveFilters={hasActiveFilters(appliedFilters)}
            changingCustomerId={changingCustomerId}
            onEdit={handleEdit}
            onToggleActive={handleToggleActive}
          />
        )}
      </div>
    </main>
  );
}

function hasActiveFilters(filters: CustomerFilterValues): boolean {
  return Boolean(
    filters.search ||
      filters.isActive ||
      filters.customerType ||
      filters.sector,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

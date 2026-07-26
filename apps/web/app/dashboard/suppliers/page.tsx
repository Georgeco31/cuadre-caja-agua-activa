"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  activateSupplier,
  ApiError,
  createSupplier,
  deactivateSupplier,
  listSuppliers,
  updateSupplier,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { Supplier, SupplierPayload } from "@/types/supplier";

type SupplierFormValues = {
  name: string;
  identification: string;
  primaryPhone: string;
  secondaryPhone: string;
  email: string;
  address: string;
  contactName: string;
  supplierType: string;
  paymentTerms: string;
  notes: string;
};

type SupplierFilterValues = {
  search: string;
  status: "" | "active" | "inactive";
  supplierType: string;
};

const emptyForm: SupplierFormValues = {
  name: "",
  identification: "",
  primaryPhone: "",
  secondaryPhone: "",
  email: "",
  address: "",
  contactName: "",
  supplierType: "",
  paymentTerms: "",
  notes: "",
};

const emptyFilters: SupplierFilterValues = {
  search: "",
  status: "",
  supplierType: "",
};

export default function SuppliersPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [filters, setFilters] = useState(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState(emptyFilters);
  const [formValues, setFormValues] = useState(emptyForm);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingSupplierId, setChangingSupplierId] = useState<number | null>(
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
    loadSuppliers(storedToken, emptyFilters);
  }, [router]);

  async function loadSuppliers(
    activeToken: string,
    activeFilters: SupplierFilterValues,
  ) {
    setIsLoading(true);
    setError("");
    try {
      const loadedSuppliers = await listSuppliers(activeToken, {
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.status
          ? { is_active: activeFilters.status === "active" }
          : {}),
        ...(activeFilters.supplierType
          ? { supplier_type: activeFilters.supplierType }
          : {}),
      });
      setSuppliers(loadedSuppliers);
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

  function openCreateForm() {
    setEditingSupplier(null);
    setFormValues(emptyForm);
    setIsFormVisible(true);
    clearNotices();
  }

  function openEditForm(supplier: Supplier) {
    setEditingSupplier(supplier);
    setFormValues({
      name: supplier.name,
      identification: supplier.identification ?? "",
      primaryPhone: supplier.primary_phone ?? "",
      secondaryPhone: supplier.secondary_phone ?? "",
      email: supplier.email ?? "",
      address: supplier.address ?? "",
      contactName: supplier.contact_name ?? "",
      supplierType: supplier.supplier_type ?? "",
      paymentTerms: supplier.payment_terms ?? "",
      notes: supplier.notes ?? "",
    });
    setIsFormVisible(true);
    clearNotices();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    if (!formValues.name.trim()) {
      setError("El nombre del proveedor es obligatorio.");
      return;
    }

    setIsSaving(true);
    clearNotices();
    const payload: SupplierPayload = {
      name: formValues.name.trim(),
      identification: optionalText(formValues.identification),
      primary_phone: optionalText(formValues.primaryPhone),
      secondary_phone: optionalText(formValues.secondaryPhone),
      email: optionalText(formValues.email),
      address: optionalText(formValues.address),
      contact_name: optionalText(formValues.contactName),
      supplier_type: optionalText(formValues.supplierType),
      payment_terms: optionalText(formValues.paymentTerms),
      notes: optionalText(formValues.notes),
    };
    try {
      const savedSupplier = editingSupplier
        ? await updateSupplier(token, editingSupplier.id, payload)
        : await createSupplier(token, payload);
      setMessage(
        `Proveedor ${editingSupplier ? "actualizado" : "registrado"}: ${
          savedSupplier.name
        }.`,
      );
      setEditingSupplier(null);
      setFormValues(emptyForm);
      setIsFormVisible(false);
      await loadSuppliers(token, appliedFilters);
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return;
      }
      setError(getErrorMessage(saveError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggleActive(supplier: Supplier) {
    if (!token) {
      return;
    }
    if (
      supplier.is_active &&
      !window.confirm(`¿Desactivar al proveedor ${supplier.name}?`)
    ) {
      return;
    }
    setChangingSupplierId(supplier.id);
    clearNotices();
    try {
      const updatedSupplier = supplier.is_active
        ? await deactivateSupplier(token, supplier.id)
        : await activateSupplier(token, supplier.id);
      setMessage(
        updatedSupplier.is_active
          ? `Proveedor activado: ${updatedSupplier.name}.`
          : `Proveedor desactivado: ${updatedSupplier.name}.`,
      );
      await loadSuppliers(token, appliedFilters);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingSupplierId(null);
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
              Proveedores
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Gestiona los datos base de quienes suministran productos y
              servicios a Agua Activa.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:bg-slate-300"
              type="button"
              disabled={isSaving}
              onClick={openCreateForm}
            >
              Nuevo proveedor
            </button>
            <LogoutButton />
          </div>
        </header>

        {isFormVisible ? (
          <form
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
            onSubmit={handleSubmit}
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">
                  {editingSupplier ? "Editar proveedor" : "Registrar proveedor"}
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  El nombre es obligatorio. La identificación, si se informa,
                  no puede repetirse.
                </p>
              </div>
              <button
                className="text-sm font-semibold text-slate-600 hover:text-slate-950"
                type="button"
                disabled={isSaving}
                onClick={() => setIsFormVisible(false)}
              >
                Cerrar
              </button>
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <Field
                label="Nombre *"
                value={formValues.name}
                disabled={isSaving}
                required
                onChange={(value) =>
                  setFormValues((current) => ({ ...current, name: value }))
                }
              />
              <Field
                label="Identificación"
                value={formValues.identification}
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({
                    ...current,
                    identification: value,
                  }))
                }
              />
              <Field
                label="Teléfono principal"
                value={formValues.primaryPhone}
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({
                    ...current,
                    primaryPhone: value,
                  }))
                }
              />
              <Field
                label="Teléfono secundario"
                value={formValues.secondaryPhone}
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({
                    ...current,
                    secondaryPhone: value,
                  }))
                }
              />
              <Field
                label="Email"
                type="email"
                value={formValues.email}
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({ ...current, email: value }))
                }
              />
              <Field
                label="Persona de contacto"
                value={formValues.contactName}
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({
                    ...current,
                    contactName: value,
                  }))
                }
              />
              <Field
                label="Tipo"
                value={formValues.supplierType}
                placeholder="insumos, servicios, mantenimiento..."
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({
                    ...current,
                    supplierType: value,
                  }))
                }
              />
              <Field
                label="Condiciones de pago"
                value={formValues.paymentTerms}
                placeholder="contado, crédito 15 días..."
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({
                    ...current,
                    paymentTerms: value,
                  }))
                }
              />
              <Field
                label="Dirección"
                value={formValues.address}
                disabled={isSaving}
                onChange={(value) =>
                  setFormValues((current) => ({ ...current, address: value }))
                }
              />
            </div>
            <label className="mt-4 block">
              <span className="text-sm font-medium text-slate-700">Notas</span>
              <textarea
                className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                value={formValues.notes}
                disabled={isSaving}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    notes: event.target.value,
                  }))
                }
              />
            </label>
            <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <button
                className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                type="button"
                disabled={isSaving}
                onClick={() => setIsFormVisible(false)}
              >
                Cancelar
              </button>
              <button
                className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
                type="submit"
                disabled={isSaving}
              >
                {isSaving ? "Guardando..." : "Guardar proveedor"}
              </button>
            </div>
          </form>
        ) : null}

        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-slate-950">
            Buscar y filtrar
          </h2>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <Field
              label="Buscar"
              value={filters.search}
              placeholder="Nombre, identificación, teléfono o contacto"
              disabled={isLoading}
              onChange={(value) =>
                setFilters((current) => ({ ...current, search: value }))
              }
            />
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Estado</span>
              <select
                className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                value={filters.status}
                disabled={isLoading}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    status: event.target.value as SupplierFilterValues["status"],
                  }))
                }
              >
                <option value="">Todos</option>
                <option value="active">Activos</option>
                <option value="inactive">Inactivos</option>
              </select>
            </label>
            <Field
              label="Tipo"
              value={filters.supplierType}
              placeholder="Ej. insumos"
              disabled={isLoading}
              onChange={(value) =>
                setFilters((current) => ({
                  ...current,
                  supplierType: value,
                }))
              }
            />
          </div>
          <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              type="button"
              disabled={isLoading}
              onClick={() => {
                setFilters(emptyFilters);
                if (token) {
                  loadSuppliers(token, emptyFilters);
                }
              }}
            >
              Limpiar
            </button>
            <button
              className="h-10 rounded-md bg-slate-900 px-4 text-sm font-semibold text-white hover:bg-slate-700"
              type="button"
              disabled={isLoading}
              onClick={() => token && loadSuppliers(token, filters)}
            >
              Aplicar filtros
            </button>
          </div>
        </section>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando proveedores..." />
        ) : suppliers.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 bg-white px-5 py-8 text-center text-sm text-slate-600">
            {hasFilters(appliedFilters)
              ? "No hay proveedores que coincidan con los filtros."
              : "Todavía no hay proveedores registrados."}
          </p>
        ) : (
          <section className="space-y-3">
            <div>
              <p className="text-sm font-medium text-water-700">Directorio</p>
              <h2 className="mt-1 text-xl font-semibold text-slate-950">
                Proveedores registrados
              </h2>
            </div>
            <div className="grid gap-4 lg:grid-cols-2">
              {suppliers.map((supplier) => (
                <article
                  className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
                  key={supplier.id}
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-950">
                        {supplier.name}
                      </h3>
                      <p className="mt-1 text-sm text-slate-600">
                        {supplier.identification ?? "Sin identificación"}
                      </p>
                    </div>
                    <span
                      className={
                        supplier.is_active
                          ? "w-fit rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700"
                          : "w-fit rounded-full bg-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700"
                      }
                    >
                      {supplier.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </div>
                  <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                    <Detail label="Teléfono" value={supplier.primary_phone} />
                    <Detail label="Email" value={supplier.email} />
                    <Detail label="Contacto" value={supplier.contact_name} />
                    <Detail label="Tipo" value={supplier.supplier_type} />
                    <Detail
                      label="Condiciones"
                      value={supplier.payment_terms}
                    />
                    <Detail label="Dirección" value={supplier.address} />
                  </dl>
                  {supplier.notes ? (
                    <p className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">
                      {supplier.notes}
                    </p>
                  ) : null}
                  <div className="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 sm:flex-row sm:justify-end">
                    <button
                      className="h-9 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                      type="button"
                      disabled={changingSupplierId === supplier.id}
                      onClick={() => openEditForm(supplier)}
                    >
                      Editar
                    </button>
                    <button
                      className={
                        supplier.is_active
                          ? "h-9 rounded-md border border-red-200 bg-white px-3 text-sm font-semibold text-red-700 hover:bg-red-50"
                          : "h-9 rounded-md border border-emerald-200 bg-white px-3 text-sm font-semibold text-emerald-700 hover:bg-emerald-50"
                      }
                      type="button"
                      disabled={changingSupplierId === supplier.id}
                      onClick={() => handleToggleActive(supplier)}
                    >
                      {changingSupplierId === supplier.id
                        ? "Guardando..."
                        : supplier.is_active
                          ? "Desactivar"
                          : "Activar"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  disabled,
  required = false,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
  required?: boolean;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        type={type}
        value={value}
        required={required}
        placeholder={placeholder}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function Detail({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {
  return (
    <div>
      <dt className="font-medium text-slate-500">{label}</dt>
      <dd className="mt-0.5 break-words text-slate-900">{value || "—"}</dd>
    </div>
  );
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function hasFilters(filters: SupplierFilterValues): boolean {
  return Boolean(filters.search || filters.status || filters.supplierType);
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

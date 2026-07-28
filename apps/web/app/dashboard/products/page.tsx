"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AccessRestricted } from "@/components/AccessRestricted";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ProductFilters,
  type ProductFilterValues,
} from "@/components/ProductFilters";
import { ProductForm } from "@/components/ProductForm";
import { ProductList } from "@/components/ProductList";
import {
  activateProduct,
  ApiError,
  createProduct,
  deactivateProduct,
  listProducts,
  updateProduct,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { Product, ProductPayload } from "@/types/product";

const emptyFilters: ProductFilterValues = {
  search: "",
  isActive: "",
  category: "",
  unit: "",
};

export default function ProductsPage() {
  const canManage = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [filters, setFilters] = useState<ProductFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<ProductFilterValues>(emptyFilters);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingProductId, setChangingProductId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadProducts(storedToken);
  }, [router]);

  async function loadProducts(
    activeToken: string,
    activeFilters: ProductFilterValues = emptyFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedProducts = await listProducts(activeToken, {
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.isActive
          ? { is_active: activeFilters.isActive === "active" }
          : {}),
        ...(activeFilters.category
          ? { category: activeFilters.category }
          : {}),
        ...(activeFilters.unit ? { unit: activeFilters.unit } : {}),
      });
      setProducts(loadedProducts);
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
    setEditingProduct(null);
    setIsFormVisible(true);
    setError("");
    setMessage("");
  }

  function handleEdit(product: Product) {
    setEditingProduct(product);
    setIsFormVisible(true);
    setError("");
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelForm() {
    setEditingProduct(null);
    setIsFormVisible(false);
  }

  async function handleSaveProduct(payload: ProductPayload): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const savedProduct = editingProduct
        ? await updateProduct(token, editingProduct.id, payload)
        : await createProduct(token, payload);
      const action = editingProduct ? "actualizado" : "registrado";

      setEditingProduct(null);
      setIsFormVisible(false);
      setMessage(`Producto ${action}: ${savedProduct.name}.`);
      await loadProducts(token, appliedFilters);
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

  async function handleToggleActive(product: Product) {
    if (!token) {
      return;
    }
    if (
      product.is_active &&
      !window.confirm(`¿Inactivar el producto ${product.name}?`)
    ) {
      return;
    }

    setChangingProductId(product.id);
    setError("");
    setMessage("");

    try {
      const updatedProduct = product.is_active
        ? await deactivateProduct(token, product.id)
        : await activateProduct(token, product.id);
      setMessage(
        updatedProduct.is_active
          ? `Producto reactivado: ${updatedProduct.name}.`
          : `Producto inactivado: ${updatedProduct.name}.`,
      );
      await loadProducts(token, appliedFilters);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingProductId(null);
    }
  }

  function handleFilterSubmit() {
    if (token) {
      loadProducts(token, filters);
    }
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    loadProducts(token, emptyFilters);
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
              Productos y precios
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              {canManage
                ? "Administra los productos de Agua Activa."
                : "Consulta los productos y precios vigentes de Agua Activa."}{" "}
              Este módulo es la base para ventas, inventario, producción y
              rutas.
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
                Nuevo producto
              </button>
            ) : null}
            <LogoutButton />
          </div>
        </header>

        {!canManage ? <AccessRestricted compact /> : null}

        {canManage && isFormVisible ? (
          <ProductForm
            key={editingProduct?.id ?? "new"}
            product={editingProduct}
            isSubmitting={isSaving}
            onSubmit={handleSaveProduct}
            onCancel={handleCancelForm}
          />
        ) : null}

        <ProductFilters
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
          <LoadingState label="Cargando productos..." />
        ) : (
          <ProductList
            products={products}
            canManage={canManage}
            showSensitiveCosts={canManage}
            hasActiveFilters={hasActiveFilters(appliedFilters)}
            changingProductId={changingProductId}
            onEdit={handleEdit}
            onToggleActive={handleToggleActive}
          />
        )}
      </div>
    </main>
  );
}

function hasActiveFilters(filters: ProductFilterValues): boolean {
  return Boolean(
    filters.search || filters.isActive || filters.category || filters.unit,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

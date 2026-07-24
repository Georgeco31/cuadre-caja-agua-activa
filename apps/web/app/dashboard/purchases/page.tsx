"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createPurchase,
  getPurchase,
  listProducts,
  listPurchases,
  listSuppliers,
  voidPurchase,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { Product } from "@/types/product";
import {
  PURCHASE_DOCUMENT_TYPE_LABELS,
  PURCHASE_PAYMENT_STATUS_LABELS,
  PURCHASE_STATUS_LABELS,
  type Purchase,
  type PurchaseDocumentType,
  type PurchaseItemPayload,
  type PurchasePaymentStatus,
  type PurchaseStatus,
} from "@/types/purchase";
import type { Supplier } from "@/types/supplier";

type PurchaseItemDraft = {
  key: number;
  productId: string;
  description: string;
  quantity: string;
  unitCost: string;
  discountAmount: string;
  taxAmount: string;
  notes: string;
};

type PurchaseFormValues = {
  supplierId: string;
  purchaseDate: string;
  documentNumber: string;
  documentType: "" | PurchaseDocumentType;
  paymentStatus: PurchasePaymentStatus;
  notes: string;
  items: PurchaseItemDraft[];
};

type PurchaseFilterValues = {
  dateFrom: string;
  dateTo: string;
  status: "" | PurchaseStatus;
  supplierId: string;
  search: string;
};

const emptyFilters: PurchaseFilterValues = {
  dateFrom: "",
  dateTo: "",
  status: "",
  supplierId: "",
  search: "",
};

export default function PurchasesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [filters, setFilters] = useState(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState(emptyFilters);
  const [formValues, setFormValues] = useState(createEmptyForm);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [viewingPurchase, setViewingPurchase] = useState<Purchase | null>(null);
  const [voidingPurchase, setVoidingPurchase] = useState<Purchase | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidError, setVoidError] = useState("");
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isVoiding, setIsVoiding] = useState(false);
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
      const [loadedSuppliers, loadedProducts, loadedPurchases] =
        await Promise.all([
          listSuppliers(activeToken, { is_active: true }),
          listProducts(activeToken, { is_active: true }),
          listPurchases(activeToken),
        ]);
      setSuppliers(loadedSuppliers);
      setProducts(loadedProducts);
      setPurchases(loadedPurchases);
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsInitialLoading(false);
    }
  }

  async function loadPurchases(
    activeToken: string,
    activeFilters: PurchaseFilterValues,
  ) {
    setIsFiltering(true);
    setError("");
    try {
      const loadedPurchases = await listPurchases(activeToken, {
        ...(activeFilters.dateFrom
          ? { date_from: activeFilters.dateFrom }
          : {}),
        ...(activeFilters.dateTo ? { date_to: activeFilters.dateTo } : {}),
        ...(activeFilters.status ? { status: activeFilters.status } : {}),
        ...(activeFilters.supplierId
          ? { supplier_id: Number(activeFilters.supplierId) }
          : {}),
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
      });
      setPurchases(loadedPurchases);
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

  async function handleCreatePurchase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    const validationMessage = validatePurchase(formValues);
    if (validationMessage) {
      setError(validationMessage);
      return;
    }

    setIsSaving(true);
    clearNotices();
    const itemPayloads: PurchaseItemPayload[] = formValues.items.map((item) => ({
      product_id: item.productId ? Number(item.productId) : null,
      description: optionalText(item.description),
      quantity: item.quantity,
      unit_cost: item.unitCost,
      discount_amount: item.discountAmount || "0",
      tax_amount: item.taxAmount || "0",
      notes: optionalText(item.notes),
    }));
    try {
      const savedPurchase = await createPurchase(token, {
        supplier_id: Number(formValues.supplierId),
        purchase_date: formValues.purchaseDate,
        document_number: optionalText(formValues.documentNumber),
        document_type: formValues.documentType || null,
        payment_status: formValues.paymentStatus,
        notes: optionalText(formValues.notes),
        items: itemPayloads,
      });
      setMessage(`Compra ${savedPurchase.purchase_number} registrada.`);
      setFormValues(createEmptyForm());
      setIsFormVisible(false);
      await loadPurchases(token, appliedFilters);
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return;
      }
      setError(getErrorMessage(saveError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleViewDetail(purchase: Purchase) {
    if (!token) {
      return;
    }
    setIsLoadingDetail(true);
    clearNotices();
    try {
      setViewingPurchase(await getPurchase(token, purchase.id));
    } catch (detailError) {
      if (redirectIfUnauthorized(detailError)) {
        return;
      }
      setError(getErrorMessage(detailError));
    } finally {
      setIsLoadingDetail(false);
    }
  }

  function openVoidDialog(purchase: Purchase) {
    setVoidingPurchase(purchase);
    setVoidReason("");
    setVoidError("");
    clearNotices();
  }

  async function handleVoidPurchase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !voidingPurchase) {
      return;
    }
    const reason = voidReason.trim();
    if (!reason) {
      setVoidError("El motivo de anulación es obligatorio.");
      return;
    }
    setIsVoiding(true);
    setVoidError("");
    try {
      const voidedPurchase = await voidPurchase(
        token,
        voidingPurchase.id,
        reason,
      );
      setMessage(`Compra ${voidedPurchase.purchase_number} anulada.`);
      setVoidingPurchase(null);
      setVoidReason("");
      if (viewingPurchase?.id === voidedPurchase.id) {
        setViewingPurchase(voidedPurchase);
      }
      await loadPurchases(token, appliedFilters);
    } catch (possibleError) {
      if (redirectIfUnauthorized(possibleError)) {
        return;
      }
      setVoidError(getErrorMessage(possibleError));
    } finally {
      setIsVoiding(false);
    }
  }

  function updateItem(
    itemKey: number,
    values: Partial<PurchaseItemDraft>,
  ) {
    setFormValues((current) => ({
      ...current,
      items: current.items.map((item) =>
        item.key === itemKey ? { ...item, ...values } : item,
      ),
    }));
  }

  function addItem() {
    setFormValues((current) => ({
      ...current,
      items: [
        ...current.items,
        createEmptyItem(
          Math.max(0, ...current.items.map((item) => item.key)) + 1,
        ),
      ],
    }));
  }

  function removeItem(itemKey: number) {
    setFormValues((current) => ({
      ...current,
      items: current.items.filter((item) => item.key !== itemKey),
    }));
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
              Compras
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra compras a proveedores. Este módulo no modifica inventario
              ni caja automáticamente.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
              type="button"
              disabled={isSaving || isInitialLoading}
              onClick={() => {
                setFormValues(createEmptyForm());
                setIsFormVisible(true);
                clearNotices();
              }}
            >
              Nueva compra
            </button>
            <LogoutButton />
          </div>
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900">
          Para ingresar productos al inventario desde una compra se usará un
          bloque posterior.
        </p>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isInitialLoading ? (
          <LoadingState label="Cargando compras..." />
        ) : (
          <>
            {isFormVisible ? (
              <form
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
                onSubmit={handleCreatePurchase}
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-950">
                      Registrar compra
                    </h2>
                    <p className="mt-1 text-sm text-slate-600">
                      Los totales oficiales serán calculados por el backend.
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
                  <label className="block">
                    <span className="text-sm font-medium text-slate-700">
                      Proveedor activo *
                    </span>
                    <select
                      className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                      value={formValues.supplierId}
                      required
                      disabled={isSaving}
                      onChange={(event) =>
                        setFormValues((current) => ({
                          ...current,
                          supplierId: event.target.value,
                        }))
                      }
                    >
                      <option value="">Seleccionar proveedor</option>
                      {suppliers.map((supplier) => (
                        <option key={supplier.id} value={supplier.id}>
                          {supplier.name}
                        </option>
                      ))}
                    </select>
                    {suppliers.length === 0 ? (
                      <span className="mt-1 block text-xs text-amber-700">
                        Registra y activa un proveedor antes de crear la compra.
                      </span>
                    ) : null}
                  </label>
                  <FormInput
                    label="Fecha de compra *"
                    type="date"
                    value={formValues.purchaseDate}
                    disabled={isSaving}
                    required
                    onChange={(value) =>
                      setFormValues((current) => ({
                        ...current,
                        purchaseDate: value,
                      }))
                    }
                  />
                  <FormInput
                    label="Número de documento"
                    value={formValues.documentNumber}
                    disabled={isSaving}
                    placeholder="Factura, nota o recibo"
                    onChange={(value) =>
                      setFormValues((current) => ({
                        ...current,
                        documentNumber: value,
                      }))
                    }
                  />
                  <label className="block">
                    <span className="text-sm font-medium text-slate-700">
                      Tipo de documento
                    </span>
                    <select
                      className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                      value={formValues.documentType}
                      disabled={isSaving}
                      onChange={(event) =>
                        setFormValues((current) => ({
                          ...current,
                          documentType: event.target
                            .value as PurchaseFormValues["documentType"],
                        }))
                      }
                    >
                      <option value="">Sin especificar</option>
                      {Object.entries(PURCHASE_DOCUMENT_TYPE_LABELS).map(
                        ([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ),
                      )}
                    </select>
                  </label>
                  <label className="block">
                    <span className="text-sm font-medium text-slate-700">
                      Estado de pago
                    </span>
                    <select
                      className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                      value={formValues.paymentStatus}
                      disabled={isSaving}
                      onChange={(event) =>
                        setFormValues((current) => ({
                          ...current,
                          paymentStatus: event.target
                            .value as PurchasePaymentStatus,
                        }))
                      }
                    >
                      {Object.entries(PURCHASE_PAYMENT_STATUS_LABELS).map(
                        ([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ),
                      )}
                    </select>
                    <span className="mt-1 block text-xs text-slate-500">
                      Informativo; aquí no se registra un pago.
                    </span>
                  </label>
                  <label className="block md:col-span-2 xl:col-span-1">
                    <span className="text-sm font-medium text-slate-700">
                      Notas
                    </span>
                    <textarea
                      className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
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
                </div>

                <div className="mt-6 flex flex-col gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-950">
                      Items de compra
                    </h3>
                    <p className="mt-1 text-sm text-slate-600">
                      El producto es opcional; sin producto debes escribir una
                      descripción.
                    </p>
                  </div>
                  <button
                    className="h-9 rounded-md border border-water-700 bg-white px-3 text-sm font-semibold text-water-700 hover:bg-water-50"
                    type="button"
                    disabled={isSaving}
                    onClick={addItem}
                  >
                    Agregar item
                  </button>
                </div>

                <div className="mt-4 space-y-4">
                  {formValues.items.map((item, index) => (
                    <article
                      className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                      key={item.key}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <h4 className="font-semibold text-slate-900">
                          Item {index + 1}
                        </h4>
                        <button
                          className="text-sm font-semibold text-red-700 hover:text-red-500 disabled:text-slate-400"
                          type="button"
                          disabled={isSaving || formValues.items.length === 1}
                          onClick={() => removeItem(item.key)}
                        >
                          Quitar
                        </button>
                      </div>
                      <div className="mt-3 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                        <label className="block">
                          <span className="text-sm font-medium text-slate-700">
                            Producto opcional
                          </span>
                          <select
                            className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                            value={item.productId}
                            disabled={isSaving}
                            onChange={(event) => {
                              const productId = event.target.value;
                              const product = products.find(
                                (candidate) =>
                                  candidate.id === Number(productId),
                              );
                              updateItem(item.key, {
                                productId,
                                ...(!item.description.trim() && product
                                  ? { description: product.name }
                                  : {}),
                              });
                            }}
                          >
                            <option value="">Descripción manual</option>
                            {products.map((product) => (
                              <option key={product.id} value={product.id}>
                                {product.sku ? `${product.sku} · ` : ""}
                                {product.name}
                              </option>
                            ))}
                          </select>
                        </label>
                        <FormInput
                          label={
                            item.productId
                              ? "Descripción"
                              : "Descripción *"
                          }
                          value={item.description}
                          disabled={isSaving}
                          required={!item.productId}
                          onChange={(value) =>
                            updateItem(item.key, { description: value })
                          }
                        />
                        <FormInput
                          label="Cantidad *"
                          type="number"
                          value={item.quantity}
                          disabled={isSaving}
                          required
                          min="0.001"
                          step="0.001"
                          onChange={(value) =>
                            updateItem(item.key, { quantity: value })
                          }
                        />
                        <FormInput
                          label="Costo unitario *"
                          type="number"
                          value={item.unitCost}
                          disabled={isSaving}
                          required
                          min="0"
                          step="0.01"
                          onChange={(value) =>
                            updateItem(item.key, { unitCost: value })
                          }
                        />
                        <FormInput
                          label="Descuento"
                          type="number"
                          value={item.discountAmount}
                          disabled={isSaving}
                          min="0"
                          step="0.01"
                          onChange={(value) =>
                            updateItem(item.key, { discountAmount: value })
                          }
                        />
                        <FormInput
                          label="Impuesto"
                          type="number"
                          value={item.taxAmount}
                          disabled={isSaving}
                          min="0"
                          step="0.01"
                          onChange={(value) =>
                            updateItem(item.key, { taxAmount: value })
                          }
                        />
                      </div>
                      <label className="mt-4 block">
                        <span className="text-sm font-medium text-slate-700">
                          Notas del item
                        </span>
                        <input
                          className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                          value={item.notes}
                          disabled={isSaving}
                          onChange={(event) =>
                            updateItem(item.key, { notes: event.target.value })
                          }
                        />
                      </label>
                      <p className="mt-3 text-right text-sm font-semibold text-slate-700">
                        Total estimado del item:{" "}
                        {formatMoney(estimateItemTotal(item))}
                      </p>
                    </article>
                  ))}
                </div>

                <div className="mt-5 rounded-lg border border-water-200 bg-water-50 p-4 text-right">
                  <p className="text-sm text-water-800">
                    Ayuda visual; no es el total oficial.
                  </p>
                  <p className="mt-1 text-xl font-semibold text-water-950">
                    Total estimado:{" "}
                    {formatMoney(
                      formValues.items.reduce(
                        (total, item) => total + estimateItemTotal(item),
                        0,
                      ),
                    )}
                  </p>
                </div>

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
                    disabled={isSaving || suppliers.length === 0}
                  >
                    {isSaving ? "Guardando..." : "Guardar compra"}
                  </button>
                </div>
              </form>
            ) : null}

            <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-base font-semibold text-slate-950">
                Buscar compras
              </h2>
              <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
                <FormInput
                  label="Desde"
                  type="date"
                  value={filters.dateFrom}
                  disabled={isFiltering}
                  onChange={(value) =>
                    setFilters((current) => ({
                      ...current,
                      dateFrom: value,
                    }))
                  }
                />
                <FormInput
                  label="Hasta"
                  type="date"
                  value={filters.dateTo}
                  disabled={isFiltering}
                  onChange={(value) =>
                    setFilters((current) => ({ ...current, dateTo: value }))
                  }
                />
                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Proveedor
                  </span>
                  <select
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                    value={filters.supplierId}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        supplierId: event.target.value,
                      }))
                    }
                  >
                    <option value="">Todos</option>
                    {suppliers.map((supplier) => (
                      <option key={supplier.id} value={supplier.id}>
                        {supplier.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Estado
                  </span>
                  <select
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                    value={filters.status}
                    disabled={isFiltering}
                    onChange={(event) =>
                      setFilters((current) => ({
                        ...current,
                        status: event.target
                          .value as PurchaseFilterValues["status"],
                      }))
                    }
                  >
                    <option value="">Todos</option>
                    <option value="active">Activas</option>
                    <option value="voided">Anuladas</option>
                  </select>
                </label>
                <FormInput
                  label="Buscar"
                  value={filters.search}
                  disabled={isFiltering}
                  placeholder="Número, documento o proveedor"
                  onChange={(value) =>
                    setFilters((current) => ({ ...current, search: value }))
                  }
                />
              </div>
              <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  type="button"
                  disabled={isFiltering}
                  onClick={() => {
                    setFilters(emptyFilters);
                    if (token) {
                      loadPurchases(token, emptyFilters);
                    }
                  }}
                >
                  Limpiar
                </button>
                <button
                  className="h-10 rounded-md bg-slate-900 px-4 text-sm font-semibold text-white hover:bg-slate-700"
                  type="button"
                  disabled={isFiltering}
                  onClick={() => token && loadPurchases(token, filters)}
                >
                  {isFiltering ? "Filtrando..." : "Aplicar filtros"}
                </button>
              </div>
            </section>

            <section className="space-y-3">
              <div>
                <p className="text-sm font-medium text-water-700">Historial</p>
                <h2 className="mt-1 text-xl font-semibold text-slate-950">
                  Compras registradas
                </h2>
              </div>
              {purchases.length === 0 ? (
                <p className="rounded-lg border border-dashed border-slate-300 bg-white px-5 py-8 text-center text-sm text-slate-600">
                  {hasFilters(appliedFilters)
                    ? "No hay compras que coincidan con los filtros."
                    : "Todavía no hay compras registradas."}
                </p>
              ) : (
                <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-sm">
                      <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                        <tr>
                          <th className="px-4 py-3">Compra</th>
                          <th className="px-4 py-3">Proveedor</th>
                          <th className="px-4 py-3">Documento</th>
                          <th className="px-4 py-3 text-right">Total</th>
                          <th className="px-4 py-3">Pago</th>
                          <th className="px-4 py-3">Estado</th>
                          <th className="px-4 py-3 text-right">Acciones</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {purchases.map((purchase) => (
                          <tr key={purchase.id}>
                            <td className="whitespace-nowrap px-4 py-3">
                              <p className="font-semibold text-slate-950">
                                {purchase.purchase_number}
                              </p>
                              <p className="mt-0.5 text-slate-500">
                                {formatDate(purchase.purchase_date)}
                              </p>
                            </td>
                            <td className="px-4 py-3 text-slate-700">
                              {purchase.supplier.name}
                            </td>
                            <td className="px-4 py-3 text-slate-700">
                              {purchase.document_number ?? "—"}
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-right font-semibold text-slate-950">
                              {formatMoney(Number(purchase.total_amount))}
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-slate-700">
                              {
                                PURCHASE_PAYMENT_STATUS_LABELS[
                                  purchase.payment_status
                                ]
                              }
                            </td>
                            <td className="whitespace-nowrap px-4 py-3">
                              <StatusBadge status={purchase.status} />
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-right">
                              <button
                                className="mr-3 font-semibold text-water-700 hover:text-water-500"
                                type="button"
                                disabled={isLoadingDetail}
                                onClick={() => handleViewDetail(purchase)}
                              >
                                Ver detalle
                              </button>
                              {purchase.status === "active" ? (
                                <button
                                  className="font-semibold text-red-700 hover:text-red-500"
                                  type="button"
                                  onClick={() => openVoidDialog(purchase)}
                                >
                                  Anular
                                </button>
                              ) : null}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </section>
          </>
        )}
      </div>

      {viewingPurchase ? (
        <PurchaseDetail
          purchase={viewingPurchase}
          onClose={() => setViewingPurchase(null)}
          onVoid={
            viewingPurchase.status === "active"
              ? () => openVoidDialog(viewingPurchase)
              : undefined
          }
        />
      ) : null}

      {voidingPurchase ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="void-purchase-title"
        >
          <form
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl"
            onSubmit={handleVoidPurchase}
          >
            <div className="border-b border-slate-200 px-5 py-4">
              <h2
                className="text-lg font-semibold text-slate-950"
                id="void-purchase-title"
              >
                Anular compra
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {voidingPurchase.purchase_number}
              </p>
            </div>
            <div className="space-y-4 p-5">
              {voidError ? <ErrorMessage message={voidError} /> : null}
              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Motivo de anulación *
                </span>
                <textarea
                  className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                  value={voidReason}
                  required
                  disabled={isVoiding}
                  onChange={(event) => setVoidReason(event.target.value)}
                />
              </label>
              <p className="text-sm leading-6 text-slate-600">
                La compra y sus items se conservarán como anulados. Esta acción
                no modifica inventario, caja ni gastos.
              </p>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  type="button"
                  disabled={isVoiding}
                  onClick={() => setVoidingPurchase(null)}
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

function PurchaseDetail({
  purchase,
  onClose,
  onVoid,
}: {
  purchase: Purchase;
  onClose: () => void;
  onVoid?: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-40 overflow-y-auto bg-slate-950/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="purchase-detail-title"
    >
      <div className="mx-auto my-6 w-full max-w-4xl rounded-lg border border-slate-200 bg-white shadow-xl">
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div>
            <h2
              className="text-lg font-semibold text-slate-950"
              id="purchase-detail-title"
            >
              {purchase.purchase_number}
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              {purchase.supplier.name} · {formatDate(purchase.purchase_date)}
            </p>
          </div>
          <button
            className="text-sm font-semibold text-slate-600 hover:text-slate-950"
            type="button"
            onClick={onClose}
          >
            Cerrar
          </button>
        </div>
        <div className="space-y-5 p-5">
          <div className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
            <Detail
              label="Documento"
              value={purchase.document_number ?? "—"}
            />
            <Detail
              label="Tipo"
              value={
                purchase.document_type
                  ? PURCHASE_DOCUMENT_TYPE_LABELS[purchase.document_type]
                  : "—"
              }
            />
            <Detail
              label="Pago"
              value={
                PURCHASE_PAYMENT_STATUS_LABELS[purchase.payment_status]
              }
            />
            <div>
              <dt className="font-medium text-slate-500">Estado</dt>
              <dd className="mt-1">
                <StatusBadge status={purchase.status} />
              </dd>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Item</th>
                  <th className="px-4 py-3 text-right">Cantidad</th>
                  <th className="px-4 py-3 text-right">Costo</th>
                  <th className="px-4 py-3 text-right">Descuento</th>
                  <th className="px-4 py-3 text-right">Impuesto</th>
                  <th className="px-4 py-3 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {purchase.items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-950">
                        {item.product_name_snapshot ??
                          item.description ??
                          "Item"}
                      </p>
                      {item.product_sku_snapshot ||
                      item.product_presentation_snapshot ? (
                        <p className="mt-0.5 text-xs text-slate-500">
                          {[item.product_sku_snapshot, item.product_presentation_snapshot]
                            .filter(Boolean)
                            .join(" · ")}
                        </p>
                      ) : null}
                      {item.description &&
                      item.description !== item.product_name_snapshot ? (
                        <p className="mt-1 text-xs text-slate-600">
                          {item.description}
                        </p>
                      ) : null}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-right text-slate-700">
                      {item.quantity}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-right text-slate-700">
                      {formatMoney(Number(item.unit_cost))}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-right text-slate-700">
                      {formatMoney(Number(item.discount_amount))}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-right text-slate-700">
                      {formatMoney(Number(item.tax_amount))}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-right font-semibold text-slate-950">
                      {formatMoney(Number(item.total_amount))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <dl className="ml-auto grid max-w-sm gap-2 text-sm">
            <MoneyDetail
              label="Subtotal después de descuentos"
              amount={purchase.subtotal_amount}
            />
            <MoneyDetail
              label="Descuentos incluidos"
              amount={purchase.discount_amount}
            />
            <MoneyDetail label="Impuestos" amount={purchase.tax_amount} />
            <MoneyDetail
              label="Total oficial"
              amount={purchase.total_amount}
              prominent
            />
          </dl>

          {purchase.notes ? (
            <p className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">
              {purchase.notes}
            </p>
          ) : null}
          {purchase.status === "voided" ? (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              Motivo de anulación: {purchase.void_reason}
            </p>
          ) : null}
          <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Esta compra es un registro administrativo. No ha modificado
            inventario ni caja.
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              type="button"
              onClick={onClose}
            >
              Cerrar
            </button>
            {onVoid ? (
              <button
                className="h-10 rounded-md bg-red-700 px-4 text-sm font-semibold text-white hover:bg-red-600"
                type="button"
                onClick={onVoid}
              >
                Anular compra
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

function FormInput({
  label,
  value,
  onChange,
  disabled,
  type = "text",
  required = false,
  placeholder,
  min,
  step,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
  type?: string;
  required?: boolean;
  placeholder?: string;
  min?: string;
  step?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        type={type}
        value={value}
        required={required}
        placeholder={placeholder}
        min={min}
        step={step}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function StatusBadge({ status }: { status: PurchaseStatus }) {
  return (
    <span
      className={
        status === "active"
          ? "inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700"
          : "inline-flex rounded-full bg-red-100 px-2.5 py-1 text-xs font-semibold text-red-700"
      }
    >
      {PURCHASE_STATUS_LABELS[status]}
    </span>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-medium text-slate-500">{label}</dt>
      <dd className="mt-0.5 text-slate-950">{value}</dd>
    </div>
  );
}

function MoneyDetail({
  label,
  amount,
  prominent = false,
}: {
  label: string;
  amount: string;
  prominent?: boolean;
}) {
  return (
    <div
      className={
        prominent
          ? "flex items-center justify-between border-t border-slate-300 pt-2 text-base font-semibold text-slate-950"
          : "flex items-center justify-between text-slate-700"
      }
    >
      <dt>{label}</dt>
      <dd>{formatMoney(Number(amount))}</dd>
    </div>
  );
}

function createEmptyForm(): PurchaseFormValues {
  return {
    supplierId: "",
    purchaseDate: getTodayISODate(),
    documentNumber: "",
    documentType: "",
    paymentStatus: "unpaid",
    notes: "",
    items: [createEmptyItem(1)],
  };
}

function createEmptyItem(key: number): PurchaseItemDraft {
  return {
    key,
    productId: "",
    description: "",
    quantity: "1",
    unitCost: "0.00",
    discountAmount: "0.00",
    taxAmount: "0.00",
    notes: "",
  };
}

function validatePurchase(values: PurchaseFormValues): string {
  if (!values.supplierId) {
    return "Selecciona un proveedor activo.";
  }
  if (!values.purchaseDate) {
    return "La fecha de compra es obligatoria.";
  }
  if (values.items.length === 0) {
    return "La compra debe tener al menos un item.";
  }
  for (const [index, item] of values.items.entries()) {
    const itemNumber = index + 1;
    if (!item.productId && !item.description.trim()) {
      return `Escribe la descripción del item ${itemNumber}.`;
    }
    const quantity = Number(item.quantity);
    const unitCost = Number(item.unitCost);
    const discount = Number(item.discountAmount || "0");
    const tax = Number(item.taxAmount || "0");
    if (!Number.isFinite(quantity) || quantity <= 0) {
      return `La cantidad del item ${itemNumber} debe ser mayor a cero.`;
    }
    if (!Number.isFinite(unitCost) || unitCost < 0) {
      return `El costo unitario del item ${itemNumber} no puede ser negativo.`;
    }
    if (!Number.isFinite(discount) || discount < 0) {
      return `El descuento del item ${itemNumber} no puede ser negativo.`;
    }
    if (!Number.isFinite(tax) || tax < 0) {
      return `El impuesto del item ${itemNumber} no puede ser negativo.`;
    }
    if (discount > quantity * unitCost) {
      return `El descuento del item ${itemNumber} deja un subtotal negativo.`;
    }
  }
  return "";
}

function estimateItemTotal(item: PurchaseItemDraft): number {
  const quantity = Number(item.quantity);
  const unitCost = Number(item.unitCost);
  const discount = Number(item.discountAmount || "0");
  const tax = Number(item.taxAmount || "0");
  if (
    !Number.isFinite(quantity) ||
    !Number.isFinite(unitCost) ||
    !Number.isFinite(discount) ||
    !Number.isFinite(tax)
  ) {
    return 0;
  }
  return Math.max(0, quantity * unitCost - discount + tax);
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function formatMoney(value: number): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(Number.isFinite(value) ? value : 0);
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function hasFilters(filters: PurchaseFilterValues): boolean {
  return Boolean(
    filters.dateFrom ||
      filters.dateTo ||
      filters.status ||
      filters.supplierId ||
      filters.search,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

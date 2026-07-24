"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createPriceList,
  createPriceListItem,
  getPriceList,
  listCustomers,
  listDeliveryRoutes,
  listPriceLists,
  listProducts,
  resolveProductPrice,
  setPriceListActive,
  setPriceListItemActive,
  updatePriceList,
  updatePriceListItem,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { Customer } from "@/types/customer";
import type { DeliveryRoute } from "@/types/deliveryRoute";
import {
  PRICE_LIST_TYPE_LABELS,
  PRICE_SOURCE_LABELS,
  type PriceList,
  type PriceListFilters,
  type PriceListItem,
  type PriceListType,
  type PriceResolution,
} from "@/types/pricing";
import type { Product } from "@/types/product";

type ListForm = {
  name: string;
  listType: PriceListType;
  customerId: string;
  routeId: string;
  priority: string;
  validFrom: string;
  validTo: string;
  notes: string;
};

type ItemForm = {
  productId: string;
  unitPrice: string;
  minQuantity: string;
  notes: string;
};

type FilterForm = {
  search: string;
  listType: "" | PriceListType;
  isActive: "" | "true" | "false";
};

const emptyFilters: FilterForm = {
  search: "",
  listType: "",
  isActive: "",
};

export default function PricingPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [routes, setRoutes] = useState<DeliveryRoute[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [priceLists, setPriceLists] = useState<PriceList[]>([]);
  const [selectedList, setSelectedList] = useState<PriceList | null>(null);
  const [filters, setFilters] = useState<FilterForm>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<FilterForm>(emptyFilters);
  const [listForm, setListForm] = useState<ListForm>(emptyListForm);
  const [itemForm, setItemForm] = useState<ItemForm>(emptyItemForm);
  const [editingListId, setEditingListId] = useState<number | null>(null);
  const [editingItemId, setEditingItemId] = useState<number | null>(null);
  const [isListFormOpen, setIsListFormOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    void loadInitialData(storedToken);
  }, [router]);

  async function loadInitialData(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const [loadedCustomers, loadedRoutes, loadedProducts, loadedLists] =
        await Promise.all([
          listCustomers(activeToken),
          listDeliveryRoutes(activeToken),
          listProducts(activeToken, { is_active: true }),
          listPriceLists(activeToken),
        ]);
      setCustomers(loadedCustomers);
      setRoutes(loadedRoutes);
      setProducts(loadedProducts);
      setPriceLists(loadedLists);
      setSelectedList(loadedLists[0] ?? null);
    } catch (loadError) {
      if (!redirectIfUnauthorized(loadError)) {
        setError(getErrorMessage(loadError));
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function loadLists(
    activeToken: string,
    activeFilters: FilterForm,
    keepSelectedId?: number | null,
  ) {
    setIsFiltering(true);
    try {
      const loadedLists = await listPriceLists(
        activeToken,
        toApiFilters(activeFilters),
      );
      setPriceLists(loadedLists);
      const selectedId = keepSelectedId ?? selectedList?.id;
      setSelectedList(
        loadedLists.find((priceList) => priceList.id === selectedId) ??
          loadedLists[0] ??
          null,
      );
      setAppliedFilters({ ...activeFilters });
    } catch (loadError) {
      if (!redirectIfUnauthorized(loadError)) {
        setError(getErrorMessage(loadError));
      }
    } finally {
      setIsFiltering(false);
    }
  }

  async function refreshSelectedList(priceListId: number) {
    if (!token) {
      return;
    }
    const detail = await getPriceList(token, priceListId);
    setSelectedList(detail);
    setPriceLists((current) =>
      current.map((priceList) =>
        priceList.id === detail.id ? detail : priceList,
      ),
    );
  }

  function openNewList() {
    setListForm(emptyListForm());
    setEditingListId(null);
    setIsListFormOpen(true);
    clearNotices();
  }

  function openListEdit(priceList: PriceList) {
    setListForm({
      name: priceList.name,
      listType: priceList.list_type,
      customerId: priceList.customer_id?.toString() ?? "",
      routeId: priceList.route_id?.toString() ?? "",
      priority: priceList.priority.toString(),
      validFrom: priceList.valid_from ?? "",
      validTo: priceList.valid_to ?? "",
      notes: priceList.notes ?? "",
    });
    setEditingListId(priceList.id);
    setIsListFormOpen(true);
    clearNotices();
  }

  async function handleSaveList(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    const validationError = validateListForm(listForm);
    if (validationError) {
      setError(validationError);
      return;
    }
    const payload = {
      name: listForm.name.trim(),
      list_type: listForm.listType,
      customer_id: listForm.customerId
        ? Number(listForm.customerId)
        : null,
      route_id: listForm.routeId ? Number(listForm.routeId) : null,
      priority: Number(listForm.priority || 0),
      valid_from: listForm.validFrom || null,
      valid_to: listForm.validTo || null,
      notes: optionalText(listForm.notes),
    };
    setIsSaving(true);
    clearNotices();
    try {
      const savedList = editingListId
        ? await updatePriceList(token, editingListId, payload)
        : await createPriceList(token, payload);
      setMessage(
        editingListId
          ? `Lista ${savedList.name} actualizada.`
          : `Lista ${savedList.name} creada.`,
      );
      setSelectedList(savedList);
      setIsListFormOpen(false);
      setEditingListId(null);
      setListForm(emptyListForm());
      await loadLists(token, appliedFilters, savedList.id);
    } catch (saveError) {
      if (!redirectIfUnauthorized(saveError)) {
        setError(getErrorMessage(saveError));
      }
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggleList(priceList: PriceList) {
    if (!token) {
      return;
    }
    setBusyId(priceList.id);
    clearNotices();
    try {
      const updated = await setPriceListActive(
        token,
        priceList.id,
        !priceList.is_active,
      );
      setMessage(
        `Lista ${updated.name} ${updated.is_active ? "activada" : "desactivada"}.`,
      );
      await loadLists(token, appliedFilters, updated.id);
    } catch (toggleError) {
      if (!redirectIfUnauthorized(toggleError)) {
        setError(getErrorMessage(toggleError));
      }
    } finally {
      setBusyId(null);
    }
  }

  function openItemEdit(item: PriceListItem) {
    setEditingItemId(item.id);
    setItemForm({
      productId: item.product_id.toString(),
      unitPrice: item.unit_price,
      minQuantity: item.min_quantity,
      notes: item.notes ?? "",
    });
    clearNotices();
  }

  async function handleSaveItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedList) {
      return;
    }
    const validationError = validateItemForm(itemForm);
    if (validationError) {
      setError(validationError);
      return;
    }
    const payload = {
      product_id: Number(itemForm.productId),
      unit_price: itemForm.unitPrice,
      min_quantity: itemForm.minQuantity,
      notes: optionalText(itemForm.notes),
    };
    setIsSaving(true);
    clearNotices();
    try {
      if (editingItemId) {
        await updatePriceListItem(token, editingItemId, payload);
        setMessage("Precio actualizado.");
      } else {
        await createPriceListItem(token, selectedList.id, payload);
        setMessage("Producto agregado a la lista.");
      }
      setEditingItemId(null);
      setItemForm(emptyItemForm());
      await refreshSelectedList(selectedList.id);
    } catch (saveError) {
      if (!redirectIfUnauthorized(saveError)) {
        setError(getErrorMessage(saveError));
      }
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggleItem(item: PriceListItem) {
    if (!token || !selectedList) {
      return;
    }
    setBusyId(-item.id);
    clearNotices();
    try {
      const updated = await setPriceListItemActive(
        token,
        item.id,
        !item.is_active,
      );
      setMessage(
        `Precio de ${updated.product_name} ${updated.is_active ? "activado" : "desactivado"}.`,
      );
      await refreshSelectedList(selectedList.id);
    } catch (toggleError) {
      if (!redirectIfUnauthorized(toggleError)) {
        setError(getErrorMessage(toggleError));
      }
    } finally {
      setBusyId(null);
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

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6">
        <div className="mx-auto max-w-7xl">
          <LoadingState label="Cargando listas de precios..." />
        </div>
      </main>
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
              Listas de precios
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Configura precios especiales por cliente, ruta o combinación
              cliente+ruta. Si no existe precio especial, se usa el precio
              normal del producto.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500"
              type="button"
              onClick={openNewList}
            >
              Nueva lista
            </button>
            <LogoutButton />
          </div>
        </header>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isListFormOpen ? (
          <ListEditor
            customers={customers}
            routes={routes}
            values={listForm}
            isSaving={isSaving}
            isEditing={editingListId !== null}
            onChange={setListForm}
            onCancel={() => setIsListFormOpen(false)}
            onSubmit={handleSaveList}
          />
        ) : null}

        <PriceListFilters
          values={filters}
          isFiltering={isFiltering}
          onChange={setFilters}
          onApply={() => token && void loadLists(token, filters)}
          onClear={() => {
            setFilters(emptyFilters);
            if (token) {
              void loadLists(token, emptyFilters);
            }
          }}
        />

        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.65fr)]">
          <PriceListCards
            priceLists={priceLists}
            selectedId={selectedList?.id ?? null}
            busyId={busyId}
            onSelect={setSelectedList}
            onToggle={(priceList) => void handleToggleList(priceList)}
          />

          {selectedList ? (
            <PriceListDetail
              priceList={selectedList}
              products={products}
              itemForm={itemForm}
              editingItemId={editingItemId}
              isSaving={isSaving}
              busyId={busyId}
              onEditList={() => openListEdit(selectedList)}
              onChangeItem={setItemForm}
              onSaveItem={handleSaveItem}
              onCancelItem={() => {
                setEditingItemId(null);
                setItemForm(emptyItemForm());
              }}
              onEditItem={openItemEdit}
              onToggleItem={(item) => void handleToggleItem(item)}
            />
          ) : (
            <section className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-600">
              Crea una lista de precios para comenzar.
            </section>
          )}
        </div>

        {token ? (
          <QuickPriceResolver
            token={token}
            customers={customers}
            routes={routes}
            products={products}
            onUnauthorized={redirectIfUnauthorized}
          />
        ) : null}
      </div>
    </main>
  );
}

function ListEditor({
  customers,
  routes,
  values,
  isSaving,
  isEditing,
  onChange,
  onCancel,
  onSubmit,
}: {
  customers: Customer[];
  routes: DeliveryRoute[];
  values: ListForm;
  isSaving: boolean;
  isEditing: boolean;
  onChange: (values: ListForm) => void;
  onCancel: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const needsCustomer =
    values.listType === "customer" || values.listType === "customer_route";
  const needsRoute =
    values.listType === "route" || values.listType === "customer_route";
  return (
    <section className="rounded-lg border border-water-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-3">
        <h2 className="font-semibold text-slate-950">
          {isEditing ? "Editar lista" : "Nueva lista de precios"}
        </h2>
      </div>
      <form className="space-y-4 p-5" onSubmit={onSubmit}>
        <div className="grid gap-4 md:grid-cols-3">
          <Field label="Nombre">
            <input
              className={inputClass}
              value={values.name}
              required
              disabled={isSaving}
              onChange={(event) =>
                onChange({ ...values, name: event.target.value })
              }
            />
          </Field>
          <Field label="Tipo">
            <select
              className={inputClass}
              value={values.listType}
              disabled={isSaving}
              onChange={(event) => {
                const listType = event.target.value as PriceListType;
                onChange({
                  ...values,
                  listType,
                  customerId:
                    listType === "customer" || listType === "customer_route"
                      ? values.customerId
                      : "",
                  routeId:
                    listType === "route" || listType === "customer_route"
                      ? values.routeId
                      : "",
                });
              }}
            >
              {Object.entries(PRICE_LIST_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Prioridad">
            <input
              className={inputClass}
              type="number"
              step="1"
              value={values.priority}
              disabled={isSaving}
              onChange={(event) =>
                onChange({ ...values, priority: event.target.value })
              }
            />
          </Field>
          {needsCustomer ? (
            <Field label="Cliente">
              <select
                className={inputClass}
                value={values.customerId}
                required
                disabled={isSaving}
                onChange={(event) =>
                  onChange({ ...values, customerId: event.target.value })
                }
              >
                <option value="">Seleccionar cliente</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name}
                    {!customer.is_active ? " (inactivo)" : ""}
                  </option>
                ))}
              </select>
            </Field>
          ) : null}
          {needsRoute ? (
            <Field label="Ruta">
              <select
                className={inputClass}
                value={values.routeId}
                required
                disabled={isSaving}
                onChange={(event) =>
                  onChange({ ...values, routeId: event.target.value })
                }
              >
                <option value="">Seleccionar ruta</option>
                {routes.map((route) => (
                  <option key={route.id} value={route.id}>
                    {route.name}
                    {!route.is_active ? " (inactiva)" : ""}
                  </option>
                ))}
              </select>
            </Field>
          ) : null}
          <Field label="Válida desde">
            <input
              className={inputClass}
              type="date"
              value={values.validFrom}
              disabled={isSaving}
              onChange={(event) =>
                onChange({ ...values, validFrom: event.target.value })
              }
            />
          </Field>
          <Field label="Válida hasta">
            <input
              className={inputClass}
              type="date"
              value={values.validTo}
              disabled={isSaving}
              onChange={(event) =>
                onChange({ ...values, validTo: event.target.value })
              }
            />
          </Field>
        </div>
        <Field label="Notas">
          <textarea
            className={`${inputClass} min-h-20 py-2`}
            value={values.notes}
            disabled={isSaving}
            onChange={(event) =>
              onChange({ ...values, notes: event.target.value })
            }
          />
        </Field>
        <div className="flex justify-end gap-3">
          <button
            className={secondaryButtonClass}
            type="button"
            disabled={isSaving}
            onClick={onCancel}
          >
            Cancelar
          </button>
          <button className={primaryButtonClass} disabled={isSaving}>
            {isSaving ? "Guardando..." : "Guardar lista"}
          </button>
        </div>
      </form>
    </section>
  );
}

function PriceListFilters({
  values,
  isFiltering,
  onChange,
  onApply,
  onClear,
}: {
  values: FilterForm;
  isFiltering: boolean;
  onChange: (values: FilterForm) => void;
  onApply: () => void;
  onClear: () => void;
}) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-[1fr_220px_180px_auto]">
        <input
          className={inputClass}
          placeholder="Buscar lista..."
          value={values.search}
          onChange={(event) =>
            onChange({ ...values, search: event.target.value })
          }
        />
        <select
          className={inputClass}
          value={values.listType}
          onChange={(event) =>
            onChange({
              ...values,
              listType: event.target.value as "" | PriceListType,
            })
          }
        >
          <option value="">Todos los tipos</option>
          {Object.entries(PRICE_LIST_TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select
          className={inputClass}
          value={values.isActive}
          onChange={(event) =>
            onChange({
              ...values,
              isActive: event.target.value as "" | "true" | "false",
            })
          }
        >
          <option value="">Todos los estados</option>
          <option value="true">Activas</option>
          <option value="false">Inactivas</option>
        </select>
        <div className="flex gap-2">
          <button
            className={primaryButtonClass}
            type="button"
            disabled={isFiltering}
            onClick={onApply}
          >
            Filtrar
          </button>
          <button
            className={secondaryButtonClass}
            type="button"
            disabled={isFiltering}
            onClick={onClear}
          >
            Limpiar
          </button>
        </div>
      </div>
    </section>
  );
}

function PriceListCards({
  priceLists,
  selectedId,
  busyId,
  onSelect,
  onToggle,
}: {
  priceLists: PriceList[];
  selectedId: number | null;
  busyId: number | null;
  onSelect: (priceList: PriceList) => void;
  onToggle: (priceList: PriceList) => void;
}) {
  return (
    <section className="space-y-3">
      <h2 className="font-semibold text-slate-950">
        Listas configuradas ({priceLists.length})
      </h2>
      {priceLists.length ? (
        priceLists.map((priceList) => (
          <article
            className={`rounded-lg border bg-white p-4 shadow-sm ${
              selectedId === priceList.id
                ? "border-water-500 ring-2 ring-water-100"
                : "border-slate-200"
            }`}
            key={priceList.id}
          >
            <button
              className="w-full text-left"
              type="button"
              onClick={() => onSelect(priceList)}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-950">
                    {priceList.name}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {PRICE_LIST_TYPE_LABELS[priceList.list_type]} · prioridad{" "}
                    {priceList.priority} · {priceList.items.length} precio(s)
                  </p>
                </div>
                <StatusPill active={priceList.is_active} />
              </div>
              {priceList.customer_name || priceList.route_name ? (
                <p className="mt-2 text-sm text-slate-600">
                  {[priceList.customer_name, priceList.route_name]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              ) : null}
            </button>
            <button
              className="mt-3 text-xs font-semibold text-water-700 hover:text-water-500 disabled:text-slate-400"
              type="button"
              disabled={busyId === priceList.id}
              onClick={() => onToggle(priceList)}
            >
              {busyId === priceList.id
                ? "Actualizando..."
                : priceList.is_active
                  ? "Desactivar"
                  : "Activar"}
            </button>
          </article>
        ))
      ) : (
        <p className="rounded-lg border border-dashed border-slate-300 bg-white p-5 text-sm text-slate-600">
          No hay listas que coincidan con los filtros.
        </p>
      )}
    </section>
  );
}

function PriceListDetail({
  priceList,
  products,
  itemForm,
  editingItemId,
  isSaving,
  busyId,
  onEditList,
  onChangeItem,
  onSaveItem,
  onCancelItem,
  onEditItem,
  onToggleItem,
}: {
  priceList: PriceList;
  products: Product[];
  itemForm: ItemForm;
  editingItemId: number | null;
  isSaving: boolean;
  busyId: number | null;
  onEditList: () => void;
  onChangeItem: (values: ItemForm) => void;
  onSaveItem: (event: FormEvent<HTMLFormElement>) => void;
  onCancelItem: () => void;
  onEditItem: (item: PriceListItem) => void;
  onToggleItem: (item: PriceListItem) => void;
}) {
  return (
    <section className="space-y-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold text-slate-950">
              {priceList.name}
            </h2>
            <StatusPill active={priceList.is_active} />
          </div>
          <p className="mt-2 text-sm text-slate-600">
            {PRICE_LIST_TYPE_LABELS[priceList.list_type]}
            {priceList.customer_name ? ` · ${priceList.customer_name}` : ""}
            {priceList.route_name ? ` · ${priceList.route_name}` : ""}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Vigencia: {priceList.valid_from ?? "sin inicio"} a{" "}
            {priceList.valid_to ?? "sin fin"} · prioridad {priceList.priority}
          </p>
        </div>
        <button
          className={secondaryButtonClass}
          type="button"
          onClick={onEditList}
        >
          Editar lista
        </button>
      </div>

      <form
        className="rounded-md border border-slate-200 bg-slate-50 p-4"
        onSubmit={onSaveItem}
      >
        <h3 className="font-semibold text-slate-950">
          {editingItemId ? "Editar precio" : "Agregar producto"}
        </h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Field label="Producto">
            <select
              className={inputClass}
              value={itemForm.productId}
              required
              disabled={isSaving}
              onChange={(event) =>
                onChangeItem({
                  ...itemForm,
                  productId: event.target.value,
                })
              }
            >
              <option value="">Seleccionar producto</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                  {product.presentation ? ` · ${product.presentation}` : ""}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Precio especial">
            <input
              className={inputClass}
              type="number"
              inputMode="decimal"
              min="0"
              step="0.01"
              value={itemForm.unitPrice}
              required
              disabled={isSaving}
              onChange={(event) =>
                onChangeItem({
                  ...itemForm,
                  unitPrice: event.target.value,
                })
              }
            />
          </Field>
          <Field label="Cantidad mínima">
            <input
              className={inputClass}
              type="number"
              inputMode="decimal"
              min="0.001"
              step="0.001"
              value={itemForm.minQuantity}
              required
              disabled={isSaving}
              onChange={(event) =>
                onChangeItem({
                  ...itemForm,
                  minQuantity: event.target.value,
                })
              }
            />
          </Field>
          <Field label="Notas">
            <input
              className={inputClass}
              value={itemForm.notes}
              disabled={isSaving}
              onChange={(event) =>
                onChangeItem({ ...itemForm, notes: event.target.value })
              }
            />
          </Field>
        </div>
        <div className="mt-3 flex justify-end gap-2">
          {editingItemId ? (
            <button
              className={secondaryButtonClass}
              type="button"
              disabled={isSaving}
              onClick={onCancelItem}
            >
              Cancelar
            </button>
          ) : null}
          <button className={primaryButtonClass} disabled={isSaving}>
            {isSaving
              ? "Guardando..."
              : editingItemId
                ? "Actualizar precio"
                : "Agregar precio"}
          </button>
        </div>
      </form>

      <div className="overflow-x-auto rounded-md border border-slate-200">
        <table className="w-full min-w-[700px] border-collapse text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-3 py-2 font-medium">Producto</th>
              <th className="px-3 py-2 font-medium">Cantidad mínima</th>
              <th className="px-3 py-2 text-right font-medium">Precio</th>
              <th className="px-3 py-2 font-medium">Estado</th>
              <th className="px-3 py-2 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {priceList.items.length ? (
              priceList.items.map((item) => (
                <tr key={item.id}>
                  <td className="px-3 py-3">
                    <p className="font-medium text-slate-950">
                      {item.product_name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {item.product_presentation ?? item.product_sku ?? ""}
                    </p>
                  </td>
                  <td className="px-3 py-3">{item.min_quantity}</td>
                  <td className="px-3 py-3 text-right font-semibold">
                    ${item.unit_price}
                  </td>
                  <td className="px-3 py-3">
                    <StatusPill active={item.is_active} />
                  </td>
                  <td className="px-3 py-3">
                    <div className="flex gap-3">
                      <button
                        className="font-semibold text-water-700 hover:text-water-500"
                        type="button"
                        onClick={() => onEditItem(item)}
                      >
                        Editar
                      </button>
                      <button
                        className="font-semibold text-slate-600 hover:text-slate-950 disabled:text-slate-400"
                        type="button"
                        disabled={busyId === -item.id}
                        onClick={() => onToggleItem(item)}
                      >
                        {busyId === -item.id
                          ? "Actualizando..."
                          : item.is_active
                            ? "Desactivar"
                            : "Activar"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-3 py-5 text-center text-slate-500" colSpan={5}>
                  Esta lista todavía no tiene productos.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function QuickPriceResolver({
  token,
  customers,
  routes,
  products,
  onUnauthorized,
}: {
  token: string;
  customers: Customer[];
  routes: DeliveryRoute[];
  products: Product[];
  onUnauthorized: (error: unknown) => boolean;
}) {
  const [productId, setProductId] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [routeId, setRouteId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [priceDate, setPriceDate] = useState(today);
  const [resolution, setResolution] = useState<PriceResolution | null>(null);
  const [error, setError] = useState("");
  const [isResolving, setIsResolving] = useState(false);
  const productById = useMemo(
    () => new Map(products.map((product) => [product.id, product])),
    [products],
  );

  async function handleResolve(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!productId || !isPositive(quantity)) {
      setError("Selecciona un producto e ingresa una cantidad mayor a cero.");
      return;
    }
    setIsResolving(true);
    setError("");
    try {
      setResolution(
        await resolveProductPrice(token, {
          product_id: Number(productId),
          ...(customerId ? { customer_id: Number(customerId) } : {}),
          ...(routeId ? { route_id: Number(routeId) } : {}),
          quantity,
          ...(priceDate ? { price_date: priceDate } : {}),
        }),
      );
    } catch (resolveError) {
      if (!onUnauthorized(resolveError)) {
        setError(getErrorMessage(resolveError));
      }
    } finally {
      setIsResolving(false);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">
        Prueba rápida de precio
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        Consulta qué precio se aplicaría para una combinación específica.
      </p>
      {error ? <div className="mt-4"><ErrorMessage message={error} /></div> : null}
      <form
        className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-6"
        onSubmit={handleResolve}
      >
        <Field label="Producto">
          <select
            className={inputClass}
            value={productId}
            required
            onChange={(event) => setProductId(event.target.value)}
          >
            <option value="">Seleccionar</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Cliente opcional">
          <select
            className={inputClass}
            value={customerId}
            onChange={(event) => setCustomerId(event.target.value)}
          >
            <option value="">Sin cliente</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Ruta opcional">
          <select
            className={inputClass}
            value={routeId}
            onChange={(event) => setRouteId(event.target.value)}
          >
            <option value="">Sin ruta</option>
            {routes.map((route) => (
              <option key={route.id} value={route.id}>
                {route.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Cantidad">
          <input
            className={inputClass}
            type="number"
            min="0.001"
            step="0.001"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
          />
        </Field>
        <Field label="Fecha">
          <input
            className={inputClass}
            type="date"
            value={priceDate}
            onChange={(event) => setPriceDate(event.target.value)}
          />
        </Field>
        <div className="flex items-end">
          <button
            className={`${primaryButtonClass} w-full`}
            disabled={isResolving}
          >
            {isResolving ? "Consultando..." : "Resolver"}
          </button>
        </div>
      </form>
      {resolution ? (
        <div className="mt-4 grid gap-3 rounded-md border border-water-200 bg-water-50 p-4 sm:grid-cols-3">
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">
              Producto
            </p>
            <p className="mt-1 font-semibold text-slate-950">
              {productById.get(resolution.product_id)?.name}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">
              Precio resuelto
            </p>
            <p className="mt-1 text-xl font-semibold text-water-700">
              ${resolution.resolved_price}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">
              Origen
            </p>
            <p className="mt-1 font-semibold text-slate-950">
              {PRICE_SOURCE_LABELS[resolution.price_source]}
            </p>
            <p className="mt-1 text-xs text-slate-600">
              {resolution.price_list_name ?? resolution.pricing_note}
            </p>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function StatusPill({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
        active
          ? "bg-emerald-100 text-emerald-700"
          : "bg-slate-100 text-slate-600"
      }`}
    >
      {active ? "Activa" : "Inactiva"}
    </span>
  );
}

function emptyListForm(): ListForm {
  return {
    name: "",
    listType: "general",
    customerId: "",
    routeId: "",
    priority: "0",
    validFrom: "",
    validTo: "",
    notes: "",
  };
}

function emptyItemForm(): ItemForm {
  return {
    productId: "",
    unitPrice: "",
    minQuantity: "1",
    notes: "",
  };
}

function validateListForm(values: ListForm): string | null {
  if (!values.name.trim()) {
    return "El nombre de la lista es obligatorio.";
  }
  if (
    (values.listType === "customer" ||
      values.listType === "customer_route") &&
    !values.customerId
  ) {
    return "Selecciona el cliente de la lista.";
  }
  if (
    (values.listType === "route" ||
      values.listType === "customer_route") &&
    !values.routeId
  ) {
    return "Selecciona la ruta de la lista.";
  }
  if (
    values.validFrom &&
    values.validTo &&
    values.validFrom > values.validTo
  ) {
    return "La fecha desde no puede ser posterior a la fecha hasta.";
  }
  return null;
}

function validateItemForm(values: ItemForm): string | null {
  if (!values.productId) {
    return "Selecciona un producto.";
  }
  if (!isNonnegativeMoney(values.unitPrice)) {
    return "El precio debe ser mayor o igual a cero y tener máximo dos decimales.";
  }
  if (!isPositive(values.minQuantity)) {
    return "La cantidad mínima debe ser mayor a cero.";
  }
  return null;
}

function toApiFilters(values: FilterForm): PriceListFilters {
  return {
    ...(values.search ? { search: values.search } : {}),
    ...(values.listType ? { list_type: values.listType } : {}),
    ...(values.isActive
      ? { is_active: values.isActive === "true" }
      : {}),
  };
}

function optionalText(value: string): string | null {
  return value.trim() || null;
}

function isNonnegativeMoney(value: string): boolean {
  return /^(?:0|[1-9]\d*)(?:\.\d{1,2})?$/.test(value);
}

function isPositive(value: string): boolean {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0;
}

function today(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function getErrorMessage(possibleError: unknown): string {
  return possibleError instanceof Error
    ? possibleError.message
    : "No se pudo completar la solicitud.";
}

const inputClass =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";
const primaryButtonClass =
  "h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300";
const secondaryButtonClass =
  "h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:border-water-500 hover:text-water-700 disabled:text-slate-400";

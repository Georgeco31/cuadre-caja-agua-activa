"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createProductionRecipe,
  createProductionRecipeItem,
  getProductionRecipe,
  getProductionRecipeCostEstimate,
  listProductionRecipes,
  listProducts,
  setProductionRecipeActive,
  setProductionRecipeItemActive,
  updateProductionRecipe,
  updateProductionRecipeItem,
  voidProductionRecipe,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import {
  PRODUCT_KIND_LABELS,
  type Product,
  type ProductKind,
} from "@/types/product";
import {
  PRODUCTION_RECIPE_STATUS_LABELS,
  type ProductionRecipe,
  type ProductionRecipeCostEstimate,
  type ProductionRecipeFilters,
  type ProductionRecipeItem,
  type ProductionRecipeItemUpdatePayload,
  type ProductionRecipePayload,
  type ProductionRecipeStatus,
  type ProductionRecipeUpdatePayload,
} from "@/types/productionRecipe";

type RecipeFilterValues = {
  search: string;
  status: ProductionRecipeStatus | "";
  outputProductId: string;
  productKind: ProductKind | "";
  isValidToday: "" | "true" | "false";
};

const emptyFilters: RecipeFilterValues = {
  search: "",
  status: "",
  outputProductId: "",
  productKind: "",
  isValidToday: "",
};

export default function ProductionRecipesPage() {
  const canVoid = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [recipes, setRecipes] = useState<ProductionRecipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] =
    useState<ProductionRecipe | null>(null);
  const [filters, setFilters] = useState<RecipeFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<RecipeFilterValues>(emptyFilters);
  const [estimate, setEstimate] =
    useState<ProductionRecipeCostEstimate | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFiltering, setIsFiltering] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [busyKey, setBusyKey] = useState("");
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
    setIsLoading(true);
    setError("");
    try {
      const [loadedProducts, loadedRecipes] = await Promise.all([
        listProducts(activeToken, { is_active: true }),
        listProductionRecipes(activeToken),
      ]);
      setProducts(loadedProducts);
      setRecipes(loadedRecipes);
    } catch (loadError) {
      handleRequestError(loadError);
    } finally {
      setIsLoading(false);
    }
  }

  async function loadRecipes(
    activeToken: string,
    activeFilters: RecipeFilterValues,
    selectedId?: number,
  ) {
    const loadedRecipes = await listProductionRecipes(
      activeToken,
      toApiFilters(activeFilters),
    );
    setRecipes(loadedRecipes);
    setAppliedFilters({ ...activeFilters });
    if (selectedId !== undefined) {
      const detail = await getProductionRecipe(activeToken, selectedId);
      setSelectedRecipe(detail);
    }
  }

  async function handleFilterSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsFiltering(true);
    clearNotices();
    try {
      await loadRecipes(token, filters);
    } catch (requestError) {
      handleRequestError(requestError);
    } finally {
      setIsFiltering(false);
    }
  }

  async function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    setIsFiltering(true);
    clearNotices();
    try {
      await loadRecipes(token, emptyFilters);
    } catch (requestError) {
      handleRequestError(requestError);
    } finally {
      setIsFiltering(false);
    }
  }

  async function handleCreate(payload: ProductionRecipePayload) {
    if (!token) {
      return false;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createProductionRecipe(token, payload);
      await loadRecipes(token, appliedFilters, created.id);
      setEstimate(null);
      setMessage(`Fórmula ${created.recipe_number} creada como inactiva.`);
      return true;
    } catch (requestError) {
      handleRequestError(requestError);
      return false;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSelect(recipe: ProductionRecipe) {
    if (!token) {
      return;
    }
    setBusyKey(`select-${recipe.id}`);
    clearNotices();
    try {
      const detail = await getProductionRecipe(token, recipe.id);
      setSelectedRecipe(detail);
      setEstimate(null);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (requestError) {
      handleRequestError(requestError);
    } finally {
      setBusyKey("");
    }
  }

  async function handleUpdateRecipe(payload: ProductionRecipeUpdatePayload) {
    if (!token || !selectedRecipe) {
      return false;
    }
    setBusyKey("recipe-header");
    clearNotices();
    try {
      const updated = await updateProductionRecipe(
        token,
        selectedRecipe.id,
        payload,
      );
      await loadRecipes(token, appliedFilters, updated.id);
      setEstimate(null);
      setMessage(`Fórmula ${updated.recipe_number} actualizada.`);
      return true;
    } catch (requestError) {
      handleRequestError(requestError);
      return false;
    } finally {
      setBusyKey("");
    }
  }

  async function handleAddItem(payload: {
    input_product_id: number;
    quantity_required: string;
    unit_cost?: string | null;
    waste_percentage?: string;
    notes?: string | null;
  }) {
    if (!token || !selectedRecipe) {
      return false;
    }
    setBusyKey("new-item");
    clearNotices();
    try {
      await createProductionRecipeItem(token, selectedRecipe.id, payload);
      await loadRecipes(token, appliedFilters, selectedRecipe.id);
      setEstimate(null);
      setMessage("Insumo agregado y costos recalculados.");
      return true;
    } catch (requestError) {
      handleRequestError(requestError);
      return false;
    } finally {
      setBusyKey("");
    }
  }

  async function handleUpdateItem(
    item: ProductionRecipeItem,
    payload: ProductionRecipeItemUpdatePayload,
  ) {
    if (!token || !selectedRecipe) {
      return false;
    }
    setBusyKey(`item-${item.id}`);
    clearNotices();
    try {
      await updateProductionRecipeItem(token, item.id, payload);
      await loadRecipes(token, appliedFilters, selectedRecipe.id);
      setEstimate(null);
      setMessage("Insumo actualizado y costos recalculados.");
      return true;
    } catch (requestError) {
      handleRequestError(requestError);
      return false;
    } finally {
      setBusyKey("");
    }
  }

  async function handleToggleItem(item: ProductionRecipeItem) {
    if (!token || !selectedRecipe) {
      return;
    }
    setBusyKey(`item-${item.id}`);
    clearNotices();
    try {
      await setProductionRecipeItemActive(token, item.id, !item.is_active);
      await loadRecipes(token, appliedFilters, selectedRecipe.id);
      setEstimate(null);
      setMessage(
        item.is_active
          ? "Insumo desactivado y excluido del costo."
          : "Insumo activado e incluido en el costo.",
      );
    } catch (requestError) {
      handleRequestError(requestError);
    } finally {
      setBusyKey("");
    }
  }

  async function handleToggleRecipe() {
    if (!token || !selectedRecipe || selectedRecipe.status === "voided") {
      return;
    }
    const nextIsActive = selectedRecipe.status !== "active";
    setBusyKey("recipe-status");
    clearNotices();
    try {
      const updated = await setProductionRecipeActive(
        token,
        selectedRecipe.id,
        nextIsActive,
      );
      await loadRecipes(token, appliedFilters, updated.id);
      setMessage(
        nextIsActive ? "Fórmula activada." : "Fórmula desactivada.",
      );
    } catch (requestError) {
      handleRequestError(requestError);
    } finally {
      setBusyKey("");
    }
  }

  async function handleVoidRecipe() {
    if (!token || !selectedRecipe || selectedRecipe.status === "voided") {
      return;
    }
    const reason = window.prompt(
      `Motivo para anular ${selectedRecipe.recipe_number}:`,
    )?.trim();
    if (!reason) {
      return;
    }
    if (!window.confirm("La fórmula quedará anulada y no podrá modificarse.")) {
      return;
    }
    setBusyKey("recipe-status");
    clearNotices();
    try {
      const updated = await voidProductionRecipe(
        token,
        selectedRecipe.id,
        reason,
      );
      await loadRecipes(token, appliedFilters, updated.id);
      setEstimate(null);
      setMessage(`Fórmula ${updated.recipe_number} anulada.`);
    } catch (requestError) {
      handleRequestError(requestError);
    } finally {
      setBusyKey("");
    }
  }

  async function handleEstimate(outputQuantity: string) {
    if (!token || !selectedRecipe) {
      return false;
    }
    setBusyKey("estimate");
    clearNotices();
    try {
      const result = await getProductionRecipeCostEstimate(
        token,
        selectedRecipe.id,
        outputQuantity,
      );
      setEstimate(result);
      return true;
    } catch (requestError) {
      handleRequestError(requestError);
      return false;
    } finally {
      setBusyKey("");
    }
  }

  function handleRequestError(possibleError: unknown) {
    if (
      possibleError instanceof ApiError &&
      possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(getErrorMessage(possibleError));
  }

  function clearNotices() {
    setError("");
    setMessage("");
  }

  const finishedProducts = products.filter(
    (product) => product.product_kind === "finished_good",
  );
  const inputProducts = products.filter(
    (product) =>
      product.id !== selectedRecipe?.output_product_id &&
      product.product_kind !== "service",
  );

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
              Fórmulas de producción
            </h1>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-600">
              Define insumos, materia prima y costos estimados para producir
              productos de Agua Activa. Este módulo no descuenta inventario
              automáticamente.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link
              className="inline-flex h-10 items-center justify-center rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700"
              href="/dashboard/products"
            >
              Clasificar productos
            </Link>
            <LogoutButton />
          </div>
        </header>

        <section className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <p className="font-semibold">
            El consumo real de insumos se implementará en un bloque posterior.
          </p>
          <p className="mt-1 leading-6">
            Crear o calcular una fórmula no modifica existencias, movimientos,
            caja, compras, ventas ni producciones registradas.
          </p>
        </section>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando fórmulas y productos..." />
        ) : (
          <>
            <div className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
              <RecipeCreateForm
                products={finishedProducts}
                isSubmitting={isSaving}
                onSubmit={handleCreate}
              />
              {selectedRecipe ? (
                <RecipeDetail
                  canVoid={canVoid}
                  key={`${selectedRecipe.id}-${selectedRecipe.updated_at}`}
                  recipe={selectedRecipe}
                  products={products}
                  inputProducts={inputProducts}
                  estimate={estimate}
                  busyKey={busyKey}
                  onUpdate={handleUpdateRecipe}
                  onAddItem={handleAddItem}
                  onUpdateItem={handleUpdateItem}
                  onToggleItem={handleToggleItem}
                  onToggleRecipe={handleToggleRecipe}
                  onVoidRecipe={handleVoidRecipe}
                  onEstimate={handleEstimate}
                  onClose={() => {
                    setSelectedRecipe(null);
                    setEstimate(null);
                  }}
                />
              ) : (
                <section className="flex min-h-72 items-center justify-center rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-950">
                      Gestiona una fórmula
                    </h2>
                    <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
                      Selecciona una fórmula de la lista para editar su
                      encabezado, agregar insumos, cambiar su estado o probar
                      una estimación.
                    </p>
                  </div>
                </section>
              )}
            </div>

            <RecipeFilters
              filters={filters}
              products={products}
              disabled={isFiltering}
              onChange={setFilters}
              onSubmit={handleFilterSubmit}
              onClear={handleClearFilters}
            />

            <RecipeList
              recipes={recipes}
              busyKey={busyKey}
              onSelect={handleSelect}
            />
          </>
        )}
      </div>
    </main>
  );
}

function RecipeCreateForm({
  products,
  isSubmitting,
  onSubmit,
}: {
  products: Product[];
  isSubmitting: boolean;
  onSubmit: (payload: ProductionRecipePayload) => Promise<boolean>;
}) {
  const [name, setName] = useState("");
  const [outputProductId, setOutputProductId] = useState("");
  const [outputQuantity, setOutputQuantity] = useState("1");
  const [validFrom, setValidFrom] = useState("");
  const [validTo, setValidTo] = useState("");
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!name.trim() || !outputProductId) {
      setValidationError("El nombre y el producto terminado son obligatorios.");
      return;
    }
    if (!isPositiveDecimal(outputQuantity, 3)) {
      setValidationError(
        "La cantidad de salida debe ser mayor a cero y tener máximo tres decimales.",
      );
      return;
    }
    if (validFrom && validTo && validFrom > validTo) {
      setValidationError("La fecha desde no puede superar la fecha hasta.");
      return;
    }
    const saved = await onSubmit({
      name: name.trim(),
      output_product_id: Number(outputProductId),
      output_quantity: outputQuantity,
      valid_from: validFrom || null,
      valid_to: validTo || null,
      notes: optionalText(notes),
    });
    if (saved) {
      setName("");
      setOutputProductId("");
      setOutputQuantity("1");
      setValidFrom("");
      setValidTo("");
      setNotes("");
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">Nueva fórmula</h2>
        <p className="mt-1 text-sm text-slate-600">
          Se crea inactiva y puede completarse después con sus insumos.
        </p>
      </div>
      <form className="space-y-4 p-4" onSubmit={handleSubmit}>
        {validationError ? <ValidationError text={validationError} /> : null}
        {products.length === 0 ? (
          <ValidationError text="No hay productos terminados activos. Clasifica al menos uno desde Productos." />
        ) : null}
        <TextInput
          label="Nombre"
          value={name}
          disabled={isSubmitting}
          required
          onChange={setName}
        />
        <SelectInput
          label="Producto terminado"
          value={outputProductId}
          disabled={isSubmitting}
          required
          options={products.map((product) => ({
            value: String(product.id),
            label: productLabel(product),
          }))}
          placeholder="Selecciona un producto"
          onChange={setOutputProductId}
        />
        <DecimalInput
          label="Cantidad de salida"
          value={outputQuantity}
          scale={3}
          disabled={isSubmitting}
          required
          onChange={setOutputQuantity}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <DateInput
            label="Vigente desde"
            value={validFrom}
            disabled={isSubmitting}
            onChange={setValidFrom}
          />
          <DateInput
            label="Vigente hasta"
            value={validTo}
            disabled={isSubmitting}
            onChange={setValidTo}
          />
        </div>
        <TextareaInput
          label="Notas"
          value={notes}
          disabled={isSubmitting}
          onChange={setNotes}
        />
        <button
          className="h-10 w-full rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
          type="submit"
          disabled={isSubmitting || products.length === 0}
        >
          {isSubmitting ? "Creando..." : "Crear fórmula"}
        </button>
      </form>
    </section>
  );
}

function RecipeDetail({
  canVoid,
  recipe,
  products,
  inputProducts,
  estimate,
  busyKey,
  onUpdate,
  onAddItem,
  onUpdateItem,
  onToggleItem,
  onToggleRecipe,
  onVoidRecipe,
  onEstimate,
  onClose,
}: {
  canVoid: boolean;
  recipe: ProductionRecipe;
  products: Product[];
  inputProducts: Product[];
  estimate: ProductionRecipeCostEstimate | null;
  busyKey: string;
  onUpdate: (payload: ProductionRecipeUpdatePayload) => Promise<boolean>;
  onAddItem: (payload: {
    input_product_id: number;
    quantity_required: string;
    unit_cost?: string | null;
    waste_percentage?: string;
    notes?: string | null;
  }) => Promise<boolean>;
  onUpdateItem: (
    item: ProductionRecipeItem,
    payload: ProductionRecipeItemUpdatePayload,
  ) => Promise<boolean>;
  onToggleItem: (item: ProductionRecipeItem) => void;
  onToggleRecipe: () => void;
  onVoidRecipe: () => void;
  onEstimate: (outputQuantity: string) => Promise<boolean>;
  onClose: () => void;
}) {
  const isVoided = recipe.status === "voided";

  return (
    <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold text-slate-950">
              {recipe.recipe_number}
            </h2>
            <StatusBadge status={recipe.status} />
          </div>
          <p className="mt-1 text-sm text-slate-600">
            {recipe.output_product_name} · salida {recipe.output_quantity}
          </p>
        </div>
        <button
          className="text-sm font-semibold text-slate-600 hover:text-slate-950"
          type="button"
          onClick={onClose}
        >
          Cerrar detalle
        </button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <CostCard
          label="Costo estimado total"
          value={recipe.estimated_material_cost}
        />
        <CostCard
          label="Costo estimado por unidad"
          value={recipe.estimated_cost_per_unit}
        />
      </div>

      {recipe.void_reason ? (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          Motivo de anulación: {recipe.void_reason}
        </p>
      ) : null}

      {!isVoided ? (
        <>
          <RecipeHeaderEditor
            recipe={recipe}
            products={products}
            disabled={Boolean(busyKey)}
            isSaving={busyKey === "recipe-header"}
            onSubmit={onUpdate}
          />
          <div className="flex flex-wrap gap-3">
            <button
              className={
                recipe.status === "active"
                  ? "h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:border-water-500"
                  : "h-9 rounded-md bg-emerald-700 px-3 text-sm font-semibold text-white hover:bg-emerald-600"
              }
              type="button"
              disabled={Boolean(busyKey)}
              onClick={onToggleRecipe}
            >
              {busyKey === "recipe-status"
                ? "Actualizando..."
                : recipe.status === "active"
                  ? "Desactivar fórmula"
                  : "Activar fórmula"}
            </button>
            {canVoid ? <button
              className="h-9 rounded-md border border-red-300 px-3 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:text-slate-400"
              type="button"
              disabled={Boolean(busyKey)}
              onClick={onVoidRecipe}
            >
              Anular fórmula
            </button> : null}
          </div>
          <RecipeItemCreateForm
            products={inputProducts}
            disabled={Boolean(busyKey)}
            isSaving={busyKey === "new-item"}
            onSubmit={onAddItem}
          />
        </>
      ) : null}

      <div className="space-y-3">
        <h3 className="font-semibold text-slate-950">
          Insumos de la fórmula ({recipe.items.length})
        </h3>
        {recipe.items.length === 0 ? (
          <p className="rounded-md bg-slate-50 px-3 py-4 text-sm text-slate-600">
            Esta fórmula todavía no tiene insumos. Debe tener al menos uno
            activo antes de poder activarse.
          </p>
        ) : (
          recipe.items.map((item) => (
            <RecipeItemEditor
              key={`${item.id}-${item.updated_at}`}
              item={item}
              disabled={isVoided || Boolean(busyKey)}
              isSaving={busyKey === `item-${item.id}`}
              onSubmit={(payload) => onUpdateItem(item, payload)}
              onToggle={() => onToggleItem(item)}
            />
          ))
        )}
      </div>

      <EstimatePanel
        recipe={recipe}
        estimate={estimate}
        disabled={busyKey === "estimate"}
        onSubmit={onEstimate}
      />
    </section>
  );
}

function RecipeHeaderEditor({
  recipe,
  products,
  disabled,
  isSaving,
  onSubmit,
}: {
  recipe: ProductionRecipe;
  products: Product[];
  disabled: boolean;
  isSaving: boolean;
  onSubmit: (payload: ProductionRecipeUpdatePayload) => Promise<boolean>;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState(recipe.name);
  const [outputProductId, setOutputProductId] = useState(
    String(recipe.output_product_id),
  );
  const [outputQuantity, setOutputQuantity] = useState(recipe.output_quantity);
  const [validFrom, setValidFrom] = useState(recipe.valid_from ?? "");
  const [validTo, setValidTo] = useState(recipe.valid_to ?? "");
  const [notes, setNotes] = useState(recipe.notes ?? "");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!name.trim() || !outputProductId) {
      setValidationError("El nombre y el producto terminado son obligatorios.");
      return;
    }
    if (!isPositiveDecimal(outputQuantity, 3)) {
      setValidationError("La cantidad de salida debe ser mayor a cero.");
      return;
    }
    if (validFrom && validTo && validFrom > validTo) {
      setValidationError("La fecha desde no puede superar la fecha hasta.");
      return;
    }
    const saved = await onSubmit({
      name: name.trim(),
      output_product_id: Number(outputProductId),
      output_quantity: outputQuantity,
      valid_from: validFrom || null,
      valid_to: validTo || null,
      notes: optionalText(notes),
    });
    if (saved) {
      setIsOpen(false);
    }
  }

  if (!isOpen) {
    return (
      <div className="rounded-md bg-slate-50 px-3 py-3">
        <div className="flex items-start justify-between gap-4">
          <div className="text-sm text-slate-600">
            <p className="font-semibold text-slate-950">{recipe.name}</p>
            <p className="mt-1">
              Vigencia: {recipe.valid_from ?? "sin inicio"} a{" "}
              {recipe.valid_to ?? "sin fin"}
            </p>
            {recipe.notes ? <p className="mt-1">{recipe.notes}</p> : null}
          </div>
          <button
            className="shrink-0 text-sm font-semibold text-water-700 hover:text-water-500"
            type="button"
            disabled={disabled}
            onClick={() => setIsOpen(true)}
          >
            Editar
          </button>
        </div>
      </div>
    );
  }

  return (
    <form
      className="space-y-3 rounded-md border border-slate-200 p-3"
      onSubmit={handleSubmit}
    >
      {validationError ? <ValidationError text={validationError} /> : null}
      <TextInput
        label="Nombre"
        value={name}
        disabled={disabled}
        required
        onChange={setName}
      />
      <SelectInput
        label="Producto terminado"
        value={outputProductId}
        disabled={disabled}
        required
        options={products
          .filter(
            (product) =>
              product.product_kind === "finished_good" ||
              product.id === recipe.output_product_id,
          )
          .map((product) => ({
            value: String(product.id),
            label: productLabel(product),
          }))}
        onChange={setOutputProductId}
      />
      <DecimalInput
        label="Cantidad de salida"
        value={outputQuantity}
        scale={3}
        disabled={disabled}
        required
        onChange={setOutputQuantity}
      />
      <div className="grid gap-3 sm:grid-cols-2">
        <DateInput
          label="Vigente desde"
          value={validFrom}
          disabled={disabled}
          onChange={setValidFrom}
        />
        <DateInput
          label="Vigente hasta"
          value={validTo}
          disabled={disabled}
          onChange={setValidTo}
        />
      </div>
      <TextareaInput
        label="Notas"
        value={notes}
        disabled={disabled}
        onChange={setNotes}
      />
      <div className="flex justify-end gap-3">
        <button
          className="h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700"
          type="button"
          disabled={disabled}
          onClick={() => setIsOpen(false)}
        >
          Cancelar
        </button>
        <button
          className="h-9 rounded-md bg-water-700 px-3 text-sm font-semibold text-white disabled:bg-slate-300"
          type="submit"
          disabled={disabled}
        >
          {isSaving ? "Guardando..." : "Guardar encabezado"}
        </button>
      </div>
    </form>
  );
}

function RecipeItemCreateForm({
  products,
  disabled,
  isSaving,
  onSubmit,
}: {
  products: Product[];
  disabled: boolean;
  isSaving: boolean;
  onSubmit: (payload: {
    input_product_id: number;
    quantity_required: string;
    unit_cost?: string | null;
    waste_percentage?: string;
    notes?: string | null;
  }) => Promise<boolean>;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitCost, setUnitCost] = useState("");
  const [waste, setWaste] = useState("0");
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState("");

  function handleProductChange(value: string) {
    setProductId(value);
    const product = products.find((item) => item.id === Number(value));
    setUnitCost(product?.cost_estimate ?? "");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!productId) {
      setValidationError("Selecciona un insumo o materia prima.");
      return;
    }
    if (!isPositiveDecimal(quantity, 3)) {
      setValidationError("La cantidad requerida debe ser mayor a cero.");
      return;
    }
    if (!isNonnegativeDecimal(unitCost, 4)) {
      setValidationError("El costo unitario debe ser mayor o igual a cero.");
      return;
    }
    if (!isNonnegativeDecimal(waste, 3)) {
      setValidationError("El porcentaje de merma no puede ser negativo.");
      return;
    }
    const saved = await onSubmit({
      input_product_id: Number(productId),
      quantity_required: quantity,
      unit_cost: unitCost,
      waste_percentage: waste,
      notes: optionalText(notes),
    });
    if (saved) {
      setProductId("");
      setQuantity("1");
      setUnitCost("");
      setWaste("0");
      setNotes("");
      setIsOpen(false);
    }
  }

  if (!isOpen) {
    return (
      <button
        className="h-10 w-full rounded-md border border-water-700 bg-water-50 px-4 text-sm font-semibold text-water-700 hover:bg-water-100 disabled:border-slate-300 disabled:bg-slate-100 disabled:text-slate-400"
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(true)}
      >
        Agregar insumo o materia prima
      </button>
    );
  }

  return (
    <form
      className="space-y-3 rounded-md border border-water-200 bg-water-50 p-3"
      onSubmit={handleSubmit}
    >
      <h3 className="font-semibold text-slate-950">Nuevo insumo</h3>
      {validationError ? <ValidationError text={validationError} /> : null}
      <SelectInput
        label="Producto de entrada"
        value={productId}
        disabled={disabled}
        required
        options={products.map((product) => ({
          value: String(product.id),
          label: `${productLabel(product)} · ${
            PRODUCT_KIND_LABELS[product.product_kind]
          }`,
        }))}
        placeholder="Selecciona un producto"
        onChange={handleProductChange}
      />
      <div className="grid gap-3 sm:grid-cols-3">
        <DecimalInput
          label="Cantidad requerida"
          value={quantity}
          scale={3}
          disabled={disabled}
          required
          onChange={setQuantity}
        />
        <DecimalInput
          label="Costo unitario"
          value={unitCost}
          scale={4}
          disabled={disabled}
          required
          onChange={setUnitCost}
        />
        <DecimalInput
          label="Merma (%)"
          value={waste}
          scale={3}
          disabled={disabled}
          required
          onChange={setWaste}
        />
      </div>
      <TextareaInput
        label="Notas"
        value={notes}
        disabled={disabled}
        onChange={setNotes}
      />
      <div className="flex justify-end gap-3">
        <button
          className="h-9 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700"
          type="button"
          disabled={disabled}
          onClick={() => setIsOpen(false)}
        >
          Cancelar
        </button>
        <button
          className="h-9 rounded-md bg-water-700 px-3 text-sm font-semibold text-white disabled:bg-slate-300"
          type="submit"
          disabled={disabled}
        >
          {isSaving ? "Agregando..." : "Agregar insumo"}
        </button>
      </div>
    </form>
  );
}

function RecipeItemEditor({
  item,
  disabled,
  isSaving,
  onSubmit,
  onToggle,
}: {
  item: ProductionRecipeItem;
  disabled: boolean;
  isSaving: boolean;
  onSubmit: (payload: ProductionRecipeItemUpdatePayload) => Promise<boolean>;
  onToggle: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [quantity, setQuantity] = useState(item.quantity_required);
  const [unitCost, setUnitCost] = useState(item.unit_cost);
  const [waste, setWaste] = useState(item.waste_percentage);
  const [notes, setNotes] = useState(item.notes ?? "");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!isPositiveDecimal(quantity, 3)) {
      setValidationError("La cantidad requerida debe ser mayor a cero.");
      return;
    }
    if (!isNonnegativeDecimal(unitCost, 4)) {
      setValidationError("El costo unitario debe ser mayor o igual a cero.");
      return;
    }
    if (!isNonnegativeDecimal(waste, 3)) {
      setValidationError("El porcentaje de merma no puede ser negativo.");
      return;
    }
    const saved = await onSubmit({
      quantity_required: quantity,
      unit_cost: unitCost,
      waste_percentage: waste,
      notes: optionalText(notes),
    });
    if (saved) {
      setIsEditing(false);
    }
  }

  return (
    <div
      className={
        item.is_active
          ? "rounded-md border border-slate-200 p-3"
          : "rounded-md border border-slate-200 bg-slate-50 p-3 opacity-75"
      }
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold text-slate-950">
              {item.input_product_name_snapshot}
            </p>
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">
              {PRODUCT_KIND_LABELS[item.input_product_kind_snapshot]}
            </span>
            {!item.is_active ? (
              <span className="rounded bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">
                Inactivo
              </span>
            ) : null}
          </div>
          <p className="mt-1 text-xs text-slate-500">
            {item.input_product_sku_snapshot ?? "Sin SKU"} ·{" "}
            {item.input_product_presentation_snapshot ?? "Sin presentación"}
          </p>
        </div>
        <p className="font-semibold text-slate-950">
          Total {formatMoney(item.total_cost)}
        </p>
      </div>

      {isEditing ? (
        <form className="mt-3 space-y-3" onSubmit={handleSubmit}>
          {validationError ? <ValidationError text={validationError} /> : null}
          <div className="grid gap-3 sm:grid-cols-3">
            <DecimalInput
              label="Cantidad"
              value={quantity}
              scale={3}
              disabled={disabled}
              required
              onChange={setQuantity}
            />
            <DecimalInput
              label="Costo unitario"
              value={unitCost}
              scale={4}
              disabled={disabled}
              required
              onChange={setUnitCost}
            />
            <DecimalInput
              label="Merma (%)"
              value={waste}
              scale={3}
              disabled={disabled}
              required
              onChange={setWaste}
            />
          </div>
          <TextareaInput
            label="Notas"
            value={notes}
            disabled={disabled}
            onChange={setNotes}
          />
          <div className="flex justify-end gap-3">
            <button
              className="h-8 rounded-md border border-slate-300 px-3 text-xs font-semibold text-slate-700"
              type="button"
              disabled={disabled}
              onClick={() => setIsEditing(false)}
            >
              Cancelar
            </button>
            <button
              className="h-8 rounded-md bg-water-700 px-3 text-xs font-semibold text-white disabled:bg-slate-300"
              type="submit"
              disabled={disabled}
            >
              {isSaving ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </form>
      ) : (
        <>
          <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
            <ValueCell label="Cantidad" value={item.quantity_required} />
            <ValueCell label="Costo unitario" value={formatMoney(item.unit_cost)} />
            <ValueCell label="Merma" value={`${item.waste_percentage}%`} />
          </div>
          {item.notes ? (
            <p className="mt-3 text-sm text-slate-600">{item.notes}</p>
          ) : null}
          {!disabled ? (
            <div className="mt-3 flex gap-4">
              <button
                className="text-xs font-semibold text-water-700 hover:text-water-500"
                type="button"
                onClick={() => setIsEditing(true)}
              >
                Editar
              </button>
              <button
                className={
                  item.is_active
                    ? "text-xs font-semibold text-red-700 hover:text-red-600"
                    : "text-xs font-semibold text-emerald-700 hover:text-emerald-600"
                }
                type="button"
                onClick={onToggle}
              >
                {item.is_active ? "Desactivar" : "Activar"}
              </button>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

function EstimatePanel({
  recipe,
  estimate,
  disabled,
  onSubmit,
}: {
  recipe: ProductionRecipe;
  estimate: ProductionRecipeCostEstimate | null;
  disabled: boolean;
  onSubmit: (outputQuantity: string) => Promise<boolean>;
}) {
  const [quantity, setQuantity] = useState(recipe.output_quantity);
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!isPositiveDecimal(quantity, 3)) {
      setValidationError("La cantidad a estimar debe ser mayor a cero.");
      return;
    }
    await onSubmit(quantity);
  }

  return (
    <section className="rounded-md border border-indigo-200 bg-indigo-50 p-3">
      <h3 className="font-semibold text-slate-950">
        Probar estimación de producción
      </h3>
      <p className="mt-1 text-sm text-slate-600">
        Escala cantidades y costos proporcionalmente, sin afectar inventario.
      </p>
      <form
        className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end"
        onSubmit={handleSubmit}
      >
        <div className="flex-1">
          <DecimalInput
            label="Cantidad a producir"
            value={quantity}
            scale={3}
            disabled={disabled}
            required
            onChange={setQuantity}
          />
        </div>
        <button
          className="h-10 rounded-md bg-indigo-700 px-4 text-sm font-semibold text-white hover:bg-indigo-600 disabled:bg-slate-300"
          type="submit"
          disabled={disabled}
        >
          {disabled ? "Calculando..." : "Calcular estimación"}
        </button>
      </form>
      {validationError ? (
        <div className="mt-3">
          <ValidationError text={validationError} />
        </div>
      ) : null}
      {estimate ? (
        <div className="mt-4 space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <CostCard
              label={`Costo para ${estimate.requested_output_quantity}`}
              value={estimate.estimated_material_cost}
            />
            <CostCard
              label="Costo por unidad"
              value={estimate.estimated_cost_per_unit}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead className="text-slate-600">
                <tr>
                  <th className="py-2 pr-3 font-medium">Insumo</th>
                  <th className="py-2 pr-3 font-medium">Cantidad base</th>
                  <th className="py-2 pr-3 font-medium">Cantidad escalada</th>
                  <th className="py-2 font-medium">Costo escalado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-indigo-100">
                {estimate.items.map((item, index) => (
                  <tr key={`${item.input_product_id}-${index}`}>
                    <td className="py-2 pr-3 font-medium text-slate-950">
                      {item.input_product_name_snapshot}
                    </td>
                    <td className="py-2 pr-3 text-slate-700">
                      {item.quantity_required_base}
                    </td>
                    <td className="py-2 pr-3 text-slate-700">
                      {item.quantity_required_scaled}
                    </td>
                    <td className="py-2 font-medium text-slate-950">
                      {formatMoney(item.total_cost_scaled)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function RecipeFilters({
  filters,
  products,
  disabled,
  onChange,
  onSubmit,
  onClear,
}: {
  filters: RecipeFilterValues;
  products: Product[];
  disabled: boolean;
  onChange: (filters: RecipeFilterValues) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onClear: () => void;
}) {
  return (
    <form
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
      onSubmit={onSubmit}
    >
      <h2 className="text-lg font-semibold text-slate-950">
        Buscar fórmulas
      </h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <TextInput
          label="Buscar"
          value={filters.search}
          disabled={disabled}
          onChange={(value) => onChange({ ...filters, search: value })}
        />
        <SelectInput
          label="Estado"
          value={filters.status}
          disabled={disabled}
          placeholder="Todos"
          options={(
            Object.keys(
              PRODUCTION_RECIPE_STATUS_LABELS,
            ) as ProductionRecipeStatus[]
          ).map((status) => ({
            value: status,
            label: PRODUCTION_RECIPE_STATUS_LABELS[status],
          }))}
          onChange={(value) =>
            onChange({
              ...filters,
              status: value as ProductionRecipeStatus | "",
            })
          }
        />
        <SelectInput
          label="Producto de salida"
          value={filters.outputProductId}
          disabled={disabled}
          placeholder="Todos"
          options={products.map((product) => ({
            value: String(product.id),
            label: productLabel(product),
          }))}
          onChange={(value) =>
            onChange({ ...filters, outputProductId: value })
          }
        />
        <SelectInput
          label="Clasificación"
          value={filters.productKind}
          disabled={disabled}
          placeholder="Todas"
          options={(
            Object.keys(PRODUCT_KIND_LABELS) as ProductKind[]
          ).map((kind) => ({
            value: kind,
            label: PRODUCT_KIND_LABELS[kind],
          }))}
          onChange={(value) =>
            onChange({ ...filters, productKind: value as ProductKind | "" })
          }
        />
        <SelectInput
          label="Vigencia hoy"
          value={filters.isValidToday}
          disabled={disabled}
          placeholder="Todas"
          options={[
            { value: "true", label: "Vigente hoy" },
            { value: "false", label: "Fuera de vigencia" },
          ]}
          onChange={(value) =>
            onChange({
              ...filters,
              isValidToday: value as "" | "true" | "false",
            })
          }
        />
      </div>
      <div className="mt-4 flex justify-end gap-3">
        <button
          className="h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700"
          type="button"
          disabled={disabled}
          onClick={onClear}
        >
          Limpiar
        </button>
        <button
          className="h-9 rounded-md bg-water-700 px-3 text-sm font-semibold text-white disabled:bg-slate-300"
          type="submit"
          disabled={disabled}
        >
          {disabled ? "Buscando..." : "Aplicar filtros"}
        </button>
      </div>
    </form>
  );
}

function RecipeList({
  recipes,
  busyKey,
  onSelect,
}: {
  recipes: ProductionRecipe[];
  busyKey: string;
  onSelect: (recipe: ProductionRecipe) => void;
}) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Fórmulas registradas
        </h2>
        <span className="text-sm text-slate-500">{recipes.length}</span>
      </div>
      {recipes.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          No se encontraron fórmulas con los filtros seleccionados.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[960px] text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Fórmula</th>
                <th className="px-4 py-3 font-medium">Producto terminado</th>
                <th className="px-4 py-3 font-medium">Cantidad salida</th>
                <th className="px-4 py-3 font-medium">Costo total</th>
                <th className="px-4 py-3 font-medium">Costo/unidad</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recipes.map((recipe) => (
                <tr key={recipe.id}>
                  <td className="px-4 py-3 align-top">
                    <p className="font-semibold text-slate-950">{recipe.name}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {recipe.recipe_number} · {recipe.items.length} ítems
                    </p>
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    <p>{recipe.output_product_name}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {PRODUCT_KIND_LABELS[recipe.output_product_kind]}
                    </p>
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {recipe.output_quantity}
                  </td>
                  <td className="px-4 py-3 align-top font-medium text-slate-950">
                    {formatMoney(recipe.estimated_material_cost)}
                  </td>
                  <td className="px-4 py-3 align-top font-medium text-slate-950">
                    {formatMoney(recipe.estimated_cost_per_unit)}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <StatusBadge status={recipe.status} />
                  </td>
                  <td className="px-4 py-3 align-top">
                    <button
                      className="font-semibold text-water-700 hover:text-water-500 disabled:text-slate-400"
                      type="button"
                      disabled={Boolean(busyKey)}
                      onClick={() => onSelect(recipe)}
                    >
                      {busyKey === `select-${recipe.id}`
                        ? "Abriendo..."
                        : "Gestionar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function StatusBadge({ status }: { status: ProductionRecipeStatus }) {
  const className =
    status === "active"
      ? "bg-emerald-50 text-emerald-700"
      : status === "voided"
        ? "bg-red-50 text-red-700"
        : "bg-slate-100 text-slate-600";
  return (
    <span
      className={`inline-flex rounded-md px-2 py-1 text-xs font-semibold ${className}`}
    >
      {PRODUCTION_RECIPE_STATUS_LABELS[status]}
    </span>
  );
}

function CostCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-3">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-xl font-semibold text-slate-950">
        {formatMoney(value)}
      </p>
    </div>
  );
}

function ValueCell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-0.5 font-medium text-slate-950">{value}</p>
    </div>
  );
}

function TextInput({
  label,
  value,
  disabled,
  required,
  onChange,
}: {
  label: string;
  value: string;
  disabled?: boolean;
  required?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        type="text"
        value={value}
        disabled={disabled}
        required={required}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function DecimalInput({
  label,
  value,
  scale,
  disabled,
  required,
  onChange,
}: {
  label: string;
  value: string;
  scale: number;
  disabled?: boolean;
  required?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        type="number"
        inputMode="decimal"
        min="0"
        step={`0.${"0".repeat(Math.max(0, scale - 1))}1`}
        value={value}
        disabled={disabled}
        required={required}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function DateInput({
  label,
  value,
  disabled,
  onChange,
}: {
  label: string;
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        type="date"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function SelectInput({
  label,
  value,
  options,
  placeholder,
  disabled,
  required,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <select
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        value={value}
        disabled={disabled}
        required={required}
        onChange={(event) => onChange(event.target.value)}
      >
        {placeholder !== undefined ? <option value="">{placeholder}</option> : null}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function TextareaInput({
  label,
  value,
  disabled,
  onChange,
}: {
  label: string;
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <textarea
        className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function ValidationError({ text }: { text: string }) {
  return (
    <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      {text}
    </p>
  );
}

function toApiFilters(
  filters: RecipeFilterValues,
): ProductionRecipeFilters {
  return {
    ...(filters.search.trim() ? { search: filters.search.trim() } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.outputProductId
      ? { output_product_id: Number(filters.outputProductId) }
      : {}),
    ...(filters.productKind ? { product_kind: filters.productKind } : {}),
    ...(filters.isValidToday
      ? { is_valid_today: filters.isValidToday === "true" }
      : {}),
  };
}

function productLabel(product: Product): string {
  const sku = product.sku ? `${product.sku} · ` : "";
  const presentation = product.presentation
    ? ` · ${product.presentation}`
    : "";
  return `${sku}${product.name}${presentation}`;
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function isPositiveDecimal(value: string, scale: number): boolean {
  if (!isNonnegativeDecimal(value, scale)) {
    return false;
  }
  return !/^0+(?:\.0+)?$/.test(value);
}

function isNonnegativeDecimal(value: string, scale: number): boolean {
  return new RegExp(`^\\d+(?:\\.\\d{1,${scale}})?$`).test(value);
}

function formatMoney(value: string): string {
  const [units, decimals = ""] = value.split(".");
  const fourDecimals = decimals.padEnd(4, "0").slice(0, 4);
  const visibleDecimals = fourDecimals.replace(/0+$/, "").padEnd(2, "0");
  return `$${units}.${visibleDecimals}`;
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createProductionMaterialConsumption,
  listInventoryLocations,
  listProductionBatches,
  listProductionMaterialConsumptions,
  listProductionRecipes,
  previewProductionMaterialConsumption,
  voidProductionMaterialConsumption,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { InventoryLocation } from "@/types/inventory";
import type { ProductionBatch } from "@/types/production";
import type { ProductionRecipe } from "@/types/productionRecipe";
import {
  PRODUCTION_MATERIAL_CONSUMPTION_STATUS_LABELS,
  type ProductionMaterialConsumption,
  type ProductionMaterialConsumptionPayload,
  type ProductionMaterialConsumptionPreview,
} from "@/types/productionMaterialConsumption";

export default function ProductionMaterialConsumptionPage() {
  const canVoid = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [batches, setBatches] = useState<ProductionBatch[]>([]);
  const [locations, setLocations] = useState<InventoryLocation[]>([]);
  const [recipes, setRecipes] = useState<ProductionRecipe[]>([]);
  const [consumptions, setConsumptions] = useState<
    ProductionMaterialConsumption[]
  >([]);
  const [selectedBatchId, setSelectedBatchId] = useState("");
  const [sourceLocationId, setSourceLocationId] = useState("");
  const [movementDate, setMovementDate] = useState(getTodayISODate());
  const [notes, setNotes] = useState("");
  const [recipeIds, setRecipeIds] = useState<Record<number, string>>({});
  const [preview, setPreview] =
    useState<ProductionMaterialConsumptionPreview | null>(null);
  const [voidingConsumption, setVoidingConsumption] =
    useState<ProductionMaterialConsumption | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidError, setVoidError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
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
    void loadData(storedToken);
  }, [router]);

  const activeConsumptionByBatch = useMemo(
    () =>
      new Map(
        consumptions
          .filter((consumption) => consumption.status === "active")
          .map((consumption) => [
            consumption.production_batch_id,
            consumption,
          ]),
      ),
    [consumptions],
  );
  const selectedBatch = batches.find(
    (batch) => batch.id === Number(selectedBatchId),
  );
  const selectedActiveConsumption = selectedBatch
    ? activeConsumptionByBatch.get(selectedBatch.id)
    : undefined;
  const previewHasInsufficientStock =
    preview?.items.some((item) => !item.has_sufficient_stock) ?? false;

  async function loadData(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const [
        loadedBatches,
        loadedLocations,
        loadedRecipes,
        loadedConsumptions,
      ] = await Promise.all([
        listProductionBatches(activeToken, { status: "active" }),
        listInventoryLocations(activeToken, { is_active: true }),
        listProductionRecipes(activeToken, { status: "active" }),
        listProductionMaterialConsumptions(activeToken),
      ]);
      setBatches(loadedBatches);
      setLocations(loadedLocations);
      setRecipes(loadedRecipes);
      setConsumptions(loadedConsumptions);
    } catch (loadError) {
      if (!redirectIfUnauthorized(loadError)) {
        setError(getErrorMessage(loadError));
      }
    } finally {
      setIsLoading(false);
    }
  }

  function handleBatchChange(value: string) {
    setSelectedBatchId(value);
    setPreview(null);
    clearNotices();
    const batch = batches.find((item) => item.id === Number(value));
    if (!batch) {
      setRecipeIds({});
      return;
    }
    setRecipeIds(
      Object.fromEntries(
        batch.items.map((item) => {
          const matchingRecipes = recipes.filter(
            (recipe) => recipe.output_product_id === item.product_id,
          );
          return [
            item.id,
            matchingRecipes.length === 1
              ? String(matchingRecipes[0].id)
              : "",
          ];
        }),
      ),
    );
  }

  function handleRecipeChange(productionItemId: number, value: string) {
    setRecipeIds((current) => ({ ...current, [productionItemId]: value }));
    setPreview(null);
    clearNotices();
  }

  function handleSourceLocationChange(value: string) {
    setSourceLocationId(value);
    setPreview(null);
    clearNotices();
  }

  function handleMovementDateChange(value: string) {
    setMovementDate(value);
    setPreview(null);
    clearNotices();
  }

  function buildPayload(): ProductionMaterialConsumptionPayload | null {
    if (!selectedBatch) {
      setError("Seleccione una producción.");
      return null;
    }
    if (selectedActiveConsumption) {
      setError("La producción ya tiene un consumo de insumos activo.");
      return null;
    }
    if (!sourceLocationId) {
      setError("Seleccione la ubicación origen de los insumos.");
      return null;
    }
    if (!movementDate) {
      setError("Seleccione la fecha del movimiento.");
      return null;
    }
    const missingRecipe = selectedBatch.items.some(
      (item) => !recipeIds[item.id],
    );
    if (missingRecipe) {
      setError("Seleccione una fórmula para cada producto producido.");
      return null;
    }
    return {
      source_location_id: Number(sourceLocationId),
      movement_date: movementDate,
      notes: notes.trim() || null,
      items: selectedBatch.items.map((item) => ({
        production_item_id: item.id,
        recipe_id: Number(recipeIds[item.id]),
      })),
    };
  }

  async function handlePreview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    clearNotices();
    const payload = buildPayload();
    if (!payload) {
      return;
    }
    setIsPreviewing(true);
    try {
      const result = await previewProductionMaterialConsumption(
        token,
        Number(selectedBatchId),
        payload,
      );
      setPreview(result);
      if (result.items.some((item) => !item.has_sufficient_stock)) {
        setError(
          "La vista previa detectó stock insuficiente. No se puede aplicar el consumo.",
        );
      } else {
        setMessage(
          "Vista previa lista. Revise las cantidades antes de confirmar.",
        );
      }
    } catch (previewError) {
      if (!redirectIfUnauthorized(previewError)) {
        setError(getErrorMessage(previewError));
      }
    } finally {
      setIsPreviewing(false);
    }
  }

  async function handleApply() {
    if (!token || !preview || previewHasInsufficientStock) {
      return;
    }
    clearNotices();
    const payload = buildPayload();
    if (!payload) {
      return;
    }
    setIsApplying(true);
    try {
      const consumption = await createProductionMaterialConsumption(
        token,
        Number(selectedBatchId),
        payload,
      );
      setMessage(
        `Consumo ${consumption.consumption_number} aplicado correctamente.`,
      );
      setPreview(null);
      await loadData(token);
    } catch (applyError) {
      if (!redirectIfUnauthorized(applyError)) {
        setError(getErrorMessage(applyError));
      }
    } finally {
      setIsApplying(false);
    }
  }

  function handleOpenVoid(consumption: ProductionMaterialConsumption) {
    setVoidingConsumption(consumption);
    setVoidReason("");
    setVoidError("");
    clearNotices();
  }

  async function handleVoid(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !voidingConsumption) {
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
      await voidProductionMaterialConsumption(
        token,
        voidingConsumption.id,
        reason,
      );
      setMessage(
        `Consumo ${voidingConsumption.consumption_number} anulado y stock revertido.`,
      );
      setVoidingConsumption(null);
      setVoidReason("");
      await loadData(token);
    } catch (possibleError) {
      if (!redirectIfUnauthorized(possibleError)) {
        setVoidError(getErrorMessage(possibleError));
      }
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
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm font-semibold">
              <Link
                className="text-water-700 hover:text-water-500"
                href="/dashboard"
              >
                Volver al dashboard
              </Link>
              <Link
                className="text-water-700 hover:text-water-500"
                href="/dashboard/production"
              >
                Ver producción
              </Link>
              <Link
                className="text-water-700 hover:text-water-500"
                href="/dashboard/production/recipes"
              >
                Ver fórmulas
              </Link>
            </div>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Consumo de insumos
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Consume materia prima e insumos desde inventario usando fórmulas
              de producción. Este proceso es explícito, trazable y reversible.
            </p>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900">
          La producción no consume insumos automáticamente. Primero revise la
          vista previa y luego confirme el consumo.
        </p>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando producciones, fórmulas e inventario..." />
        ) : (
          <>
            <form
              className="space-y-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              onSubmit={handlePreview}
            >
              <div>
                <h2 className="text-lg font-semibold text-slate-950">
                  Preparar consumo
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Seleccione la producción, la bodega de origen y una fórmula
                  activa para cada producto.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <label className="block md:col-span-2">
                  <span className="text-sm font-medium text-slate-700">
                    Producción activa
                  </span>
                  <select
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                    value={selectedBatchId}
                    onChange={(event) =>
                      handleBatchChange(event.target.value)
                    }
                  >
                    <option value="">Seleccione una producción</option>
                    {batches.map((batch) => {
                      const activeConsumption =
                        activeConsumptionByBatch.get(batch.id);
                      return (
                        <option
                          disabled={Boolean(activeConsumption)}
                          key={batch.id}
                          value={batch.id}
                        >
                          {batch.production_number} · {batch.production_date}
                          {activeConsumption
                            ? ` · Consumida (${activeConsumption.consumption_number})`
                            : ""}
                        </option>
                      );
                    })}
                  </select>
                </label>

                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Fecha del movimiento
                  </span>
                  <input
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                    type="date"
                    value={movementDate}
                    onChange={(event) =>
                      handleMovementDateChange(event.target.value)
                    }
                  />
                </label>

                <label className="block md:col-span-2">
                  <span className="text-sm font-medium text-slate-700">
                    Ubicación origen de insumos
                  </span>
                  <select
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                    value={sourceLocationId}
                    onChange={(event) =>
                      handleSourceLocationChange(event.target.value)
                    }
                  >
                    <option value="">Seleccione una ubicación</option>
                    {locations.map((location) => (
                      <option key={location.id} value={location.id}>
                        {location.name}
                        {location.code ? ` · ${location.code}` : ""}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="text-sm font-medium text-slate-700">
                    Notas
                  </span>
                  <input
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                    placeholder="Opcional"
                    value={notes}
                    onChange={(event) => setNotes(event.target.value)}
                  />
                </label>
              </div>

              {selectedBatch ? (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
                    Productos producidos y fórmulas
                  </h3>
                  {selectedBatch.items.map((item) => {
                    const matchingRecipes = recipes.filter(
                      (recipe) =>
                        recipe.output_product_id === item.product_id,
                    );
                    return (
                      <div
                        className="grid gap-3 rounded-md border border-slate-200 p-4 md:grid-cols-[1fr_1.3fr]"
                        key={item.id}
                      >
                        <div>
                          <p className="font-medium text-slate-950">
                            {item.product_name_snapshot}
                          </p>
                          <p className="mt-1 text-sm text-slate-600">
                            Producido: {formatQuantity(item.quantity_produced)}
                            {" · "}Merma: {formatQuantity(item.quantity_waste)}
                          </p>
                        </div>
                        <label className="block">
                          <span className="text-sm font-medium text-slate-700">
                            Fórmula activa
                          </span>
                          <select
                            className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100"
                            value={recipeIds[item.id] ?? ""}
                            onChange={(event) =>
                              handleRecipeChange(item.id, event.target.value)
                            }
                          >
                            <option value="">Seleccione una fórmula</option>
                            {matchingRecipes.map((recipe) => (
                              <option key={recipe.id} value={recipe.id}>
                                {recipe.recipe_number} · {recipe.name} · Base{" "}
                                {formatQuantity(recipe.output_quantity)}
                              </option>
                            ))}
                          </select>
                          {matchingRecipes.length === 0 ? (
                            <p className="mt-1 text-sm text-red-700">
                              No existe una fórmula activa para este producto.
                            </p>
                          ) : null}
                        </label>
                      </div>
                    );
                  })}
                </div>
              ) : null}

              <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md bg-water-700 px-5 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
                  type="submit"
                  disabled={
                    isPreviewing ||
                    isApplying ||
                    !selectedBatch ||
                    Boolean(selectedActiveConsumption)
                  }
                >
                  {isPreviewing
                    ? "Generando vista previa..."
                    : "Generar vista previa"}
                </button>
              </div>
            </form>

            {preview ? (
              <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-950">
                      Vista previa del consumo
                    </h2>
                    <p className="mt-1 text-sm text-slate-600">
                      Estas cantidades y costos fueron calculados por el
                      backend. Aún no se ha modificado el inventario.
                    </p>
                  </div>
                  <p className="text-lg font-semibold text-slate-950">
                    Total: {formatMoney(preview.total_material_cost)}
                  </p>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-sm">
                    <thead className="bg-slate-50 text-left text-slate-600">
                      <tr>
                        <th className="px-3 py-3 font-semibold">Producto</th>
                        <th className="px-3 py-3 font-semibold">Insumo</th>
                        <th className="px-3 py-3 text-right font-semibold">
                          A consumir
                        </th>
                        <th className="px-3 py-3 text-right font-semibold">
                          Stock
                        </th>
                        <th className="px-3 py-3 text-right font-semibold">
                          Costo unit.
                        </th>
                        <th className="px-3 py-3 text-right font-semibold">
                          Total
                        </th>
                        <th className="px-3 py-3 font-semibold">Estado</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {preview.items.map((item, index) => (
                        <tr key={`${item.production_item_id}-${item.input_product_id}-${index}`}>
                          <td className="px-3 py-3 text-slate-700">
                            {item.output_product_name}
                            <span className="mt-1 block text-xs text-slate-500">
                              {item.recipe_name}
                            </span>
                          </td>
                          <td className="px-3 py-3 font-medium text-slate-950">
                            {item.input_product_name}
                          </td>
                          <td className="px-3 py-3 text-right text-slate-700">
                            {formatQuantity(item.quantity_consumed)}
                          </td>
                          <td className="px-3 py-3 text-right text-slate-700">
                            {formatQuantity(item.available_stock)}
                          </td>
                          <td className="px-3 py-3 text-right text-slate-700">
                            {formatMoney(item.unit_cost)}
                          </td>
                          <td className="px-3 py-3 text-right font-medium text-slate-950">
                            {formatMoney(item.total_cost)}
                          </td>
                          <td className="px-3 py-3">
                            <span
                              className={
                                item.has_sufficient_stock
                                  ? "rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-800"
                                  : "rounded-full bg-red-100 px-2 py-1 text-xs font-semibold text-red-800"
                              }
                            >
                              {item.has_sufficient_stock
                                ? "Stock suficiente"
                                : "Stock insuficiente"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-slate-600">
                    Al confirmar se crearán salidas de inventario trazables para
                    cada insumo.
                  </p>
                  <button
                    className="h-10 rounded-md bg-emerald-700 px-5 text-sm font-semibold text-white hover:bg-emerald-600 disabled:bg-slate-300"
                    type="button"
                    disabled={isApplying || previewHasInsufficientStock}
                    onClick={handleApply}
                  >
                    {isApplying ? "Consumiendo insumos..." : "Consumir insumos"}
                  </button>
                </div>
              </section>
            ) : null}

            <section className="space-y-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">
                  Consumos recientes
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Historial de consumos activos y anulados, con sus movimientos
                  de inventario relacionados.
                </p>
              </div>
              {consumptions.length === 0 ? (
                <p className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-600">
                  Todavía no hay consumos de insumos registrados.
                </p>
              ) : (
                <div className="grid gap-4 lg:grid-cols-2">
                  {consumptions.map((consumption) => (
                    <article
                      className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
                      key={consumption.id}
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h3 className="font-semibold text-slate-950">
                            {consumption.consumption_number}
                          </h3>
                          <p className="mt-1 text-sm text-slate-600">
                            {consumption.production_number} · {" "}
                            {consumption.source_location_name}
                          </p>
                        </div>
                        <span
                          className={
                            consumption.status === "active"
                              ? "rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-800"
                              : "rounded-full bg-slate-200 px-2 py-1 text-xs font-semibold text-slate-700"
                          }
                        >
                          {
                            PRODUCTION_MATERIAL_CONSUMPTION_STATUS_LABELS[
                              consumption.status
                            ]
                          }
                        </span>
                      </div>
                      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <dt className="text-slate-500">Fecha</dt>
                          <dd className="font-medium text-slate-800">
                            {formatDate(consumption.movement_date)}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-slate-500">Costo total</dt>
                          <dd className="font-medium text-slate-800">
                            {formatMoney(consumption.total_material_cost)}
                          </dd>
                        </div>
                      </dl>
                      <div className="mt-4 space-y-2 border-t border-slate-100 pt-4">
                        {consumption.items.map((item) => (
                          <div
                            className="flex items-center justify-between gap-3 text-sm"
                            key={item.id}
                          >
                            <span className="text-slate-700">
                              {item.input_product_name_snapshot}
                            </span>
                            <span className="font-medium text-slate-950">
                              {formatQuantity(item.quantity_consumed)}
                            </span>
                          </div>
                        ))}
                      </div>
                      {consumption.void_reason ? (
                        <p className="mt-4 rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-700">
                          Motivo de anulación: {consumption.void_reason}
                        </p>
                      ) : null}
                      {canVoid && consumption.status === "active" ? (
                        <div className="mt-4 flex justify-end">
                          <button
                            className="h-9 rounded-md border border-red-300 bg-white px-4 text-sm font-semibold text-red-700 hover:bg-red-50"
                            type="button"
                            onClick={() => handleOpenVoid(consumption)}
                          >
                            Anular consumo
                          </button>
                        </div>
                      ) : null}
                    </article>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>

      {canVoid && voidingConsumption ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="void-material-consumption-title"
        >
          <form
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-xl"
            onSubmit={handleVoid}
          >
            <div className="border-b border-slate-200 px-5 py-4">
              <h2
                className="text-lg font-semibold text-slate-950"
                id="void-material-consumption-title"
              >
                Anular consumo de insumos
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {voidingConsumption.consumption_number}
              </p>
            </div>
            <div className="space-y-4 p-5">
              {voidError ? <ErrorMessage message={voidError} /> : null}
              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Motivo de anulación
                </span>
                <textarea
                  className="mt-1 min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
                  required
                  disabled={isVoiding}
                  value={voidReason}
                  onChange={(event) => setVoidReason(event.target.value)}
                />
              </label>
              <p className="text-sm text-slate-600">
                Los movimientos quedarán anulados y el stock de todos los
                insumos volverá a la ubicación de origen.
              </p>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <button
                  className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
                  type="button"
                  disabled={isVoiding}
                  onClick={() => setVoidingConsumption(null)}
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

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function formatMoney(value: string): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(Number(value));
}

function formatQuantity(value: string): string {
  return new Intl.NumberFormat("es-EC", {
    maximumFractionDigits: 3,
  }).format(Number(value));
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

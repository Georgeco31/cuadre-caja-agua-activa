"use client";

import Link from "next/link";
import { useMemo, useState, type FormEvent } from "react";

import type { DeliveryRoute } from "@/types/deliveryRoute";
import type {
  InventoryLocation,
  InventoryStock,
} from "@/types/inventory";
import type { Product } from "@/types/product";
import type { RouteLoadPayload } from "@/types/routeLoad";
import type { Vehicle } from "@/types/vehicle";

type RouteLoadFormProps = {
  routes: DeliveryRoute[];
  vehicles: Vehicle[];
  locations: InventoryLocation[];
  products: Product[];
  stocks: InventoryStock[];
  isSubmitting?: boolean;
  onSubmit: (payload: RouteLoadPayload) => Promise<boolean>;
};

type LoadLine = {
  productId: number;
  quantityLoaded: string;
};

export function RouteLoadForm({
  routes,
  vehicles,
  locations,
  products,
  stocks,
  isSubmitting = false,
  onSubmit,
}: RouteLoadFormProps) {
  const [loadDate, setLoadDate] = useState(currentDate());
  const [routeId, setRouteId] = useState("");
  const [vehicleId, setVehicleId] = useState("");
  const [sourceLocationId, setSourceLocationId] = useState("");
  const [destinationLocationId, setDestinationLocationId] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedProductId, setSelectedProductId] = useState("");
  const [lines, setLines] = useState<LoadLine[]>([]);
  const [validationError, setValidationError] = useState("");

  const productsById = useMemo(
    () => new Map(products.map((product) => [product.id, product])),
    [products],
  );
  const locationsById = useMemo(
    () => new Map(locations.map((location) => [location.id, location])),
    [locations],
  );
  const destinationLocations = useMemo(() => {
    const selectedVehicleId = Number(vehicleId);
    return locations.filter(
      (location) =>
        location.location_type === "vehicle" &&
        location.id !== Number(sourceLocationId) &&
        (!selectedVehicleId ||
          location.vehicle_id === null ||
          location.vehicle_id === selectedVehicleId),
    );
  }, [locations, sourceLocationId, vehicleId]);

  function handleVehicleChange(value: string) {
    setVehicleId(value);
    const destination = locationsById.get(Number(destinationLocationId));
    if (
      destination?.vehicle_id !== null &&
      destination?.vehicle_id !== Number(value)
    ) {
      setDestinationLocationId("");
    }
  }

  function handleSourceChange(value: string) {
    setSourceLocationId(value);
    if (value === destinationLocationId) {
      setDestinationLocationId("");
    }
  }

  function handleAddProduct() {
    setValidationError("");
    const productId = Number(selectedProductId);
    if (!productsById.has(productId)) {
      setValidationError("Selecciona un producto activo.");
      return;
    }
    if (lines.some((line) => line.productId === productId)) {
      setValidationError("El producto seleccionado ya está en la carga.");
      return;
    }
    setLines([...lines, { productId, quantityLoaded: "" }]);
    setSelectedProductId("");
  }

  function updateLine(productId: number, quantityLoaded: string) {
    setLines(
      lines.map((line) =>
        line.productId === productId ? { ...line, quantityLoaded } : line,
      ),
    );
  }

  function removeLine(productId: number) {
    setLines(lines.filter((line) => line.productId !== productId));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!loadDate) {
      setValidationError("La fecha de carga es obligatoria.");
      return;
    }
    if (!routeId || !vehicleId || !sourceLocationId || !destinationLocationId) {
      setValidationError(
        "Selecciona ruta, vehículo, ubicación origen y ubicación destino.",
      );
      return;
    }
    if (sourceLocationId === destinationLocationId) {
      setValidationError("Las ubicaciones de origen y destino deben ser distintas.");
      return;
    }
    if (lines.length === 0) {
      setValidationError("Agrega al menos un producto a la carga.");
      return;
    }
    if (lines.some((line) => !isValidQuantity(line.quantityLoaded))) {
      setValidationError(
        "Todas las cantidades deben ser mayores a cero y tener máximo tres decimales.",
      );
      return;
    }

    const saved = await onSubmit({
      load_date: loadDate,
      route_id: Number(routeId),
      vehicle_id: Number(vehicleId),
      source_location_id: Number(sourceLocationId),
      destination_location_id: Number(destinationLocationId),
      notes: optionalText(notes),
      items: lines.map((line) => ({
        product_id: line.productId,
        quantity_loaded: line.quantityLoaded.trim(),
      })),
    });
    if (saved) {
      setNotes("");
      setSelectedProductId("");
      setLines([]);
    }
  }

  function availableStock(productId: number): string {
    if (!sourceLocationId) {
      return "Selecciona origen";
    }
    const stock = stocks.find(
      (item) =>
        item.product_id === productId &&
        item.location_id === Number(sourceLocationId),
    );
    return stock ? formatQuantity(stock.quantity_on_hand) : "0";
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar carga de camión
        </h2>
      </div>
      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <Field label="Fecha de carga">
            <input
              className={fieldClassName}
              type="date"
              value={loadDate}
              required
              disabled={isSubmitting}
              onChange={(event) => setLoadDate(event.target.value)}
            />
          </Field>
          <Field label="Ruta">
            <select
              className={fieldClassName}
              value={routeId}
              required
              disabled={isSubmitting || routes.length === 0}
              onChange={(event) => setRouteId(event.target.value)}
            >
              <option value="">Seleccionar ruta</option>
              {routes.map((route) => (
                <option key={route.id} value={route.id}>
                  {route.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Vehículo">
            <select
              className={fieldClassName}
              value={vehicleId}
              required
              disabled={isSubmitting || vehicles.length === 0}
              onChange={(event) => handleVehicleChange(event.target.value)}
            >
              <option value="">Seleccionar vehículo</option>
              {vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.name}
                  {vehicle.plate ? ` · ${vehicle.plate}` : ""}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Ubicación origen">
            <select
              className={fieldClassName}
              value={sourceLocationId}
              required
              disabled={isSubmitting || locations.length === 0}
              onChange={(event) => handleSourceChange(event.target.value)}
            >
              <option value="">Seleccionar origen</option>
              {locations
                .filter((location) => location.id !== Number(destinationLocationId))
                .map((location) => (
                  <option key={location.id} value={location.id}>
                    {location.name}
                  </option>
                ))}
            </select>
          </Field>
          <Field label="Ubicación destino del vehículo">
            <select
              className={fieldClassName}
              value={destinationLocationId}
              required
              disabled={isSubmitting || destinationLocations.length === 0}
              onChange={(event) => setDestinationLocationId(event.target.value)}
            >
              <option value="">Seleccionar destino</option>
              {destinationLocations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Observaciones">
            <input
              className={fieldClassName}
              value={notes}
              disabled={isSubmitting}
              onChange={(event) => setNotes(event.target.value)}
            />
          </Field>
        </div>

        <div className="space-y-3 border-t border-slate-200 pt-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <Field label="Producto">
              <select
                className={fieldClassName}
                value={selectedProductId}
                disabled={isSubmitting || products.length === 0}
                onChange={(event) => setSelectedProductId(event.target.value)}
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
            <button
              className="h-10 rounded-md border border-water-700 bg-white px-4 text-sm font-semibold text-water-700 hover:bg-water-50 disabled:border-slate-300 disabled:text-slate-400"
              type="button"
              disabled={isSubmitting || products.length === 0}
              onClick={handleAddProduct}
            >
              Agregar producto
            </button>
          </div>

          {products.length === 0 ? (
            <p className="text-sm text-slate-600">
              No hay productos activos. Revisa el catálogo en {" "}
              <Link
                className="font-semibold text-water-700 hover:text-water-500"
                href="/dashboard/products"
              >
                Productos
              </Link>
              .
            </p>
          ) : null}

          {lines.length > 0 ? (
            <div className="overflow-x-auto rounded-md border border-slate-200">
              <table className="w-full min-w-[680px] text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-3 py-2 font-medium">Producto</th>
                    <th className="px-3 py-2 text-right font-medium">
                      Stock disponible
                    </th>
                    <th className="w-48 px-3 py-2 font-medium">Cantidad</th>
                    <th className="w-24 px-3 py-2 font-medium">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {lines.map((line) => {
                    const product = productsById.get(line.productId);
                    return (
                      <tr key={line.productId}>
                        <td className="px-3 py-3">
                          <p className="font-medium text-slate-950">
                            {product?.name}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            {product?.sku ?? "Sin SKU"}
                          </p>
                        </td>
                        <td className="px-3 py-3 text-right font-semibold text-slate-950">
                          {availableStock(line.productId)}
                        </td>
                        <td className="px-3 py-3">
                          <input
                            className={lineFieldClassName}
                            aria-label={`Cantidad a cargar de ${product?.name ?? "producto"}`}
                            type="number"
                            inputMode="decimal"
                            min="0.001"
                            step="0.001"
                            value={line.quantityLoaded}
                            required
                            disabled={isSubmitting}
                            onChange={(event) =>
                              updateLine(line.productId, event.target.value)
                            }
                          />
                        </td>
                        <td className="px-3 py-3">
                          <button
                            className="font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                            type="button"
                            disabled={isSubmitting}
                            onClick={() => removeLine(line.productId)}
                          >
                            Quitar
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="rounded-md bg-slate-50 px-3 py-4 text-sm text-slate-600">
              Agrega los productos que saldrán hacia el vehículo.
            </p>
          )}
        </div>

        <div className="flex justify-end border-t border-slate-200 pt-5">
          <button
            className="h-11 w-full rounded-md bg-water-700 px-5 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300 sm:w-auto"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Guardando carga..." : "Registrar carga"}
          </button>
        </div>
      </form>
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
    <label className="block flex-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

const fieldClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";
const lineFieldClassName =
  "h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100";

function currentDate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function isValidQuantity(value: string): boolean {
  const normalized = value.trim();
  return /^\d+(\.\d{1,3})?$/.test(normalized) && /[1-9]/.test(normalized);
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function formatQuantity(value: string): string {
  const [units, decimals = ""] = value.split(".");
  const visibleDecimals = decimals
    .padEnd(3, "0")
    .slice(0, 3)
    .replace(/0+$/, "");
  return visibleDecimals ? `${units}.${visibleDecimals}` : units;
}

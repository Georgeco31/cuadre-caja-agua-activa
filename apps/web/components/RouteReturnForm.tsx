"use client";

import Link from "next/link";
import { useMemo, useState, type FormEvent, type ReactNode } from "react";

import type {
  InventoryLocation,
  InventoryStock,
} from "@/types/inventory";
import type { RouteLoad } from "@/types/routeLoad";
import type { RouteReturnPayload } from "@/types/routeReturn";

type RouteReturnFormProps = {
  loads: RouteLoad[];
  locations: InventoryLocation[];
  stocks: InventoryStock[];
  isSubmitting?: boolean;
  onSubmit: (payload: RouteReturnPayload) => Promise<boolean>;
};

export function RouteReturnForm({
  loads,
  locations,
  stocks,
  isSubmitting = false,
  onSubmit,
}: RouteReturnFormProps) {
  const [returnDate, setReturnDate] = useState(currentDate());
  const [routeLoadId, setRouteLoadId] = useState("");
  const [destinationLocationId, setDestinationLocationId] = useState("");
  const [notes, setNotes] = useState("");
  const [quantities, setQuantities] = useState<Record<number, string>>({});
  const [validationError, setValidationError] = useState("");

  const selectedLoad = useMemo(
    () => loads.find((load) => load.id === Number(routeLoadId)) ?? null,
    [loads, routeLoadId],
  );
  const destinationLocations = useMemo(
    () =>
      locations.filter(
        (location) =>
          location.location_type !== "vehicle" &&
          location.id !== selectedLoad?.destination_location_id,
      ),
    [locations, selectedLoad],
  );

  function handleLoadChange(value: string) {
    setRouteLoadId(value);
    setDestinationLocationId("");
    setQuantities({});
    setValidationError("");
  }

  function updateQuantity(loadItemId: number, value: string) {
    setQuantities((current) => ({ ...current, [loadItemId]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    if (!returnDate) {
      setValidationError("La fecha de retorno es obligatoria.");
      return;
    }
    if (!selectedLoad) {
      setValidationError("Selecciona una carga de camión activa.");
      return;
    }
    if (!destinationLocationId) {
      setValidationError("Selecciona la ubicación destino del retorno.");
      return;
    }

    const selectedItems = selectedLoad.items
      .map((item) => ({
        item,
        quantity: (quantities[item.id] ?? "").trim(),
      }))
      .filter(({ quantity }) => quantity !== "");
    if (selectedItems.length === 0) {
      setValidationError("Registra al menos una cantidad devuelta mayor a cero.");
      return;
    }
    if (selectedItems.some(({ quantity }) => !isValidQuantity(quantity))) {
      setValidationError(
        "Las cantidades devueltas deben ser mayores a cero y tener máximo tres decimales.",
      );
      return;
    }
    if (
      selectedItems.some(
        ({ item, quantity }) =>
          compareQuantities(quantity, item.quantity_loaded) > 0,
      )
    ) {
      setValidationError("Una cantidad devuelta supera la cantidad cargada.");
      return;
    }

    const saved = await onSubmit({
      return_date: returnDate,
      route_load_id: selectedLoad.id,
      destination_location_id: Number(destinationLocationId),
      notes: optionalText(notes),
      items: selectedItems.map(({ item, quantity }) => ({
        route_load_item_id: item.id,
        quantity_returned: quantity,
      })),
    });
    if (saved) {
      setRouteLoadId("");
      setDestinationLocationId("");
      setNotes("");
      setQuantities({});
    }
  }

  function availableStock(productId: number): string {
    if (!selectedLoad) {
      return "0";
    }
    const stock = stocks.find(
      (item) =>
        item.product_id === productId &&
        item.location_id === selectedLoad.destination_location_id,
    );
    return stock ? formatQuantity(stock.quantity_on_hand) : "0";
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3 sm:px-5">
        <h2 className="text-lg font-semibold text-slate-950">
          Registrar retorno de ruta
        </h2>
      </div>
      <form className="space-y-5 p-4 sm:p-5" onSubmit={handleSubmit}>
        {validationError ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {validationError}
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <Field label="Fecha de retorno">
            <input
              className={fieldClassName}
              type="date"
              value={returnDate}
              required
              disabled={isSubmitting}
              onChange={(event) => setReturnDate(event.target.value)}
            />
          </Field>
          <Field label="Carga de camión">
            <select
              className={fieldClassName}
              value={routeLoadId}
              required
              disabled={isSubmitting || loads.length === 0}
              onChange={(event) => handleLoadChange(event.target.value)}
            >
              <option value="">Seleccionar carga activa</option>
              {loads.map((load) => (
                <option key={load.id} value={load.id}>
                  {load.load_number} · {load.route_name} · {load.vehicle_name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Ubicación destino">
            <select
              className={fieldClassName}
              value={destinationLocationId}
              required
              disabled={
                isSubmitting || !selectedLoad || destinationLocations.length === 0
              }
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
        </div>

        {loads.length === 0 ? (
          <p className="text-sm text-slate-600">
            No hay cargas activas disponibles. Revisa el módulo de {" "}
            <Link
              className="font-semibold text-water-700 hover:text-water-500"
              href="/dashboard/route-loads"
            >
              Carga de camión
            </Link>
            .
          </p>
        ) : null}

        {selectedLoad ? (
          <div className="grid gap-3 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm sm:grid-cols-3">
            <Summary label="Ruta" value={selectedLoad.route_name} />
            <Summary label="Vehículo" value={selectedLoad.vehicle_name} />
            <Summary
              label="Origen del retorno"
              value={selectedLoad.destination_location_name}
            />
          </div>
        ) : null}

        <div className="space-y-3 border-t border-slate-200 pt-5">
          <h3 className="text-sm font-semibold text-slate-950">
            Productos cargados
          </h3>
          {selectedLoad ? (
            <div className="overflow-x-auto rounded-md border border-slate-200">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-3 py-2 font-medium">Producto</th>
                    <th className="px-3 py-2 text-right font-medium">Cargado</th>
                    <th className="px-3 py-2 text-right font-medium">
                      Stock en vehículo
                    </th>
                    <th className="w-52 px-3 py-2 font-medium">
                      Cantidad a devolver
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {selectedLoad.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-3 py-3">
                        <p className="font-medium text-slate-950">
                          {item.product_name_snapshot}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {item.product_sku_snapshot ?? "Sin SKU"}
                          {item.product_presentation_snapshot
                            ? ` · ${item.product_presentation_snapshot}`
                            : ""}
                        </p>
                      </td>
                      <td className="px-3 py-3 text-right font-semibold text-slate-950">
                        {formatQuantity(item.quantity_loaded)}
                      </td>
                      <td className="px-3 py-3 text-right font-semibold text-slate-950">
                        {availableStock(item.product_id)}
                      </td>
                      <td className="px-3 py-3">
                        <input
                          className={lineFieldClassName}
                          aria-label={`Cantidad a devolver de ${item.product_name_snapshot}`}
                          type="number"
                          inputMode="decimal"
                          min="0.001"
                          max={item.quantity_loaded}
                          step="0.001"
                          placeholder="0"
                          value={quantities[item.id] ?? ""}
                          disabled={isSubmitting}
                          onChange={(event) =>
                            updateQuantity(item.id, event.target.value)
                          }
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="rounded-md bg-slate-50 px-3 py-4 text-sm text-slate-600">
              Selecciona una carga para ver los productos disponibles para retorno.
            </p>
          )}
        </div>

        <Field label="Observaciones">
          <textarea
            className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
            value={notes}
            disabled={isSubmitting}
            onChange={(event) => setNotes(event.target.value)}
          />
        </Field>

        <div className="flex justify-end border-t border-slate-200 pt-5">
          <button
            className="h-11 w-full rounded-md bg-water-700 px-5 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300 sm:w-auto"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Guardando retorno..." : "Registrar retorno"}
          </button>
        </div>
      </form>
    </section>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block flex-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-950">{value}</p>
    </div>
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
  return /^\d+(\.\d{1,3})?$/.test(value) && /[1-9]/.test(value);
}

function compareQuantities(left: string, right: string): number {
  const leftUnits = quantityUnits(left);
  const rightUnits = quantityUnits(right);
  return leftUnits === rightUnits ? 0 : leftUnits > rightUnits ? 1 : -1;
}

function quantityUnits(value: string): bigint {
  const [units, decimals = ""] = value.split(".");
  return BigInt(`${units}${decimals.padEnd(3, "0").slice(0, 3)}`);
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

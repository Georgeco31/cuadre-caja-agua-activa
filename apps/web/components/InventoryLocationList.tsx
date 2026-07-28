import {
  INVENTORY_LOCATION_TYPE_LABELS,
  type InventoryLocation,
} from "@/types/inventory";
import type { Vehicle } from "@/types/vehicle";

type InventoryLocationListProps = {
  locations: InventoryLocation[];
  vehicles: Vehicle[];
  canManage?: boolean;
  changingLocationId?: number | null;
  onEdit: (location: InventoryLocation) => void;
  onToggleActive: (location: InventoryLocation) => void;
};

export function InventoryLocationList({
  locations,
  vehicles,
  canManage = true,
  changingLocationId = null,
  onEdit,
  onToggleActive,
}: InventoryLocationListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">Ubicaciones</h2>
        <span className="text-sm text-slate-500">{locations.length}</span>
      </div>

      {locations.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Todavía no hay ubicaciones de inventario.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[840px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Ubicación</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Vehículo</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                {canManage ? (
                  <th className="px-4 py-3 font-medium">Acciones</th>
                ) : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {locations.map((location) => {
                const isChanging = changingLocationId === location.id;
                const vehicle = vehicles.find(
                  (item) => item.id === location.vehicle_id,
                );
                return (
                  <tr key={location.id}>
                    {canManage ? (
                      <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">
                        {location.name}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {location.code ?? "Sin código"}
                      </p>
                      {location.description ? (
                        <p className="mt-1 max-w-64 text-xs text-slate-500">
                          {location.description}
                        </p>
                      ) : null}
                      </td>
                    ) : null}
                    <td className="px-4 py-3 align-top text-slate-700">
                      {INVENTORY_LOCATION_TYPE_LABELS[location.location_type]}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {vehicle?.name ?? "Sin vehículo"}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          location.is_active
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {location.is_active ? "Activa" : "Inactiva"}
                      </span>
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="flex items-center gap-3">
                        <button
                          className="font-semibold text-water-700 hover:text-water-500 disabled:text-slate-400"
                          type="button"
                          disabled={isChanging}
                          onClick={() => onEdit(location)}
                        >
                          Editar
                        </button>
                        <button
                          className={
                            location.is_active
                              ? "font-semibold text-red-700 hover:text-red-600 disabled:text-slate-400"
                              : "font-semibold text-emerald-700 hover:text-emerald-600 disabled:text-slate-400"
                          }
                          type="button"
                          disabled={isChanging}
                          onClick={() => onToggleActive(location)}
                        >
                          {isChanging
                            ? "Actualizando..."
                            : location.is_active
                              ? "Inactivar"
                              : "Reactivar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}


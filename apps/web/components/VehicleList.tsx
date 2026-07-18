import {
  FUEL_TYPE_LABELS,
  VEHICLE_TYPE_LABELS,
  type Vehicle,
} from "@/types/vehicle";

type VehicleListProps = {
  vehicles: Vehicle[];
  hasActiveFilters?: boolean;
  changingVehicleId?: number | null;
  onEdit: (vehicle: Vehicle) => void;
  onToggleActive: (vehicle: Vehicle) => void;
};

export function VehicleList({
  vehicles,
  hasActiveFilters = false,
  changingVehicleId = null,
  onEdit,
  onToggleActive,
}: VehicleListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Vehículos registrados
        </h2>
        <span className="text-sm text-slate-500">{vehicles.length}</span>
      </div>

      {vehicles.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron vehículos con los filtros seleccionados."
            : "Todavía no hay vehículos registrados."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1320px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Vehículo</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Marca y modelo</th>
                <th className="px-4 py-3 font-medium">Combustible</th>
                <th className="px-4 py-3 font-medium">Capacidad</th>
                <th className="px-4 py-3 font-medium">Chofer de referencia</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {vehicles.map((vehicle) => {
                const isChanging = changingVehicleId === vehicle.id;

                return (
                  <tr key={vehicle.id}>
                    <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">{vehicle.name}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {vehicle.plate ?? "Sin placa"} · {vehicle.code ?? "Sin código"}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {VEHICLE_TYPE_LABELS[vehicle.vehicle_type]}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{formatBrandModel(vehicle)}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {[vehicle.year, vehicle.color].filter(Boolean).join(" · ") ||
                          "Sin año ni color"}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {FUEL_TYPE_LABELS[vehicle.fuel_type]}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {vehicle.capacity_reference ?? "Sin referencia"}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {vehicle.reference_driver ?? "Sin referencia"}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          vehicle.is_active
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {vehicle.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="flex items-center gap-3">
                        <button
                          className="font-semibold text-water-700 hover:text-water-500 disabled:cursor-not-allowed disabled:text-slate-400"
                          type="button"
                          disabled={isChanging}
                          onClick={() => onEdit(vehicle)}
                        >
                          Editar
                        </button>
                        <button
                          className={
                            vehicle.is_active
                              ? "font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                              : "font-semibold text-emerald-700 hover:text-emerald-600 disabled:cursor-not-allowed disabled:text-slate-400"
                          }
                          type="button"
                          disabled={isChanging}
                          onClick={() => onToggleActive(vehicle)}
                        >
                          {isChanging
                            ? "Actualizando..."
                            : vehicle.is_active
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

function formatBrandModel(vehicle: Vehicle): string {
  return [vehicle.brand, vehicle.model].filter(Boolean).join(" ") || "Sin marca/modelo";
}

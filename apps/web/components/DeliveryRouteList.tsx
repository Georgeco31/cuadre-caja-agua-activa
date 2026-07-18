import type { DeliveryRoute } from "@/types/deliveryRoute";

type DeliveryRouteListProps = {
  deliveryRoutes: DeliveryRoute[];
  hasActiveFilters?: boolean;
  changingRouteId?: number | null;
  onEdit: (deliveryRoute: DeliveryRoute) => void;
  onToggleActive: (deliveryRoute: DeliveryRoute) => void;
};

export function DeliveryRouteList({
  deliveryRoutes,
  hasActiveFilters = false,
  changingRouteId = null,
  onEdit,
  onToggleActive,
}: DeliveryRouteListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Rutas registradas
        </h2>
        <span className="text-sm text-slate-500">{deliveryRoutes.length}</span>
      </div>

      {deliveryRoutes.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron rutas con los filtros seleccionados."
            : "Todavía no hay rutas registradas."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1280px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Ruta</th>
                <th className="px-4 py-3 font-medium">Zona y sector</th>
                <th className="px-4 py-3 font-medium">Días de atención</th>
                <th className="px-4 py-3 font-medium">Referencias</th>
                <th className="px-4 py-3 font-medium">Efectivo esperado</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {deliveryRoutes.map((deliveryRoute) => {
                const isChanging = changingRouteId === deliveryRoute.id;

                return (
                  <tr key={deliveryRoute.id}>
                    <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">
                        {deliveryRoute.name}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {deliveryRoute.code ?? "Sin código"}
                      </p>
                      {deliveryRoute.description ? (
                        <p className="mt-1 max-w-64 text-xs text-slate-500">
                          {deliveryRoute.description}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{deliveryRoute.zone ?? "Sin zona"}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {deliveryRoute.sector ?? "Sin sector"}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {deliveryRoute.service_days ?? "Sin días definidos"}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>
                        Chofer: {deliveryRoute.reference_driver ?? "Sin referencia"}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Vehículo: {deliveryRoute.reference_vehicle ?? "Sin referencia"}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top font-medium text-slate-950">
                      {formatMoney(deliveryRoute.expected_daily_cash)}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          deliveryRoute.is_active
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {deliveryRoute.is_active ? "Activa" : "Inactiva"}
                      </span>
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="flex items-center gap-3">
                        <button
                          className="font-semibold text-water-700 hover:text-water-500 disabled:cursor-not-allowed disabled:text-slate-400"
                          type="button"
                          disabled={isChanging}
                          onClick={() => onEdit(deliveryRoute)}
                        >
                          Editar
                        </button>
                        <button
                          className={
                            deliveryRoute.is_active
                              ? "font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                              : "font-semibold text-emerald-700 hover:text-emerald-600 disabled:cursor-not-allowed disabled:text-slate-400"
                          }
                          type="button"
                          disabled={isChanging}
                          onClick={() => onToggleActive(deliveryRoute)}
                        >
                          {isChanging
                            ? "Actualizando..."
                            : deliveryRoute.is_active
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

function formatMoney(value: string): string {
  const [units, decimals = ""] = value.split(".");
  return `$${units}.${decimals.padEnd(2, "0").slice(0, 2)}`;
}

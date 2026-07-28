import {
  CUSTOMER_TYPE_LABELS,
  type Customer,
} from "@/types/customer";

type CustomerListProps = {
  customers: Customer[];
  canManage?: boolean;
  hasActiveFilters?: boolean;
  changingCustomerId?: number | null;
  onEdit: (customer: Customer) => void;
  onToggleActive: (customer: Customer) => void;
};

export function CustomerList({
  customers,
  canManage = true,
  hasActiveFilters = false,
  changingCustomerId = null,
  onEdit,
  onToggleActive,
}: CustomerListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Clientes registrados
        </h2>
        <span className="text-sm text-slate-500">{customers.length}</span>
      </div>

      {customers.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron clientes con los filtros seleccionados."
            : "Todavía no hay clientes registrados."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Cliente</th>
                <th className="px-4 py-3 font-medium">Contacto</th>
                <th className="px-4 py-3 font-medium">Ubicación</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Crédito</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                {canManage ? (
                  <th className="px-4 py-3 font-medium">Acciones</th>
                ) : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {customers.map((customer) => {
                const isChanging = changingCustomerId === customer.id;

                return (
                  <tr key={customer.id}>
                    {canManage ? (
                      <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">{customer.name}</p>
                      <p className="mt-1 max-w-56 text-xs text-slate-500">
                        {customer.route_reference ?? "Sin ruta o zona"}
                      </p>
                      </td>
                    ) : null}
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{customer.primary_phone ?? "Sin teléfono"}</p>
                      {customer.secondary_phone ? (
                        <p className="mt-1 text-xs text-slate-500">
                          {customer.secondary_phone}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{customer.sector ?? "Sin sector"}</p>
                      {customer.address ? (
                        <p className="mt-1 max-w-64 text-xs text-slate-500">
                          {customer.address}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {CUSTOMER_TYPE_LABELS[customer.customer_type]}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {customer.credit_allowed
                        ? formatMoney(customer.credit_limit)
                        : "No permitido"}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          customer.is_active
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {customer.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="flex items-center gap-3">
                        <button
                          className="font-semibold text-water-700 hover:text-water-500 disabled:cursor-not-allowed disabled:text-slate-400"
                          type="button"
                          disabled={isChanging}
                          onClick={() => onEdit(customer)}
                        >
                          Editar
                        </button>
                        <button
                          className={
                            customer.is_active
                              ? "font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                              : "font-semibold text-emerald-700 hover:text-emerald-600 disabled:cursor-not-allowed disabled:text-slate-400"
                          }
                          type="button"
                          disabled={isChanging}
                          onClick={() => onToggleActive(customer)}
                        >
                          {isChanging
                            ? "Actualizando..."
                            : customer.is_active
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

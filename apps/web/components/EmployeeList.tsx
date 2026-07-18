import {
  EMPLOYEE_TYPE_LABELS,
  PAYMENT_FREQUENCY_LABELS,
  type Employee,
} from "@/types/employee";

type EmployeeListProps = {
  employees: Employee[];
  hasActiveFilters?: boolean;
  changingEmployeeId?: number | null;
  onEdit: (employee: Employee) => void;
  onToggleActive: (employee: Employee) => void;
};

export function EmployeeList({
  employees,
  hasActiveFilters = false,
  changingEmployeeId = null,
  onEdit,
  onToggleActive,
}: EmployeeListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Empleados registrados
        </h2>
        <span className="text-sm text-slate-500">{employees.length}</span>
      </div>

      {employees.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron empleados con los filtros seleccionados."
            : "Todavía no hay empleados registrados."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1180px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Empleado</th>
                <th className="px-4 py-3 font-medium">Contacto</th>
                <th className="px-4 py-3 font-medium">Cargo y tipo</th>
                <th className="px-4 py-3 font-medium">Sueldo base</th>
                <th className="px-4 py-3 font-medium">Fecha de ingreso</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {employees.map((employee) => {
                const isChanging = changingEmployeeId === employee.id;

                return (
                  <tr key={employee.id}>
                    <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">
                        {employee.first_name} {employee.last_name}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {employee.identification ?? "Sin identificación"}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{employee.primary_phone ?? "Sin teléfono"}</p>
                      {employee.secondary_phone ? (
                        <p className="mt-1 text-xs text-slate-500">
                          {employee.secondary_phone}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{employee.job_position ?? "Sin cargo"}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {EMPLOYEE_TYPE_LABELS[employee.employee_type]}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">
                        {formatMoney(employee.base_salary)}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {PAYMENT_FREQUENCY_LABELS[employee.payment_frequency]}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {formatDate(employee.hire_date)}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          employee.is_active
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {employee.is_active ? "Activo" : "Inactivo"}
                      </span>
                      {!employee.is_active && employee.termination_date ? (
                        <p className="mt-1 text-xs text-slate-500">
                          Salida: {formatDate(employee.termination_date)}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <div className="flex items-center gap-3">
                        <button
                          className="font-semibold text-water-700 hover:text-water-500 disabled:cursor-not-allowed disabled:text-slate-400"
                          type="button"
                          disabled={isChanging}
                          onClick={() => onEdit(employee)}
                        >
                          Editar
                        </button>
                        <button
                          className={
                            employee.is_active
                              ? "font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                              : "font-semibold text-emerald-700 hover:text-emerald-600 disabled:cursor-not-allowed disabled:text-slate-400"
                          }
                          type="button"
                          disabled={isChanging}
                          onClick={() => onToggleActive(employee)}
                        >
                          {isChanging
                            ? "Actualizando..."
                            : employee.is_active
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

function formatDate(value: string | null): string {
  if (!value) {
    return "Sin fecha";
  }
  return new Intl.DateTimeFormat("es-EC", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

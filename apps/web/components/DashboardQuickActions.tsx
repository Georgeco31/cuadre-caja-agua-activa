import Link from "next/link";

const actions = [
  {
    href: "/dashboard/route-loads",
    title: "Carga de camión",
    description: "Mover productos desde bodega hacia un vehículo para una ruta.",
    primary: false,
  },
  {
    href: "/dashboard/production",
    title: "Producción",
    description: "Registrar producción y envasado diario.",
    primary: false,
  },
  {
    href: "/dashboard/inventory",
    title: "Inventario",
    description: "Controlar stock por ubicación con entradas, salidas y ajustes.",
    primary: false,
  },
  {
    href: "/dashboard/receivables",
    title: "Cobros y abonos",
    description: "Registrar pagos sobre ventas a crédito.",
    primary: false,
  },
  {
    href: "/dashboard/receivables/reports",
    title: "Cuentas por cobrar",
    description: "Consultar clientes con saldo pendiente y estado de cuenta.",
    primary: false,
  },
  {
    href: "/dashboard/sales/credit",
    title: "Ventas a crédito",
    description: "Registrar ventas pendientes de cobro.",
    primary: false,
  },
  {
    href: "/dashboard/sales/cash",
    title: "Ventas de contado",
    description: "Registrar ventas pagadas al momento.",
    primary: false,
  },
  {
    href: "/dashboard/vehicles",
    title: "Vehículos",
    description: "Registrar camiones y vehículos para el control operativo.",
    primary: false,
  },
  {
    href: "/dashboard/delivery-routes",
    title: "Rutas",
    description: "Registrar rutas y zonas de entrega para el control operativo.",
    primary: false,
  },
  {
    href: "/dashboard/employees",
    title: "Empleados",
    description: "Registrar empleados, cargos y datos base para pagos futuros.",
    primary: false,
  },
  {
    href: "/dashboard/products",
    title: "Productos",
    description: "Registrar productos, presentaciones y precios base.",
    primary: false,
  },
  {
    href: "/dashboard/customers",
    title: "Clientes",
    description: "Registrar y consultar clientes de Agua Activa.",
    primary: false,
  },
  {
    href: "/dashboard/cash-session",
    title: "Registrar o consultar cuadre",
    description: "Abrir, crear o continuar el cuadre de una fecha.",
    primary: true,
  },
  {
    href: "/dashboard/history",
    title: "Ver historial",
    description: "Consultar cuadres registrados y sus detalles.",
    primary: false,
  },
  {
    href: "/dashboard/reports",
    title: "Ver resumen acumulado",
    description: "Revisar totales acumulados por rango y estado.",
    primary: false,
  },
] as const;

export function DashboardQuickActions() {
  return (
    <section aria-labelledby="dashboard-actions-title" className="space-y-3">
      <div>
        <p className="text-sm font-medium text-water-700">Operación</p>
        <h2
          id="dashboard-actions-title"
          className="mt-1 text-xl font-semibold text-slate-950"
        >
          Acciones rápidas
        </h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {actions.map((action) => (
          <Link
            className={
              action.primary
                ? "rounded-lg border border-water-700 bg-water-700 p-4 text-white shadow-sm transition hover:bg-water-500"
                : "rounded-lg border border-slate-200 bg-white p-4 text-slate-950 shadow-sm transition hover:border-water-500"
            }
            href={action.href}
            key={action.href}
          >
            <span className="block text-base font-semibold">
              {action.title}
            </span>
            <span
              className={
                action.primary
                  ? "mt-2 block text-sm leading-6 text-water-50"
                  : "mt-2 block text-sm leading-6 text-slate-600"
              }
            >
              {action.description}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}

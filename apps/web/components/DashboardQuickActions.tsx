import type { UserRole } from "@/types/auth";

import { ActionCard } from "@/components/ui/ActionCard";
import { StatusBadge } from "@/components/ui/StatusBadge";

type DashboardAction = {
  href: string;
  title: string;
  description: string;
  icon: string;
  primary?: boolean;
  adminOnly?: boolean;
};

type DashboardActionGroup = {
  id: string;
  title: string;
  description: string;
  actions: DashboardAction[];
};

const actionGroups: DashboardActionGroup[] = [
  {
    id: "caja",
    title: "Inicio / Caja",
    description: "Cuadre diario e historial de sesiones.",
    actions: [
      {
        href: "/dashboard/cash-session",
        title: "Registrar o consultar cuadre",
        description: "Abrir, crear o continuar el cuadre de una fecha.",
        icon: "CJ",
        primary: true,
      },
      {
        href: "/dashboard/history",
        title: "Ver historial",
        description: "Consultar cuadres registrados y sus detalles.",
        icon: "HI",
      },
    ],
  },
  {
    id: "operacion",
    title: "Operación diaria",
    description: "Seguimiento del día, gastos, compras y equipo.",
    actions: [
      {
        href: "/dashboard/daily-summary",
        title: "Resumen diario",
        description: "Ver caja, producción, rutas, ventas y alertas del día.",
        icon: "RD",
      },
      {
        href: "/dashboard/operating-expenses",
        title: "Gastos operativos",
        description: "Registrar gastos generales fuera del cuadre diario de caja.",
        icon: "GO",
      },
      {
        href: "/dashboard/purchases",
        title: "Compras",
        description:
          "Registrar compras sin afectar caja ni inventario automáticamente.",
        icon: "CO",
      },
      {
        href: "/dashboard/employees/control",
        title: "Control de empleados",
        description: "Asistencia, anticipos y préstamos de empleados.",
        icon: "CE",
      },
      {
        href: "/dashboard/payroll",
        title: "Roles de pago",
        description:
          "Calcular roles de empleados sin modificar caja automáticamente.",
        icon: "NP",
      },
    ],
  },
  {
    id: "ventas",
    title: "Ventas y clientes",
    description: "Ventas, cartera, clientes y precios.",
    actions: [
      {
        href: "/dashboard/sales/cash",
        title: "Ventas de contado",
        description: "Registrar ventas pagadas al momento.",
        icon: "VC",
      },
      {
        href: "/dashboard/sales/credit",
        title: "Ventas a crédito",
        description: "Registrar ventas pendientes de cobro.",
        icon: "CR",
      },
      {
        href: "/dashboard/customers",
        title: "Clientes",
        description: "Registrar y consultar clientes de Agua Activa.",
        icon: "CL",
      },
      {
        href: "/dashboard/receivables",
        title: "Cobros y abonos",
        description: "Registrar pagos sobre ventas a crédito.",
        icon: "CA",
      },
      {
        href: "/dashboard/receivables/reports",
        title: "Cuentas por cobrar",
        description:
          "Consultar clientes con saldo pendiente y estado de cuenta.",
        icon: "CC",
      },
      {
        href: "/dashboard/pricing",
        title: "Listas de precios",
        description: "Gestionar precios especiales por cliente o ruta.",
        icon: "LP",
        adminOnly: true,
      },
    ],
  },
  {
    id: "rutas",
    title: "Rutas",
    description: "Planeación, carga, retorno, cierre y control de efectivo.",
    actions: [
      {
        href: "/dashboard/delivery-routes",
        title: "Rutas",
        description:
          "Registrar rutas y zonas de entrega para el control operativo.",
        icon: "RU",
      },
      {
        href: "/dashboard/vehicles",
        title: "Vehículos",
        description:
          "Registrar camiones y vehículos para el control operativo.",
        icon: "VH",
      },
      {
        href: "/dashboard/route-loads",
        title: "Carga de camión",
        description:
          "Mover productos desde bodega hacia un vehículo para una ruta.",
        icon: "CG",
      },
      {
        href: "/dashboard/route-returns",
        title: "Retorno de ruta",
        description: "Registrar productos que regresan del vehículo a bodega.",
        icon: "RT",
      },
      {
        href: "/dashboard/route-activity",
        title: "Actividad de ruta",
        description: "Consultar ventas y cobros asociados a una carga de ruta.",
        icon: "AR",
      },
      {
        href: "/dashboard/route-closures",
        title: "Cierre de ruta",
        description:
          "Comparar efectivo esperado contra efectivo entregado por una ruta.",
        icon: "CI",
      },
      {
        href: "/dashboard/route-cash-receipts",
        title: "Dinero de ruta en caja",
        description:
          "Registrar efectivo de rutas cerradas dentro de un cuadre abierto.",
        icon: "DC",
      },
      {
        href: "/dashboard/route-cash-comparison",
        title: "Rutas vs caja",
        description:
          "Comparar efectivo entregado por rutas con el cuadre general de caja.",
        icon: "RC",
      },
    ],
  },
  {
    id: "inventario",
    title: "Inventario y producción",
    description: "Productos, existencias, lotes, fórmulas e insumos.",
    actions: [
      {
        href: "/dashboard/products",
        title: "Productos",
        description: "Registrar productos, presentaciones y precios base.",
        icon: "PR",
      },
      {
        href: "/dashboard/inventory",
        title: "Inventario",
        description:
          "Controlar stock por ubicación con entradas, salidas y ajustes.",
        icon: "IN",
      },
      {
        href: "/dashboard/production",
        title: "Producción",
        description: "Registrar producción y envasado diario.",
        icon: "PD",
      },
      {
        href: "/dashboard/production/recipes",
        title: "Fórmulas de producción",
        description:
          "Definir insumos, materia prima y costos estimados de producción.",
        icon: "FP",
      },
      {
        href: "/dashboard/production/material-consumption",
        title: "Consumo de insumos",
        description:
          "Consumir materia prima usando fórmulas de producción.",
        icon: "CI",
      },
    ],
  },
  {
    id: "administracion",
    title: "Administración",
    description: "Personal, proveedores y control de acceso.",
    actions: [
      {
        href: "/dashboard/employees",
        title: "Empleados",
        description:
          "Registrar empleados, cargos y datos base para pagos futuros.",
        icon: "EM",
      },
      {
        href: "/dashboard/suppliers",
        title: "Proveedores",
        description: "Gestionar proveedores de Agua Activa.",
        icon: "PV",
      },
      {
        href: "/dashboard/users",
        title: "Usuarios y permisos",
        description: "Crear cuentas, asignar roles y controlar accesos.",
        icon: "UP",
        adminOnly: true,
      },
    ],
  },
  {
    id: "reportes",
    title: "Reportes y control",
    description: "Análisis acumulado, gerencia y descargas.",
    actions: [
      {
        href: "/dashboard/reports",
        title: "Ver resumen acumulado",
        description: "Revisar totales acumulados por rango y estado.",
        icon: "RA",
      },
      {
        href: "/dashboard/monthly-summary",
        title: "Reporte mensual",
        description:
          "Revisar caja, producción, ventas, rutas y alertas de todo el mes.",
        icon: "RM",
      },
      {
        href: "/dashboard/management",
        title: "Panel gerencial",
        description:
          "Ver indicadores, alertas y gráficos generales del negocio.",
        icon: "PG",
        adminOnly: true,
      },
      {
        href: "/dashboard/exports",
        title: "Exportaciones",
        description: "Descargar reportes del ERP en Excel y PDF.",
        icon: "EX",
        adminOnly: true,
      },
    ],
  },
];

const frequentActionHrefs = new Set([
  "/dashboard/cash-session",
  "/dashboard/sales/cash",
  "/dashboard/route-loads",
  "/dashboard/daily-summary",
]);

export function DashboardQuickActions({ role }: { role?: UserRole }) {
  const canViewAction = (action: DashboardAction) =>
    !action.adminOnly || role === "admin_auditor";
  const frequentActions = actionGroups
    .flatMap((group) => group.actions)
    .filter(
      (action) => canViewAction(action) && frequentActionHrefs.has(action.href),
    );

  return (
    <section
      aria-labelledby="dashboard-actions-title"
      className="space-y-8"
      id="modulos"
    >
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
          Acceso directo
        </p>
        <h2
          className="mt-2 text-2xl font-semibold tracking-tight text-slate-950"
          id="dashboard-actions-title"
        >
          Acciones frecuentes
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Atajos a las tareas habituales de la operación diaria.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {frequentActions.map((action) => (
          <ActionCard
            description={action.description}
            href={action.href}
            icon={action.icon}
            key={`frequent-${action.href}`}
            title={action.title}
            variant={action.primary ? "primary" : "secondary"}
          />
        ))}
      </div>

      <div className="space-y-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-water-700">
              Navegación completa
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
              Todos los módulos
            </h2>
          </div>
          <StatusBadge label="7 grupos operativos" tone="info" />
        </div>

        {actionGroups.map((group) => {
          const visibleActions = group.actions.filter(canViewAction);
          if (visibleActions.length === 0) {
            return null;
          }

          return (
            <section
              aria-labelledby={`dashboard-group-${group.id}`}
              className="rounded-3xl border border-slate-200 bg-white p-4 shadow-card sm:p-6"
              key={group.id}
            >
              <div className="mb-4">
                <h3
                  className="text-lg font-semibold text-slate-950"
                  id={`dashboard-group-${group.id}`}
                >
                  {group.title}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {group.description}
                </p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
                {visibleActions.map((action) => (
                  <ActionCard
                    badge={
                      action.adminOnly ? (
                        <StatusBadge label="Admin" tone="neutral" />
                      ) : undefined
                    }
                    description={action.description}
                    href={action.href}
                    icon={action.icon}
                    key={action.href}
                    title={action.title}
                    variant={action.primary ? "primary" : "secondary"}
                  />
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </section>
  );
}

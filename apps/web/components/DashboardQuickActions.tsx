import type { UserRole } from "@/types/auth";

import {
  DashboardModuleGroup,
  type DashboardModuleAction,
} from "@/components/DashboardModuleGroup";
import { ActionCard } from "@/components/ui/ActionCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { canAccessDashboardPath } from "@/lib/frontendPermissions";

type DashboardAction = {
  href: string;
  title: string;
  description: string;
  icon: string;
  operatorDescription?: string;
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
    id: "operacion",
    title: "Operación diaria",
    description: "Caja, seguimiento del día, gastos, compras y equipo.",
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
        operatorDescription: "Consultar los gastos operativos registrados.",
        icon: "GO",
      },
      {
        href: "/dashboard/purchases",
        title: "Compras",
        description:
          "Registrar compras sin afectar caja ni inventario automáticamente.",
        operatorDescription: "Consultar las compras registradas.",
        icon: "CO",
      },
      {
        href: "/dashboard/employees/control",
        title: "Control de empleados",
        description: "Asistencia, anticipos y préstamos de empleados.",
        icon: "CE",
        adminOnly: true,
      },
      {
        href: "/dashboard/payroll",
        title: "Roles de pago",
        description:
          "Calcular roles de empleados sin modificar caja automáticamente.",
        icon: "NP",
        adminOnly: true,
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
        href: "/dashboard/simple-routes",
        title: "Rutas simples (recomendado)",
        description:
          "Registrar la hoja diaria de George sin inventario ni ventas oficiales.",
        icon: "RS",
        primary: true,
      },
      {
        href: "/dashboard/delivery-routes",
        title: "Rutas tradicionales (legacy)",
        description:
          "Registrar rutas y zonas de entrega para el control operativo.",
        operatorDescription: "Consultar rutas y zonas de entrega.",
        icon: "RU",
      },
      {
        href: "/dashboard/vehicles",
        title: "Vehículos",
        description:
          "Registrar camiones y vehículos para el control operativo.",
        operatorDescription: "Consultar los vehículos registrados.",
        icon: "VH",
      },
      {
        href: "/dashboard/route-loads",
        title: "Carga de camión",
        description:
          "Mover productos desde bodega hacia un vehículo para una ruta.",
        operatorDescription: "Consultar las cargas de camión registradas.",
        icon: "CG",
      },
      {
        href: "/dashboard/route-returns",
        title: "Retorno de ruta",
        description: "Registrar productos que regresan del vehículo a bodega.",
        operatorDescription: "Consultar los retornos de ruta registrados.",
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
        operatorDescription: "Consultar los cierres financieros de ruta.",
        icon: "CI",
      },
      {
        href: "/dashboard/route-cash-receipts",
        title: "Dinero de ruta en caja",
        description:
          "Registrar efectivo de rutas cerradas dentro de un cuadre abierto.",
        operatorDescription: "Consultar el dinero de ruta registrado en caja.",
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
        operatorDescription: "Consultar productos, presentaciones y precios vigentes.",
        icon: "PR",
      },
      {
        href: "/dashboard/inventory",
        title: "Inventario",
        description:
          "Controlar stock por ubicación con entradas, salidas y ajustes.",
        operatorDescription:
          "Consultar stock y registrar entradas o salidas sin costos.",
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
        adminOnly: true,
      },
      {
        href: "/dashboard/production/material-consumption",
        title: "Consumo de insumos",
        description:
          "Consumir materia prima usando fórmulas de producción.",
        icon: "CI",
        adminOnly: true,
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
        adminOnly: true,
      },
      {
        href: "/dashboard/suppliers",
        title: "Proveedores",
        description: "Gestionar proveedores de Agua Activa.",
        operatorDescription: "Consultar el directorio de proveedores.",
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
        adminOnly: true,
      },
      {
        href: "/dashboard/monthly-summary",
        title: "Reporte mensual",
        description:
          "Revisar caja, producción, ventas, rutas y alertas de todo el mes.",
        icon: "RM",
        adminOnly: true,
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
  "/dashboard/sales/credit",
  "/dashboard/customers",
  "/dashboard/route-loads",
  "/dashboard/production",
  "/dashboard/reports",
  "/dashboard/exports",
]);

export function DashboardQuickActions({ role }: { role?: UserRole }) {
  const canViewAction = (action: DashboardAction) =>
    canAccessDashboardPath(role, action.href);
  const orderedGroups = [...actionGroups].sort(
    (first, second) =>
      groupDisplayOrder.indexOf(first.id) - groupDisplayOrder.indexOf(second.id),
  );
  const frequentActions = orderedGroups
    .flatMap((group) => group.actions)
    .filter(
      (action) => canViewAction(action) && frequentActionHrefs.has(action.href),
    );
  const visibleActionCount = orderedGroups
    .flatMap((group) => group.actions)
    .filter(canViewAction).length;

  return (
    <section
      aria-labelledby="dashboard-actions-title"
      className="scroll-mt-24 space-y-8"
      id="modulos"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
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
            Entra directamente a las tareas habituales de la operación.
          </p>
        </div>
        <StatusBadge
          label={`${visibleActionCount} destinos disponibles`}
          tone="info"
        />
      </div>

      <div className="grid min-w-0 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {frequentActions.map((action) => (
          <ActionCard
            description={
              role === "operator" && action.operatorDescription
                ? action.operatorDescription
                : action.description
            }
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
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Los mismos accesos del ERP, organizados por área de trabajo.
            </p>
          </div>
          <StatusBadge label="6 grupos operativos" tone="neutral" />
        </div>

        <div className="grid min-w-0 items-start gap-5 xl:grid-cols-2">
          {orderedGroups.map((group, index) => {
            const visibleActions: DashboardModuleAction[] = group.actions
              .filter(canViewAction)
              .map((action) => ({
                badge: action.adminOnly ? (
                  <StatusBadge label="Admin" tone="neutral" />
                ) : undefined,
                description:
                  role === "operator" && action.operatorDescription
                    ? action.operatorDescription
                    : action.description,
                href: action.href,
                icon: action.icon,
                title: action.title,
                variant: action.primary ? "primary" : "secondary",
              }));

            if (visibleActions.length === 0) {
              return null;
            }

            return (
              <DashboardModuleGroup
                actions={visibleActions}
                description={group.description}
                id={group.id}
                index={index + 1}
                key={group.id}
                title={group.title}
              />
            );
          })}
        </div>
      </div>
    </section>
  );
}

const groupDisplayOrder = [
  "operacion",
  "ventas",
  "rutas",
  "inventario",
  "reportes",
  "administracion",
];

export type SimpleRouteExportType =
  | "summary"
  | "detail"
  | "sales"
  | "pending"
  | "collections"
  | "expenses"
  | "settlements";

export type SimpleRouteExportFilters = {
  start_date?: string;
  end_date?: string;
  seller?: string;
  route_label?: string;
  status?: "draft" | "in_progress" | "settled" | "cancelled";
  sale_type?: "cash" | "credit" | "partial" | "all";
  route_sheet_id?: number;
};

export type SimpleRouteExportDefinition = {
  type: SimpleRouteExportType;
  label: string;
  description: string;
  filename: string;
};

export const SIMPLE_ROUTE_EXPORT_NOTICE =
  "Estas exportaciones usan únicamente Rutas Simples. No incluyen ventas oficiales, cartera formal ni inventario.";

export const SIMPLE_ROUTE_EXPORTS: SimpleRouteExportDefinition[] = [
  {
    type: "summary",
    label: "Resumen de Rutas Simples",
    description: "Indicadores, estados, rutas y ranking del período.",
    filename: "resumen-rutas-simples.xlsx",
  },
  {
    type: "detail",
    label: "Detalle de Ruta Simple",
    description: "Hoja completa con viajes, ventas, abonos, gastos y cuadre.",
    filename: "ruta-simple.xlsx",
  },
  {
    type: "sales",
    label: "Ventas de Ruta",
    description: "Ventas de contado, fiado y parcial con productos.",
    filename: "ventas-rutas-simples.xlsx",
  },
  {
    type: "pending",
    label: "Fiados de Ruta",
    description: "Saldos pendientes después de los abonos registrados.",
    filename: "fiados-rutas-simples.xlsx",
  },
  {
    type: "collections",
    label: "Abonos de Ruta",
    description: "Abonos recibidos dentro de cada Ruta Simple.",
    filename: "abonos-rutas-simples.xlsx",
  },
  {
    type: "expenses",
    label: "Gastos de Ruta",
    description: "Gastos registrados por vendedor, ruta y categoría.",
    filename: "gastos-rutas-simples.xlsx",
  },
  {
    type: "settlements",
    label: "Cuadres de Ruta",
    description: "Diferencias de producto y efectivo por Ruta Simple.",
    filename: "cuadres-rutas-simples.xlsx",
  },
];

const ENDPOINTS: Record<Exclude<SimpleRouteExportType, "detail">, string> = {
  summary: "simple-routes-summary.xlsx",
  sales: "simple-route-sales.xlsx",
  pending: "simple-route-pending.xlsx",
  collections: "simple-route-collections.xlsx",
  expenses: "simple-route-expenses.xlsx",
  settlements: "simple-route-settlements.xlsx",
};

export function buildSimpleRouteExportPath(
  type: SimpleRouteExportType,
  filters: SimpleRouteExportFilters = {},
): string {
  if (
    filters.start_date &&
    filters.end_date &&
    filters.end_date < filters.start_date
  ) {
    throw new Error("La fecha hasta no puede ser menor que la fecha desde.");
  }
  if (type === "detail") {
    const routeSheetId = Number(filters.route_sheet_id);
    if (!Number.isInteger(routeSheetId) || routeSheetId <= 0) {
      throw new Error("Selecciona una Ruta Simple para exportar su detalle.");
    }
    return `/reports/exports/simple-routes/${routeSheetId}.xlsx`;
  }

  const searchParams = new URLSearchParams();
  if (filters.start_date) searchParams.set("start_date", filters.start_date);
  if (filters.end_date) searchParams.set("end_date", filters.end_date);
  if (filters.seller?.trim()) searchParams.set("seller", filters.seller.trim());
  if (filters.route_label?.trim()) {
    searchParams.set("route_label", filters.route_label.trim());
  }
  if (
    filters.status &&
    (type === "summary" || type === "settlements")
  ) {
    searchParams.set("status", filters.status);
  }
  if (filters.sale_type && type === "sales") {
    searchParams.set("sale_type", filters.sale_type);
  }
  const query = searchParams.toString();
  return `/reports/exports/${ENDPOINTS[type]}${query ? `?${query}` : ""}`;
}

export function getSimpleRouteExportFilename(
  type: SimpleRouteExportType,
  routeSheetId?: number,
): string {
  if (type === "detail" && routeSheetId) {
    return `ruta-simple-${routeSheetId}.xlsx`;
  }
  return (
    SIMPLE_ROUTE_EXPORTS.find((definition) => definition.type === type)
      ?.filename ?? "rutas-simples.xlsx"
  );
}

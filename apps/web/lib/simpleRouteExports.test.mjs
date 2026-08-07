import assert from "node:assert/strict";
import test from "node:test";

import { canAccessDashboardPath } from "./frontendPermissions.ts";
import {
  buildSimpleRouteExportPath,
  getSimpleRouteExportFilename,
  SIMPLE_ROUTE_EXPORT_NOTICE,
  SIMPLE_ROUTE_EXPORTS,
} from "./simpleRouteExports.ts";

test("simple route export catalog exposes every requested Excel report", () => {
  assert.deepEqual(
    SIMPLE_ROUTE_EXPORTS.map((report) => report.label),
    [
      "Resumen de Rutas Simples",
      "Detalle de Ruta Simple",
      "Ventas de Ruta",
      "Fiados de Ruta",
      "Abonos de Ruta",
      "Gastos de Ruta",
      "Cuadres de Ruta",
    ],
  );
  assert.equal(
    SIMPLE_ROUTE_EXPORT_NOTICE,
    "Estas exportaciones usan únicamente Rutas Simples. No incluyen ventas oficiales, cartera formal ni inventario.",
  );
});

test("simple route paths use the dedicated endpoints and supported filters", () => {
  assert.equal(
    buildSimpleRouteExportPath("summary", {
      start_date: "2026-08-01",
      end_date: "2026-08-31",
      seller: " George ",
      route_label: "Centro",
      status: "settled",
    }),
    "/reports/exports/simple-routes-summary.xlsx?start_date=2026-08-01&end_date=2026-08-31&seller=George&route_label=Centro&status=settled",
  );
  assert.equal(
    buildSimpleRouteExportPath("sales", { sale_type: "partial" }),
    "/reports/exports/simple-route-sales.xlsx?sale_type=partial",
  );
  assert.equal(
    buildSimpleRouteExportPath("collections"),
    "/reports/exports/simple-route-collections.xlsx",
  );
});

test("detail export requires a selected simple route", () => {
  assert.throws(
    () => buildSimpleRouteExportPath("detail"),
    /Selecciona una Ruta Simple/,
  );
  assert.equal(
    buildSimpleRouteExportPath("detail", { route_sheet_id: 17 }),
    "/reports/exports/simple-routes/17.xlsx",
  );
  assert.equal(getSimpleRouteExportFilename("detail", 17), "ruta-simple-17.xlsx");
});

test("operator cannot see exports or enter the direct URL", () => {
  assert.equal(
    canAccessDashboardPath("operator", "/dashboard/exports"),
    false,
  );
  assert.equal(
    canAccessDashboardPath("operator", "/dashboard/exports/simple-routes"),
    false,
  );
  assert.equal(
    canAccessDashboardPath("admin_auditor", "/dashboard/exports"),
    true,
  );
});

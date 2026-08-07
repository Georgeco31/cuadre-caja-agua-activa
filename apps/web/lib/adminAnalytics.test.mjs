import assert from "node:assert/strict";
import test from "node:test";

import {
  ADMIN_ANALYTICS_TEXT,
  canShowAdminAnalytics,
  getAnalyticsPreset,
  getAnalyticsViewState,
  getSalesComparison,
} from "./adminAnalytics.ts";

test("admin sees analytics while operator keeps the simple operational panel", () => {
  assert.equal(canShowAdminAnalytics("admin_auditor"), true);
  assert.equal(canShowAdminAnalytics("operator"), false);
  assert.equal(canShowAdminAnalytics(null), false);
});

test("analytics presets prepare today, last seven days and current month", () => {
  const today = new Date(2026, 6, 29, 12, 0, 0);
  assert.deepEqual(getAnalyticsPreset("today", today), {
    start_date: "2026-07-29",
    end_date: "2026-07-29",
  });
  assert.deepEqual(getAnalyticsPreset("last7", today), {
    start_date: "2026-07-23",
    end_date: "2026-07-29",
  });
  assert.deepEqual(getAnalyticsPreset("month", today), {
    start_date: "2026-07-01",
    end_date: "2026-07-29",
  });
});

test("analytics view states cover loading, error, empty and ready", () => {
  assert.equal(
    getAnalyticsViewState({ error: "", hasData: false, isLoading: true }),
    "loading",
  );
  assert.equal(
    getAnalyticsViewState({
      error: "No disponible",
      hasData: false,
      isLoading: false,
    }),
    "error",
  );
  assert.equal(
    getAnalyticsViewState({ error: "", hasData: false, isLoading: false }),
    "empty",
  );
  assert.equal(
    getAnalyticsViewState({ error: "", hasData: true, isLoading: false }),
    "ready",
  );
});

test("dashboard uses the approved names and separation note", () => {
  assert.equal(ADMIN_ANALYTICS_TEXT.officialSales, "Ventas oficiales");
  assert.equal(ADMIN_ANALYTICS_TEXT.routeSales, "Ventas de ruta");
  assert.equal(
    ADMIN_ANALYTICS_TEXT.totalWithRoutes,
    "Total vendido con rutas",
  );
  assert.equal(
    ADMIN_ANALYTICS_TEXT.separationNote,
    "Las rutas simples son control operativo separado. No afectan cartera formal, inventario ni ventas oficiales.",
  );
  assert.notEqual(
    ADMIN_ANALYTICS_TEXT.officialCreditSales,
    ADMIN_ANALYTICS_TEXT.routePending,
  );
  assert.notEqual(
    ADMIN_ANALYTICS_TEXT.officialCollections,
    ADMIN_ANALYTICS_TEXT.routeCollections,
  );
});

test("sales comparison keeps official and route amounts separate", () => {
  assert.deepEqual(getSalesComparison("150.00", "50.00"), [
    {
      key: "official",
      label: "Ventas oficiales",
      amount: 150,
      percentage: 75,
    },
    {
      key: "routes",
      label: "Ventas de ruta",
      amount: 50,
      percentage: 25,
    },
  ]);
  assert.deepEqual(
    getSalesComparison("0.00", "0.00").map((item) => item.percentage),
    [0, 0],
  );
});

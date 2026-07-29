import assert from "node:assert/strict";
import test from "node:test";

import {
  getRouteSettlementMessages,
  requiresDifferenceObservation,
  ROUTE_SETTLEMENT_STATUS_LABELS,
} from "./routeSettlement.ts";

test("labels the three simple settlement states", () => {
  assert.equal(ROUTE_SETTLEMENT_STATUS_LABELS.pending, "Pendiente");
  assert.equal(ROUTE_SETTLEMENT_STATUS_LABELS.balanced, "Cuadrada");
  assert.equal(
    ROUTE_SETTLEMENT_STATUS_LABELS.with_difference,
    "Con diferencia",
  );
});

test("shows clear pending and balanced messages", () => {
  assert.deepEqual(
    getRouteSettlementMessages({
      route_return_id: null,
      delivered_cash_amount: null,
      physical_vs_registered_difference: null,
      cash_difference: null,
      status: "pending",
      items: [],
    }),
    [
      "No hay retorno registrado todavía.",
      "No hay dinero entregado registrado todavía.",
    ],
  );
  assert.deepEqual(
    getRouteSettlementMessages({
      route_return_id: 2,
      delivered_cash_amount: "90.00",
      physical_vs_registered_difference: "0.000",
      cash_difference: "0.00",
      status: "balanced",
      items: [{ physical_vs_registered_difference: "0.000" }],
    }),
    ["La ruta está cuadrada."],
  );
});

test("shows product and cash differences and requires an observation", () => {
  assert.deepEqual(
    getRouteSettlementMessages({
      route_return_id: 2,
      delivered_cash_amount: "85.00",
      physical_vs_registered_difference: "5.000",
      cash_difference: "-5.00",
      status: "with_difference",
      items: [{ physical_vs_registered_difference: "5.000" }],
    }),
    [
      "La ruta tiene diferencia de producto.",
      "La ruta tiene diferencia de dinero.",
    ],
  );
  assert.equal(requiresDifferenceObservation(["5.000"], 0), true);
  assert.equal(requiresDifferenceObservation(["0.000"], -500), true);
  assert.equal(requiresDifferenceObservation(["0.000"], 0), false);
  assert.equal(
    requiresDifferenceObservation(["5.000", "-5.000"], 0),
    true,
  );
});

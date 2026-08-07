import assert from "node:assert/strict";
import test from "node:test";

import {
  calculateSimpleRouteSalePreview,
  simpleRouteIndependenceNotices,
  simpleRouteSettlementTone,
} from "./simpleRoute.ts";

test("calculates cash, credit and partial simple route sales", () => {
  assert.deepEqual(calculateSimpleRouteSalePreview("2", "10", "cash", ""), {
    total: 20,
    paid: 20,
    pending: 0,
    isValid: true,
  });
  assert.deepEqual(calculateSimpleRouteSalePreview("2", "10", "credit", ""), {
    total: 20,
    paid: 0,
    pending: 20,
    isValid: true,
  });
  assert.deepEqual(calculateSimpleRouteSalePreview("2", "10", "partial", "7.5"), {
    total: 20,
    paid: 7.5,
    pending: 12.5,
    isValid: true,
  });
});

test("rejects a partial payment equal to the total", () => {
  assert.equal(
    calculateSimpleRouteSalePreview("2", "10", "partial", "20").isValid,
    false,
  );
});

test("maps pending, balanced, difference and cancelled tones", () => {
  assert.equal(simpleRouteSettlementTone("pending"), "neutral");
  assert.equal(simpleRouteSettlementTone("balanced"), "success");
  assert.equal(simpleRouteSettlementTone("with_difference"), "warning");
  assert.equal(simpleRouteSettlementTone("cancelled"), "danger");
});

test("keeps the four independence promises visible", () => {
  assert.deepEqual(simpleRouteIndependenceNotices(), [
    "No crea ventas oficiales.",
    "No crea cartera formal.",
    "No modifica inventario.",
    "Caja recibe una referencia única del efectivo liquidado.",
  ]);
});

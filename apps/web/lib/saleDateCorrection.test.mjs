import assert from "node:assert/strict";
import test from "node:test";

import {
  canShowSaleDateCorrectionAction,
  getSaleDateCorrectionErrorMessage,
  SALE_DATE_CORRECTION_PERMISSION_MESSAGE,
  validateSaleDateCorrectionForm,
} from "./saleDateCorrection.ts";

test("shows the correction action only to admin on active sales", () => {
  assert.equal(canShowSaleDateCorrectionAction(true, "active"), true);
  assert.equal(canShowSaleDateCorrectionAction(false, "active"), false);
  assert.equal(canShowSaleDateCorrectionAction(true, "voided"), false);
});

test("requires a different valid date and a non-blank reason", () => {
  assert.equal(
    validateSaleDateCorrectionForm("2026-07-28", "", "Error de digitación"),
    "La nueva fecha de venta es obligatoria y debe ser válida.",
  );
  assert.equal(
    validateSaleDateCorrectionForm(
      "2026-07-28",
      "2026-02-30",
      "Error de digitación",
    ),
    "La nueva fecha de venta es obligatoria y debe ser válida.",
  );
  assert.equal(
    validateSaleDateCorrectionForm(
      "2026-07-28",
      "2026-07-28",
      "Error de digitación",
    ),
    "La nueva fecha debe ser diferente de la fecha actual.",
  );
  assert.equal(
    validateSaleDateCorrectionForm("2026-07-28", "2026-07-27", "   "),
    "El motivo de corrección es obligatorio.",
  );
  assert.equal(
    validateSaleDateCorrectionForm(
      "2026-07-28",
      "2026-07-27",
      "Error de digitación",
    ),
    null,
  );
});

test("translates a direct 403 into the operator guidance", () => {
  const error = Object.assign(new Error("Forbidden"), { status: 403 });
  assert.equal(
    getSaleDateCorrectionErrorMessage(error),
    SALE_DATE_CORRECTION_PERMISSION_MESSAGE,
  );
});

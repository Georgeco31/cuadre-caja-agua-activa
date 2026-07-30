import assert from "node:assert/strict";
import test from "node:test";

import {
  buildCustomerCreditExportPath,
  buildCustomerSalesSummaryPath,
  getCustomerSalesSummaryMetrics,
  validateDateRange,
} from "./customerSalesReporting.ts";

test("customer summary metrics expose cash, credit, total and pending balance", () => {
  assert.deepEqual(
    getCustomerSalesSummaryMetrics({
      cash_sales_total: "100.00",
      credit_sales_total: "60.00",
      total_sales_amount: "160.00",
      pending_credit_amount: "40.00",
    }),
    [
      { label: "Ventas contado", value: "100.00" },
      { label: "Ventas crédito", value: "60.00" },
      { label: "Total vendido", value: "160.00" },
      { label: "Saldo pendiente", value: "40.00" },
    ],
  );
});

test("customer summary request includes the selected date range", () => {
  assert.equal(
    buildCustomerSalesSummaryPath(7, {
      start_date: "2026-07-01",
      end_date: "2026-07-31",
    }),
    "/customers/7/sales-summary?start_date=2026-07-01&end_date=2026-07-31",
  );
});

test("customer credit export requires a customer and calls the dedicated endpoint", () => {
  assert.throws(
    () => buildCustomerCreditExportPath(0),
    /Selecciona un cliente/,
  );
  assert.equal(
    buildCustomerCreditExportPath(7, {
      start_date: "2026-07-01",
      end_date: "2026-07-31",
    }),
    "/reports/exports/customer-credit-sales.xlsx?customer_id=7&start_date=2026-07-01&end_date=2026-07-31",
  );
});

test("date range validation blocks inverted periods", () => {
  assert.equal(
    validateDateRange({
      start_date: "2026-07-31",
      end_date: "2026-07-01",
    }),
    "La fecha hasta no puede ser menor que la fecha desde.",
  );
});

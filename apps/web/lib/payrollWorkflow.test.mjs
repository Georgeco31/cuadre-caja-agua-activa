import assert from "node:assert/strict";
import test from "node:test";

import {
  getPayrollRunActions,
  PAYROLL_PERMISSION_MESSAGE,
} from "./payrollWorkflow.ts";
import { canAccessDashboardPath } from "./frontendPermissions.ts";

test("draft payroll is editable and can be approved only with employees", () => {
  assert.deepEqual(getPayrollRunActions("draft", 0), {
    canAddEmployee: true,
    canEditItems: true,
    canApprove: false,
    canMarkPaid: false,
    canCancel: true,
  });
  assert.equal(getPayrollRunActions("draft", 1).canApprove, true);
});

test("approved payroll is locked but can be paid or cancelled", () => {
  assert.deepEqual(getPayrollRunActions("approved", 1), {
    canAddEmployee: false,
    canEditItems: false,
    canApprove: false,
    canMarkPaid: true,
    canCancel: true,
  });
});

test("paid and cancelled payroll cannot be changed", () => {
  assert.deepEqual(getPayrollRunActions("paid", 1), {
    canAddEmployee: false,
    canEditItems: false,
    canApprove: false,
    canMarkPaid: false,
    canCancel: false,
  });
  assert.deepEqual(getPayrollRunActions("cancelled", 1), {
    canAddEmployee: false,
    canEditItems: false,
    canApprove: false,
    canMarkPaid: false,
    canCancel: false,
  });
});

test("operator cannot see payroll or enter its direct URL", () => {
  assert.equal(
    canAccessDashboardPath("operator", "/dashboard/payroll"),
    false,
  );
  assert.equal(
    canAccessDashboardPath("operator", "/dashboard/payroll/123"),
    false,
  );
  assert.equal(
    canAccessDashboardPath("admin_auditor", "/dashboard/payroll"),
    true,
  );
  assert.equal(
    PAYROLL_PERMISSION_MESSAGE,
    "No tienes permiso para gestionar roles de pago.",
  );
});

export type PayrollWorkflowStatus =
  | "draft"
  | "approved"
  | "paid"
  | "cancelled";

export type PayrollRunActions = {
  canAddEmployee: boolean;
  canEditItems: boolean;
  canApprove: boolean;
  canMarkPaid: boolean;
  canCancel: boolean;
};

export const PAYROLL_PERMISSION_MESSAGE =
  "No tienes permiso para gestionar roles de pago.";

export function getPayrollRunActions(
  status: PayrollWorkflowStatus,
  itemsCount: number,
): PayrollRunActions {
  return {
    canAddEmployee: status === "draft",
    canEditItems: status === "draft",
    canApprove: status === "draft" && itemsCount > 0,
    canMarkPaid: status === "approved",
    canCancel: status === "draft" || status === "approved",
  };
}

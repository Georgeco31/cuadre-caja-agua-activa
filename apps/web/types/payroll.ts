export type PayrollStatus = "draft" | "approved" | "paid" | "cancelled";

export const PAYROLL_STATUS_LABELS: Record<PayrollStatus, string> = {
  draft: "Borrador",
  approved: "Aprobado",
  paid: "Pagado",
  cancelled: "Cancelado",
};

export type PayrollLoanDeductionPayload = {
  employee_loan_id: number;
  amount_deducted: string;
};

export type PayrollItemValuesPayload = {
  base_salary_amount?: string | null;
  bonus_amount: string;
  other_income_amount: string;
  other_deductions_amount: string;
  advance_ids: number[];
  loan_deductions: PayrollLoanDeductionPayload[];
  notes?: string | null;
};

export type PayrollItemPayload = PayrollItemValuesPayload & {
  employee_id: number;
};

export type PayrollItemUpdatePayload = PayrollItemValuesPayload & {
  correction_reason: string;
};

export type PayrollPreviewPayload = {
  period_start: string;
  period_end: string;
  employee_ids?: number[];
  items: PayrollItemPayload[];
};

export type PayrollRunPayload = {
  period_start: string;
  period_end: string;
  payroll_date?: string | null;
  label: string;
  notes?: string | null;
  employee_ids?: number[];
  items?: PayrollItemPayload[];
};

export type PayrollAdvanceDeduction = {
  id?: number;
  payroll_item_id?: number;
  employee_advance_id: number;
  amount_deducted: string;
  advance_number_snapshot: string;
  advance_date_snapshot: string;
  reason_snapshot: string;
  applied_at?: string | null;
  created_at?: string;
};

export type PayrollLoanDeduction = {
  id?: number;
  payroll_item_id?: number;
  employee_loan_id: number;
  amount_deducted: string;
  loan_number_snapshot: string;
  loan_date_snapshot: string;
  loan_balance_snapshot: string;
  reason_snapshot: string;
  loan_payment_id?: number | null;
  applied_at?: string | null;
  created_at?: string;
};

export type PayrollCalculatedItem = {
  id?: number;
  payroll_run_id?: number;
  employee_id: number;
  employee_name_snapshot: string;
  employee_identification_snapshot: string | null;
  job_position_snapshot: string | null;
  payment_frequency_snapshot: string;
  base_salary_snapshot: string;
  attendance_days: number;
  absent_days: number;
  permission_days: number;
  vacation_days: number;
  sick_days: number;
  late_days: number;
  hours_worked: string;
  base_salary_amount: string;
  bonus_amount: string;
  other_income_amount: string;
  gross_amount: string;
  advances_deducted_amount: string;
  loan_deductions_amount: string;
  other_deductions_amount: string;
  total_deductions_amount: string;
  net_pay_amount: string;
  notes: string | null;
  created_at?: string;
  updated_at?: string;
  advance_deductions: PayrollAdvanceDeduction[];
  loan_deductions: PayrollLoanDeduction[];
};

export type PayrollPreview = {
  period_start: string;
  period_end: string;
  employees_count: number;
  gross_total: string;
  bonuses_total: string;
  advances_deducted_total: string;
  loan_deductions_total: string;
  other_deductions_total: string;
  total_deductions: string;
  net_pay_total: string;
  items: PayrollCalculatedItem[];
};

export type PayrollAuditLog = {
  id: number;
  payroll_run_id: number;
  action: string;
  actor_id: number;
  reason: string | null;
  details: string | null;
  created_at: string;
};

export type PayrollRunSummary = {
  id: number;
  payroll_number: string;
  label: string;
  period_start: string;
  period_end: string;
  payroll_date: string;
  status: PayrollStatus;
  employees_count: number;
  gross_total: string;
  bonuses_total: string;
  advances_deducted_total: string;
  loan_deductions_total: string;
  other_deductions_total: string;
  total_deductions: string;
  net_pay_total: string;
  notes: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  approved_by: number | null;
  approved_at: string | null;
  paid_by: number | null;
  paid_at: string | null;
  cancelled_by: number | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
};

export type PayrollRun = PayrollRunSummary & {
  items: PayrollCalculatedItem[];
  audit_logs: PayrollAuditLog[];
};

export type PayrollRunFilters = {
  date_from?: string;
  date_to?: string;
  status?: PayrollStatus | "";
  employee_id?: number;
  search?: string;
};

export type EmployeePayrollAdvanceSummary = {
  id: number;
  advance_number: string;
  advance_date: string;
  amount: string;
  reserved_amount: string;
  estimated_balance: string;
  available_for_payroll: boolean;
};

export type EmployeePayrollLoanSummary = {
  id: number;
  loan_number: string;
  loan_date: string;
  principal_amount: string;
  paid_amount: string;
  balance_amount: string;
  reserved_amount: string;
  estimated_balance: string;
  available_for_payroll: boolean;
};

export type EmployeePayrollSummary = {
  employee_id: number;
  employee_name: string;
  base_salary: string;
  active_advances_total: string;
  active_loans_balance_total: string;
  reserved_advances_total: string;
  reserved_loans_total: string;
  estimated_pending_balance_after_reserved: string;
  advances: EmployeePayrollAdvanceSummary[];
  loans: EmployeePayrollLoanSummary[];
  paid_payroll_runs_count: number;
  gross_paid_total: string;
  advances_deducted_total: string;
  loan_deductions_total: string;
  other_deductions_total: string;
  net_paid_total: string;
  latest_paid_payroll_items: PayrollCalculatedItem[];
};

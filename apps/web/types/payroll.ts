export type PayrollStatus = "active" | "voided";

export const PAYROLL_STATUS_LABELS: Record<PayrollStatus, string> = {
  active: "Activo",
  voided: "Anulado",
};

export type PayrollLoanDeductionPayload = {
  employee_loan_id: number;
  amount_deducted: string;
};

export type PayrollItemPayload = {
  employee_id: number;
  bonus_amount: string;
  other_income_amount: string;
  other_deductions_amount: string;
  advance_ids: number[];
  loan_deductions: PayrollLoanDeductionPayload[];
  notes?: string | null;
};

export type PayrollPreviewPayload = {
  period_start: string;
  period_end: string;
  employee_ids?: number[];
  items: PayrollItemPayload[];
};

export type PayrollRunPayload = PayrollPreviewPayload & {
  payroll_date: string;
  notes?: string | null;
};

export type PayrollAdvanceDeduction = {
  id?: number;
  payroll_item_id?: number;
  employee_advance_id: number;
  amount_deducted: string;
  advance_number_snapshot: string;
  advance_date_snapshot: string;
  reason_snapshot: string;
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

export type PayrollRunSummary = {
  id: number;
  payroll_number: string;
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
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type PayrollRun = PayrollRunSummary & {
  items: PayrollCalculatedItem[];
};

export type PayrollRunFilters = {
  date_from?: string;
  date_to?: string;
  status?: PayrollStatus | "";
  employee_id?: number;
  search?: string;
};

export type EmployeePayrollSummary = {
  employee_id: number;
  employee_name: string;
  payroll_runs_count: number;
  gross_total: string;
  advances_deducted_total: string;
  loan_deductions_total: string;
  other_deductions_total: string;
  net_pay_total: string;
  latest_payroll_items: PayrollCalculatedItem[];
};

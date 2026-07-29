export type AttendanceStatus =
  | "present"
  | "absent"
  | "late"
  | "permission"
  | "vacation"
  | "sick";

export type EmployeeAdvanceStatus = "active" | "deducted" | "voided";
export type EmployeeLoanStatus = "active" | "paid" | "voided";
export type EmployeeLoanPaymentStatus = "active" | "voided";

export const ATTENDANCE_STATUS_LABELS: Record<AttendanceStatus, string> = {
  present: "Presente",
  absent: "Ausente",
  late: "Atraso",
  permission: "Permiso",
  vacation: "Vacaciones",
  sick: "Enfermedad",
};

export const EMPLOYEE_CONTROL_STATUS_LABELS: Record<
  EmployeeAdvanceStatus | EmployeeLoanStatus | EmployeeLoanPaymentStatus,
  string
> = {
  active: "Activo",
  deducted: "Descontado",
  paid: "Pagado",
  voided: "Anulado",
};

export type EmployeeAttendance = {
  id: number;
  employee_id: number;
  employee_name: string;
  attendance_date: string;
  status: AttendanceStatus;
  check_in_time: string | null;
  check_out_time: string | null;
  hours_worked: string | null;
  notes: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type EmployeeAttendancePayload = {
  employee_id: number;
  attendance_date: string;
  status: AttendanceStatus;
  check_in_time?: string | null;
  check_out_time?: string | null;
  hours_worked?: string | null;
  notes?: string | null;
};

export type EmployeeAttendanceUpdatePayload = Partial<
  Omit<EmployeeAttendancePayload, "employee_id">
>;

export type EmployeeAdvance = {
  id: number;
  advance_number: string;
  employee_id: number;
  employee_name: string;
  advance_date: string;
  amount: string;
  reason: string;
  status: EmployeeAdvanceStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  deducted_at: string | null;
  deducted_by: number | null;
  deducted_payroll_run_id: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type EmployeeAdvancePayload = {
  employee_id: number;
  advance_date: string;
  amount: string;
  reason: string;
  notes?: string | null;
};

export type EmployeeLoan = {
  id: number;
  loan_number: string;
  employee_id: number;
  employee_name: string;
  loan_date: string;
  principal_amount: string;
  paid_amount: string;
  balance_amount: string;
  status: EmployeeLoanStatus;
  reason: string;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type EmployeeLoanPayload = {
  employee_id: number;
  loan_date: string;
  principal_amount: string;
  reason: string;
  notes?: string | null;
};

export type EmployeeLoanPayment = {
  id: number;
  payment_number: string;
  employee_loan_id: number;
  loan_number: string;
  employee_id: number;
  employee_name: string;
  payroll_run_id: number | null;
  payment_date: string;
  amount: string;
  notes: string | null;
  status: EmployeeLoanPaymentStatus;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type EmployeeLoanPaymentPayload = {
  payment_date: string;
  amount: string;
  notes?: string | null;
};

export type EmployeeControlFilters = {
  date_from?: string;
  date_to?: string;
  employee_id?: number;
  status?: string;
};

export type EmployeeLoanPaymentFilters = EmployeeControlFilters & {
  loan_id?: number;
};

export type EmployeeAccountSummary = {
  employee_id: number;
  employee_name: string;
  advances_total_active: string;
  loans_principal_total: string;
  loans_paid_total: string;
  loans_balance_total: string;
  active_loans_count: number;
  paid_loans_count: number;
  attendance_count_period: number;
  latest_advances: EmployeeAdvance[];
  latest_loans: EmployeeLoan[];
  latest_loan_payments: EmployeeLoanPayment[];
};

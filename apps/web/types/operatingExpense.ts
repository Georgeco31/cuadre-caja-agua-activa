import type { Supplier } from "@/types/supplier";

export type OperatingExpenseStatus = "active" | "voided";
export type OperatingExpensePaymentStatus = "unpaid" | "paid" | "partial";
export type OperatingExpensePaymentMethod =
  | "cash"
  | "transfer"
  | "card"
  | "check"
  | "other"
  | "unknown";
export type RecurringOperatingExpenseFrequency =
  | "weekly"
  | "monthly"
  | "quarterly"
  | "yearly";

export const OPERATING_EXPENSE_STATUS_LABELS: Record<
  OperatingExpenseStatus,
  string
> = {
  active: "Activo",
  voided: "Anulado",
};

export const OPERATING_EXPENSE_PAYMENT_STATUS_LABELS: Record<
  OperatingExpensePaymentStatus,
  string
> = {
  unpaid: "Pendiente",
  paid: "Pagado",
  partial: "Parcial",
};

export const OPERATING_EXPENSE_PAYMENT_METHOD_LABELS: Record<
  OperatingExpensePaymentMethod,
  string
> = {
  cash: "Efectivo",
  transfer: "Transferencia",
  card: "Tarjeta",
  check: "Cheque",
  other: "Otro",
  unknown: "No informado",
};

export const RECURRING_OPERATING_EXPENSE_FREQUENCY_LABELS: Record<
  RecurringOperatingExpenseFrequency,
  string
> = {
  weekly: "Semanal",
  monthly: "Mensual",
  quarterly: "Trimestral",
  yearly: "Anual",
};

export type OperatingExpenseCategory = {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type OperatingExpenseCategoryPayload = {
  name: string;
  description?: string | null;
};

export type OperatingExpenseCategoryUpdatePayload =
  Partial<OperatingExpenseCategoryPayload>;

export type OperatingExpenseCategoryFilters = {
  search?: string;
  is_active?: boolean | "";
};

export type OperatingExpense = {
  id: number;
  expense_number: string;
  expense_date: string;
  category_id: number;
  supplier_id: number | null;
  description: string;
  amount: string;
  payment_status: OperatingExpensePaymentStatus;
  payment_method: OperatingExpensePaymentMethod;
  document_number: string | null;
  due_date: string | null;
  paid_date: string | null;
  recurring_template_id: number | null;
  status: OperatingExpenseStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  category: OperatingExpenseCategory;
  supplier: Supplier | null;
};

export type OperatingExpensePayload = {
  expense_date: string;
  category_id: number;
  supplier_id?: number | null;
  description: string;
  amount: string;
  payment_status: OperatingExpensePaymentStatus;
  payment_method: OperatingExpensePaymentMethod;
  document_number?: string | null;
  due_date?: string | null;
  paid_date?: string | null;
  notes?: string | null;
};

export type OperatingExpenseUpdatePayload = Partial<OperatingExpensePayload>;

export type OperatingExpenseFilters = {
  date_from?: string;
  date_to?: string;
  status?: OperatingExpenseStatus | "";
  payment_status?: OperatingExpensePaymentStatus | "";
  category_id?: number;
  supplier_id?: number;
  payment_method?: OperatingExpensePaymentMethod | "";
  search?: string;
};

export type RecurringOperatingExpense = {
  id: number;
  name: string;
  category_id: number;
  supplier_id: number | null;
  description: string;
  amount: string;
  frequency: RecurringOperatingExpenseFrequency;
  start_date: string;
  end_date: string | null;
  next_due_date: string | null;
  payment_method: OperatingExpensePaymentMethod;
  is_active: boolean;
  notes: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  category: OperatingExpenseCategory;
  supplier: Supplier | null;
};

export type RecurringOperatingExpensePayload = {
  name: string;
  category_id: number;
  supplier_id?: number | null;
  description: string;
  amount: string;
  frequency: RecurringOperatingExpenseFrequency;
  start_date: string;
  end_date?: string | null;
  next_due_date?: string | null;
  payment_method: OperatingExpensePaymentMethod;
  notes?: string | null;
};

export type RecurringOperatingExpenseUpdatePayload =
  Partial<RecurringOperatingExpensePayload>;

export type RecurringOperatingExpenseFilters = {
  search?: string;
  is_active?: boolean | "";
  category_id?: number;
  supplier_id?: number;
  frequency?: RecurringOperatingExpenseFrequency | "";
};

export type RecurringOperatingExpenseCreateExpensePayload = {
  expense_date: string;
  due_date?: string | null;
  paid_date?: string | null;
  payment_status: OperatingExpensePaymentStatus;
  notes?: string | null;
};

export type OperatingExpenseSummaryCategory = {
  category_id: number;
  category_name: string;
  total_amount: string;
  expenses_count: number;
};

export type OperatingExpenseSummarySupplier = {
  supplier_id: number | null;
  supplier_name: string;
  total_amount: string;
  expenses_count: number;
};

export type OperatingExpenseSummaryPaymentStatus = {
  payment_status: OperatingExpensePaymentStatus;
  total_amount: string;
  expenses_count: number;
};

export type OperatingExpenseSummary = {
  total_expenses_amount: string;
  paid_amount: string;
  unpaid_amount: string;
  partial_amount: string;
  expenses_count: number;
  voided_count: number;
  by_category: OperatingExpenseSummaryCategory[];
  by_supplier: OperatingExpenseSummarySupplier[];
  by_payment_status: OperatingExpenseSummaryPaymentStatus[];
};

export type OperatingExpenseSummaryFilters = {
  date_from?: string;
  date_to?: string;
  category_id?: number;
  supplier_id?: number;
};

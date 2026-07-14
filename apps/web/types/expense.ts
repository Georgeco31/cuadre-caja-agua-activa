export type ExpenseTiming = "before_count" | "after_count";

export type Expense = {
  id: number;
  cash_session_id: number;
  description: string;
  amount: string;
  category: string | null;
  expense_timing: ExpenseTiming;
  expense_date: string;
  notes: string | null;
  created_at: string;
};

export type ExpensePayload = {
  description: string;
  amount: string;
  expense_timing?: ExpenseTiming;
  category?: string;
  expense_date?: string;
  notes?: string;
};

export type Expense = {
  id: number;
  cash_session_id: number;
  description: string;
  amount: string;
  category: string | null;
  expense_date: string;
  notes: string | null;
  created_at: string;
};

export type ExpensePayload = {
  description: string;
  amount: string;
  category?: string;
  expense_date?: string;
  notes?: string;
};

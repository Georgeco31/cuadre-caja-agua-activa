import type { CashCountItem } from "@/types/cashSession";
import type { Expense } from "@/types/expense";
import type { CashSessionSummary } from "@/types/summary";

export type CorrectionLog = {
  id: number;
  cash_session_id: number;
  reason: string;
  previous_total: string;
  new_total: string;
  created_by: number | null;
  created_at: string;
};

export type CorrectionCountItemPayload = {
  denomination_id: number;
  quantity: number;
  reason: string;
};

export type CorrectionExpensePayload = {
  description: string;
  amount: string;
  category?: string;
  expense_date?: string;
  notes?: string;
  reason: string;
};

export type CorrectionCountItemResponse = {
  count_item: CashCountItem;
  summary: CashSessionSummary;
  correction_log: CorrectionLog;
};

export type CorrectionExpenseResponse = {
  expense: Expense;
  summary: CashSessionSummary;
  correction_log: CorrectionLog;
};

import type { CashSessionStatus } from "@/types/cashSession";

export type CashSessionSummary = {
  cash_session_id: number;
  session_date: string;
  status: CashSessionStatus;
  total_coins: string;
  total_bills: string;
  total_counted: string;
  total_expenses: string;
  final_total: string;
};

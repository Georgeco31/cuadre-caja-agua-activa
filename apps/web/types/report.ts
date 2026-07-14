export type CashSummaryReportStatus = "open" | "closed" | "corrected";

export type CashSummaryReportFilters = {
  date_from?: string;
  date_to?: string;
  status?: CashSummaryReportStatus | "";
};

export type CashSummaryReport = {
  date_from: string | null;
  date_to: string | null;
  status: string | null;
  total_sessions: number;
  open_sessions: number;
  closed_sessions: number;
  total_counted: string;
  total_pre_count_expenses: string;
  total_post_count_expenses: string;
  total_expenses: string;
  final_total: string;
};

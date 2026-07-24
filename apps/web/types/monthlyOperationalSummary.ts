export type MonthlyOperationalPeriod = {
  year: number;
  month: number;
  date_from: string;
  date_to: string;
  days_in_month: number;
};

export type MonthlyCashSummary = {
  cash_sessions_count: number;
  open_cash_sessions_count: number;
  closed_cash_sessions_count: number;
  total_coins: string;
  total_bills: string;
  total_counted: string;
  total_expenses: string;
  total_final: string;
  average_daily_counted: string;
  days_with_cash_session: number;
  days_without_cash_session: number;
};

export type MonthlyProductionProduct = {
  product_id: number;
  product_name_snapshot: string;
  quantity_produced: string;
  quantity_waste: string;
  quantity_net: string;
};

export type MonthlyProductionSummary = {
  production_batches_count: number;
  active_production_batches_count: number;
  voided_production_batches_count: number;
  total_quantity_produced: string;
  total_quantity_waste: string;
  total_quantity_net: string;
  products: MonthlyProductionProduct[];
};

export type MonthlyProductSold = {
  product_id: number;
  product_name_snapshot: string;
  quantity: string;
  amount: string;
};

export type MonthlySalesSummary = {
  cash_sales_total: string;
  credit_sales_total: string;
  total_sales_amount: string;
  cash_sales_count: number;
  credit_sales_count: number;
  voided_sales_count: number;
  products_sold: MonthlyProductSold[];
};

export type MonthlyReceivablesSummary = {
  payments_total: string;
  payments_count: number;
  voided_payments_count: number;
  credit_sales_created_total: string;
  pending_credit_total: string;
  customers_with_credit_sales_count: number;
};

export type MonthlyRouteOperationsSummary = {
  route_loads_count: number;
  active_route_loads_count: number;
  voided_route_loads_count: number;
  route_returns_count: number;
  active_route_returns_count: number;
  voided_route_returns_count: number;
  total_quantity_loaded: string;
  total_quantity_returned: string;
};

export type MonthlyRouteFinancialSummary = {
  route_closures_count: number;
  active_route_closures_count: number;
  voided_route_closures_count: number;
  expected_cash_total: string;
  delivered_cash_total: string;
  difference_total: string;
  closures_with_shortage_count: number;
  closures_with_surplus_count: number;
  closures_balanced_count: number;
};

export type MonthlyRouteCashReceiptsSummary = {
  receipts_count: number;
  active_receipts_count: number;
  voided_receipts_count: number;
  delivered_cash_total: string;
  received_amount_total: string;
  difference_total: string;
};

export type MonthlyOperationalDailyRow = {
  date: string;
  cash_session_exists: boolean;
  cash_total_counted: string;
  cash_total_expenses: string;
  cash_total_final: string;
  production_quantity_net: string;
  cash_sales_total: string;
  credit_sales_total: string;
  payments_total: string;
  route_delivered_cash_total: string;
  route_cash_registered_total: string;
  alerts_count: number;
  alert_codes: string[];
};

export type MonthlyOperationalAlertByCode = {
  code: string;
  count: number;
  message: string;
};

export type MonthlyOperationalAlertsSummary = {
  total_alerts: number;
  days_with_alerts_count: number;
  alerts_by_code: MonthlyOperationalAlertByCode[];
};

export type MonthlyOperationalSummary = {
  period: MonthlyOperationalPeriod;
  cash_summary: MonthlyCashSummary;
  production_summary: MonthlyProductionSummary;
  sales_summary: MonthlySalesSummary;
  receivables_summary: MonthlyReceivablesSummary;
  route_operations_summary: MonthlyRouteOperationsSummary;
  route_financial_summary: MonthlyRouteFinancialSummary;
  route_cash_receipts_summary: MonthlyRouteCashReceiptsSummary;
  daily_rows: MonthlyOperationalDailyRow[];
  alerts_summary: MonthlyOperationalAlertsSummary;
  totals: {
    total_business_cash_inflow_reference: string;
  };
};

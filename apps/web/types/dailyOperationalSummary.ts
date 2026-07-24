export type DailyOperationalAlert = {
  type: "warning" | "info" | "success";
  code: string;
  message: string;
};

export type DailyCashSummary = {
  cash_session_exists: boolean;
  cash_session_id: number | null;
  cash_session_status: string | null;
  total_coins: string;
  total_bills: string;
  total_counted: string;
  total_expenses: string;
  total_final: string;
  pre_count_expenses_total: string;
  post_count_expenses_total: string;
  expenses_count: number;
  route_cash_receipts_total: string;
  route_cash_receipts_count: number;
};

export type DailyProductionProduct = {
  product_id: number;
  product_name_snapshot: string;
  quantity_produced: string;
  quantity_waste: string;
  quantity_net: string;
};

export type DailyProductionSummary = {
  production_batches_count: number;
  active_production_batches_count: number;
  voided_production_batches_count: number;
  total_quantity_produced: string;
  total_quantity_waste: string;
  total_quantity_net: string;
  products: DailyProductionProduct[];
};

export type DailyRouteLoad = {
  id: number;
  load_number: string;
  route_name: string;
  vehicle_name: string;
  status: string;
  total_quantity_loaded: string;
};

export type DailyRouteLoadsSummary = {
  route_loads_count: number;
  active_route_loads_count: number;
  voided_route_loads_count: number;
  total_items_loaded: number;
  total_quantity_loaded: string;
  loads: DailyRouteLoad[];
};

export type DailyRouteReturn = {
  id: number;
  return_number: string;
  route_name: string;
  vehicle_name: string;
  status: string;
  total_quantity_returned: string;
};

export type DailyRouteReturnsSummary = {
  route_returns_count: number;
  active_route_returns_count: number;
  voided_route_returns_count: number;
  total_quantity_returned: string;
  returns: DailyRouteReturn[];
};

export type DailyRouteClosure = {
  id: number;
  closure_number: string;
  route_name_snapshot: string;
  vehicle_name_snapshot: string;
  expected_cash_total: string;
  delivered_cash_total: string;
  difference_amount: string;
  status: string;
};

export type DailyRouteClosuresSummary = {
  route_closures_count: number;
  active_route_closures_count: number;
  voided_route_closures_count: number;
  expected_cash_total: string;
  delivered_cash_total: string;
  difference_total: string;
  closures_with_shortage_count: number;
  closures_with_surplus_count: number;
  closures_balanced_count: number;
  closures: DailyRouteClosure[];
};

export type DailyRouteCashReceipt = {
  id: number;
  receipt_number: string;
  closure_number_snapshot: string;
  route_name_snapshot: string;
  vehicle_name_snapshot: string;
  delivered_cash_total: string;
  received_amount: string;
  difference_amount: string;
  status: string;
};

export type DailyRouteCashReceiptsSummary = {
  receipts_count: number;
  active_receipts_count: number;
  voided_receipts_count: number;
  delivered_cash_total: string;
  received_amount_total: string;
  difference_total: string;
  receipts: DailyRouteCashReceipt[];
};

export type DailyProductSold = {
  product_id: number;
  product_name_snapshot: string;
  quantity: string;
  amount: string;
};

export type DailySalesSummary = {
  cash_sales_total: string;
  credit_sales_total: string;
  total_sales_amount: string;
  cash_sales_count: number;
  credit_sales_count: number;
  voided_sales_count: number;
  products_sold: DailyProductSold[];
};

export type DailyReceivablesSummary = {
  payments_total: string;
  payments_count: number;
  voided_payments_count: number;
  credit_sales_created_total: string;
  outstanding_balance_created_today: string;
  customers_with_credit_sales_count: number;
};

export type DailyOperationalTotals = {
  total_business_cash_inflow_reference: string;
  total_route_delivered_cash: string;
  total_route_cash_registered: string;
  total_cash_counted: string;
  total_cash_final: string;
};

export type DailyOperationalSummary = {
  date: string;
  cash_summary: DailyCashSummary;
  production_summary: DailyProductionSummary;
  route_loads_summary: DailyRouteLoadsSummary;
  route_returns_summary: DailyRouteReturnsSummary;
  route_closures_summary: DailyRouteClosuresSummary;
  route_cash_receipts_summary: DailyRouteCashReceiptsSummary;
  sales_summary: DailySalesSummary;
  receivables_summary: DailyReceivablesSummary;
  alerts: DailyOperationalAlert[];
  totals: DailyOperationalTotals;
};

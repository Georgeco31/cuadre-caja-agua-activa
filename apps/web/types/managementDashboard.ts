export type ManagementDashboardFilters = {
  date_from?: string;
  date_to?: string;
};

export type ManagementDashboardPeriod = {
  date_from: string;
  date_to: string;
};

export type ManagementCashSummary = {
  cash_sessions_count: number;
  cash_total_counted: string;
  cash_total_expenses_after_count: string;
  cash_final_total: string;
  open_cash_sessions_count: number;
  closed_cash_sessions_count: number;
};

export type ManagementSalesSummary = {
  cash_sales_total: string;
  credit_sales_total: string;
  sales_total: string;
  active_sales_count: number;
  voided_sales_count: number;
  average_sale_amount: string;
};

export type ManagementReceivablesSummary = {
  credit_sales_total: string;
  payments_total: string;
  pending_balance_total: string;
  customers_with_balance_count: number;
  overdue_balance_total: string;
  overdue_customers_count: number;
};

export type ManagementExpenseCategory = {
  category_id: number;
  category_name: string;
  total_amount: string;
};

export type ManagementOperatingExpensesSummary = {
  operating_expenses_total: string;
  paid_expenses_total: string;
  unpaid_expenses_total: string;
  voided_expenses_count: number;
  top_categories: ManagementExpenseCategory[];
};

export type ManagementSupplierTotal = {
  supplier_id: number;
  supplier_name: string;
  total_amount: string;
};

export type ManagementPurchasesSummary = {
  purchases_total: string;
  active_purchases_count: number;
  voided_purchases_count: number;
  unpaid_purchases_total: string;
  paid_purchases_total: string;
  top_suppliers: ManagementSupplierTotal[];
};

export type ManagementProductionSummary = {
  production_batches_count: number;
  production_items_total_quantity: string;
  production_waste_total_quantity: string;
  production_applied_to_inventory_count: number;
  material_consumptions_count: number;
  material_consumptions_total_cost: string;
};

export type ManagementLowStockItem = {
  product_id: number;
  product_sku: string | null;
  product_name: string;
  total_stock_quantity: string;
  alert_threshold: string;
};

export type ManagementInventorySummary = {
  active_locations_count: number;
  active_products_with_stock_count: number;
  total_stock_quantity: string;
  low_stock_items: ManagementLowStockItem[];
};

export type ManagementRoutesSummary = {
  route_loads_count: number;
  route_returns_count: number;
  route_closures_count: number;
  route_expected_cash_total: string;
  route_delivered_cash_total: string;
  route_difference_total: string;
  route_cash_receipts_total: string;
};

export type ManagementPayrollSummary = {
  payroll_runs_count: number;
  gross_pay_total: string;
  deductions_total: string;
  net_pay_total: string;
  voided_payroll_runs_count: number;
};

export type ManagementDailySalesPoint = {
  date: string;
  cash_sales_total: string;
  credit_sales_total: string;
  payments_total: string;
};

export type ManagementDailyCashPoint = {
  date: string;
  cash_total_counted: string;
  cash_final_total: string;
};

export type ManagementDailyExpensesPoint = {
  date: string;
  operating_expenses_total: string;
  cash_expenses_total: string;
};

export type ManagementProductionProductPoint = {
  product_id: number;
  product_name: string;
  quantity_produced: string;
};

export type ManagementCharts = {
  daily_sales: ManagementDailySalesPoint[];
  daily_cash: ManagementDailyCashPoint[];
  daily_expenses: ManagementDailyExpensesPoint[];
  production_by_product: ManagementProductionProductPoint[];
  purchases_by_supplier: ManagementSupplierTotal[];
};

export type ManagementAlert = {
  type: "info" | "warning";
  title: string;
  message: string;
  count: number;
};

export type ManagementDashboard = {
  period: ManagementDashboardPeriod;
  cash: ManagementCashSummary;
  sales: ManagementSalesSummary;
  receivables: ManagementReceivablesSummary;
  operating_expenses: ManagementOperatingExpensesSummary;
  purchases: ManagementPurchasesSummary;
  production: ManagementProductionSummary;
  inventory: ManagementInventorySummary;
  routes: ManagementRoutesSummary;
  payroll: ManagementPayrollSummary;
  charts: ManagementCharts;
  alerts: ManagementAlert[];
};

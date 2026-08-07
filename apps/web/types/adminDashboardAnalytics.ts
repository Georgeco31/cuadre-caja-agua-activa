export type AdminDashboardAnalyticsFilters = {
  start_date?: string;
  end_date?: string;
};

export type AdminBestSalesDay = {
  date: string;
  amount: string;
};

export type AdminTopCustomer = {
  customer_id: number;
  customer_name: string;
  sales_count: number;
  total_amount: string;
};

export type AdminDailySalesPoint = {
  date: string;
  cash_sales_amount: string;
  credit_sales_amount: string;
  total_sales_amount: string;
};

export type AdminSalesMixPoint = {
  sale_type: "cash" | "credit";
  amount: string;
  percentage: string;
};

export type AdminSimpleRouteDailySalesPoint = {
  date: string;
  amount: string;
};

export type AdminSimpleRouteRanking = {
  label: string;
  amount: string;
  count: number;
};

export type AdminDashboardAnalytics = {
  period_start: string;
  period_end: string;
  official_sales_amount: string;
  official_cash_sales_amount: string;
  official_credit_sales_amount: string;
  simple_route_sales_amount: string;
  total_sales_with_routes_amount: string;
  official_credit_collections_amount: string;
  official_credit_pending_amount: string;
  simple_route_cash_sales_amount: string;
  simple_route_credit_sales_amount: string;
  simple_route_partial_sales_amount: string;
  simple_route_paid_amount: string;
  simple_route_pending_amount: string;
  simple_route_collections_amount: string;
  simple_route_expenses_amount: string;
  simple_route_expected_cash_amount: string;
  simple_route_cash_delivered_amount: string;
  simple_route_cash_difference_amount: string;
  simple_route_best_day: AdminBestSalesDay | null;
  simple_route_daily_sales: AdminSimpleRouteDailySalesPoint[];
  simple_route_top_routes: AdminSimpleRouteRanking[];
  simple_route_top_sellers: AdminSimpleRouteRanking[];
  simple_route_sheets_count: number;
  simple_route_sheets_with_difference: number;

  // Alias 62A: siguen representando exclusivamente el dominio oficial.
  total_sales_amount: string;
  cash_sales_amount: string;
  credit_sales_amount: string;
  collections_amount: string;
  pending_credit_amount: string;
  expenses_amount: string;
  net_amount: string | null;
  net_amount_note: string;
  best_sales_day: AdminBestSalesDay | null;
  average_daily_sales: string;
  customers_served_count: number;
  top_customers: AdminTopCustomer[];
  daily_sales: AdminDailySalesPoint[];
  sales_mix: AdminSalesMixPoint[];
};

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

export type AdminDashboardAnalytics = {
  period_start: string;
  period_end: string;
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

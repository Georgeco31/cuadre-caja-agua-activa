export type RouteCashComparisonStatus =
  | "no_cash_session"
  | "no_route_closures"
  | "matched"
  | "cash_higher_than_routes"
  | "routes_higher_than_cash";

export type RouteCashComparisonFilters = {
  date_from?: string;
  date_to?: string;
};

export type RouteCashComparisonClosure = {
  id: number;
  closure_number: string;
  route_name_snapshot: string;
  vehicle_name_snapshot: string;
  expected_cash_total: string;
  delivered_cash_total: string;
  difference_amount: string;
};

export type RouteCashComparisonTotals = {
  route_closures_count: number;
  route_expected_cash_total: string;
  route_delivered_cash_total: string;
  route_difference_total: string;
  cash_total_counted: string;
  cash_total_expenses: string;
  cash_total_final: string;
  cash_vs_route_delivered_difference: string;
};

export type RouteCashComparisonRow = {
  date: string;
  route_closures_count: number;
  route_expected_cash_total: string;
  route_delivered_cash_total: string;
  route_difference_total: string;
  cash_session_exists: boolean;
  has_cash_session: boolean;
  has_route_closures: boolean;
  cash_session_id: number | null;
  cash_session_status: string | null;
  cash_total_coins: string;
  cash_total_bills: string;
  cash_total_counted: string;
  cash_total_expenses: string;
  cash_total_final: string;
  cash_vs_route_delivered_difference: string;
  comparison_status: RouteCashComparisonStatus;
  route_closures: RouteCashComparisonClosure[];
};

export type RouteCashComparisonReport = {
  date_from: string;
  date_to: string;
  totals: RouteCashComparisonTotals;
  rows: RouteCashComparisonRow[];
};

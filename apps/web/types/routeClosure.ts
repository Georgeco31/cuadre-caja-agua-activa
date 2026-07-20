export type RouteClosureStatus = "active" | "voided";

export const ROUTE_CLOSURE_STATUS_LABELS: Record<RouteClosureStatus, string> = {
  active: "Activo",
  voided: "Anulado",
};

export type RouteClosure = {
  id: number;
  closure_number: string;
  closure_date: string;
  route_load_id: number;
  route_load_status: "active" | "voided";
  route_id: number;
  vehicle_id: number;
  load_number_snapshot: string;
  route_name_snapshot: string;
  vehicle_name_snapshot: string;
  cash_sales_total: string;
  credit_sales_total: string;
  payments_total: string;
  expected_cash_total: string;
  delivered_cash_total: string;
  difference_amount: string;
  status: RouteClosureStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type RouteClosurePayload = {
  closure_date: string;
  route_load_id: number;
  delivered_cash_total: string;
  notes?: string | null;
};

export type RouteClosureFilters = {
  date_from?: string;
  date_to?: string;
  status?: RouteClosureStatus | "";
  route_id?: number;
  vehicle_id?: number;
  route_load_id?: number;
  search?: string;
};

export type RouteLoadFinancialClosure = {
  status: "not_closed" | "closed";
  active_closure: RouteClosure | null;
};

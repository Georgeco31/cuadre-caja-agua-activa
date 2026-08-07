export type SimpleRouteStatus =
  | "draft"
  | "in_progress"
  | "settled"
  | "cancelled";
export type SimpleRouteSettlementStatus =
  | "pending"
  | "balanced"
  | "with_difference"
  | "cancelled";
export type SimpleRouteSaleType = "cash" | "credit" | "partial";
export type SimpleRouteMovementType = "out" | "return";
export type SimpleRouteItemCategory =
  | "full_jug"
  | "empty_jug"
  | "gallon"
  | "pack"
  | "loaned_jug"
  | "returned_jug"
  | "jug_to_refill"
  | "refilled_jug"
  | "other";
export type SimpleRouteExpenseCategory =
  | "fuel"
  | "lunch"
  | "glue"
  | "cap_removal"
  | "other";

export const SIMPLE_ROUTE_STATUS_LABELS: Record<SimpleRouteStatus, string> = {
  draft: "Borrador",
  in_progress: "En progreso",
  settled: "Liquidada",
  cancelled: "Cancelada",
};

export const SIMPLE_ROUTE_SETTLEMENT_LABELS: Record<
  SimpleRouteSettlementStatus,
  string
> = {
  pending: "Pendiente",
  balanced: "Cuadrada",
  with_difference: "Con diferencia",
  cancelled: "Cancelada",
};

export const SIMPLE_ROUTE_CATEGORY_LABELS: Record<
  SimpleRouteItemCategory,
  string
> = {
  full_jug: "Bidón lleno",
  empty_jug: "Bidón vacío",
  gallon: "Galón",
  pack: "Paca",
  loaned_jug: "Bidón prestado",
  returned_jug: "Bidón devuelto",
  jug_to_refill: "Bidón para rellenar",
  refilled_jug: "Bidón relleno",
  other: "Otro",
};

export interface SimpleRouteTripItem {
  id: number;
  movement_type: SimpleRouteMovementType;
  product_id: number | null;
  item_label: string;
  item_category: SimpleRouteItemCategory;
  quantity: string;
  notes: string | null;
  created_at: string;
}

export interface SimpleRouteTrip {
  id: number;
  route_sheet_id: number;
  trip_number: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  items: SimpleRouteTripItem[];
}

export interface SimpleRouteSaleItem {
  id: number;
  product_id: number | null;
  product_name_snapshot: string;
  item_category: SimpleRouteItemCategory;
  quantity: string;
  unit_price: string;
  subtotal: string;
}

export interface SimpleRouteSale {
  id: number;
  route_sheet_id: number;
  customer_id: number | null;
  customer_name_snapshot: string | null;
  sale_type: SimpleRouteSaleType;
  sale_date: string;
  total_amount: string;
  paid_amount: string;
  pending_amount: string;
  remaining_amount: string;
  status: "active" | "voided";
  notes: string | null;
  items: SimpleRouteSaleItem[];
}

export interface SimpleRouteCollection {
  id: number;
  route_sheet_id: number;
  simple_route_sale_id: number | null;
  customer_id: number | null;
  customer_name_snapshot: string | null;
  amount: string;
  collection_date: string;
  notes: string | null;
}

export interface SimpleRouteExpense {
  id: number;
  route_sheet_id: number;
  description: string;
  amount: string;
  category: SimpleRouteExpenseCategory;
  expense_date: string;
  notes: string | null;
}

export interface SimpleRouteCashReceipt {
  id: number;
  route_sheet_id: number;
  cash_session_id: number;
  amount: string;
  received_by: number;
  received_at: string;
  notes: string | null;
  seller_name?: string | null;
  route_label?: string | null;
}

export interface SimpleRouteSheet {
  id: number;
  route_date: string;
  seller_name: string;
  employee_id: number | null;
  employee_name: string | null;
  vehicle_id: number | null;
  vehicle_name: string | null;
  route_label: string | null;
  status: SimpleRouteStatus;
  cash_delivered: string | null;
  cash_received_in_cash_session: boolean;
  cash_session_id: number | null;
  notes: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  settled_by: number | null;
  settled_at: string | null;
  cancelled_by: number | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  trips: SimpleRouteTrip[];
  sales: SimpleRouteSale[];
  collections: SimpleRouteCollection[];
  expenses: SimpleRouteExpense[];
  cash_receipt: SimpleRouteCashReceipt | null;
}

export interface SimpleRouteProductSettlement {
  product_id: number | null;
  item_label: string;
  item_category: SimpleRouteItemCategory;
  total_out: string;
  total_returned: string;
  physical_sold: string;
  registered_sold: string;
  physical_difference: string;
}

export interface SimpleRouteSettlement {
  route_sheet_id: number;
  status: SimpleRouteSettlementStatus;
  products: SimpleRouteProductSettlement[];
  route_sales_total: string;
  cash_sales_collected: string;
  partial_sales_collected: string;
  route_credit_total: string;
  collections_total: string;
  expenses_total: string;
  expected_cash: string;
  cash_delivered: string | null;
  cash_difference: string | null;
  cash_receipt_status: "pending" | "received";
  cash_session_id: number | null;
}

export interface SimpleRouteListItem {
  id: number;
  route_date: string;
  seller_name: string;
  vehicle_name: string | null;
  route_label: string | null;
  status: SimpleRouteStatus;
  route_sales_total: string;
  route_credit_total: string;
  expenses_total: string;
  expected_cash: string;
  cash_delivered: string | null;
  cash_difference: string | null;
  settlement_status: SimpleRouteSettlementStatus;
  cash_received_in_cash_session: boolean;
}

export interface SimpleRouteAnalytics {
  date_from: string;
  date_to: string;
  routes_count: number;
  total_route_sales: string;
  total_cash_sales: string;
  total_credit_sales: string;
  total_collected: string;
  total_expenses: string;
  total_expected_cash: string;
  total_delivered_cash: string;
  total_difference: string;
  top_routes: Array<{ label: string; total: string; count: number }>;
  top_sellers: Array<{ label: string; total: string; count: number }>;
  best_sales_day: { route_date: string; total: string } | null;
  daily_trend: Array<{ route_date: string; total: string }>;
  routes_with_differences: number[];
}

export interface SimpleRouteSheetPayload {
  route_date: string;
  seller_name: string;
  employee_id?: number | null;
  vehicle_id?: number | null;
  route_label?: string | null;
  notes?: string | null;
}

export interface SimpleRouteTripItemPayload {
  movement_type: SimpleRouteMovementType;
  product_id?: number | null;
  item_label?: string | null;
  item_category: SimpleRouteItemCategory;
  quantity: string;
  notes?: string | null;
}

export interface SimpleRouteSalePayload {
  customer_id?: number | null;
  customer_name?: string | null;
  sale_type: SimpleRouteSaleType;
  paid_amount?: string | null;
  notes?: string | null;
  items: Array<{
    product_id?: number | null;
    product_name?: string | null;
    item_category: SimpleRouteItemCategory;
    quantity: string;
    unit_price: string;
  }>;
}

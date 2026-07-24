export type RouteCashReceiptStatus = "active" | "voided";

export const ROUTE_CASH_RECEIPT_STATUS_LABELS: Record<
  RouteCashReceiptStatus,
  string
> = {
  active: "Activo",
  voided: "Anulado",
};

export type RouteCashReceipt = {
  id: number;
  receipt_number: string;
  receipt_date: string;
  route_closure_id: number;
  cash_session_id: number;
  route_load_id: number;
  route_id: number;
  vehicle_id: number;
  closure_number_snapshot: string;
  route_name_snapshot: string;
  vehicle_name_snapshot: string;
  delivered_cash_total: string;
  received_amount: string;
  difference_amount: string;
  status: RouteCashReceiptStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  route_closure: {
    id: number;
    closure_number: string;
    closure_date: string;
    route_load_id: number;
    route_id: number;
    vehicle_id: number;
    delivered_cash_total: string;
    status: "active" | "voided";
  };
  cash_session: {
    id: number;
    session_date: string;
    status: "open" | "closed" | "corrected";
  };
};

export type RouteCashReceiptPayload = {
  receipt_date: string;
  route_closure_id: number;
  cash_session_id: number;
  received_amount?: string;
  notes?: string | null;
};

export type RouteCashReceiptFilters = {
  date_from?: string;
  date_to?: string;
  status?: RouteCashReceiptStatus | "";
  route_id?: number;
  vehicle_id?: number;
  route_closure_id?: number;
  cash_session_id?: number;
  search?: string;
};

export type RouteClosureCashReceipt = {
  status: "not_received" | "received";
  active_receipt: RouteCashReceipt | null;
};

export type CashSessionRouteCashReceipts = {
  cash_session_id: number;
  session_date: string;
  status: "open" | "closed" | "corrected";
  receipts: RouteCashReceipt[];
  totals: {
    receipts_count: number;
    delivered_cash_total: string;
    received_amount_total: string;
    difference_total: string;
  };
};

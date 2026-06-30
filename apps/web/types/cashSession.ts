export type CashSessionStatus = "open" | "closed";

export type CashSession = {
  id: number;
  session_date: string;
  status: CashSessionStatus;
  notes: string | null;
  created_by: number | null;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
};

export type CashSessionPayload = {
  session_date: string;
  notes?: string | null;
};

export type CashSessionFilters = {
  date_from?: string;
  date_to?: string;
  status?: CashSessionStatus | "";
};

export type CashCountItemPayload = {
  denomination_id: number;
  quantity: number;
};

export type CashCountItem = {
  id: number;
  cash_session_id: number;
  denomination_id: number;
  quantity: number;
  subtotal: string;
};

export type SalePaymentMethod = "cash" | "transfer" | "card" | "other";
export type SaleStatus = "active" | "voided";

export const SALE_PAYMENT_METHOD_LABELS: Record<SalePaymentMethod, string> = {
  cash: "Efectivo",
  transfer: "Transferencia",
  card: "Tarjeta",
  other: "Otro",
};

export const SALE_STATUS_LABELS: Record<SaleStatus, string> = {
  active: "Activa",
  voided: "Anulada",
};

export type SaleItem = {
  id: number;
  sale_id: number;
  product_id: number;
  product_sku_snapshot: string | null;
  product_name_snapshot: string;
  product_presentation_snapshot: string | null;
  quantity: string;
  unit_price: string;
  subtotal: string;
  created_at: string;
};

export type CashSale = {
  id: number;
  sale_number: string;
  sale_date: string;
  customer_id: number | null;
  customer_name_snapshot: string;
  sale_type: "cash";
  payment_method: SalePaymentMethod;
  status: SaleStatus;
  total_amount: string;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: SaleItem[];
};

export type CashSaleItemPayload = {
  product_id: number;
  quantity: string;
  unit_price?: string;
};

export type CashSalePayload = {
  sale_date: string;
  customer_id?: number | null;
  payment_method: SalePaymentMethod;
  notes?: string | null;
  items: CashSaleItemPayload[];
};

export type CashSaleFilters = {
  date_from?: string;
  date_to?: string;
  status?: SaleStatus | "";
  customer_id?: number;
  payment_method?: SalePaymentMethod | "";
  search?: string;
};

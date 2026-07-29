export type SalePaymentMethod = "cash" | "transfer" | "card" | "other";
export type SaleStatus = "active" | "voided";
export type SaleType = "cash" | "credit";
export type CreditStatus = "none" | "pending" | "paid" | "voided";

import type { PriceSource } from "@/types/pricing";

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

export const CREDIT_STATUS_LABELS: Record<CreditStatus, string> = {
  none: "No aplica",
  pending: "Pendiente",
  paid: "Pagada",
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
  price_source: PriceSource | null;
  price_list_id: number | null;
  price_list_name_snapshot: string | null;
  pricing_note: string | null;
  created_at: string;
};

export type Sale = {
  id: number;
  sale_number: string;
  sale_date: string;
  customer_id: number | null;
  customer_name_snapshot: string;
  sale_type: SaleType;
  payment_method: SalePaymentMethod;
  status: SaleStatus;
  total_amount: string;
  paid_amount: string;
  balance_amount: string;
  credit_status: CreditStatus;
  due_date: string | null;
  route_load_id: number | null;
  route_load_number: string | null;
  route_name: string | null;
  route_vehicle_name: string | null;
  route_load_status: "active" | "voided" | null;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: SaleItem[];
};

export type CashSale = Sale;
export type CreditSale = Sale;

export type CashSaleItemPayload = {
  product_id: number;
  quantity: string;
  unit_price?: string;
};

export type CashSalePayload = {
  sale_date: string;
  customer_id?: number | null;
  route_load_id?: number | null;
  payment_method: SalePaymentMethod;
  notes?: string | null;
  items: CashSaleItemPayload[];
};

export type CreditSalePayload = {
  sale_date: string;
  customer_id: number;
  route_load_id?: number | null;
  due_date?: string | null;
  notes?: string | null;
  items: CashSaleItemPayload[];
};

export type SaleDateCorrectionPayload = {
  new_sale_date: string;
  reason: string;
};

export type SaleDateCorrectionResponse = {
  sale: Sale;
  correction_id: number;
  correction_type: "date_change";
  previous_sale_date: string;
  new_sale_date: string;
  reason: string;
  corrected_by: number;
  corrected_at: string;
};

export type CashSaleFilters = {
  date_from?: string;
  date_to?: string;
  status?: SaleStatus | "";
  customer_id?: number;
  payment_method?: SalePaymentMethod | "";
  sale_type?: SaleType | "";
  route_load_id?: number;
  search?: string;
};

export type CustomerCreditBalance = {
  customer_id: number;
  customer_name: string;
  total_credit_sales: string;
  total_paid: string;
  total_balance: string;
};

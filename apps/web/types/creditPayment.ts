export type CreditPaymentMethod = "cash" | "transfer" | "card" | "other";
export type CreditPaymentStatus = "active" | "voided";

export const CREDIT_PAYMENT_METHOD_LABELS: Record<
  CreditPaymentMethod,
  string
> = {
  cash: "Efectivo",
  transfer: "Transferencia",
  card: "Tarjeta",
  other: "Otro",
};

export const CREDIT_PAYMENT_STATUS_LABELS: Record<
  CreditPaymentStatus,
  string
> = {
  active: "Activo",
  voided: "Anulado",
};

export type CreditPayment = {
  id: number;
  sale_id: number;
  sale_number: string;
  customer_id: number;
  customer_name: string;
  payment_date: string;
  amount: string;
  payment_method: CreditPaymentMethod;
  status: CreditPaymentStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  sale_paid_amount: string;
  sale_balance_amount: string;
  sale_credit_status: "pending" | "paid" | "voided";
};

export type CreditPaymentPayload = {
  payment_date: string;
  amount: string;
  payment_method: CreditPaymentMethod;
  notes?: string | null;
};

export type CreditPaymentFilters = {
  date_from?: string;
  date_to?: string;
  customer_id?: number;
  sale_id?: number;
  status?: CreditPaymentStatus | "";
  payment_method?: CreditPaymentMethod | "";
};

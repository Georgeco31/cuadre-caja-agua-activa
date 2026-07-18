import type {
  CreditPaymentMethod,
  CreditPaymentStatus,
} from "@/types/creditPayment";

export type ReceivablesSummary = {
  total_customers_with_balance: number;
  total_credit_sales: string;
  total_paid: string;
  total_balance: string;
};

export type ReceivableCustomer = {
  customer_id: number;
  customer_name: string;
  primary_phone: string | null;
  sector: string | null;
  is_active: boolean;
  total_credit_sales: string;
  total_paid: string;
  total_balance: string;
  pending_sales_count: number;
};

export type ReceivableSale = {
  sale_id: number;
  sale_number: string;
  sale_date: string;
  due_date: string | null;
  total_amount: string;
  paid_amount: string;
  balance_amount: string;
  credit_status: "pending" | "paid";
  status: "active";
};

export type ReceivablePayment = {
  payment_id: number;
  sale_id: number;
  sale_number: string;
  payment_date: string;
  amount: string;
  payment_method: CreditPaymentMethod;
  status: CreditPaymentStatus;
  notes: string | null;
  void_reason: string | null;
};

export type CustomerStatement = {
  customer_id: number;
  customer_name: string;
  primary_phone: string | null;
  sector: string | null;
  is_active: boolean;
  total_credit_sales: string;
  total_paid: string;
  total_balance: string;
  credit_sales: ReceivableSale[];
  payments: ReceivablePayment[];
};

export type OverdueReceivable = {
  sale_id: number;
  sale_number: string;
  customer_id: number;
  customer_name: string;
  primary_phone: string | null;
  sector: string | null;
  sale_date: string;
  due_date: string;
  total_amount: string;
  paid_amount: string;
  balance_amount: string;
};

export type ReceivableCustomerFilters = {
  search?: string;
  only_with_balance?: boolean;
  is_active?: boolean | "";
  date_from?: string;
  date_to?: string;
};

export type CustomerStatementFilters = {
  date_from?: string;
  date_to?: string;
  include_paid?: boolean;
};

export type ReceivablesSummaryFilters = {
  date_from?: string;
  date_to?: string;
};

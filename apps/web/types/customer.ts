export type CustomerType =
  | "household"
  | "store"
  | "business"
  | "distributor"
  | "other";

export const CUSTOMER_TYPE_LABELS: Record<CustomerType, string> = {
  household: "Casa",
  store: "Tienda",
  business: "Negocio",
  distributor: "Distribuidor",
  other: "Otro",
};

export type Customer = {
  id: number;
  name: string;
  primary_phone: string | null;
  secondary_phone: string | null;
  address: string | null;
  sector: string | null;
  customer_type: CustomerType;
  route_reference: string | null;
  credit_allowed: boolean;
  credit_limit: string;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type CustomerPayload = {
  name: string;
  primary_phone?: string | null;
  secondary_phone?: string | null;
  address?: string | null;
  sector?: string | null;
  customer_type: CustomerType;
  route_reference?: string | null;
  credit_allowed: boolean;
  credit_limit: string;
  notes?: string | null;
};

export type CustomerUpdatePayload = Partial<CustomerPayload>;

export type CustomerFilters = {
  search?: string;
  is_active?: boolean | "";
  customer_type?: CustomerType | "";
  sector?: string;
};

export type CustomerSalesSummary = {
  customer_id: number;
  customer_name: string;
  period_start: string | null;
  period_end: string | null;
  cash_sales_count: number;
  cash_sales_total: string;
  credit_sales_count: number;
  credit_sales_total: string;
  total_sales_count: number;
  total_sales_amount: string;
  total_collected_amount: string;
  pending_credit_amount: string;
  last_sale_date: string | null;
  cancelled_sales_count: number;
  cancelled_sales_total: string;
};

export type CustomerSalesFilters = {
  start_date?: string;
  end_date?: string;
  sale_type?: "cash" | "credit" | "all";
  status?: "active" | "voided";
};

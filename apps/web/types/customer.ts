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

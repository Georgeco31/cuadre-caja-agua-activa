export type Supplier = {
  id: number;
  name: string;
  identification: string | null;
  primary_phone: string | null;
  secondary_phone: string | null;
  email: string | null;
  address: string | null;
  contact_name: string | null;
  supplier_type: string | null;
  payment_terms: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type SupplierPayload = {
  name: string;
  identification?: string | null;
  primary_phone?: string | null;
  secondary_phone?: string | null;
  email?: string | null;
  address?: string | null;
  contact_name?: string | null;
  supplier_type?: string | null;
  payment_terms?: string | null;
  notes?: string | null;
};

export type SupplierUpdatePayload = Partial<SupplierPayload>;

export type SupplierFilters = {
  search?: string;
  is_active?: boolean | "";
  supplier_type?: string;
};

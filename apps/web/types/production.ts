export type ProductionStatus = "active" | "voided";

export const PRODUCTION_STATUS_LABELS: Record<ProductionStatus, string> = {
  active: "Activa",
  voided: "Anulada",
};

export type ProductionItem = {
  id: number;
  production_batch_id: number;
  product_id: number;
  product_sku_snapshot: string | null;
  product_name_snapshot: string;
  product_presentation_snapshot: string | null;
  quantity_produced: string;
  quantity_waste: string;
  notes: string | null;
  created_at: string;
};

export type ProductionBatch = {
  id: number;
  production_number: string;
  production_date: string;
  status: ProductionStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: ProductionItem[];
};

export type ProductionItemPayload = {
  product_id: number;
  quantity_produced: string;
  quantity_waste: string;
  notes?: string | null;
};

export type ProductionBatchPayload = {
  production_date: string;
  notes?: string | null;
  items: ProductionItemPayload[];
};

export type ProductionBatchFilters = {
  date_from?: string;
  date_to?: string;
  status?: ProductionStatus | "";
  product_id?: number;
  search?: string;
};

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

export type ProductionInventoryState = "not_applied" | "applied" | "voided";
export type ProductionInventoryApplicationStatus = "active" | "voided";

export type ProductionInventoryApplicationItem = {
  id: number;
  application_id: number;
  production_item_id: number;
  product_id: number;
  inventory_movement_id: number;
  movement_date: string;
  quantity_applied: string;
  created_at: string;
};

export type ProductionInventoryApplication = {
  state: ProductionInventoryState;
  application_id: number | null;
  production_batch_id: number;
  location_id: number | null;
  location_name: string | null;
  status: ProductionInventoryApplicationStatus | null;
  applied_at: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number | null;
  created_at: string | null;
  updated_at: string | null;
  items: ProductionInventoryApplicationItem[];
};

export type ProductionInventoryApplyPayload = {
  location_id: number;
  movement_date: string;
  notes?: string | null;
};

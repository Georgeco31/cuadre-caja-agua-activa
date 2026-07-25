import type { ProductKind } from "@/types/product";

export type ProductionMaterialConsumptionStatus = "active" | "voided";

export const PRODUCTION_MATERIAL_CONSUMPTION_STATUS_LABELS: Record<
  ProductionMaterialConsumptionStatus,
  string
> = {
  active: "Activo",
  voided: "Anulado",
};

export type ProductionMaterialConsumptionSelection = {
  production_item_id: number;
  recipe_id: number;
};

export type ProductionMaterialConsumptionPreviewPayload = {
  source_location_id: number;
  movement_date: string;
  items: ProductionMaterialConsumptionSelection[];
};

export type ProductionMaterialConsumptionPayload =
  ProductionMaterialConsumptionPreviewPayload & {
    notes?: string | null;
  };

export type ProductionMaterialConsumptionPreviewItem = {
  production_item_id: number;
  output_product_name: string;
  recipe_id: number;
  recipe_name: string;
  input_product_id: number;
  input_product_name: string;
  quantity_consumed: string;
  available_stock: string;
  unit_cost: string;
  total_cost: string;
  has_sufficient_stock: boolean;
};

export type ProductionMaterialConsumptionPreview = {
  production_batch_id: number;
  source_location_id: number;
  total_material_cost: string;
  items: ProductionMaterialConsumptionPreviewItem[];
};

export type ProductionMaterialConsumptionItem = {
  id: number;
  consumption_id: number;
  production_item_id: number;
  recipe_id: number;
  recipe_item_id: number;
  input_product_id: number;
  input_product_sku_snapshot: string | null;
  input_product_name_snapshot: string;
  input_product_kind_snapshot: ProductKind;
  input_product_presentation_snapshot: string | null;
  recipe_number_snapshot: string;
  recipe_name_snapshot: string;
  quantity_required_base: string;
  quantity_consumed: string;
  unit_cost: string;
  total_cost: string;
  inventory_movement_id: number;
  created_at: string;
};

export type ProductionMaterialConsumption = {
  id: number;
  consumption_number: string;
  production_batch_id: number;
  production_number: string;
  source_location_id: number;
  source_location_name: string;
  movement_date: string;
  status: ProductionMaterialConsumptionStatus;
  total_material_cost: string;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: ProductionMaterialConsumptionItem[];
};

export type ProductionBatchMaterialConsumption = {
  status: "not_consumed" | "consumed";
  active_consumption: ProductionMaterialConsumption | null;
};

export type ProductionMaterialConsumptionFilters = {
  date_from?: string;
  date_to?: string;
  status?: ProductionMaterialConsumptionStatus | "";
  production_batch_id?: number;
  source_location_id?: number;
  input_product_id?: number;
  search?: string;
};

import type { ProductKind } from "@/types/product";

export type ProductionRecipeStatus = "active" | "inactive" | "voided";

export const PRODUCTION_RECIPE_STATUS_LABELS: Record<
  ProductionRecipeStatus,
  string
> = {
  active: "Activa",
  inactive: "Inactiva",
  voided: "Anulada",
};

export type ProductionRecipeItem = {
  id: number;
  recipe_id: number;
  input_product_id: number;
  input_product_sku_snapshot: string | null;
  input_product_name_snapshot: string;
  input_product_kind_snapshot: ProductKind;
  input_product_presentation_snapshot: string | null;
  quantity_required: string;
  unit_cost: string;
  total_cost: string;
  waste_percentage: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ProductionRecipe = {
  id: number;
  recipe_number: string;
  name: string;
  output_product_id: number;
  output_product_name: string;
  output_product_kind: ProductKind;
  output_quantity: string;
  status: ProductionRecipeStatus;
  valid_from: string | null;
  valid_to: string | null;
  estimated_material_cost: string;
  estimated_cost_per_unit: string;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: ProductionRecipeItem[];
};

export type ProductionRecipePayload = {
  name: string;
  output_product_id: number;
  output_quantity: string;
  valid_from?: string | null;
  valid_to?: string | null;
  notes?: string | null;
};

export type ProductionRecipeUpdatePayload = Partial<ProductionRecipePayload>;

export type ProductionRecipeItemPayload = {
  input_product_id: number;
  quantity_required: string;
  unit_cost?: string | null;
  waste_percentage?: string;
  notes?: string | null;
};

export type ProductionRecipeItemUpdatePayload =
  Partial<ProductionRecipeItemPayload>;

export type ProductionRecipeFilters = {
  search?: string;
  status?: ProductionRecipeStatus | "";
  output_product_id?: number;
  product_kind?: ProductKind | "";
  is_valid_today?: boolean;
};

export type ProductionRecipeCostItem = {
  input_product_id: number;
  input_product_name_snapshot: string;
  quantity_required_base: string;
  quantity_required_scaled: string;
  unit_cost: string;
  total_cost_scaled: string;
};

export type ProductionRecipeCostEstimate = {
  recipe_id: number;
  recipe_number: string;
  output_product_id: number;
  output_product_name: string;
  base_output_quantity: string;
  requested_output_quantity: string;
  estimated_material_cost: string;
  estimated_cost_per_unit: string;
  items: ProductionRecipeCostItem[];
};

export type ProductCategory =
  | "water"
  | "bottle"
  | "gallon"
  | "dispenser"
  | "container"
  | "other";

export type ProductUnit =
  | "unit"
  | "pack"
  | "liter"
  | "gallon"
  | "bottle"
  | "container"
  | "other";

export const PRODUCT_CATEGORY_LABELS: Record<ProductCategory, string> = {
  water: "Agua",
  bottle: "Botella",
  gallon: "Galón",
  dispenser: "Dispensador",
  container: "Envase",
  other: "Otro",
};

export const PRODUCT_UNIT_LABELS: Record<ProductUnit, string> = {
  unit: "Unidad",
  pack: "Pack",
  liter: "Litro",
  gallon: "Galón",
  bottle: "Botella",
  container: "Envase",
  other: "Otro",
};

export type Product = {
  id: number;
  sku: string | null;
  name: string;
  description: string | null;
  category: ProductCategory;
  unit: ProductUnit;
  presentation: string | null;
  default_price: string;
  cost_estimate: string;
  is_returnable_container: boolean;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ProductPayload = {
  sku?: string | null;
  name: string;
  description?: string | null;
  category: ProductCategory;
  unit: ProductUnit;
  presentation?: string | null;
  default_price: string;
  cost_estimate: string;
  is_returnable_container: boolean;
  notes?: string | null;
};

export type ProductUpdatePayload = Partial<ProductPayload>;

export type ProductFilters = {
  search?: string;
  is_active?: boolean | "";
  category?: ProductCategory | "";
  unit?: ProductUnit | "";
};

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

export type ProductKind =
  | "finished_good"
  | "raw_material"
  | "supply"
  | "packaging"
  | "service"
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

export const PRODUCT_KIND_LABELS: Record<ProductKind, string> = {
  finished_good: "Producto terminado",
  raw_material: "Materia prima",
  supply: "Insumo",
  packaging: "Empaque",
  service: "Servicio",
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
  product_kind: ProductKind;
  production_notes: string | null;
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
  product_kind: ProductKind;
  production_notes?: string | null;
  is_returnable_container: boolean;
  notes?: string | null;
};

export type ProductUpdatePayload = Partial<ProductPayload>;

export type ProductFilters = {
  search?: string;
  is_active?: boolean | "";
  category?: ProductCategory | "";
  unit?: ProductUnit | "";
  product_kind?: ProductKind | "";
};

export type ProductProductionClassificationPayload = {
  product_kind: ProductKind;
  production_notes?: string | null;
};

export type PriceListType =
  | "general"
  | "customer"
  | "route"
  | "customer_route"
  | "special";

export type PriceSource =
  | "default"
  | "general"
  | "special"
  | "customer"
  | "route"
  | "customer_route"
  | "manual";

export const PRICE_LIST_TYPE_LABELS: Record<PriceListType, string> = {
  general: "General",
  customer: "Cliente",
  route: "Ruta",
  customer_route: "Cliente + ruta",
  special: "Especial",
};

export const PRICE_SOURCE_LABELS: Record<PriceSource, string> = {
  default: "Precio normal",
  general: "Precio general",
  special: "Precio especial",
  customer: "Precio por cliente",
  route: "Precio por ruta",
  customer_route: "Precio por cliente + ruta",
  manual: "Precio manual",
};

export type PriceListItem = {
  id: number;
  price_list_id: number;
  product_id: number;
  product_name: string;
  product_sku: string | null;
  product_presentation: string | null;
  unit_price: string;
  min_quantity: string;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PriceList = {
  id: number;
  name: string;
  list_type: PriceListType;
  customer_id: number | null;
  customer_name: string | null;
  route_id: number | null;
  route_name: string | null;
  priority: number;
  valid_from: string | null;
  valid_to: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
  items: PriceListItem[];
};

export type PriceListPayload = {
  name: string;
  list_type: PriceListType;
  customer_id?: number | null;
  route_id?: number | null;
  priority: number;
  valid_from?: string | null;
  valid_to?: string | null;
  is_active?: boolean;
  notes?: string | null;
};

export type PriceListUpdatePayload = Partial<
  Omit<PriceListPayload, "is_active">
>;

export type PriceListFilters = {
  search?: string;
  list_type?: PriceListType | "";
  customer_id?: number;
  route_id?: number;
  is_active?: boolean | "";
};

export type PriceListItemPayload = {
  product_id: number;
  unit_price: string;
  min_quantity: string;
  is_active?: boolean;
  notes?: string | null;
};

export type PriceListItemUpdatePayload = Partial<
  Omit<PriceListItemPayload, "is_active">
>;

export type PriceResolution = {
  product_id: number;
  default_price: string;
  resolved_price: string;
  price_source: PriceSource;
  price_list_id: number | null;
  price_list_name: string | null;
  pricing_note: string;
};

export type PriceResolutionParams = {
  product_id: number;
  customer_id?: number;
  route_id?: number;
  route_load_id?: number;
  quantity?: string;
  price_date?: string;
};

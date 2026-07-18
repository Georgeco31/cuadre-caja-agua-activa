export type InventoryLocationType =
  | "warehouse"
  | "vehicle"
  | "production_area"
  | "other";

export type InventoryMovementType =
  | "entry"
  | "exit"
  | "adjustment_in"
  | "adjustment_out";

export type InventoryMovementStatus = "active" | "voided";

export const INVENTORY_LOCATION_TYPE_LABELS: Record<
  InventoryLocationType,
  string
> = {
  warehouse: "Bodega",
  vehicle: "Vehículo",
  production_area: "Área de producción",
  other: "Otro",
};

export const INVENTORY_MOVEMENT_TYPE_LABELS: Record<
  InventoryMovementType,
  string
> = {
  entry: "Entrada",
  exit: "Salida",
  adjustment_in: "Ajuste positivo",
  adjustment_out: "Ajuste negativo",
};

export const INVENTORY_MOVEMENT_STATUS_LABELS: Record<
  InventoryMovementStatus,
  string
> = {
  active: "Activo",
  voided: "Anulado",
};

export type InventoryLocation = {
  id: number;
  code: string | null;
  name: string;
  location_type: InventoryLocationType;
  vehicle_id: number | null;
  description: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type InventoryLocationPayload = {
  code?: string | null;
  name: string;
  location_type: InventoryLocationType;
  vehicle_id?: number | null;
  description?: string | null;
  notes?: string | null;
};

export type InventoryLocationUpdatePayload = Partial<InventoryLocationPayload>;

export type InventoryLocationFilters = {
  search?: string;
  is_active?: boolean | "";
  location_type?: InventoryLocationType | "";
};

export type InventoryStock = {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string | null;
  product_presentation: string | null;
  location_id: number;
  location_name: string;
  quantity_on_hand: string;
  created_at: string;
  updated_at: string;
};

export type InventoryStockFilters = {
  product_id?: number;
  location_id?: number;
  only_positive?: boolean;
};

export type InventoryMovement = {
  id: number;
  movement_date: string;
  movement_type: InventoryMovementType;
  product_id: number;
  location_id: number;
  location_name: string;
  product_sku_snapshot: string | null;
  product_name_snapshot: string;
  product_presentation_snapshot: string | null;
  quantity: string;
  unit_cost: string | null;
  total_cost: string | null;
  reason: string | null;
  status: InventoryMovementStatus;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
};

export type InventoryMovementPayload = {
  movement_date: string;
  movement_type: InventoryMovementType;
  product_id: number;
  location_id: number;
  quantity: string;
  unit_cost?: string | null;
  reason?: string | null;
};

export type InventoryMovementFilters = {
  date_from?: string;
  date_to?: string;
  product_id?: number;
  location_id?: number;
  movement_type?: InventoryMovementType | "";
  status?: InventoryMovementStatus | "";
};


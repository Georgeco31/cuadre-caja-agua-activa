export type RouteReturnStatus = "active" | "voided";
export type RouteReturnMovementStatus = "active" | "voided";

export const ROUTE_RETURN_STATUS_LABELS: Record<RouteReturnStatus, string> = {
  active: "Activo",
  voided: "Anulado",
};

export type RouteReturnItem = {
  id: number;
  route_return_id: number;
  route_load_item_id: number;
  product_id: number;
  product_sku_snapshot: string | null;
  product_name_snapshot: string;
  product_presentation_snapshot: string | null;
  quantity_loaded: string;
  quantity_returned: string;
  source_exit_movement_id: number;
  destination_entry_movement_id: number;
  source_exit_movement_status: RouteReturnMovementStatus;
  destination_entry_movement_status: RouteReturnMovementStatus;
  created_at: string;
};

export type RouteReturn = {
  id: number;
  return_number: string;
  return_date: string;
  route_load_id: number;
  route_load_number: string;
  route_load_status: "active" | "voided";
  route_id: number;
  route_name: string;
  vehicle_id: number;
  vehicle_name: string;
  source_location_id: number;
  source_location_name: string;
  destination_location_id: number;
  destination_location_name: string;
  status: RouteReturnStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: RouteReturnItem[];
};

export type RouteReturnItemPayload = {
  route_load_item_id: number;
  quantity_returned: string;
};

export type RouteReturnPayload = {
  return_date: string;
  route_load_id: number;
  destination_location_id: number;
  notes?: string | null;
  items: RouteReturnItemPayload[];
};

export type RouteReturnFilters = {
  date_from?: string;
  date_to?: string;
  status?: RouteReturnStatus | "";
  route_id?: number;
  vehicle_id?: number;
  route_load_id?: number;
  product_id?: number;
  search?: string;
};

export type RouteLoadStatus = "active" | "voided";
export type RouteLoadMovementStatus = "active" | "voided";

export const ROUTE_LOAD_STATUS_LABELS: Record<RouteLoadStatus, string> = {
  active: "Activa",
  voided: "Anulada",
};

export type RouteLoadItem = {
  id: number;
  route_load_id: number;
  product_id: number;
  product_sku_snapshot: string | null;
  product_name_snapshot: string;
  product_presentation_snapshot: string | null;
  quantity_loaded: string;
  source_exit_movement_id: number;
  destination_entry_movement_id: number;
  source_exit_movement_status: RouteLoadMovementStatus;
  destination_entry_movement_status: RouteLoadMovementStatus;
  created_at: string;
};

export type RouteLoad = {
  id: number;
  load_number: string;
  load_date: string;
  route_id: number;
  route_name: string;
  vehicle_id: number;
  vehicle_name: string;
  source_location_id: number;
  source_location_name: string;
  destination_location_id: number;
  destination_location_name: string;
  status: RouteLoadStatus;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  items: RouteLoadItem[];
};

export type RouteLoadItemPayload = {
  product_id: number;
  quantity_loaded: string;
};

export type RouteLoadPayload = {
  load_date: string;
  route_id: number;
  vehicle_id: number;
  source_location_id: number;
  destination_location_id: number;
  notes?: string | null;
  items: RouteLoadItemPayload[];
};

export type RouteLoadFilters = {
  date_from?: string;
  date_to?: string;
  status?: RouteLoadStatus | "";
  route_id?: number;
  vehicle_id?: number;
  product_id?: number;
  search?: string;
};

import type { RouteLoadStatus } from "@/types/routeLoad";

export type RouteSettlementStatus =
  | "pending"
  | "balanced"
  | "with_difference";

export type RouteSettlementItem = {
  product_id: number;
  product_name_snapshot: string;
  product_presentation_snapshot: string | null;
  loaded_quantity: string;
  returned_quantity: string | null;
  physical_sold_quantity: string | null;
  registered_sold_quantity: string;
  physical_vs_registered_difference: string | null;
};

export type RouteSettlement = {
  route_load_id: number;
  load_number: string;
  load_date: string;
  route_load_status: RouteLoadStatus;
  route_id: number;
  route_name: string;
  vehicle_id: number;
  vehicle_name: string;
  responsible_name: string | null;
  route_return_id: number | null;
  return_number: string | null;
  return_date: string | null;
  route_closure_id: number | null;
  closure_number: string | null;
  closure_date: string | null;
  total_loaded_quantity: string;
  total_returned_quantity: string | null;
  physical_sold_quantity: string | null;
  registered_sold_quantity: string;
  physical_vs_registered_difference: string | null;
  cash_sales_amount: string;
  credit_sales_amount: string;
  registered_sales_amount: string;
  registered_payments_amount: string;
  expected_cash_amount: string;
  delivered_cash_amount: string | null;
  cash_difference: string | null;
  status: RouteSettlementStatus;
  return_observation: string | null;
  settlement_observation: string | null;
  difference_reason: string | null;
  messages: string[];
  items: RouteSettlementItem[];
};

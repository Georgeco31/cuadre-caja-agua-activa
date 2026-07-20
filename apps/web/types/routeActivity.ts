import type { CreditPayment } from "@/types/creditPayment";
import type { Sale } from "@/types/sale";
import type { RouteLoadStatus } from "@/types/routeLoad";

export type RouteActivityProduct = {
  product_id: number;
  product_name_snapshot: string;
  total_quantity: string;
  total_amount: string;
};

export type RouteCommercialActivity = {
  load_id: number;
  load_number: string;
  load_date: string;
  route_id: number;
  route_name: string;
  vehicle_id: number;
  vehicle_name: string;
  status: RouteLoadStatus;
  cash_sales: Sale[];
  credit_sales: Sale[];
  payments: CreditPayment[];
  cash_sales_total: string;
  credit_sales_total: string;
  payments_total: string;
  expected_cash_total: string;
  products_sold: RouteActivityProduct[];
};

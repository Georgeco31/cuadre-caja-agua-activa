export type DeliveryRoute = {
  id: number;
  code: string | null;
  name: string;
  description: string | null;
  zone: string | null;
  sector: string | null;
  service_days: string | null;
  reference_driver: string | null;
  reference_vehicle: string | null;
  expected_daily_cash: string;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type DeliveryRoutePayload = {
  code?: string | null;
  name: string;
  description?: string | null;
  zone?: string | null;
  sector?: string | null;
  service_days?: string | null;
  reference_driver?: string | null;
  reference_vehicle?: string | null;
  expected_daily_cash: string;
  notes?: string | null;
};

export type DeliveryRouteUpdatePayload = Partial<DeliveryRoutePayload>;

export type DeliveryRouteFilters = {
  search?: string;
  is_active?: boolean | "";
  zone?: string;
  sector?: string;
};

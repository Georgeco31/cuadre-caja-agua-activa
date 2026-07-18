export type VehicleType = "truck" | "van" | "motorcycle" | "car" | "other";

export type FuelType = "gasoline" | "diesel" | "electric" | "hybrid" | "other";

export const VEHICLE_TYPE_LABELS: Record<VehicleType, string> = {
  truck: "Camión",
  van: "Furgoneta",
  motorcycle: "Motocicleta",
  car: "Auto",
  other: "Otro",
};

export const FUEL_TYPE_LABELS: Record<FuelType, string> = {
  gasoline: "Gasolina",
  diesel: "Diésel",
  electric: "Eléctrico",
  hybrid: "Híbrido",
  other: "Otro",
};

export type Vehicle = {
  id: number;
  code: string | null;
  name: string;
  plate: string | null;
  vehicle_type: VehicleType;
  brand: string | null;
  model: string | null;
  year: number | null;
  color: string | null;
  fuel_type: FuelType;
  capacity_reference: string | null;
  reference_driver: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type VehiclePayload = {
  code?: string | null;
  name: string;
  plate?: string | null;
  vehicle_type: VehicleType;
  brand?: string | null;
  model?: string | null;
  year?: number | null;
  color?: string | null;
  fuel_type: FuelType;
  capacity_reference?: string | null;
  reference_driver?: string | null;
  notes?: string | null;
};

export type VehicleUpdatePayload = Partial<VehiclePayload>;

export type VehicleFilters = {
  search?: string;
  is_active?: boolean | "";
  vehicle_type?: VehicleType | "";
  fuel_type?: FuelType | "";
};

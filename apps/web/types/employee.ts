export type EmployeeType =
  | "driver"
  | "assistant"
  | "office"
  | "production"
  | "sales"
  | "other";

export type PaymentFrequency =
  | "daily"
  | "weekly"
  | "biweekly"
  | "monthly"
  | "other";

export const EMPLOYEE_TYPE_LABELS: Record<EmployeeType, string> = {
  driver: "Chofer",
  assistant: "Ayudante",
  office: "Oficina",
  production: "Producción",
  sales: "Ventas",
  other: "Otro",
};

export const PAYMENT_FREQUENCY_LABELS: Record<PaymentFrequency, string> = {
  daily: "Diario",
  weekly: "Semanal",
  biweekly: "Quincenal",
  monthly: "Mensual",
  other: "Otro",
};

export type Employee = {
  id: number;
  first_name: string;
  last_name: string;
  identification: string | null;
  primary_phone: string | null;
  secondary_phone: string | null;
  address: string | null;
  job_position: string | null;
  employee_type: EmployeeType;
  base_salary: string;
  payment_frequency: PaymentFrequency;
  hire_date: string | null;
  termination_date: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type EmployeePayload = {
  first_name: string;
  last_name: string;
  identification?: string | null;
  primary_phone?: string | null;
  secondary_phone?: string | null;
  address?: string | null;
  job_position?: string | null;
  employee_type: EmployeeType;
  base_salary: string;
  payment_frequency: PaymentFrequency;
  hire_date?: string | null;
  notes?: string | null;
};

export type EmployeeUpdatePayload = Partial<
  EmployeePayload & { termination_date: string | null }
>;

export type EmployeeFilters = {
  search?: string;
  is_active?: boolean | "";
  employee_type?: EmployeeType | "";
  job_position?: string;
};

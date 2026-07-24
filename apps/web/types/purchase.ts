import type { Supplier } from "@/types/supplier";

export type PurchaseStatus = "active" | "voided";
export type PurchasePaymentStatus = "unpaid" | "partial" | "paid";
export type PurchaseDocumentType =
  | "factura"
  | "nota_venta"
  | "recibo"
  | "otro";

export const PURCHASE_STATUS_LABELS: Record<PurchaseStatus, string> = {
  active: "Activa",
  voided: "Anulada",
};

export const PURCHASE_PAYMENT_STATUS_LABELS: Record<
  PurchasePaymentStatus,
  string
> = {
  unpaid: "Pendiente",
  partial: "Parcial",
  paid: "Pagada",
};

export const PURCHASE_DOCUMENT_TYPE_LABELS: Record<
  PurchaseDocumentType,
  string
> = {
  factura: "Factura",
  nota_venta: "Nota de venta",
  recibo: "Recibo",
  otro: "Otro",
};

export type PurchaseItem = {
  id: number;
  purchase_id: number;
  product_id: number | null;
  description: string | null;
  product_sku_snapshot: string | null;
  product_name_snapshot: string | null;
  product_presentation_snapshot: string | null;
  quantity: string;
  unit_cost: string;
  discount_amount: string;
  tax_amount: string;
  subtotal_amount: string;
  total_amount: string;
  notes: string | null;
  created_at: string;
};

export type Purchase = {
  id: number;
  purchase_number: string;
  supplier_id: number;
  purchase_date: string;
  document_number: string | null;
  document_type: PurchaseDocumentType | null;
  status: PurchaseStatus;
  payment_status: PurchasePaymentStatus;
  subtotal_amount: string;
  discount_amount: string;
  tax_amount: string;
  total_amount: string;
  notes: string | null;
  void_reason: string | null;
  voided_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  supplier: Supplier;
  items: PurchaseItem[];
};

export type PurchaseItemPayload = {
  product_id?: number | null;
  description?: string | null;
  quantity: string;
  unit_cost: string;
  discount_amount: string;
  tax_amount: string;
  notes?: string | null;
};

export type PurchasePayload = {
  supplier_id: number;
  purchase_date: string;
  document_number?: string | null;
  document_type?: PurchaseDocumentType | null;
  payment_status: PurchasePaymentStatus;
  notes?: string | null;
  items: PurchaseItemPayload[];
};

export type PurchaseFilters = {
  date_from?: string;
  date_to?: string;
  status?: PurchaseStatus | "";
  payment_status?: PurchasePaymentStatus | "";
  supplier_id?: number;
  product_id?: number;
  search?: string;
};

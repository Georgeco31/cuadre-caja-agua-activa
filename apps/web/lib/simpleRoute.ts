import type {
  SimpleRouteSaleType,
  SimpleRouteSettlementStatus,
} from "@/types/simpleRoute";

export function calculateSimpleRouteSalePreview(
  quantity: string,
  unitPrice: string,
  saleType: SimpleRouteSaleType,
  collected: string,
): { total: number; paid: number; pending: number; isValid: boolean } {
  const total = cents(Number(quantity) * Number(unitPrice));
  if (!Number.isFinite(total) || total < 0) {
    return { total: 0, paid: 0, pending: 0, isValid: false };
  }
  if (saleType === "cash") {
    return { total, paid: total, pending: 0, isValid: total >= 0 };
  }
  if (saleType === "credit") {
    return { total, paid: 0, pending: total, isValid: total >= 0 };
  }
  const paid = cents(Number(collected));
  return {
    total,
    paid,
    pending: cents(total - paid),
    isValid: paid > 0 && paid < total,
  };
}

export function simpleRouteSettlementTone(
  status: SimpleRouteSettlementStatus,
): "neutral" | "success" | "warning" | "danger" {
  if (status === "balanced") return "success";
  if (status === "with_difference") return "warning";
  if (status === "cancelled") return "danger";
  return "neutral";
}

export function simpleRouteIndependenceNotices(): string[] {
  return [
    "No crea ventas oficiales.",
    "No crea cartera formal.",
    "No modifica inventario.",
    "Caja recibe una referencia única del efectivo liquidado.",
  ];
}

function cents(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

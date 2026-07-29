import type {
  RouteSettlement,
  RouteSettlementStatus,
} from "@/types/routeSettlement";

export const ROUTE_SETTLEMENT_STATUS_LABELS: Record<
  RouteSettlementStatus,
  string
> = {
  pending: "Pendiente",
  balanced: "Cuadrada",
  with_difference: "Con diferencia",
};

export function getRouteSettlementMessages(
  settlement: Pick<
    RouteSettlement,
    | "route_return_id"
    | "delivered_cash_amount"
    | "physical_vs_registered_difference"
    | "cash_difference"
    | "status"
    | "items"
  >,
): string[] {
  const messages: string[] = [];
  if (settlement.route_return_id === null) {
    messages.push("No hay retorno registrado todavía.");
  }
  if (settlement.delivered_cash_amount === null) {
    messages.push("No hay dinero entregado registrado todavía.");
  }
  if (
    settlement.items.some((item) =>
      isNonZero(item.physical_vs_registered_difference),
    )
  ) {
    messages.push("La ruta tiene diferencia de producto.");
  }
  if (isNonZero(settlement.cash_difference)) {
    messages.push("La ruta tiene diferencia de dinero.");
  }
  if (settlement.status === "balanced") {
    messages.push("La ruta está cuadrada.");
  }
  return messages;
}

export function requiresDifferenceObservation(
  physicalDifferences: Array<string | null>,
  estimatedCashDifferenceInCents: number | null,
): boolean {
  return (
    physicalDifferences.some(isNonZero) ||
    (estimatedCashDifferenceInCents !== null &&
      estimatedCashDifferenceInCents !== 0)
  );
}

function isNonZero(value: string | null): boolean {
  if (value === null) {
    return false;
  }
  const numericValue = Number(value);
  return Number.isFinite(numericValue) && numericValue !== 0;
}

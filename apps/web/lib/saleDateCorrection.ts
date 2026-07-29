import type { SaleStatus } from "@/types/sale";

export const SALE_DATE_CORRECTION_PERMISSION_MESSAGE =
  "No tienes permiso para corregir ventas. Solicita autorización a George.";

export function canShowSaleDateCorrectionAction(
  canCorrectDate: boolean,
  status: SaleStatus,
): boolean {
  return canCorrectDate && status === "active";
}

export function validateSaleDateCorrectionForm(
  currentSaleDate: string,
  newSaleDate: string,
  reason: string,
): string | null {
  if (!isValidIsoDate(newSaleDate)) {
    return "La nueva fecha de venta es obligatoria y debe ser válida.";
  }
  if (newSaleDate === currentSaleDate) {
    return "La nueva fecha debe ser diferente de la fecha actual.";
  }
  if (!reason.trim()) {
    return "El motivo de corrección es obligatorio.";
  }
  return null;
}

export function getSaleDateCorrectionErrorMessage(error: unknown): string {
  if (getErrorStatus(error) === 403) {
    return SALE_DATE_CORRECTION_PERMISSION_MESSAGE;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return "No se pudo corregir la fecha de la venta.";
}

function isValidIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.valueOf()) &&
    parsed.toISOString().slice(0, 10) === value;
}

function getErrorStatus(error: unknown): number | undefined {
  if (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    typeof error.status === "number"
  ) {
    return error.status;
  }
  return undefined;
}

export function parseMoneyInputToCents(value: string): number | null {
  const normalizedValue = value.trim().replace(",", ".");
  if (!/^\d+(?:\.\d*)?$/.test(normalizedValue)) {
    return null;
  }

  const [dollarsPart, centsPart = ""] = normalizedValue.split(".");
  const extraDecimals = centsPart.slice(2);
  if (extraDecimals.length > 0 && /[1-9]/.test(extraDecimals)) {
    return null;
  }

  const dollars = Number(dollarsPart);
  const cents = Number(centsPart.slice(0, 2).padEnd(2, "0"));
  if (!Number.isSafeInteger(dollars) || !Number.isSafeInteger(cents)) {
    return null;
  }

  const totalCents = dollars * 100 + cents;
  if (!Number.isSafeInteger(totalCents)) {
    return null;
  }

  return totalCents;
}

export function formatCentsAsMoneyInput(cents: number): string {
  const dollarsPart = Math.trunc(cents / 100);
  const centsPart = String(cents % 100).padStart(2, "0");

  return `${dollarsPart}.${centsPart}`;
}

export function isValidMoneyInputDraft(value: string): boolean {
  return value === "" || /^\d*(?:[.,]\d{0,2})?$/.test(value);
}

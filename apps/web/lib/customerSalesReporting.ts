export type DateRange = {
  start_date?: string;
  end_date?: string;
};

export type CustomerSalesSummaryQuery = DateRange & {
  sale_type?: "cash" | "credit" | "all";
  status?: "active" | "voided";
};

export function getCustomerSalesSummaryMetrics(summary: {
  cash_sales_total: string;
  credit_sales_total: string;
  total_sales_amount: string;
  pending_credit_amount: string;
}) {
  return [
    { label: "Ventas contado", value: summary.cash_sales_total },
    { label: "Ventas crédito", value: summary.credit_sales_total },
    { label: "Total vendido", value: summary.total_sales_amount },
    { label: "Saldo pendiente", value: summary.pending_credit_amount },
  ];
}

export function validateDateRange(filters: DateRange): string | null {
  if (
    filters.start_date &&
    filters.end_date &&
    filters.end_date < filters.start_date
  ) {
    return "La fecha hasta no puede ser menor que la fecha desde.";
  }
  return null;
}

export function buildCustomerSalesSummaryPath(
  customerId: number,
  filters: CustomerSalesSummaryQuery = {},
): string {
  if (!Number.isInteger(customerId) || customerId <= 0) {
    throw new Error("Selecciona un cliente válido.");
  }
  const rangeError = validateDateRange(filters);
  if (rangeError) {
    throw new Error(rangeError);
  }
  const params = new URLSearchParams();
  if (filters.start_date) {
    params.set("start_date", filters.start_date);
  }
  if (filters.end_date) {
    params.set("end_date", filters.end_date);
  }
  if (filters.sale_type) {
    params.set("sale_type", filters.sale_type);
  }
  if (filters.status) {
    params.set("status", filters.status);
  }
  const query = params.toString();
  return `/customers/${customerId}/sales-summary${query ? `?${query}` : ""}`;
}

export function buildCustomerCreditExportPath(
  customerId: number,
  filters: DateRange = {},
): string {
  if (!Number.isInteger(customerId) || customerId <= 0) {
    throw new Error("Selecciona un cliente antes de exportar.");
  }
  const rangeError = validateDateRange(filters);
  if (rangeError) {
    throw new Error(rangeError);
  }
  const params = new URLSearchParams({ customer_id: String(customerId) });
  if (filters.start_date) {
    params.set("start_date", filters.start_date);
  }
  if (filters.end_date) {
    params.set("end_date", filters.end_date);
  }
  return `/reports/exports/customer-credit-sales.xlsx?${params.toString()}`;
}

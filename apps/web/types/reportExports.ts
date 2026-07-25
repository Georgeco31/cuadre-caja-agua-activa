export type ReportExportType =
  | "management-dashboard"
  | "monthly-summary"
  | "daily-operational-summary"
  | "sales"
  | "receivables"
  | "operating-expenses"
  | "purchases"
  | "inventory"
  | "production"
  | "routes"
  | "payroll";

export type ReportExportDefinition = {
  type: ReportExportType;
  label: string;
  description: string;
  endpoint: string;
  filename: string;
  filterMode: "dates" | "month" | "date" | "none";
};

export type ReportExportFormat = "excel" | "pdf";

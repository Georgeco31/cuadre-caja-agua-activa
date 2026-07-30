"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LogoutButton } from "@/components/LogoutButton";
import { DashboardShell } from "@/components/ui/DashboardShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { ResponsiveToolbar } from "@/components/ui/ResponsiveToolbar";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  ApiError,
  downloadFile,
  getCurrentUser,
  listCustomers,
} from "@/lib/api";
import { getToken, removeToken, saveUser } from "@/lib/auth";
import { buildCustomerCreditExportPath } from "@/lib/customerSalesReporting";
import type { Customer } from "@/types/customer";
import type {
  ReportExportDefinition,
  ReportExportFormat,
  ReportExportType,
} from "@/types/reportExports";

const EXCEL_REPORTS: ReportExportDefinition[] = [
  {
    type: "management-dashboard",
    label: "Panel gerencial",
    description: "Indicadores, alertas y series generales del negocio.",
    endpoint: "management-dashboard.xlsx",
    filename: "panel-gerencial.xlsx",
    filterMode: "dates",
  },
  {
    type: "monthly-summary",
    label: "Resumen mensual",
    description: "Caja, ventas, producción, rutas y alertas de un mes.",
    endpoint: "monthly-summary.xlsx",
    filename: "resumen-mensual.xlsx",
    filterMode: "month",
  },
  {
    type: "sales",
    label: "Ventas",
    description: "Ventas de contado y crédito con su detalle de productos.",
    endpoint: "sales.xlsx",
    filename: "ventas.xlsx",
    filterMode: "dates",
  },
  {
    type: "receivables",
    label: "Cartera",
    description: "Clientes con saldo, estados de cuenta y vencidos.",
    endpoint: "receivables.xlsx",
    filename: "cartera.xlsx",
    filterMode: "dates",
  },
  {
    type: "operating-expenses",
    label: "Gastos operativos",
    description: "Gastos generales y su estado de pago.",
    endpoint: "operating-expenses.xlsx",
    filename: "gastos-operativos.xlsx",
    filterMode: "dates",
  },
  {
    type: "purchases",
    label: "Compras",
    description: "Compras administrativas y sus ítems.",
    endpoint: "purchases.xlsx",
    filename: "compras.xlsx",
    filterMode: "dates",
  },
  {
    type: "inventory",
    label: "Inventario",
    description: "Stock actual, ubicaciones y movimientos recientes.",
    endpoint: "inventory.xlsx",
    filename: "inventario.xlsx",
    filterMode: "none",
  },
  {
    type: "production",
    label: "Producción",
    description: "Lotes, aplicaciones, consumos y fórmulas.",
    endpoint: "production.xlsx",
    filename: "produccion.xlsx",
    filterMode: "dates",
  },
  {
    type: "routes",
    label: "Rutas",
    description: "Cargas, retornos, cierres, recibos y actividad comercial.",
    endpoint: "routes.xlsx",
    filename: "rutas.xlsx",
    filterMode: "dates",
  },
  {
    type: "payroll",
    label: "Nómina",
    description: "Roles base, detalle y deducciones registradas.",
    endpoint: "payroll.xlsx",
    filename: "nomina-base.xlsx",
    filterMode: "dates",
  },
];

const PDF_REPORTS: ReportExportDefinition[] = [
  {
    type: "management-dashboard",
    label: "Panel gerencial",
    description: "Indicadores y alertas ejecutivas de todo el negocio.",
    endpoint: "management-dashboard.pdf",
    filename: "panel-gerencial.pdf",
    filterMode: "dates",
  },
  {
    type: "monthly-summary",
    label: "Resumen mensual",
    description: "Resumen ejecutivo de caja, ventas, producción y rutas.",
    endpoint: "monthly-summary.pdf",
    filename: "resumen-mensual.pdf",
    filterMode: "month",
  },
  {
    type: "daily-operational-summary",
    label: "Resumen diario operativo",
    description: "Caja, producción, ventas, cobros, rutas y alertas del día.",
    endpoint: "daily-operational-summary.pdf",
    filename: "resumen-operativo.pdf",
    filterMode: "date",
  },
  {
    type: "receivables",
    label: "Cartera",
    description: "Totales y clientes con cuentas por cobrar pendientes.",
    endpoint: "receivables.pdf",
    filename: "cartera.pdf",
    filterMode: "dates",
  },
  {
    type: "payroll",
    label: "Nómina base",
    description: "Totales y roles de pago resumidos por empleado.",
    endpoint: "payroll.pdf",
    filename: "nomina-base.pdf",
    filterMode: "dates",
  },
];

export default function ReportExportsPage() {
  const router = useRouter();
  const currentMonthDates = useMemo(getCurrentMonthDates, []);
  const [token, setToken] = useState<string | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<
    Record<ReportExportFormat, ReportExportType>
  >({
    excel: "management-dashboard",
    pdf: "management-dashboard",
  });
  const [dateFrom, setDateFrom] = useState(currentMonthDates.from);
  const [dateTo, setDateTo] = useState(currentMonthDates.to);
  const [selectedMonth, setSelectedMonth] = useState(getCurrentMonthValue);
  const [selectedDate, setSelectedDate] = useState(getCurrentDateValue);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState("");
  const [error, setError] = useState("");
  const [downloadingFormat, setDownloadingFormat] =
    useState<ReportExportFormat | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [isDownloadingCustomerCredit, setIsDownloadingCustomerCredit] =
    useState(false);
  const [accountName, setAccountName] = useState("Agua Activa");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    void authorizePage(storedToken);
  }, [router]);

  async function authorizePage(activeToken: string) {
    try {
      const currentUser = await getCurrentUser(activeToken);
      saveUser(currentUser);
      setAccountName(currentUser.username);
      if (currentUser.role !== "admin_auditor") {
        setForbidden(true);
        setError("No tienes permisos para acceder a las exportaciones.");
        return;
      }
      setCustomers(await listCustomers(activeToken));
      setToken(activeToken);
    } catch (loadError) {
      if (loadError instanceof ApiError && loadError.status === 401) {
        removeToken();
        router.replace("/login");
        return;
      }
      setError(
        loadError instanceof Error
          ? loadError.message
          : "No se pudo validar tu sesión.",
      );
    }
  }

  const selectedReports = useMemo(
    () => ({
      excel: findReport(EXCEL_REPORTS, selectedTypes.excel),
      pdf: findReport(PDF_REPORTS, selectedTypes.pdf),
    }),
    [selectedTypes],
  );

  async function handleDownload(
    event: FormEvent<HTMLFormElement>,
    format: ReportExportFormat,
  ) {
    event.preventDefault();
    if (!token) {
      return;
    }
    const report = selectedReports[format];
    if (
      report.filterMode === "dates" &&
      dateFrom &&
      dateTo &&
      dateTo < dateFrom
    ) {
      setError("La fecha hasta no puede ser menor que la fecha desde.");
      return;
    }

    const searchParams = new URLSearchParams();
    let filename = report.filename;
    if (report.filterMode === "dates") {
      if (dateFrom) {
        searchParams.set("date_from", dateFrom);
      }
      if (dateTo) {
        searchParams.set("date_to", dateTo);
      }
    }
    if (report.filterMode === "month") {
      const period = parseMonthValue(selectedMonth);
      if (!period) {
        setError("Selecciona un mes válido.");
        return;
      }
      searchParams.set("year", String(period.year));
      searchParams.set("month", String(period.month));
      filename = `resumen-mensual-${selectedMonth}.${format === "excel" ? "xlsx" : "pdf"}`;
    }
    if (report.filterMode === "date") {
      if (!selectedDate) {
        setError("Selecciona una fecha válida.");
        return;
      }
      searchParams.set("date", selectedDate);
      filename = `resumen-operativo-${selectedDate}.pdf`;
    }

    setDownloadingFormat(format);
    setError("");
    try {
      const query = searchParams.toString();
      await downloadFile(
        token,
        `/reports/exports/${report.endpoint}${query ? `?${query}` : ""}`,
        filename,
      );
    } catch (downloadError) {
      if (
        downloadError instanceof ApiError &&
        downloadError.status === 401
      ) {
        removeToken();
        router.replace("/login");
        return;
      }
      setError(getErrorMessage(downloadError, format));
    } finally {
      setDownloadingFormat(null);
    }
  }

  async function handleCustomerCreditDownload(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    if (!token) {
      return;
    }
    try {
      const customerId = Number(selectedCustomerId);
      const endpoint = buildCustomerCreditExportPath(customerId, {
        ...(dateFrom ? { start_date: dateFrom } : {}),
        ...(dateTo ? { end_date: dateTo } : {}),
      });
      setIsDownloadingCustomerCredit(true);
      setError("");
      await downloadFile(
        token,
        endpoint,
        `ventas-credito-cliente-${customerId}.xlsx`,
      );
    } catch (downloadError) {
      if (
        downloadError instanceof ApiError &&
        downloadError.status === 401
      ) {
        removeToken();
        router.replace("/login");
        return;
      }
      setError(
        downloadError instanceof Error
          ? downloadError.message
          : "No se pudo exportar el crédito del cliente.",
      );
    } finally {
      setIsDownloadingCustomerCredit(false);
    }
  }

  function useCurrentMonth() {
    const dates = getCurrentMonthDates();
    setDateFrom(dates.from);
    setDateTo(dates.to);
    setSelectedMonth(getCurrentMonthValue());
    setSelectedDate(getCurrentDateValue());
  }

  function selectReport(
    format: ReportExportFormat,
    reportType: ReportExportType,
  ) {
    setSelectedTypes((current) => ({
      ...current,
      [format]: reportType,
    }));
  }

  return (
    <DashboardShell
      activeHref="/dashboard/reports"
      dateLabel={formatTopbarDate(new Date())}
      roleLabel={forbidden ? "Operador" : "Administrador / auditor"}
      userName={accountName}
    >
      <div className="mx-auto flex w-full min-w-0 max-w-screen-2xl flex-col gap-7 px-4 py-7 sm:px-6 sm:py-9 xl:gap-9 xl:px-8">
        <PageHeader
          actions={<LogoutButton />}
          description="Descarga reportes detallados en Excel o resúmenes ejecutivos en PDF. Todas las exportaciones conservan sus filtros y son solo lectura."
          eyebrow="Reportes y control"
          meta={
            <Link
              className="inline-flex min-h-10 items-center text-sm font-semibold text-water-700 hover:text-water-600"
              href="/dashboard"
            >
              ← Volver al dashboard
            </Link>
          }
          title="Centro de exportaciones"
        />

        {forbidden && error ? <ErrorMessage message={error} /> : null}

        {!forbidden ? (
          <>
            <ResponsiveToolbar
              actions={
                <button
                  className="min-h-11 w-full rounded-xl border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400 sm:w-auto"
                  disabled={downloadingFormat !== null}
                  onClick={useCurrentMonth}
                  type="button"
                >
                  Restablecer período actual
                </button>
              }
            >
              <div className="flex items-start gap-3">
                <StatusBadge label="Solo lectura" tone="success" />
                <p className="max-w-2xl text-sm leading-6 text-slate-600">
                  Selecciona un formato y un reporte. El período actual ya está
                  preparado como punto de partida.
                </p>
              </div>
            </ResponsiveToolbar>

            <div className="grid min-w-0 items-start gap-6 xl:grid-cols-2">
              <ExportSection
                dateFrom={dateFrom}
                dateTo={dateTo}
                disabled={downloadingFormat !== null || !token}
                format="excel"
                isDownloading={downloadingFormat === "excel"}
                onDateFromChange={setDateFrom}
                onDateToChange={setDateTo}
                onReportChange={(value) => selectReport("excel", value)}
                onSelectedDateChange={setSelectedDate}
                onSelectedMonthChange={setSelectedMonth}
                onSubmit={(event) => handleDownload(event, "excel")}
                reports={EXCEL_REPORTS}
                selectedDate={selectedDate}
                selectedMonth={selectedMonth}
                selectedReport={selectedReports.excel}
              />

              <ExportSection
                dateFrom={dateFrom}
                dateTo={dateTo}
                disabled={downloadingFormat !== null || !token}
                format="pdf"
                isDownloading={downloadingFormat === "pdf"}
                onDateFromChange={setDateFrom}
                onDateToChange={setDateTo}
                onReportChange={(value) => selectReport("pdf", value)}
                onSelectedDateChange={setSelectedDate}
                onSelectedMonthChange={setSelectedMonth}
                onSubmit={(event) => handleDownload(event, "pdf")}
                reports={PDF_REPORTS}
                selectedDate={selectedDate}
                selectedMonth={selectedMonth}
                selectedReport={selectedReports.pdf}
              />
            </div>

            <CustomerCreditExportSection
              customers={customers}
              dateFrom={dateFrom}
              dateTo={dateTo}
              disabled={
                downloadingFormat !== null ||
                isDownloadingCustomerCredit ||
                !token
              }
              isDownloading={isDownloadingCustomerCredit}
              onDateFromChange={setDateFrom}
              onDateToChange={setDateTo}
              onSelectedCustomerChange={setSelectedCustomerId}
              onSubmit={handleCustomerCreditDownload}
              selectedCustomerId={selectedCustomerId}
            />

            {error ? <ErrorMessage message={error} /> : null}

            <p className="rounded-2xl border border-water-100 bg-water-50 px-5 py-4 text-sm leading-6 text-water-900">
              Los archivos reflejan los datos registrados en el sistema para el
              período seleccionado y no modifican información.
            </p>
          </>
        ) : null}
      </div>
    </DashboardShell>
  );
}

function CustomerCreditExportSection({
  customers,
  dateFrom,
  dateTo,
  disabled,
  isDownloading,
  onDateFromChange,
  onDateToChange,
  onSelectedCustomerChange,
  onSubmit,
  selectedCustomerId,
}: {
  customers: Customer[];
  dateFrom: string;
  dateTo: string;
  disabled: boolean;
  isDownloading: boolean;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onSelectedCustomerChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  selectedCustomerId: string;
}) {
  return (
    <section className="overflow-hidden rounded-3xl border border-water-200 bg-white shadow-card">
      <div className="border-b border-water-100 bg-water-50 p-5 sm:p-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-water-700">
          Exportación especializada · Excel
        </p>
        <h2 className="mt-1.5 text-xl font-semibold text-slate-950">
          Ventas a crédito por cliente
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Genera un libro con resumen, cobrado, saldo pendiente y el detalle de
          productos de cada venta activa del cliente.
        </p>
      </div>
      <form
        className="grid gap-4 p-5 sm:grid-cols-2 sm:p-6 xl:grid-cols-[minmax(260px,1.4fr)_minmax(180px,0.7fr)_minmax(180px,0.7fr)_auto] xl:items-end"
        onSubmit={onSubmit}
      >
        <label className="block">
          <span className="text-sm font-semibold text-slate-800">
            Cliente obligatorio
          </span>
          <select
            className="mt-2 h-11 w-full rounded-xl border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
            disabled={disabled}
            onChange={(event) =>
              onSelectedCustomerChange(event.target.value)
            }
            value={selectedCustomerId}
          >
            <option value="">Selecciona un cliente</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.name}
              </option>
            ))}
          </select>
        </label>
        <DateField
          disabled={disabled}
          label="Fecha desde (opcional)"
          onChange={onDateFromChange}
          value={dateFrom}
        />
        <DateField
          disabled={disabled}
          label="Fecha hasta (opcional)"
          onChange={onDateToChange}
          value={dateTo}
        />
        <button
          className="min-h-11 rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          disabled={disabled}
          type="submit"
        >
          {isDownloading
            ? "Preparando Excel..."
            : "Exportar crédito del cliente"}
        </button>
      </form>
    </section>
  );
}

type ExportSectionProps = {
  format: ReportExportFormat;
  reports: ReportExportDefinition[];
  selectedReport: ReportExportDefinition;
  dateFrom: string;
  dateTo: string;
  selectedMonth: string;
  selectedDate: string;
  disabled: boolean;
  isDownloading: boolean;
  onReportChange: (value: ReportExportType) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onSelectedMonthChange: (value: string) => void;
  onSelectedDateChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function ExportSection({
  format,
  reports,
  selectedReport,
  dateFrom,
  dateTo,
  selectedMonth,
  selectedDate,
  disabled,
  isDownloading,
  onReportChange,
  onDateFromChange,
  onDateToChange,
  onSelectedMonthChange,
  onSelectedDateChange,
  onSubmit,
}: ExportSectionProps) {
  const isPdf = format === "pdf";
  return (
    <section className="min-w-0 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card">
      <div className="border-b border-slate-200 bg-slate-50/80 p-5 sm:p-6">
        <div className="flex items-start gap-4">
          <span
            aria-hidden="true"
            className={
              isPdf
                ? "inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-800 text-xs font-black text-white"
                : "inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-water-700 text-xs font-black text-white"
            }
          >
            {isPdf ? "PDF" : "XLS"}
          </span>
          <div>
            <h2 className="text-xl font-semibold text-slate-950">
              {isPdf ? "Exportaciones PDF" : "Exportaciones Excel"}
            </h2>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              {isPdf
                ? "Resúmenes ejecutivos listos para revisar o imprimir."
                : "Reportes detallados con filtros básicos para análisis."}
            </p>
          </div>
        </div>
        {isPdf ? (
          <p className="mt-4 rounded-xl border border-water-100 bg-water-50 px-4 py-3 text-sm font-medium leading-6 text-water-800">
            Para reportes detallados usa Excel. El PDF está pensado como
            resumen ejecutivo o impresión.
          </p>
        ) : null}
      </div>
      <form
        className="min-w-0 space-y-6 p-5 sm:p-6"
        onSubmit={onSubmit}
      >
        <label className="block">
          <span className="text-sm font-semibold text-slate-800">
            Tipo de reporte
          </span>
          <select
            className="mt-2 h-11 w-full rounded-xl border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
            disabled={disabled}
            onChange={(event) =>
              onReportChange(event.target.value as ReportExportType)
            }
            value={selectedReport.type}
          >
            {reports.map((report) => (
              <option key={report.type} value={report.type}>
                {report.label}
              </option>
            ))}
          </select>
          <span className="mt-2 block text-sm text-slate-600">
            {selectedReport.description}
          </span>
        </label>

        {selectedReport.filterMode === "dates" ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <DateField
              disabled={disabled}
              label="Fecha desde"
              onChange={onDateFromChange}
              value={dateFrom}
            />
            <DateField
              disabled={disabled}
              label="Fecha hasta"
              onChange={onDateToChange}
              value={dateTo}
            />
          </div>
        ) : null}

        {selectedReport.filterMode === "month" ? (
          <label className="block max-w-sm">
            <span className="text-sm font-semibold text-slate-800">
              Mes del reporte
            </span>
            <input
              className="mt-2 h-11 w-full rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              disabled={disabled}
              onChange={(event) => onSelectedMonthChange(event.target.value)}
              required
              type="month"
              value={selectedMonth}
            />
          </label>
        ) : null}

        {selectedReport.filterMode === "date" ? (
          <DateField
            disabled={disabled}
            label="Fecha del reporte"
            onChange={onSelectedDateChange}
            value={selectedDate}
          />
        ) : null}

        {selectedReport.filterMode === "none" ? (
          <p className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
            Este reporte muestra el estado actual del inventario y no requiere
            un período.
          </p>
        ) : null}

        <button
          className={
            isPdf
              ? "min-h-11 w-full rounded-xl bg-slate-800 px-5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
              : "min-h-11 w-full rounded-xl bg-water-700 px-5 text-sm font-semibold text-white shadow-water transition hover:bg-water-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none sm:w-auto"
          }
          disabled={disabled}
          type="submit"
        >
          {isDownloading
            ? `Preparando ${isPdf ? "PDF" : "Excel"}...`
            : `Descargar ${isPdf ? "PDF" : "Excel"}`}
        </button>
      </form>
    </section>
  );
}

function DateField({
  disabled,
  label,
  onChange,
  value,
}: {
  disabled: boolean;
  label: string;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <label className="block max-w-sm">
      <span className="text-sm font-semibold text-slate-800">{label}</span>
      <input
        className="mt-2 h-11 w-full rounded-xl border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        required={label === "Fecha del reporte"}
        type="date"
        value={value}
      />
    </label>
  );
}

function findReport(
  reports: ReportExportDefinition[],
  type: ReportExportType,
): ReportExportDefinition {
  return reports.find((report) => report.type === type) ?? reports[0];
}

function getCurrentMonthValue(): string {
  return getCurrentDateValue().slice(0, 7);
}

function getCurrentDateValue(): string {
  return toLocalISODate(new Date());
}

function getCurrentMonthDates(): { from: string; to: string } {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  return {
    from: toLocalISODate(new Date(year, month, 1)),
    to: toLocalISODate(new Date(year, month + 1, 0)),
  };
}

function toLocalISODate(value: Date): string {
  const localDate = new Date(
    value.getTime() - value.getTimezoneOffset() * 60_000,
  );
  return localDate.toISOString().slice(0, 10);
}

function parseMonthValue(
  value: string,
): { year: number; month: number } | null {
  const match = /^(\d{4})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (!Number.isInteger(year) || month < 1 || month > 12) {
    return null;
  }
  return { year, month };
}

function getErrorMessage(
  possibleError: unknown,
  format: ReportExportFormat,
): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return `No se pudo descargar el archivo ${format === "pdf" ? "PDF" : "Excel"}.`;
}

function formatTopbarDate(value: Date): string {
  return new Intl.DateTimeFormat("es-EC", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(value);
}

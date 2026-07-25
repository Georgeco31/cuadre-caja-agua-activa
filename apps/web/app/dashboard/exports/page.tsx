"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LogoutButton } from "@/components/LogoutButton";
import { ApiError, downloadFile } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
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
  const [error, setError] = useState("");
  const [downloadingFormat, setDownloadingFormat] =
    useState<ReportExportFormat | null>(null);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
  }, [router]);

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
        (downloadError.status === 401 || downloadError.status === 403)
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
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-7 px-4 py-6 sm:px-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Exportaciones del ERP
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Descarga reportes detallados en Excel o resúmenes ejecutivos en
              PDF. Todas las exportaciones son solo lectura.
            </p>
          </div>
          <LogoutButton />
        </header>

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

        {error ? <ErrorMessage message={error} /> : null}

        <button
          className="h-11 self-start rounded-md border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
          disabled={downloadingFormat !== null}
          onClick={useCurrentMonth}
          type="button"
        >
          Restablecer período actual
        </button>

        <p className="rounded-lg border border-water-100 bg-water-50 px-4 py-3 text-sm leading-6 text-water-900">
          Los archivos reflejan los datos registrados en el sistema para el
          período seleccionado y no modifican información.
        </p>
      </div>
    </main>
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
    <section className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-slate-950">
          {isPdf ? "Exportaciones PDF" : "Exportaciones Excel"}
        </h2>
        <p className="mt-1 text-sm leading-6 text-slate-600">
          {isPdf
            ? "Descarga reportes ejecutivos del ERP en formato PDF. Estas exportaciones son solo lectura y no modifican información del sistema."
            : "Descarga reportes detallados del ERP en formato Excel con filtros básicos."}
        </p>
        {isPdf ? (
          <p className="mt-2 text-sm font-medium text-water-800">
            Para reportes detallados use Excel. El PDF está pensado como
            resumen ejecutivo o impresión.
          </p>
        ) : null}
      </div>

      <form
        className="space-y-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
        onSubmit={onSubmit}
      >
        <label className="block">
          <span className="text-sm font-semibold text-slate-800">
            Tipo de reporte
          </span>
          <select
            className="mt-2 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
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
              className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
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
          <p className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
            Este reporte muestra el estado actual del inventario y no requiere
            un período.
          </p>
        ) : null}

        <button
          className={
            isPdf
              ? "h-11 rounded-md bg-slate-800 px-5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              : "h-11 rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
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
        className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
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

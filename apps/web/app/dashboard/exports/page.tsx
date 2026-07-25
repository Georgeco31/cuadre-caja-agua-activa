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
  ReportExportType,
} from "@/types/reportExports";

const REPORTS: ReportExportDefinition[] = [
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

export default function ReportExportsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [reportType, setReportType] =
    useState<ReportExportType>("management-dashboard");
  const [dateFrom, setDateFrom] = useState(() => getCurrentMonthDates().from);
  const [dateTo, setDateTo] = useState(() => getCurrentMonthDates().to);
  const [selectedMonth, setSelectedMonth] = useState(getCurrentMonthValue);
  const [error, setError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
  }, [router]);

  const selectedReport = useMemo(
    () => REPORTS.find((report) => report.type === reportType) ?? REPORTS[0],
    [reportType],
  );

  async function handleDownload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    if (
      selectedReport.filterMode === "dates" &&
      dateFrom &&
      dateTo &&
      dateTo < dateFrom
    ) {
      setError("La fecha hasta no puede ser menor que la fecha desde.");
      return;
    }

    const searchParams = new URLSearchParams();
    let filename = selectedReport.filename;
    if (selectedReport.filterMode === "dates") {
      if (dateFrom) {
        searchParams.set("date_from", dateFrom);
      }
      if (dateTo) {
        searchParams.set("date_to", dateTo);
      }
    }
    if (selectedReport.filterMode === "month") {
      const period = parseMonthValue(selectedMonth);
      if (!period) {
        setError("Selecciona un mes válido.");
        return;
      }
      searchParams.set("year", String(period.year));
      searchParams.set("month", String(period.month));
      filename = `resumen-mensual-${selectedMonth}.xlsx`;
    }

    setIsDownloading(true);
    setError("");
    try {
      const query = searchParams.toString();
      await downloadFile(
        token,
        `/reports/exports/${selectedReport.endpoint}${
          query ? `?${query}` : ""
        }`,
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
      setError(getErrorMessage(downloadError));
    } finally {
      setIsDownloading(false);
    }
  }

  function useCurrentMonth() {
    const currentDates = getCurrentMonthDates();
    setDateFrom(currentDates.from);
    setDateTo(currentDates.to);
    setSelectedMonth(getCurrentMonthValue());
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
              Exportaciones Excel
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Descarga reportes del ERP en formato Excel. Estas exportaciones
              son solo lectura y no modifican información del sistema.
            </p>
          </div>
          <LogoutButton />
        </header>

        <form
          className="space-y-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
          onSubmit={handleDownload}
        >
          <label className="block">
            <span className="text-sm font-semibold text-slate-800">
              Tipo de reporte
            </span>
            <select
              className="mt-2 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
              disabled={isDownloading}
              onChange={(event) =>
                setReportType(event.target.value as ReportExportType)
              }
              value={reportType}
            >
              {REPORTS.map((report) => (
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
                disabled={isDownloading}
                label="Fecha desde"
                onChange={setDateFrom}
                value={dateFrom}
              />
              <DateField
                disabled={isDownloading}
                label="Fecha hasta"
                onChange={setDateTo}
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
                disabled={isDownloading}
                onChange={(event) => setSelectedMonth(event.target.value)}
                required
                type="month"
                value={selectedMonth}
              />
            </label>
          ) : null}

          {selectedReport.filterMode === "none" ? (
            <p className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
              Este reporte muestra el estado actual del inventario y no requiere
              un período.
            </p>
          ) : null}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-11 rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={isDownloading || !token}
              type="submit"
            >
              {isDownloading ? "Preparando Excel..." : "Descargar Excel"}
            </button>
            <button
              className="h-11 rounded-md border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700 disabled:cursor-not-allowed disabled:text-slate-400"
              disabled={isDownloading}
              onClick={useCurrentMonth}
              type="button"
            >
              Usar mes actual
            </button>
          </div>
        </form>

        {error ? <ErrorMessage message={error} /> : null}

        <p className="rounded-lg border border-water-100 bg-water-50 px-4 py-3 text-sm leading-6 text-water-900">
          Los archivos reflejan los datos registrados en el sistema para el
          período seleccionado.
        </p>
      </div>
    </main>
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
    <label className="block">
      <span className="text-sm font-semibold text-slate-800">{label}</span>
      <input
        className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100"
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        type="date"
        value={value}
      />
    </label>
  );
}

function getCurrentMonthValue(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 7);
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

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo descargar el archivo Excel.";
}

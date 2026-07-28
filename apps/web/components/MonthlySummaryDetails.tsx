import {
  formatMoney,
  formatQuantity,
} from "@/components/DailySummaryCards";
import { ReportSection } from "@/components/ui/ReportSection";
import type {
  MonthlyOperationalDailyRow,
  MonthlyOperationalSummary,
} from "@/types/monthlyOperationalSummary";

type MonthlySummaryDetailsProps = {
  report: MonthlyOperationalSummary;
};

const alertLabels: Record<string, string> = {
  cash_session_missing: "Sin cuadre",
  cash_session_open: "Cuadre abierto",
  route_shortage: "Faltante de ruta",
  route_closure_without_cash_receipt: "Cierre sin registro",
  route_cash_receipt_difference: "Diferencia de ruta",
  no_production: "Sin producción",
  no_sales: "Sin ventas",
  routes_loaded_without_closure: "Carga sin cierre",
};

export function MonthlySummaryDetails({
  report,
}: MonthlySummaryDetailsProps) {
  return (
    <div className="min-w-0 space-y-8">
      <ReportSection
        description="Desglose de cantidades producidas y ventas registradas durante el mes."
        eyebrow="Productos"
        id="monthly-products-title"
        title="Producción y ventas por producto"
      >
        <div className="grid min-w-0 gap-5 xl:grid-cols-2">
          <ProductPanel title="Productos producidos">
            {report.production_summary.products.length ? (
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <HeaderCell>Producto</HeaderCell>
                    <HeaderCell>Producido</HeaderCell>
                    <HeaderCell>Merma</HeaderCell>
                    <HeaderCell>Neto</HeaderCell>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {report.production_summary.products.map((product) => (
                    <tr key={product.product_id}>
                      <Cell className="font-medium text-slate-950">
                        {product.product_name_snapshot}
                      </Cell>
                      <Cell>
                        {formatQuantity(product.quantity_produced)}
                      </Cell>
                      <Cell>{formatQuantity(product.quantity_waste)}</Cell>
                      <Cell>{formatQuantity(product.quantity_net)}</Cell>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState message="No hay productos producidos en este mes." />
            )}
          </ProductPanel>

          <ProductPanel title="Productos vendidos">
            {report.sales_summary.products_sold.length ? (
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <HeaderCell>Producto</HeaderCell>
                    <HeaderCell>Cantidad</HeaderCell>
                    <HeaderCell>Monto</HeaderCell>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {report.sales_summary.products_sold.map((product) => (
                    <tr key={product.product_id}>
                      <Cell className="font-medium text-slate-950">
                        {product.product_name_snapshot}
                      </Cell>
                      <Cell>{formatQuantity(product.quantity)}</Cell>
                      <Cell>{formatMoney(product.amount)}</Cell>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState message="No hay productos vendidos en este mes." />
            )}
          </ProductPanel>
        </div>
      </ReportSection>

      <ReportSection
        description={`El reporte incluye los ${report.period.days_in_month} días del mes, incluso cuando no hubo registros.`}
        eyebrow="Detalle diario"
        id="monthly-days-title"
        title="Comportamiento por día"
      >
        <div className="space-y-3 md:hidden">
          {report.daily_rows.map((row) => (
            <DailyCard key={row.date} row={row} />
          ))}
        </div>

        <div className="hidden max-w-full overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-card md:block">
          <table className="w-full min-w-[1480px] border-collapse text-left text-sm">
            <thead className="bg-slate-100 text-slate-700">
              <tr>
                <HeaderCell>Fecha</HeaderCell>
                <HeaderCell>Cuadre</HeaderCell>
                <HeaderCell>Contado</HeaderCell>
                <HeaderCell>Gastos</HeaderCell>
                <HeaderCell>Total final</HeaderCell>
                <HeaderCell>Producción neta</HeaderCell>
                <HeaderCell>Venta contado</HeaderCell>
                <HeaderCell>Venta crédito</HeaderCell>
                <HeaderCell>Cobros</HeaderCell>
                <HeaderCell>Entregado rutas</HeaderCell>
                <HeaderCell>Registrado en caja</HeaderCell>
                <HeaderCell>Alertas</HeaderCell>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {report.daily_rows.map((row) => (
                <tr className="align-top text-slate-700" key={row.date}>
                  <Cell className="whitespace-nowrap font-medium text-slate-950">
                    {formatDate(row.date)}
                  </Cell>
                  <Cell>{row.cash_session_exists ? "Sí" : "No"}</Cell>
                  <MoneyCell value={row.cash_total_counted} />
                  <MoneyCell value={row.cash_total_expenses} />
                  <MoneyCell value={row.cash_total_final} />
                  <Cell>{formatQuantity(row.production_quantity_net)}</Cell>
                  <MoneyCell value={row.cash_sales_total} />
                  <MoneyCell value={row.credit_sales_total} />
                  <MoneyCell value={row.payments_total} />
                  <MoneyCell value={row.route_delivered_cash_total} />
                  <MoneyCell value={row.route_cash_registered_total} />
                  <Cell className="min-w-64">
                    <AlertBadges codes={row.alert_codes} />
                  </Cell>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ReportSection>
    </div>
  );
}

function DailyCard({ row }: { row: MonthlyOperationalDailyRow }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-slate-950">
            {formatDate(row.date)}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {row.cash_session_exists ? "Con cuadre de caja" : "Sin cuadre"}
          </p>
        </div>
        <span
          className={
            row.alerts_count
              ? "rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-800"
              : "rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800"
          }
        >
          {row.alerts_count} alerta(s)
        </span>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
        <DailyMetric label="Contado" value={formatMoney(row.cash_total_counted)} />
        <DailyMetric label="Gastos" value={formatMoney(row.cash_total_expenses)} />
        <DailyMetric
          label="Producción neta"
          value={formatQuantity(row.production_quantity_net)}
        />
        <DailyMetric
          label="Ventas"
          value={formatMoney(
            String(
              Number(row.cash_sales_total) + Number(row.credit_sales_total),
            ),
          )}
        />
        <DailyMetric label="Cobros" value={formatMoney(row.payments_total)} />
        <DailyMetric
          label="Ruta en caja"
          value={formatMoney(row.route_cash_registered_total)}
        />
      </dl>

      {row.alert_codes.length ? (
        <div className="mt-4 border-t border-slate-100 pt-3">
          <AlertBadges codes={row.alert_codes} />
        </div>
      ) : null}
    </article>
  );
}

function DailyMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="mt-0.5 break-words font-medium tabular-nums text-slate-900">
        {value}
      </dd>
    </div>
  );
}

function AlertBadges({ codes }: { codes: string[] }) {
  if (!codes.length) {
    return <span className="text-xs text-emerald-700">Sin alertas</span>;
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {codes.map((code) => (
        <span
          className="rounded-full bg-amber-100 px-2 py-1 text-xs font-medium text-amber-800"
          key={code}
        >
          {alertLabels[code] ?? code}
        </span>
      ))}
    </div>
  );
}

function ProductPanel({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <article className="min-w-0 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card">
      <h3 className="border-b border-slate-200 bg-slate-50/80 px-4 py-3.5 font-semibold text-slate-950">
        {title}
      </h3>
      <div className="max-w-full overflow-x-auto">{children}</div>
    </article>
  );
}

function HeaderCell({ children }: { children: React.ReactNode }) {
  return (
    <th className="whitespace-nowrap px-3 py-3 font-semibold" scope="col">
      {children}
    </th>
  );
}

function Cell({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <td className={`px-3 py-4 ${className}`}>{children}</td>;
}

function MoneyCell({ value }: { value: string }) {
  return (
    <Cell className="whitespace-nowrap text-right tabular-nums">
      {formatMoney(value)}
    </Cell>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="px-4 py-7 text-center">
      <p className="text-sm font-medium text-slate-700">Sin registros</p>
      <p className="mt-1 text-sm text-slate-500">{message}</p>
    </div>
  );
}

function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  return year && month && day ? `${day}/${month}/${year}` : value;
}

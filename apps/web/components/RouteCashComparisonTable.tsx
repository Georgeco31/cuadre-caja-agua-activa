import type {
  RouteCashComparisonReport,
  RouteCashComparisonRow,
  RouteCashComparisonStatus,
} from "@/types/routeCashComparison";

type RouteCashComparisonTableProps = {
  report: RouteCashComparisonReport;
};

const summaryItems = [
  ["Esperado por rutas", "route_expected_cash_total"],
  ["Entregado por rutas", "route_delivered_cash_total"],
  ["Diferencia interna de rutas", "route_difference_total"],
  ["Total contado en caja", "cash_total_counted"],
  ["Gastos de caja", "cash_total_expenses"],
  ["Total final de caja", "cash_total_final"],
  ["Diferencia caja vs rutas", "cash_vs_route_delivered_difference"],
] as const;

const statusLabels: Record<RouteCashComparisonStatus, string> = {
  no_cash_session: "Sin cuadre de caja",
  no_route_closures: "Sin rutas cerradas",
  matched: "Coincide",
  cash_higher_than_routes: "Caja mayor que rutas",
  routes_higher_than_cash: "Rutas mayor que caja",
};

const statusStyles: Record<RouteCashComparisonStatus, string> = {
  no_cash_session: "border-amber-200 bg-amber-50 text-amber-800",
  no_route_closures: "border-slate-200 bg-slate-100 text-slate-700",
  matched: "border-emerald-200 bg-emerald-50 text-emerald-800",
  cash_higher_than_routes: "border-sky-200 bg-sky-50 text-sky-800",
  routes_higher_than_cash: "border-orange-200 bg-orange-50 text-orange-800",
};

export function RouteCashComparisonTable({
  report,
}: RouteCashComparisonTableProps) {
  return (
    <div className="space-y-6">
      <section
        aria-labelledby="route-cash-summary-title"
        className="space-y-4"
      >
        <div>
          <p className="text-sm font-medium text-water-700">
            {report.totals.route_closures_count} cierres activos en el rango
          </p>
          <h2
            className="mt-1 text-xl font-semibold text-slate-950"
            id="route-cash-summary-title"
          >
            Resumen general
          </h2>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {summaryItems.map(([label, key]) => (
            <div
              className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
              key={key}
            >
              <p className="text-sm text-slate-600">{label}</p>
              <p className="mt-2 text-xl font-semibold text-slate-950">
                {formatMoney(report.totals[key])}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section
        aria-labelledby="route-cash-rows-title"
        className="space-y-4"
      >
        <div>
          <p className="text-sm font-medium text-water-700">Detalle diario</p>
          <h2
            className="mt-1 text-xl font-semibold text-slate-950"
            id="route-cash-rows-title"
          >
            Comparación por fecha
          </h2>
        </div>

        {report.rows.length === 0 ? (
          <p className="rounded-lg border border-slate-200 bg-white px-4 py-5 text-sm text-slate-600 shadow-sm">
            No hay cuadres de caja ni cierres de ruta activos para las fechas
            seleccionadas.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="min-w-[1500px] w-full border-collapse text-left text-sm">
              <thead className="bg-slate-100 text-slate-700">
                <tr>
                  <HeaderCell>Fecha</HeaderCell>
                  <HeaderCell>Cierres</HeaderCell>
                  <HeaderCell>Esperado rutas</HeaderCell>
                  <HeaderCell>Entregado rutas</HeaderCell>
                  <HeaderCell>Diferencia rutas</HeaderCell>
                  <HeaderCell>Cuadre de caja</HeaderCell>
                  <HeaderCell>Total contado</HeaderCell>
                  <HeaderCell>Gastos caja</HeaderCell>
                  <HeaderCell>Total final</HeaderCell>
                  <HeaderCell>Diferencia caja vs rutas</HeaderCell>
                  <HeaderCell>Estado</HeaderCell>
                  <HeaderCell>Detalle</HeaderCell>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {report.rows.map((row) => (
                  <tr className="align-top text-slate-700" key={row.date}>
                    <Cell className="font-medium text-slate-950">
                      {formatDate(row.date)}
                    </Cell>
                    <Cell>{row.route_closures_count}</Cell>
                    <MoneyCell value={row.route_expected_cash_total} />
                    <MoneyCell value={row.route_delivered_cash_total} />
                    <MoneyCell value={row.route_difference_total} />
                    <Cell>{getCashSessionLabel(row)}</Cell>
                    <MoneyCell value={row.cash_total_counted} />
                    <MoneyCell value={row.cash_total_expenses} />
                    <MoneyCell value={row.cash_total_final} />
                    <MoneyCell
                      value={row.cash_vs_route_delivered_difference}
                    />
                    <Cell>
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${statusStyles[row.comparison_status]}`}
                      >
                        {statusLabels[row.comparison_status]}
                      </span>
                    </Cell>
                    <Cell className="min-w-64">
                      <RouteClosureDetails row={row} />
                    </Cell>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function RouteClosureDetails({ row }: { row: RouteCashComparisonRow }) {
  if (!row.has_route_closures) {
    return <span className="text-slate-500">Sin cierres activos</span>;
  }

  return (
    <details>
      <summary className="cursor-pointer font-semibold text-water-700 hover:text-water-500">
        Ver {row.route_closures_count}{" "}
        {row.route_closures_count === 1 ? "cierre" : "cierres"}
      </summary>
      <div className="mt-3 space-y-3">
        {row.route_closures.map((closure) => (
          <div
            className="rounded-md border border-slate-200 bg-slate-50 p-3"
            key={closure.id}
          >
            <p className="font-semibold text-slate-950">
              {closure.route_name_snapshot}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {closure.closure_number} · {closure.vehicle_name_snapshot}
            </p>
            <dl className="mt-2 grid grid-cols-3 gap-2 text-xs">
              <div>
                <dt className="text-slate-500">Esperado</dt>
                <dd className="mt-0.5 font-medium text-slate-800">
                  {formatMoney(closure.expected_cash_total)}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Entregado</dt>
                <dd className="mt-0.5 font-medium text-slate-800">
                  {formatMoney(closure.delivered_cash_total)}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Diferencia</dt>
                <dd className="mt-0.5 font-medium text-slate-800">
                  {formatMoney(closure.difference_amount)}
                </dd>
              </div>
            </dl>
          </div>
        ))}
      </div>
    </details>
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
  return <Cell className="whitespace-nowrap">{formatMoney(value)}</Cell>;
}

function getCashSessionLabel(row: RouteCashComparisonRow): string {
  if (!row.has_cash_session) {
    return "No existe";
  }

  const status =
    row.cash_session_status === "closed"
      ? "Cerrado"
      : row.cash_session_status === "corrected"
        ? "Corregido"
        : "Abierto";
  return `Sí · ${status}`;
}

function formatMoney(value: string): string {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return `$${value}`;
  }

  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(numericValue);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

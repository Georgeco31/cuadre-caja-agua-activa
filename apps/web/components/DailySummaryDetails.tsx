import {
  formatMoney,
  formatQuantity,
  formatStatus,
} from "@/components/DailySummaryCards";
import type { DailyOperationalSummary } from "@/types/dailyOperationalSummary";

type DailySummaryDetailsProps = {
  report: DailyOperationalSummary;
};

export function DailySummaryDetails({ report }: DailySummaryDetailsProps) {
  return (
    <section aria-labelledby="daily-details-title" className="space-y-5">
      <div>
        <p className="text-sm font-medium text-water-700">Detalle</p>
        <h2
          className="mt-1 text-xl font-semibold text-slate-950"
          id="daily-details-title"
        >
          Registros resumidos
        </h2>
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <DetailPanel title="Productos producidos">
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
                    <BodyCell>{product.product_name_snapshot}</BodyCell>
                    <BodyCell>
                      {formatQuantity(product.quantity_produced)}
                    </BodyCell>
                    <BodyCell>
                      {formatQuantity(product.quantity_waste)}
                    </BodyCell>
                    <BodyCell>{formatQuantity(product.quantity_net)}</BodyCell>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyDetail message="No hay productos producidos para esta fecha." />
          )}
        </DetailPanel>

        <DetailPanel title="Productos vendidos">
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
                    <BodyCell>{product.product_name_snapshot}</BodyCell>
                    <BodyCell>{formatQuantity(product.quantity)}</BodyCell>
                    <BodyCell>{formatMoney(product.amount)}</BodyCell>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyDetail message="No hay productos vendidos para esta fecha." />
          )}
        </DetailPanel>

        <DetailPanel title="Cargas de ruta">
          {report.route_loads_summary.loads.length ? (
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <HeaderCell>Carga</HeaderCell>
                  <HeaderCell>Ruta / vehículo</HeaderCell>
                  <HeaderCell>Cantidad</HeaderCell>
                  <HeaderCell>Estado</HeaderCell>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {report.route_loads_summary.loads.map((load) => (
                  <tr key={load.id}>
                    <BodyCell>{load.load_number}</BodyCell>
                    <BodyCell>
                      {load.route_name}
                      <span className="block text-xs text-slate-500">
                        {load.vehicle_name}
                      </span>
                    </BodyCell>
                    <BodyCell>
                      {formatQuantity(load.total_quantity_loaded)}
                    </BodyCell>
                    <BodyCell>{formatStatus(load.status)}</BodyCell>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyDetail message="No hay cargas de ruta para esta fecha." />
          )}
        </DetailPanel>

        <DetailPanel title="Retornos de ruta">
          {report.route_returns_summary.returns.length ? (
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <HeaderCell>Retorno</HeaderCell>
                  <HeaderCell>Ruta / vehículo</HeaderCell>
                  <HeaderCell>Cantidad</HeaderCell>
                  <HeaderCell>Estado</HeaderCell>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {report.route_returns_summary.returns.map((routeReturn) => (
                  <tr key={routeReturn.id}>
                    <BodyCell>{routeReturn.return_number}</BodyCell>
                    <BodyCell>
                      {routeReturn.route_name}
                      <span className="block text-xs text-slate-500">
                        {routeReturn.vehicle_name}
                      </span>
                    </BodyCell>
                    <BodyCell>
                      {formatQuantity(routeReturn.total_quantity_returned)}
                    </BodyCell>
                    <BodyCell>{formatStatus(routeReturn.status)}</BodyCell>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyDetail message="No hay retornos de ruta para esta fecha." />
          )}
        </DetailPanel>

        <DetailPanel title="Cierres de ruta">
          {report.route_closures_summary.closures.length ? (
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <HeaderCell>Cierre</HeaderCell>
                  <HeaderCell>Ruta / vehículo</HeaderCell>
                  <HeaderCell>Esperado</HeaderCell>
                  <HeaderCell>Entregado</HeaderCell>
                  <HeaderCell>Diferencia</HeaderCell>
                  <HeaderCell>Estado</HeaderCell>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {report.route_closures_summary.closures.map((closure) => (
                  <tr key={closure.id}>
                    <BodyCell>{closure.closure_number}</BodyCell>
                    <BodyCell>
                      {closure.route_name_snapshot}
                      <span className="block text-xs text-slate-500">
                        {closure.vehicle_name_snapshot}
                      </span>
                    </BodyCell>
                    <BodyCell>
                      {formatMoney(closure.expected_cash_total)}
                    </BodyCell>
                    <BodyCell>
                      {formatMoney(closure.delivered_cash_total)}
                    </BodyCell>
                    <BodyCell>
                      {formatMoney(closure.difference_amount)}
                    </BodyCell>
                    <BodyCell>{formatStatus(closure.status)}</BodyCell>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyDetail message="No hay cierres de ruta para esta fecha." />
          )}
        </DetailPanel>

        <DetailPanel title="Dinero de ruta en caja">
          {report.route_cash_receipts_summary.receipts.length ? (
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <HeaderCell>Registro</HeaderCell>
                  <HeaderCell>Cierre / ruta</HeaderCell>
                  <HeaderCell>Entregado</HeaderCell>
                  <HeaderCell>Recibido</HeaderCell>
                  <HeaderCell>Diferencia</HeaderCell>
                  <HeaderCell>Estado</HeaderCell>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {report.route_cash_receipts_summary.receipts.map((receipt) => (
                  <tr key={receipt.id}>
                    <BodyCell>{receipt.receipt_number}</BodyCell>
                    <BodyCell>
                      {receipt.closure_number_snapshot}
                      <span className="block text-xs text-slate-500">
                        {receipt.route_name_snapshot}
                      </span>
                    </BodyCell>
                    <BodyCell>
                      {formatMoney(receipt.delivered_cash_total)}
                    </BodyCell>
                    <BodyCell>{formatMoney(receipt.received_amount)}</BodyCell>
                    <BodyCell>
                      {formatMoney(receipt.difference_amount)}
                    </BodyCell>
                    <BodyCell>{formatStatus(receipt.status)}</BodyCell>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyDetail message="No hay dinero de ruta registrado en caja para esta fecha." />
          )}
        </DetailPanel>
      </div>
    </section>
  );
}

type DetailPanelProps = {
  title: string;
  children: React.ReactNode;
};

function DetailPanel({ title, children }: DetailPanelProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <h3 className="border-b border-slate-200 px-4 py-3 text-base font-semibold text-slate-950">
        {title}
      </h3>
      <div className="overflow-x-auto">{children}</div>
    </div>
  );
}

function HeaderCell({ children }: { children: React.ReactNode }) {
  return (
    <th className="whitespace-nowrap px-4 py-3 font-medium" scope="col">
      {children}
    </th>
  );
}

function BodyCell({ children }: { children: React.ReactNode }) {
  return (
    <td className="whitespace-nowrap px-4 py-3 text-slate-700">{children}</td>
  );
}

function EmptyDetail({ message }: { message: string }) {
  return <p className="px-4 py-5 text-sm text-slate-500">{message}</p>;
}

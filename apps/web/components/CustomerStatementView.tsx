import {
  CREDIT_PAYMENT_METHOD_LABELS,
  CREDIT_PAYMENT_STATUS_LABELS,
} from "@/types/creditPayment";
import type { CustomerStatement } from "@/types/receivable";

type CustomerStatementViewProps = {
  statement: CustomerStatement;
  includePaid: boolean;
};

export function CustomerStatementView({
  statement,
  includePaid,
}: CustomerStatementViewProps) {
  return (
    <>
      <section className="grid gap-4 border-y border-slate-200 py-5 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <p className="text-xs font-semibold uppercase text-slate-500">
            Cliente
          </p>
          <p className="mt-1 font-semibold text-slate-950">
            {statement.customer_name}
          </p>
          <p className="mt-1 text-sm text-slate-600">
            {statement.primary_phone ?? "Sin teléfono"}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase text-slate-500">
            Sector
          </p>
          <p className="mt-1 font-semibold text-slate-950">
            {statement.sector ?? "Sin sector"}
          </p>
          <p className="mt-1 text-sm text-slate-600">
            {statement.is_active ? "Cliente activo" : "Cliente inactivo"}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase text-slate-500">
            Total vendido
          </p>
          <p className="mt-1 text-xl font-semibold text-slate-950">
            {formatMoney(statement.total_credit_sales)}
          </p>
          <p className="mt-1 text-sm text-emerald-700">
            Pagado: {formatMoney(statement.total_paid)}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase text-slate-500">
            Saldo pendiente
          </p>
          <p className="mt-1 text-xl font-semibold text-amber-700">
            {formatMoney(statement.total_balance)}
          </p>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="text-lg font-semibold text-slate-950">
            Ventas a crédito
          </h2>
          <span className="text-sm text-slate-500">
            {statement.credit_sales.length}
          </span>
        </div>

        {statement.credit_sales.length === 0 ? (
          <p className="px-4 py-8 text-sm text-slate-600">
            {includePaid
              ? "No hay ventas a crédito activas en el rango seleccionado."
              : "No hay ventas pendientes en el rango seleccionado."}
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px] border-collapse text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3 font-medium">Venta</th>
                  <th className="px-4 py-3 font-medium">Fecha</th>
                  <th className="px-4 py-3 font-medium">Vencimiento</th>
                  <th className="px-4 py-3 text-right font-medium">Total</th>
                  <th className="px-4 py-3 text-right font-medium">Pagado</th>
                  <th className="px-4 py-3 text-right font-medium">Saldo</th>
                  <th className="px-4 py-3 font-medium">Crédito</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {statement.credit_sales.map((sale) => (
                  <tr key={sale.sale_id}>
                    <td className="px-4 py-3 align-top font-medium text-slate-950">
                      {sale.sale_number}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {formatDate(sale.sale_date)}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {sale.due_date ? formatDate(sale.due_date) : "Sin fecha"}
                    </td>
                    <td className="px-4 py-3 text-right align-top text-slate-700">
                      {formatMoney(sale.total_amount)}
                    </td>
                    <td className="px-4 py-3 text-right align-top text-emerald-700">
                      {formatMoney(sale.paid_amount)}
                    </td>
                    <td className="px-4 py-3 text-right align-top font-semibold text-amber-700">
                      {formatMoney(sale.balance_amount)}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          sale.credit_status === "paid"
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700"
                        }
                      >
                        {sale.credit_status === "paid" ? "Pagada" : "Pendiente"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="text-lg font-semibold text-slate-950">
            Pagos y abonos
          </h2>
          <span className="text-sm text-slate-500">
            {statement.payments.length}
          </span>
        </div>

        {statement.payments.length === 0 ? (
          <p className="px-4 py-8 text-sm text-slate-600">
            No hay pagos registrados para las ventas del rango seleccionado.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px] border-collapse text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3 font-medium">Fecha</th>
                  <th className="px-4 py-3 font-medium">Venta</th>
                  <th className="px-4 py-3 text-right font-medium">Monto</th>
                  <th className="px-4 py-3 font-medium">Método</th>
                  <th className="px-4 py-3 font-medium">Estado</th>
                  <th className="px-4 py-3 font-medium">Observación</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {statement.payments.map((payment) => (
                  <tr key={payment.payment_id}>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {formatDate(payment.payment_date)}
                    </td>
                    <td className="px-4 py-3 align-top font-medium text-slate-950">
                      {payment.sale_number}
                    </td>
                    <td className="px-4 py-3 text-right align-top font-semibold text-slate-950">
                      {formatMoney(payment.amount)}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {CREDIT_PAYMENT_METHOD_LABELS[payment.payment_method]}
                    </td>
                    <td className="px-4 py-3 align-top">
                      <span
                        className={
                          payment.status === "active"
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {CREDIT_PAYMENT_STATUS_LABELS[payment.status]}
                      </span>
                    </td>
                    <td className="max-w-80 px-4 py-3 align-top text-slate-700">
                      <p>{payment.notes ?? "Sin observación"}</p>
                      {payment.status === "voided" ? (
                        <p className="mt-1 text-xs text-red-700">
                          Motivo: {payment.void_reason}
                        </p>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(
    new Date(`${value}T00:00:00`),
  );
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

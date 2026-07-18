import {
  CREDIT_PAYMENT_METHOD_LABELS,
  CREDIT_PAYMENT_STATUS_LABELS,
  type CreditPayment,
} from "@/types/creditPayment";

type CreditPaymentListProps = {
  payments: CreditPayment[];
  isLoading?: boolean;
  hasCustomerFilter?: boolean;
  voidingPaymentId?: number | null;
  onVoid: (payment: CreditPayment) => void;
};

export function CreditPaymentList({
  payments,
  isLoading = false,
  hasCustomerFilter = false,
  voidingPaymentId = null,
  onVoid,
}: CreditPaymentListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Historial de abonos
        </h2>
        <span className="text-sm text-slate-500">{payments.length}</span>
      </div>

      {isLoading ? (
        <p className="px-4 py-8 text-sm text-slate-600">Cargando abonos...</p>
      ) : payments.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasCustomerFilter
            ? "No hay abonos registrados para el cliente seleccionado."
            : "Todavía no hay abonos registrados."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1120px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Venta</th>
                <th className="px-4 py-3 font-medium">Cliente</th>
                <th className="px-4 py-3 text-right font-medium">Monto</th>
                <th className="px-4 py-3 font-medium">Método</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 font-medium">Observación</th>
                <th className="px-4 py-3 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {payments.map((payment) => {
                const isVoiding = voidingPaymentId === payment.id;
                return (
                  <tr key={payment.id}>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {formatDate(payment.payment_date)}
                    </td>
                    <td className="px-4 py-3 align-top font-medium text-slate-950">
                      {payment.sale_number}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {payment.customer_name}
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
                    <td className="max-w-72 px-4 py-3 align-top text-slate-700">
                      <p>{payment.notes ?? "Sin observación"}</p>
                      {payment.status === "voided" ? (
                        <p className="mt-1 text-xs text-red-700">
                          Motivo: {payment.void_reason}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top">
                      {payment.status === "active" ? (
                        <button
                          className="font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                          type="button"
                          disabled={isVoiding}
                          onClick={() => onVoid(payment)}
                        >
                          {isVoiding ? "Anulando..." : "Anular"}
                        </button>
                      ) : (
                        <span className="text-slate-400">Sin acciones</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
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

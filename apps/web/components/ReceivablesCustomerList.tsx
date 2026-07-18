import Link from "next/link";

import type { ReceivableCustomer } from "@/types/receivable";

type ReceivablesCustomerListProps = {
  customers: ReceivableCustomer[];
  hasActiveFilters?: boolean;
  isLoading?: boolean;
};

export function ReceivablesCustomerList({
  customers,
  hasActiveFilters = false,
  isLoading = false,
}: ReceivablesCustomerListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Cartera por cliente
        </h2>
        <span className="text-sm text-slate-500">{customers.length}</span>
      </div>

      {isLoading ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          Actualizando cartera...
        </p>
      ) : customers.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron clientes con los filtros seleccionados."
            : "Todavía no hay clientes con movimientos de crédito."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1180px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Cliente</th>
                <th className="px-4 py-3 font-medium">Teléfono</th>
                <th className="px-4 py-3 font-medium">Sector</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3 text-right font-medium">
                  Total crédito
                </th>
                <th className="px-4 py-3 text-right font-medium">Pagado</th>
                <th className="px-4 py-3 text-right font-medium">Saldo</th>
                <th className="px-4 py-3 text-right font-medium">
                  Ventas pendientes
                </th>
                <th className="px-4 py-3 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {customers.map((customer) => (
                <tr key={customer.customer_id}>
                  <td className="px-4 py-3 align-top font-medium text-slate-950">
                    {customer.customer_name}
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {customer.primary_phone ?? "Sin teléfono"}
                  </td>
                  <td className="px-4 py-3 align-top text-slate-700">
                    {customer.sector ?? "Sin sector"}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <span
                      className={
                        customer.is_active
                          ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                          : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                      }
                    >
                      {customer.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right align-top text-slate-700">
                    {formatMoney(customer.total_credit_sales)}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-emerald-700">
                    {formatMoney(customer.total_paid)}
                  </td>
                  <td className="px-4 py-3 text-right align-top font-semibold text-amber-700">
                    {formatMoney(customer.total_balance)}
                  </td>
                  <td className="px-4 py-3 text-right align-top text-slate-700">
                    {customer.pending_sales_count}
                  </td>
                  <td className="px-4 py-3 align-top">
                    <Link
                      className="font-semibold text-water-700 hover:text-water-500"
                      href={`/dashboard/receivables/reports/${customer.customer_id}`}
                    >
                      Ver estado de cuenta
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function formatMoney(value: string): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : "$0.00";
}

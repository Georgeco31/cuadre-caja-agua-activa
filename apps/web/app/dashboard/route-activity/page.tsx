"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  getRouteCommercialActivity,
  listRouteLoads,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import {
  CREDIT_PAYMENT_METHOD_LABELS,
  type CreditPayment,
} from "@/types/creditPayment";
import type { RouteCommercialActivity } from "@/types/routeActivity";
import {
  ROUTE_LOAD_STATUS_LABELS,
  type RouteLoad,
} from "@/types/routeLoad";
import type { Sale } from "@/types/sale";

export default function RouteActivityPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [loads, setLoads] = useState<RouteLoad[]>([]);
  const [selectedLoadId, setSelectedLoadId] = useState("");
  const [activity, setActivity] = useState<RouteCommercialActivity | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingActivity, setIsLoadingActivity] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    loadInitialData(storedToken);
  }, [router]);

  async function loadInitialData(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const loadedLoads = await listRouteLoads(activeToken);
      setLoads(loadedLoads);
      if (loadedLoads.length > 0) {
        const firstLoadId = loadedLoads[0].id;
        setSelectedLoadId(String(firstLoadId));
        await loadActivity(activeToken, firstLoadId);
      }
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setIsLoading(false);
    }
  }

  async function loadActivity(activeToken: string, loadId: number) {
    setIsLoadingActivity(true);
    setError("");
    try {
      setActivity(await getRouteCommercialActivity(activeToken, loadId));
    } catch (loadError) {
      setActivity(null);
      handleError(loadError);
    } finally {
      setIsLoadingActivity(false);
    }
  }

  function handleError(possibleError: unknown) {
    if (
      possibleError instanceof ApiError &&
      (possibleError.status === 401 || possibleError.status === 403)
    ) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(
      possibleError instanceof Error
        ? possibleError.message
        : "No se pudo completar la solicitud.",
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Actividad de ruta
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Consulta ventas y cobros asociados a una carga de ruta.
            </p>
          </div>
          <LogoutButton />
        </header>

        <p className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Este módulo solo consulta actividad comercial asociada a la ruta.
          Todavía no cierra ruta ni modifica caja.
        </p>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <LoadingState label="Cargando actividad de rutas..." />
        ) : (
          <>
            <section className="border-b border-slate-200 pb-6">
              <label className="block max-w-2xl">
                <span className="text-sm font-medium text-slate-700">
                  Carga de ruta
                </span>
                <select
                  className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100"
                  value={selectedLoadId}
                  disabled={isLoadingActivity || loads.length === 0}
                  onChange={(event) => {
                    const value = event.target.value;
                    setSelectedLoadId(value);
                    if (token && value) {
                      loadActivity(token, Number(value));
                    } else {
                      setActivity(null);
                    }
                  }}
                >
                  <option value="">Seleccionar carga</option>
                  {loads.map((load) => (
                    <option key={load.id} value={load.id}>
                      {load.load_number} · {load.route_name} · {load.vehicle_name}
                      {load.status === "voided" ? " · Anulada" : ""}
                    </option>
                  ))}
                </select>
              </label>
              {loads.length === 0 ? (
                <p className="mt-3 text-sm text-slate-600">
                  Todavía no hay cargas de ruta registradas.
                </p>
              ) : null}
            </section>

            {isLoadingActivity ? (
              <LoadingState label="Consultando actividad comercial..." />
            ) : activity ? (
              <ActivityDetail activity={activity} />
            ) : loads.length > 0 ? (
              <p className="py-8 text-sm text-slate-600">
                Selecciona una carga para consultar su actividad comercial.
              </p>
            ) : null}
          </>
        )}
      </div>
    </main>
  );
}

function ActivityDetail({ activity }: { activity: RouteCommercialActivity }) {
  return (
    <div className="space-y-6">
      <section className="grid gap-4 border-b border-slate-200 pb-6 sm:grid-cols-2 lg:grid-cols-5">
        <Summary label="Carga" value={activity.load_number} />
        <Summary label="Fecha" value={formatDate(activity.load_date)} />
        <Summary label="Ruta" value={activity.route_name} />
        <Summary label="Vehículo" value={activity.vehicle_name} />
        <Summary
          label="Estado"
          value={ROUTE_LOAD_STATUS_LABELS[activity.status]}
        />
      </section>

      <section aria-labelledby="route-totals-title">
        <h2 id="route-totals-title" className="text-lg font-semibold text-slate-950">
          Resumen comercial
        </h2>
        <div className="mt-3 grid gap-4 border-y border-slate-200 py-5 sm:grid-cols-2 lg:grid-cols-4">
          <Amount label="Ventas de contado" value={activity.cash_sales_total} />
          <Amount label="Ventas a crédito" value={activity.credit_sales_total} />
          <Amount label="Cobros y abonos" value={activity.payments_total} />
          <Amount
            label="Efectivo esperado"
            value={activity.expected_cash_total}
            emphasized
          />
        </div>
      </section>

      <SalesTable title="Ventas de contado" sales={activity.cash_sales} />
      <SalesTable title="Ventas a crédito" sales={activity.credit_sales} />
      <PaymentsTable payments={activity.payments} />

      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="text-lg font-semibold text-slate-950">
            Productos vendidos
          </h2>
          <span className="text-sm text-slate-500">
            {activity.products_sold.length}
          </span>
        </div>
        {activity.products_sold.length === 0 ? (
          <EmptyRow text="No hay productos vendidos asociados a esta carga." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] border-collapse text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3 font-medium">Producto</th>
                  <th className="px-4 py-3 text-right font-medium">Cantidad</th>
                  <th className="px-4 py-3 text-right font-medium">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activity.products_sold.map((product) => (
                  <tr key={product.product_id}>
                    <td className="px-4 py-3 font-medium text-slate-950">
                      {product.product_name_snapshot}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-700">
                      {formatQuantity(product.total_quantity)}
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-slate-950">
                      {formatMoney(product.total_amount)}
                    </td>
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

function SalesTable({ title, sales }: { title: string; sales: Sale[] }) {
  return (
    <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
        <span className="text-sm text-slate-500">{sales.length}</span>
      </div>
      {sales.length === 0 ? (
        <EmptyRow text="No hay ventas asociadas a esta carga." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Venta</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Cliente</th>
                <th className="px-4 py-3 text-right font-medium">Productos</th>
                <th className="px-4 py-3 text-right font-medium">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td className="px-4 py-3 font-medium text-slate-950">
                    {sale.sale_number}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {formatDate(sale.sale_date)}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {sale.customer_name_snapshot}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-700">
                    {sale.items.length}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-950">
                    {formatMoney(sale.total_amount)}
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

function PaymentsTable({ payments }: { payments: CreditPayment[] }) {
  return (
    <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">Cobros y abonos</h2>
        <span className="text-sm text-slate-500">{payments.length}</span>
      </div>
      {payments.length === 0 ? (
        <EmptyRow text="No hay cobros asociados a esta carga." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Venta</th>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Cliente</th>
                <th className="px-4 py-3 font-medium">Método</th>
                <th className="px-4 py-3 text-right font-medium">Monto</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {payments.map((payment) => (
                <tr key={payment.id}>
                  <td className="px-4 py-3 font-medium text-slate-950">
                    {payment.sale_number}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {formatDate(payment.payment_date)}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {payment.customer_name}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {CREDIT_PAYMENT_METHOD_LABELS[payment.payment_method]}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-950">
                    {formatMoney(payment.amount)}
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

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <dl>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-slate-950">{value}</dd>
    </dl>
  );
}

function Amount({
  label,
  value,
  emphasized = false,
}: {
  label: string;
  value: string;
  emphasized?: boolean;
}) {
  return (
    <dl>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd
        className={`mt-1 text-2xl font-semibold ${emphasized ? "text-water-700" : "text-slate-950"}`}
      >
        {formatMoney(value)}
      </dd>
    </dl>
  );
}

function EmptyRow({ text }: { text: string }) {
  return <p className="px-4 py-8 text-sm text-slate-600">{text}</p>;
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

function formatQuantity(value: string): string {
  return value.replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1");
}

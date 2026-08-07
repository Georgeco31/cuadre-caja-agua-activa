"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  getSimpleRouteAnalytics,
  listSimpleRoutes,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import {
  SIMPLE_ROUTE_SETTLEMENT_LABELS,
  SIMPLE_ROUTE_STATUS_LABELS,
  type SimpleRouteAnalytics,
  type SimpleRouteListItem,
  type SimpleRouteStatus,
} from "@/types/simpleRoute";

export default function SimpleRoutesPage() {
  const router = useRouter();
  const isAdmin = useIsAdminAuditor();
  const [token, setToken] = useState<string | null>(null);
  const [routes, setRoutes] = useState<SimpleRouteListItem[]>([]);
  const [analytics, setAnalytics] = useState<SimpleRouteAnalytics | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<SimpleRouteStatus | "">("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    void load(storedToken);
  }, [router, isAdmin]);

  async function load(activeToken: string) {
    setLoading(true);
    setError("");
    try {
      const today = currentDate();
      const monthStart = `${today.slice(0, 8)}01`;
      const [loadedRoutes, loadedAnalytics] = await Promise.all([
        listSimpleRoutes(activeToken),
        isAdmin
          ? getSimpleRouteAnalytics(activeToken, monthStart, today)
          : Promise.resolve(null),
      ]);
      setRoutes(loadedRoutes);
      setAnalytics(loadedAnalytics);
    } catch (loadError) {
      if (loadError instanceof ApiError && loadError.status === 401) {
        removeToken();
        router.replace("/login");
        return;
      }
      setError(errorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }

  const visibleRoutes = useMemo(() => {
    const normalized = search.trim().toLocaleLowerCase("es");
    return routes.filter((route) => {
      if (status && route.status !== status) return false;
      if (!normalized) return true;
      return [route.seller_name, route.route_label, route.vehicle_name]
        .filter(Boolean)
        .some((value) => value!.toLocaleLowerCase("es").includes(normalized));
    });
  }, [routes, search, status]);

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Link className="text-sm font-semibold text-water-700" href="/dashboard">
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Rutas simples
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Hoja diaria rápida para viajes, ventas informales, fiados, abonos,
              gastos y dinero entregado.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              className="inline-flex h-10 items-center rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500"
              href="/dashboard/simple-routes/new"
            >
              Nueva hoja
            </Link>
            <LogoutButton />
          </div>
        </header>

        <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm leading-6 text-sky-950">
          <strong>Flujo recomendado para Agua Activa.</strong> Estas ventas no son
          ventas oficiales, no crean cartera formal y no mueven inventario. Solo
          el efectivo liquidado puede registrarse como referencia en un cuadre de caja.
        </div>

        {error ? <ErrorMessage message={error} /> : null}
        {loading ? <LoadingState label="Cargando hojas de ruta..." /> : null}

        {!loading && analytics ? (
          <section aria-label="Estadísticas operativas" className="space-y-3">
            <div className="flex items-end justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-water-700">
                  Rutas simples / operativo
                </p>
                <h2 className="text-lg font-semibold text-slate-950">Este mes</h2>
              </div>
              <span className="text-sm text-slate-500">{analytics.routes_count} hojas</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              <Metric label="Venta ruta" value={money(analytics.total_route_sales)} />
              <Metric label="Fiado" value={money(analytics.total_credit_sales)} />
              <Metric label="Cobrado" value={money(analytics.total_collected)} />
              <Metric label="Gastos" value={money(analytics.total_expenses)} />
              <Metric
                label="Diferencia entregada"
                value={money(analytics.total_difference)}
                alert={Number(analytics.total_difference) !== 0}
              />
            </div>
          </section>
        ) : null}

        {!loading ? (
          <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-[minmax(0,1fr)_220px_auto]">
              <label>
                <span className="text-sm font-medium text-slate-700">Buscar</span>
                <input
                  className={fieldClass}
                  placeholder="Vendedor, zona o vehículo"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </label>
              <label>
                <span className="text-sm font-medium text-slate-700">Estado</span>
                <select
                  className={fieldClass}
                  value={status}
                  onChange={(event) => setStatus(event.target.value as SimpleRouteStatus | "")}
                >
                  <option value="">Todos</option>
                  {Object.entries(SIMPLE_ROUTE_STATUS_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </label>
              <button
                className="mt-auto h-10 rounded-md border border-slate-300 px-4 text-sm font-semibold text-slate-700"
                type="button"
                onClick={() => token && load(token)}
              >
                Actualizar
              </button>
            </div>
            {visibleRoutes.length === 0 ? (
              <p className="px-4 py-10 text-center text-sm text-slate-600">
                No hay hojas para los filtros seleccionados.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[1120px] text-left text-sm">
                  <thead className="bg-slate-50 text-slate-600">
                    <tr>
                      {[
                        "Fecha", "Vendedor / zona", "Estado", "Venta ruta", "Fiado",
                        "Gastos", "Esperado", "Entregado", "Diferencia", "Caja", "",
                      ].map((label) => (
                        <th className="px-3 py-3 font-medium" key={label}>{label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {visibleRoutes.map((route) => (
                      <tr key={route.id}>
                        <td className="px-3 py-3">{dateLabel(route.route_date)}</td>
                        <td className="px-3 py-3">
                          <p className="font-semibold text-slate-950">{route.seller_name}</p>
                          <p className="text-xs text-slate-500">{route.route_label ?? "Sin zona"}</p>
                        </td>
                        <td className="px-3 py-3">
                          <Badge label={SIMPLE_ROUTE_SETTLEMENT_LABELS[route.settlement_status]} status={route.settlement_status} />
                        </td>
                        <MoneyCell value={route.route_sales_total} />
                        <MoneyCell value={route.route_credit_total} />
                        <MoneyCell value={route.expenses_total} />
                        <MoneyCell value={route.expected_cash} />
                        <MoneyCell value={route.cash_delivered} />
                        <MoneyCell value={route.cash_difference} alert />
                        <td className="px-3 py-3 text-xs font-semibold">
                          {route.cash_received_in_cash_session ? "Recibido" : "Pendiente"}
                        </td>
                        <td className="px-3 py-3">
                          <Link className="font-semibold text-water-700" href={`/dashboard/simple-routes/${route.id}`}>
                            Abrir
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        ) : null}
      </div>
    </main>
  );
}

function Metric({ label, value, alert = false }: { label: string; value: string; alert?: boolean }) {
  return (
    <div className={`rounded-lg border bg-white p-4 ${alert ? "border-amber-300" : "border-slate-200"}`}>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function MoneyCell({ value, alert = false }: { value: string | null; alert?: boolean }) {
  const hasAlert = alert && value !== null && Number(value) !== 0;
  return <td className={`px-3 py-3 text-right font-semibold ${hasAlert ? "text-amber-700" : "text-slate-800"}`}>{value === null ? "—" : money(value)}</td>;
}

function Badge({ label, status }: { label: string; status: string }) {
  const color = status === "balanced" ? "bg-emerald-50 text-emerald-700" : status === "with_difference" ? "bg-amber-50 text-amber-800" : status === "cancelled" ? "bg-red-50 text-red-700" : "bg-slate-100 text-slate-700";
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${color}`}>{label}</span>;
}

function money(value: string): string {
  return new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(Number(value));
}

function dateLabel(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}

function currentDate(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 10);
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "No se pudo completar la solicitud.";
}

const fieldClass = "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100";

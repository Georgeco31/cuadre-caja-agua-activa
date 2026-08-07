"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  addSimpleRouteCollection,
  addSimpleRouteExpense,
  addSimpleRouteSale,
  addSimpleRouteTrip,
  addSimpleRouteTripItem,
  cancelSimpleRoute,
  getCashSessionByDate,
  getSimpleRoute,
  getSimpleRouteSettlement,
  listProducts,
  receiveSimpleRouteCash,
  settleSimpleRoute,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { calculateSimpleRouteSalePreview } from "@/lib/simpleRoute";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import type { Product } from "@/types/product";
import {
  SIMPLE_ROUTE_CATEGORY_LABELS,
  SIMPLE_ROUTE_SETTLEMENT_LABELS,
  SIMPLE_ROUTE_STATUS_LABELS,
  type SimpleRouteExpenseCategory,
  type SimpleRouteItemCategory,
  type SimpleRouteMovementType,
  type SimpleRouteSaleType,
  type SimpleRouteSettlement,
  type SimpleRouteSheet,
  type SimpleRouteTrip,
} from "@/types/simpleRoute";

type Props = { sheetId: number };

export function SimpleRouteSheetWorkspace({ sheetId }: Props) {
  const router = useRouter();
  const isAdmin = useIsAdminAuditor();
  const [token, setToken] = useState<string | null>(null);
  const [sheet, setSheet] = useState<SimpleRouteSheet | null>(null);
  const [settlement, setSettlement] = useState<SimpleRouteSettlement | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [cashSessionId, setCashSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    void load(storedToken);
  }, [router, sheetId]);

  async function load(activeToken: string) {
    setLoading(true);
    setError("");
    try {
      const [loadedSheet, loadedSettlement, loadedProducts] = await Promise.all([
        getSimpleRoute(activeToken, sheetId),
        getSimpleRouteSettlement(activeToken, sheetId),
        listProducts(activeToken),
      ]);
      setSheet(loadedSheet);
      setSettlement(loadedSettlement);
      setProducts(loadedProducts.filter((product) => product.is_active));
      try {
        const cashSession = await getCashSessionByDate(activeToken, loadedSheet.route_date);
        setCashSessionId(cashSession.status === "open" ? cashSession.id : null);
      } catch {
        setCashSessionId(null);
      }
    } catch (loadError) {
      handleError(loadError);
    } finally {
      setLoading(false);
    }
  }

  async function act(action: () => Promise<unknown>, success: string) {
    if (!token) return false;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await action();
      setMessage(success);
      await load(token);
      return true;
    } catch (actionError) {
      handleError(actionError);
      return false;
    } finally {
      setBusy(false);
    }
  }

  function handleError(possibleError: unknown) {
    if (possibleError instanceof ApiError && possibleError.status === 401) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(possibleError instanceof Error ? possibleError.message : "No se pudo completar la solicitud.");
  }

  if (loading) return <LoadingState label="Cargando hoja de ruta..." />;
  if (!sheet || !settlement || !token) return <main className="min-h-screen bg-slate-50 p-6">{error ? <ErrorMessage message={error} /> : null}</main>;
  const editable = sheet.status === "draft" || sheet.status === "in_progress";

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-6 sm:px-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link className="text-sm font-semibold text-water-700" href="/dashboard/simple-routes">Volver a rutas simples</Link>
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-semibold text-slate-950">Hoja de ruta #{sheet.id}</h1>
              <RouteBadge label={SIMPLE_ROUTE_STATUS_LABELS[sheet.status]} status={sheet.status} />
            </div>
            <p className="mt-2 text-sm text-slate-600">{dateLabel(sheet.route_date)} · {sheet.seller_name} · {sheet.route_label ?? "Sin zona"}</p>
          </div>
          <LogoutButton />
        </header>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Info label="Vendedor" value={sheet.seller_name} />
          <Info label="Vehículo" value={sheet.vehicle_name ?? "Sin vehículo"} />
          <Info label="Ruta / zona" value={sheet.route_label ?? "Sin zona"} />
          <Info label="Estado del cuadre" value={SIMPLE_ROUTE_SETTLEMENT_LABELS[settlement.status]} alert={settlement.status === "with_difference"} />
        </div>
        <p className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
          Operativo independiente: no mueve stock, no crea venta oficial, no crea cartera formal y no cambia precios del catálogo.
        </p>
        {error ? <ErrorMessage message={error} /> : null}
        {message ? <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{message}</p> : null}

        <Section title="1. Viajes" subtitle="Productos que salen y regresan en cada viaje.">
          <div className="space-y-4">
            {sheet.trips.map((trip) => (
              <TripCard
                key={trip.id}
                trip={trip}
                products={products}
                disabled={!editable || busy}
                onAdd={(payload) => act(() => addSimpleRouteTripItem(token, sheet.id, trip.id, payload), "Movimiento de viaje registrado.")}
              />
            ))}
            {sheet.trips.length === 0 ? <Empty text="Todavía no hay viajes." /> : null}
            {editable ? (
              <button className={secondaryButton} disabled={busy} type="button" onClick={() => act(() => addSimpleRouteTrip(token, sheet.id), "Viaje agregado.")}>
                + Agregar viaje
              </button>
            ) : null}
          </div>
        </Section>

        <Section title="2. Ventas de ruta" subtitle="Cliente libre, contado, fiado o parcial. No son ventas oficiales.">
          <RouteSalesTable sheet={sheet} />
          {editable ? <SaleForm products={products} disabled={busy} onSubmit={(payload) => act(() => addSimpleRouteSale(token, sheet.id, payload), "Venta de ruta registrada.")} /> : null}
        </Section>

        <div className="grid gap-5 xl:grid-cols-2">
          <Section title="3. Abonos de ruta" subtitle="Aumentan el efectivo esperado; no crean cobros oficiales.">
            <SimpleRows rows={sheet.collections.map((item) => ({ left: item.customer_name_snapshot ?? "Sin nombre", right: money(item.amount), detail: item.notes }))} empty="Sin abonos." />
            {editable ? <CollectionForm sheet={sheet} disabled={busy} onSubmit={(payload) => act(() => addSimpleRouteCollection(token, sheet.id, payload), "Abono registrado.")} /> : null}
          </Section>
          <Section title="4. Gastos de ruta" subtitle="Reducen el efectivo esperado; no crean gastos oficiales.">
            <SimpleRows rows={sheet.expenses.map((item) => ({ left: item.description, right: money(item.amount), detail: item.notes }))} empty="Sin gastos." />
            {editable ? <ExpenseForm disabled={busy} onSubmit={(payload) => act(() => addSimpleRouteExpense(token, sheet.id, payload), "Gasto de ruta registrado.")} /> : null}
          </Section>
        </div>

        <SettlementSection settlement={settlement} />

        <Section title="6. Liquidación y caja" subtitle="Solo se registra una recepción por hoja; no se suma otra vez al conteo físico.">
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-950">Dinero entregado</p>
              <p className="mt-2 text-2xl font-semibold">{sheet.cash_delivered === null ? "Pendiente" : money(sheet.cash_delivered)}</p>
              {isAdmin && editable ? <SettleForm expected={settlement.expected_cash} disabled={busy} onSubmit={(amount) => act(() => settleSimpleRoute(token, sheet.id, amount), "Hoja liquidada.")} /> : null}
            </div>
            <div className="rounded-lg border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-950">Recepción en caja</p>
              <p className="mt-2 text-sm text-slate-600">
                {sheet.cash_received_in_cash_session ? `Recibido en cuadre #${sheet.cash_session_id}` : cashSessionId ? `Cuadre abierto #${cashSessionId} disponible` : "Pendiente: no hay un cuadre abierto para esta fecha."}
              </p>
              {isAdmin && sheet.status === "settled" && !sheet.cash_received_in_cash_session && cashSessionId ? (
                <button className={`${primaryButton} mt-4`} disabled={busy} type="button" onClick={() => act(() => receiveSimpleRouteCash(token, sheet.id, cashSessionId), "Efectivo recibido en caja con trazabilidad.")}>
                  Registrar recepción en caja
                </button>
              ) : null}
              {sheet.cash_received_in_cash_session ? <Link className="mt-4 inline-block text-sm font-semibold text-water-700" href={`/dashboard/history/${sheet.cash_session_id}`}>Ver cuadre vinculado</Link> : null}
            </div>
          </div>
          {isAdmin && sheet.status !== "cancelled" && !sheet.cash_received_in_cash_session ? (
            <button className="mt-5 text-sm font-semibold text-red-700" disabled={busy} type="button" onClick={() => {
              const reason = window.prompt("Motivo obligatorio de cancelación:");
              if (reason?.trim()) void act(() => cancelSimpleRoute(token, sheet.id, reason.trim()), "Hoja cancelada.");
            }}>Cancelar hoja con motivo</button>
          ) : null}
        </Section>
      </div>
    </main>
  );
}

function TripCard({ trip, products, disabled, onAdd }: { trip: SimpleRouteTrip; products: Product[]; disabled: boolean; onAdd: (payload: Parameters<typeof addSimpleRouteTripItem>[3]) => Promise<boolean> }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <h3 className="font-semibold text-slate-950">Viaje {trip.trip_number}</h3>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <MovementList title="Salieron" items={trip.items.filter((item) => item.movement_type === "out")} />
        <MovementList title="Regresaron" items={trip.items.filter((item) => item.movement_type === "return")} />
      </div>
      {!disabled ? <TripItemForm products={products} onSubmit={onAdd} /> : null}
    </article>
  );
}

function MovementList({ title, items }: { title: string; items: SimpleRouteTrip["items"] }) {
  return <div className="rounded-md bg-white p-3"><p className="text-xs font-bold uppercase text-slate-500">{title}</p>{items.length ? <ul className="mt-2 space-y-1 text-sm">{items.map((item) => <li className="flex justify-between gap-3" key={item.id}><span>{item.item_label}</span><strong>{quantity(item.quantity)}</strong></li>)}</ul> : <p className="mt-2 text-sm text-slate-500">Sin registros</p>}</div>;
}

function TripItemForm({ products, onSubmit }: { products: Product[]; onSubmit: (payload: Parameters<typeof addSimpleRouteTripItem>[3]) => Promise<boolean> }) {
  const [movement, setMovement] = useState<SimpleRouteMovementType>("out");
  const [productId, setProductId] = useState("");
  const [label, setLabel] = useState("");
  const [category, setCategory] = useState<SimpleRouteItemCategory>("full_jug");
  const [amount, setAmount] = useState("");
  async function submit(event: FormEvent) { event.preventDefault(); const ok = await onSubmit({ movement_type: movement, product_id: productId ? Number(productId) : null, item_label: productId ? null : label, item_category: category, quantity: amount }); if (ok) { setAmount(""); setLabel(""); } }
  return <form className="mt-3 grid gap-2 rounded-md border border-dashed border-slate-300 bg-white p-3 sm:grid-cols-2 lg:grid-cols-6" onSubmit={submit}>
    <select className={compactField} value={movement} onChange={(e) => setMovement(e.target.value as SimpleRouteMovementType)}><option value="out">Sale</option><option value="return">Regresa</option></select>
    <select className={compactField} value={productId} onChange={(e) => setProductId(e.target.value)}><option value="">Etiqueta libre</option>{products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}</select>
    <input className={compactField} disabled={Boolean(productId)} placeholder="Producto / etiqueta" required={!productId} value={label} onChange={(e) => setLabel(e.target.value)} />
    <select className={compactField} value={category} onChange={(e) => setCategory(e.target.value as SimpleRouteItemCategory)}>{Object.entries(SIMPLE_ROUTE_CATEGORY_LABELS).map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select>
    <input className={compactField} min="0.001" step="0.001" type="number" required placeholder="Cantidad" value={amount} onChange={(e) => setAmount(e.target.value)} />
    <button className={primaryButton} type="submit">Agregar</button>
  </form>;
}

function RouteSalesTable({ sheet }: { sheet: SimpleRouteSheet }) {
  if (!sheet.sales.length) return <Empty text="Todavía no hay ventas de ruta." />;
  return <div className="overflow-x-auto"><table className="w-full min-w-[800px] text-sm"><thead className="bg-slate-50 text-slate-600"><tr><th className="px-3 py-2 text-left">Cliente</th><th className="px-3 py-2 text-left">Producto</th><th className="px-3 py-2">Tipo</th><th className="px-3 py-2 text-right">Total</th><th className="px-3 py-2 text-right">Cobrado</th><th className="px-3 py-2 text-right">Saldo</th></tr></thead><tbody className="divide-y divide-slate-100">{sheet.sales.map((sale) => <tr key={sale.id}><td className="px-3 py-2">{sale.customer_name_snapshot ?? "Sin nombre"}</td><td className="px-3 py-2">{sale.items.map((item) => `${item.product_name_snapshot} × ${quantity(item.quantity)}`).join(", ")}</td><td className="px-3 py-2 text-center">{sale.sale_type === "cash" ? "Contado" : sale.sale_type === "credit" ? "Fiado" : "Parcial"}</td><td className="px-3 py-2 text-right">{money(sale.total_amount)}</td><td className="px-3 py-2 text-right">{money(sale.paid_amount)}</td><td className="px-3 py-2 text-right font-semibold">{money(sale.remaining_amount)}</td></tr>)}</tbody></table></div>;
}

function SaleForm({ products, disabled, onSubmit }: { products: Product[]; disabled: boolean; onSubmit: (payload: Parameters<typeof addSimpleRouteSale>[2]) => Promise<boolean> }) {
  const [customer, setCustomer] = useState(""); const [productId, setProductId] = useState(""); const [label, setLabel] = useState(""); const [category, setCategory] = useState<SimpleRouteItemCategory>("full_jug"); const [amount, setAmount] = useState(""); const [price, setPrice] = useState(""); const [saleType, setSaleType] = useState<SimpleRouteSaleType>("cash"); const [paid, setPaid] = useState(""); const preview = useMemo(() => calculateSimpleRouteSalePreview(amount, price, saleType, paid), [amount, price, saleType, paid]);
  async function submit(event: FormEvent) { event.preventDefault(); const ok = await onSubmit({ customer_name: customer.trim() || null, sale_type: saleType, ...(saleType === "partial" ? { paid_amount: paid } : {}), items: [{ product_id: productId ? Number(productId) : null, product_name: productId ? null : label, item_category: category, quantity: amount, unit_price: price }] }); if (ok) { setCustomer(""); setAmount(""); setPaid(""); } }
  return <form className="mt-4 grid gap-3 rounded-lg border border-dashed border-slate-300 p-4 sm:grid-cols-2 xl:grid-cols-4" onSubmit={submit}>
    <Field label="Cliente libre (opcional)"><input className={fieldClass} placeholder="Sin nombre o nombre informal" value={customer} onChange={(e) => setCustomer(e.target.value)} /></Field>
    <Field label="Producto del catálogo"><select className={fieldClass} value={productId} onChange={(e) => { setProductId(e.target.value); const product = products.find((item) => item.id === Number(e.target.value)); if (product) setPrice(product.default_price); }}><option value="">Usar etiqueta libre</option>{products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}</select></Field>
    <Field label="Etiqueta libre"><input className={fieldClass} disabled={Boolean(productId)} required={!productId} value={label} onChange={(e) => setLabel(e.target.value)} /></Field>
    <Field label="Categoría"><select className={fieldClass} value={category} onChange={(e) => setCategory(e.target.value as SimpleRouteItemCategory)}>{Object.entries(SIMPLE_ROUTE_CATEGORY_LABELS).map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select></Field>
    <Field label="Cantidad"><input className={fieldClass} min="0.001" step="0.001" type="number" required value={amount} onChange={(e) => setAmount(e.target.value)} /></Field>
    <Field label="Precio unitario"><input className={fieldClass} min="0" step="0.01" type="number" required value={price} onChange={(e) => setPrice(e.target.value)} /></Field>
    <Field label="Tipo"><select className={fieldClass} value={saleType} onChange={(e) => setSaleType(e.target.value as SimpleRouteSaleType)}><option value="cash">Contado</option><option value="credit">Fiado</option><option value="partial">Parcial</option></select></Field>
    <Field label={saleType === "partial" ? "Cobrado" : "Total calculado"}>{saleType === "partial" ? <input className={fieldClass} min="0.01" step="0.01" type="number" required value={paid} onChange={(e) => setPaid(e.target.value)} /> : <div className={`${fieldClass} flex items-center bg-slate-50 font-semibold`}>{money(String(preview.total))}</div>}</Field>
    <button className={`${primaryButton} sm:col-span-2 xl:col-span-4`} disabled={disabled} type="submit">Registrar venta de ruta</button>
  </form>;
}

function CollectionForm({ sheet, disabled, onSubmit }: { sheet: SimpleRouteSheet; disabled: boolean; onSubmit: (payload: Parameters<typeof addSimpleRouteCollection>[2]) => Promise<boolean> }) {
  const credits = sheet.sales.filter((sale) => Number(sale.remaining_amount) > 0); const [saleId, setSaleId] = useState(""); const [customer, setCustomer] = useState(""); const [amount, setAmount] = useState(""); const [notes, setNotes] = useState(""); async function submit(event: FormEvent) { event.preventDefault(); const ok = await onSubmit({ simple_route_sale_id: saleId ? Number(saleId) : null, customer_name: customer.trim() || null, amount, notes: notes.trim() || null }); if (ok) { setAmount(""); setNotes(""); } }
  return <form className="mt-4 grid gap-3 sm:grid-cols-2" onSubmit={submit}><Field label="Fiado enlazado (opcional)"><select className={fieldClass} value={saleId} onChange={(e) => setSaleId(e.target.value)}><option value="">Abono libre</option>{credits.map((sale) => <option key={sale.id} value={sale.id}>#{sale.id} · {sale.customer_name_snapshot ?? "Sin nombre"} · {money(sale.remaining_amount)}</option>)}</select></Field><Field label="Cliente"><input className={fieldClass} value={customer} onChange={(e) => setCustomer(e.target.value)} /></Field><Field label="Monto"><input className={fieldClass} min="0.01" step="0.01" type="number" required value={amount} onChange={(e) => setAmount(e.target.value)} /></Field><Field label="Observación"><input className={fieldClass} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field><button className={`${primaryButton} sm:col-span-2`} disabled={disabled} type="submit">Registrar abono</button></form>;
}

function ExpenseForm({ disabled, onSubmit }: { disabled: boolean; onSubmit: (payload: Parameters<typeof addSimpleRouteExpense>[2]) => Promise<boolean> }) {
  const [description, setDescription] = useState(""); const [category, setCategory] = useState<SimpleRouteExpenseCategory>("fuel"); const [amount, setAmount] = useState(""); const [notes, setNotes] = useState(""); async function submit(event: FormEvent) { event.preventDefault(); const ok = await onSubmit({ description, category, amount, notes: notes.trim() || null }); if (ok) { setDescription(""); setAmount(""); setNotes(""); } }
  return <form className="mt-4 grid gap-3 sm:grid-cols-2" onSubmit={submit}><Field label="Descripción"><input className={fieldClass} required value={description} onChange={(e) => setDescription(e.target.value)} /></Field><Field label="Categoría"><select className={fieldClass} value={category} onChange={(e) => setCategory(e.target.value as SimpleRouteExpenseCategory)}><option value="fuel">Combustible</option><option value="lunch">Almuerzo</option><option value="glue">Cola</option><option value="cap_removal">Retiro de tapas</option><option value="other">Otro</option></select></Field><Field label="Monto"><input className={fieldClass} min="0.01" step="0.01" type="number" required value={amount} onChange={(e) => setAmount(e.target.value)} /></Field><Field label="Observación"><input className={fieldClass} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field><button className={`${primaryButton} sm:col-span-2`} disabled={disabled} type="submit">Registrar gasto</button></form>;
}

function SettlementSection({ settlement }: { settlement: SimpleRouteSettlement }) {
  return <Section title="5. Cuadre de ruta" subtitle="Comparación física y de efectivo."><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Info label="Ventas ruta" value={money(settlement.route_sales_total)} /><Info label="Fiado" value={money(settlement.route_credit_total)} /><Info label="Abonos" value={money(settlement.collections_total)} /><Info label="Gastos" value={money(settlement.expenses_total)} /><Info label="Efectivo esperado" value={money(settlement.expected_cash)} /><Info label="Entregado" value={settlement.cash_delivered === null ? "Pendiente" : money(settlement.cash_delivered)} /><Info label="Diferencia efectivo" value={settlement.cash_difference === null ? "Pendiente" : money(settlement.cash_difference)} alert={Number(settlement.cash_difference) !== 0} /><Info label="Estado" value={SIMPLE_ROUTE_SETTLEMENT_LABELS[settlement.status]} alert={settlement.status === "with_difference"} /></div><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[720px] text-sm"><thead className="bg-slate-50"><tr><th className="px-3 py-2 text-left">Producto</th><th className="px-3 py-2 text-right">Salió</th><th className="px-3 py-2 text-right">Regresó</th><th className="px-3 py-2 text-right">Vendido físico</th><th className="px-3 py-2 text-right">Registrado</th><th className="px-3 py-2 text-right">Diferencia</th></tr></thead><tbody>{settlement.products.map((item) => <tr className="border-t border-slate-100" key={`${item.product_id ?? item.item_label}-${item.item_category}`}><td className="px-3 py-2">{item.item_label}</td><td className="px-3 py-2 text-right">{quantity(item.total_out)}</td><td className="px-3 py-2 text-right">{quantity(item.total_returned)}</td><td className="px-3 py-2 text-right">{quantity(item.physical_sold)}</td><td className="px-3 py-2 text-right">{quantity(item.registered_sold)}</td><td className={`px-3 py-2 text-right font-semibold ${Number(item.physical_difference) ? "text-amber-700" : "text-emerald-700"}`}>{quantity(item.physical_difference)}</td></tr>)}</tbody></table>{settlement.products.length === 0 ? <Empty text="Sin productos para comparar." /> : null}</div></Section>;
}

function SettleForm({ expected, disabled, onSubmit }: { expected: string; disabled: boolean; onSubmit: (amount: string) => Promise<boolean> }) { const [amount, setAmount] = useState(expected); async function submit(event: FormEvent) { event.preventDefault(); await onSubmit(amount); } return <form className="mt-4 flex gap-2" onSubmit={submit}><input className={fieldClass} min="0" step="0.01" type="number" required value={amount} onChange={(e) => setAmount(e.target.value)} /><button className={primaryButton} disabled={disabled} type="submit">Liquidar</button></form>; }
function Section({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) { return <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"><h2 className="text-lg font-semibold text-slate-950">{title}</h2><p className="mt-1 text-sm text-slate-600">{subtitle}</p><div className="mt-4">{children}</div></section>; }
function Field({ label, children }: { label: string; children: ReactNode }) { return <label className="block"><span className="text-sm font-medium text-slate-700">{label}</span>{children}</label>; }
function Info({ label, value, alert = false }: { label: string; value: string; alert?: boolean }) { return <div className={`rounded-lg border bg-white p-3 ${alert ? "border-amber-300" : "border-slate-200"}`}><p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p><p className={`mt-1 font-semibold ${alert ? "text-amber-800" : "text-slate-950"}`}>{value}</p></div>; }
function SimpleRows({ rows, empty }: { rows: Array<{ left: string; right: string; detail: string | null }>; empty: string }) { return rows.length ? <ul className="divide-y divide-slate-100 rounded-md border border-slate-200">{rows.map((row, index) => <li className="flex justify-between gap-3 p-3" key={`${row.left}-${index}`}><span><strong className="text-sm">{row.left}</strong>{row.detail ? <small className="block text-slate-500">{row.detail}</small> : null}</span><strong className="text-sm">{row.right}</strong></li>)}</ul> : <Empty text={empty} />; }
function Empty({ text }: { text: string }) { return <p className="rounded-md bg-slate-50 px-3 py-4 text-sm text-slate-500">{text}</p>; }
function RouteBadge({ label, status }: { label: string; status: string }) { const color = status === "settled" ? "bg-emerald-50 text-emerald-700" : status === "cancelled" ? "bg-red-50 text-red-700" : "bg-sky-50 text-sky-700"; return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${color}`}>{label}</span>; }
function money(value: string): string { return new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(Number(value)); }
function quantity(value: string): string { return Number(value).toLocaleString("es-EC", { maximumFractionDigits: 3 }); }
function dateLabel(value: string): string { return new Intl.DateTimeFormat("es-EC", { dateStyle: "long" }).format(new Date(`${value}T00:00:00`)); }
const fieldClass = "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100";
const compactField = "h-10 min-w-0 rounded-md border border-slate-300 bg-white px-2 text-sm text-slate-950 outline-none focus:border-water-500";
const primaryButton = "h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300";
const secondaryButton = "h-10 rounded-md border border-water-300 bg-white px-4 text-sm font-semibold text-water-700 hover:bg-water-50 disabled:text-slate-400";

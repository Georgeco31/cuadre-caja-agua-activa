import Link from "next/link";

import type { SimpleRouteCashReceipt } from "@/types/simpleRoute";

export function SimpleRouteCashReceiptList({
  receipts,
}: {
  receipts: SimpleRouteCashReceipt[];
}) {
  const total = receipts.reduce((sum, receipt) => sum + Number(receipt.amount), 0);
  return (
    <section className="rounded-lg border border-sky-200 bg-sky-50 p-4 shadow-sm">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-sky-700">
            Rutas simples / referencia
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-950">
            Efectivo de rutas recibido en este cuadre
          </h2>
        </div>
        <p className="text-xl font-semibold text-slate-950">{money(total)}</p>
      </div>
      <p className="mt-2 text-sm leading-6 text-sky-950">
        Es trazabilidad del efectivo entregado. No se suma al total contado para
        evitar doble conteo y no representa ventas oficiales.
      </p>
      {receipts.length ? (
        <ul className="mt-4 divide-y divide-sky-100 rounded-md border border-sky-200 bg-white">
          {receipts.map((receipt) => (
            <li className="flex flex-wrap items-center justify-between gap-3 p-3" key={receipt.id}>
              <span>
                <Link className="font-semibold text-water-700" href={`/dashboard/simple-routes/${receipt.route_sheet_id}`}>
                  Hoja #{receipt.route_sheet_id} · {receipt.seller_name ?? "Sin vendedor"}
                </Link>
                <small className="block text-slate-500">{receipt.route_label ?? "Sin zona"}</small>
              </span>
              <strong>{money(Number(receipt.amount))}</strong>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm text-slate-600">No hay efectivo de rutas simples recibido.</p>
      )}
    </section>
  );
}

function money(value: number): string {
  return new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(value);
}

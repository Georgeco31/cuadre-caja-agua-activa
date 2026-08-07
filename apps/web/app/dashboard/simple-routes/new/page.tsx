"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LogoutButton } from "@/components/LogoutButton";
import { ApiError, createSimpleRoute, listVehicles } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { Vehicle } from "@/types/vehicle";

export default function NewSimpleRoutePage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [routeDate, setRouteDate] = useState(currentDate());
  const [sellerName, setSellerName] = useState("");
  const [vehicleId, setVehicleId] = useState("");
  const [routeLabel, setRouteLabel] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    listVehicles(storedToken)
      .then((items) => setVehicles(items.filter((item) => item.is_active)))
      .catch((loadError) => setError(message(loadError)));
  }, [router]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !sellerName.trim()) return;
    setSaving(true);
    setError("");
    try {
      const sheet = await createSimpleRoute(token, {
        route_date: routeDate,
        seller_name: sellerName.trim(),
        vehicle_id: vehicleId ? Number(vehicleId) : null,
        route_label: routeLabel.trim() || null,
        notes: notes.trim() || null,
      });
      router.push(`/dashboard/simple-routes/${sheet.id}`);
    } catch (saveError) {
      if (saveError instanceof ApiError && saveError.status === 401) {
        removeToken();
        router.replace("/login");
        return;
      }
      setError(message(saveError));
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto w-full max-w-3xl px-4 py-6 sm:px-6">
        <header className="flex items-start justify-between gap-4 border-b border-slate-200 pb-5">
          <div>
            <Link className="text-sm font-semibold text-water-700" href="/dashboard/simple-routes">
              Volver a rutas simples
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">Nueva hoja de ruta</h1>
            <p className="mt-2 text-sm text-slate-600">Solo pide los datos del encabezado. Los viajes y ventas se agregan en la hoja.</p>
          </div>
          <LogoutButton />
        </header>

        {error ? <div className="mt-5"><ErrorMessage message={error} /></div> : null}
        <form className="mt-6 space-y-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6" onSubmit={submit}>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Fecha">
              <input className={fieldClass} type="date" required value={routeDate} onChange={(event) => setRouteDate(event.target.value)} />
            </Field>
            <Field label="Vendedor">
              <input className={fieldClass} required autoFocus placeholder="Nombre del vendedor" value={sellerName} onChange={(event) => setSellerName(event.target.value)} />
            </Field>
            <Field label="Vehículo (opcional)">
              <select className={fieldClass} value={vehicleId} onChange={(event) => setVehicleId(event.target.value)}>
                <option value="">Sin vehículo</option>
                {vehicles.map((vehicle) => <option key={vehicle.id} value={vehicle.id}>{vehicle.name}</option>)}
              </select>
            </Field>
            <Field label="Ruta o zona (opcional)">
              <input className={fieldClass} placeholder="Centro, Norte..." value={routeLabel} onChange={(event) => setRouteLabel(event.target.value)} />
            </Field>
          </div>
          <Field label="Observaciones">
            <textarea className={`${fieldClass} min-h-24 py-2`} value={notes} onChange={(event) => setNotes(event.target.value)} />
          </Field>
          <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
            Esta hoja no descuenta stock, no crea ventas oficiales y permite clientes sin registro formal.
          </div>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Link className="inline-flex h-11 items-center justify-center rounded-md border border-slate-300 px-5 text-sm font-semibold text-slate-700" href="/dashboard/simple-routes">Cancelar</Link>
            <button className="h-11 rounded-md bg-water-700 px-5 text-sm font-semibold text-white disabled:bg-slate-300" disabled={saving} type="submit">
              {saving ? "Creando..." : "Crear y abrir hoja"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="text-sm font-medium text-slate-700">{label}</span>{children}</label>;
}
function currentDate(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 10);
}
function message(error: unknown): string { return error instanceof Error ? error.message : "No se pudo completar la solicitud."; }
const fieldClass = "mt-1 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100";

import Link from "next/link";

type AccessRestrictedProps = {
  compact?: boolean;
  message?: string;
};

export function AccessRestricted({
  compact = false,
  message,
}: AccessRestrictedProps) {
  if (compact) {
    return (
      <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
        {message ??
          "Tienes acceso de consulta. Los registros y cambios críticos están disponibles solo para el administrador/auditor."}
      </p>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <section className="mx-auto flex min-h-[70vh] w-full max-w-2xl items-center">
        <div className="w-full rounded-2xl border border-amber-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-700">
            Acceso restringido
          </p>
          <h1 className="mt-3 text-2xl font-semibold text-slate-950">
            Esta sección está disponible solo para administrador/auditor.
          </h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            No tienes permiso para realizar esta acción. Solicita autorización
            a George para cambios críticos.
          </p>
          <Link
            className="mt-6 inline-flex min-h-11 items-center justify-center rounded-xl bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-600"
            href="/dashboard"
          >
            Volver al panel operativo
          </Link>
        </div>
      </section>
    </main>
  );
}

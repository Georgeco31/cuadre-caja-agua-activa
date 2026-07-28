export function BackupReminderCard() {
  return (
    <section
      className="rounded-3xl border border-amber-200 bg-amber-50 p-5 shadow-card sm:p-6"
      id="alertas"
    >
      <div className="flex items-start gap-4">
        <span
          aria-hidden="true"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-sm font-bold text-amber-800"
        >
          !
        </span>
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-amber-800">
            Recordatorio operativo
          </p>
          <h2 className="mt-2 text-lg font-semibold text-amber-950">
            Respaldo al cierre del día
          </h2>
          <p className="mt-2 text-sm leading-6 text-amber-900">
            Recuerda hacer backup al finalizar las pruebas o al cerrar el día.
          </p>
        </div>
      </div>
    </section>
  );
}

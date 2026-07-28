export function BackupReminderCard() {
  return (
    <article className="rounded-2xl border border-water-100 bg-water-50/70 p-4">
      <div className="flex items-start gap-3">
        <span
          aria-hidden="true"
          className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-water-100 text-sm font-bold text-water-800"
        >
          B
        </span>
        <div className="min-w-0">
          <h3 className="font-semibold text-slate-950">
            Respaldo al cierre del día
          </h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            Recuerda hacer backup al finalizar las pruebas o al cerrar el día.
          </p>
        </div>
      </div>
    </article>
  );
}

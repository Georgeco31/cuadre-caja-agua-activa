type DateSelectorProps = {
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
};

export function DateSelector({
  value,
  disabled = false,
  onChange,
}: DateSelectorProps) {
  return (
    <section
      aria-labelledby="cash-session-date-title"
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_220px] lg:items-end">
        <div>
          <p className="text-sm font-medium text-water-700">Cuadre de caja</p>
          <h2
            id="cash-session-date-title"
            className="mt-1 text-xl font-semibold text-slate-950"
          >
            Fecha del cuadre
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Selecciona la fecha que deseas registrar o consultar.
          </p>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">
            Fecha del cuadre
          </span>
          <input
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
            type="date"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            disabled={disabled}
            required
          />
        </label>
      </div>
    </section>
  );
}

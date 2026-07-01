import type { Denomination } from "@/types/denomination";

type DenominationCountTableProps = {
  title: string;
  denominations: Denomination[];
  disabled: boolean;
  quantities: Record<number, string>;
  savedDenominationIds: Set<number>;
  savingId: number | null;
  onQuantityChange: (denominationId: number, value: string) => void;
  onSave: (denomination: Denomination) => void;
};

export function DenominationCountTable({
  title,
  denominations,
  disabled,
  quantities,
  savedDenominationIds,
  savingId,
  onQuantityChange,
  onSave,
}: DenominationCountTableProps) {
  return (
    <section
      aria-labelledby={`${title.toLowerCase()}-title`}
      className="rounded-lg border border-slate-200 bg-white shadow-sm"
    >
      <div className="border-b border-slate-200 px-4 py-3">
        <h2
          id={`${title.toLowerCase()}-title`}
          className="text-lg font-semibold text-slate-950"
        >
          {title}
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Las cantidades se cargan desde el cuadre guardado. Si no hay conteo,
          se muestra 0.
        </p>
      </div>

      <div className="divide-y divide-slate-100">
        {denominations.map((denomination) => {
          const isSaving = savingId === denomination.id;
          const isAnyRowSaving = savingId !== null;
          const isSaved = savedDenominationIds.has(denomination.id);

          return (
            <div
              className="grid gap-3 px-4 py-3 sm:grid-cols-[1fr_120px_160px_128px] sm:items-center"
              key={denomination.id}
            >
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium text-slate-950">
                    {denomination.label}
                  </p>
                  {isSaved ? (
                    <span className="rounded-md border border-water-100 bg-water-50 px-2 py-0.5 text-xs font-medium text-water-700">
                      Guardado
                    </span>
                  ) : null}
                </div>
                <p className="text-sm text-slate-600">
                  Valor: {formatMoney(denomination.value)}
                </p>
              </div>

              <p className="text-sm font-medium text-slate-700 sm:text-right">
                {formatMoney(denomination.value)}
              </p>

              <label className="block">
                <span className="sr-only">
                  Cantidad para {denomination.label}
                </span>
                <input
                  className="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100 disabled:text-slate-500"
                  type="number"
                  inputMode="numeric"
                  min={0}
                  step={1}
                  value={quantities[denomination.id] ?? ""}
                  onChange={(event) =>
                    onQuantityChange(denomination.id, event.target.value)
                  }
                  disabled={disabled}
                />
              </label>

              <button
                className="h-10 rounded-md bg-water-700 px-3 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
                type="button"
                onClick={() => onSave(denomination)}
                disabled={disabled || isAnyRowSaving}
              >
                {isSaving
                  ? "Guardando..."
                  : isSaved
                    ? "Actualizar"
                    : "Guardar"}
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function formatMoney(value: string): string {
  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) {
    return `$${value}`;
  }

  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(numberValue);
}

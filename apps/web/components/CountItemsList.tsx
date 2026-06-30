import type { CountItemDetail } from "@/types/countItem";

type CountItemsListProps = {
  countItems: CountItemDetail[];
};

export function CountItemsList({ countItems }: CountItemsListProps) {
  const coins = countItems.filter((item) => item.denomination_type === "coin");
  const bills = countItems.filter((item) => item.denomination_type === "bill");

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <CountItemSection title="Monedas contadas" countItems={coins} />
      <CountItemSection title="Billetes contados" countItems={bills} />
    </div>
  );
}

type CountItemSectionProps = {
  title: string;
  countItems: CountItemDetail[];
};

function CountItemSection({ title, countItems }: CountItemSectionProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      </div>

      {countItems.length === 0 ? (
        <p className="px-4 py-6 text-sm text-slate-600">
          No hay conteos registrados.
        </p>
      ) : (
        <div className="divide-y divide-slate-100">
          {countItems.map((item) => (
            <div
              className="grid gap-3 px-4 py-3 sm:grid-cols-[1fr_96px_96px] sm:items-center"
              key={item.id}
            >
              <div>
                <p className="font-medium text-slate-950">
                  {item.denomination_label}
                </p>
                <p className="text-sm text-slate-600">
                  Valor: {formatMoney(item.denomination_value)}
                </p>
              </div>
              <p className="text-sm text-slate-700">
                Cantidad: {item.quantity}
              </p>
              <p className="text-sm font-semibold text-slate-950">
                {formatMoney(item.subtotal)}
              </p>
            </div>
          ))}
        </div>
      )}
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

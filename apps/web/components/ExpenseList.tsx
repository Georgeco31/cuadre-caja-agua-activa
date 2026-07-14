import type { Expense } from "@/types/expense";

type ExpenseListProps = {
  titleId?: string;
  title?: string;
  emptyMessage?: string;
  expenses: Expense[];
};

export function ExpenseList({
  titleId = "expense-list-title",
  title = "Gastos registrados",
  emptyMessage = "Todavía no hay gastos registrados para este cuadre.",
  expenses,
}: ExpenseListProps) {
  return (
    <section
      aria-labelledby={titleId}
      className="rounded-lg border border-slate-200 bg-white shadow-sm"
    >
      <div className="border-b border-slate-200 px-4 py-3">
        <h2
          id={titleId}
          className="text-lg font-semibold text-slate-950"
        >
          {title}
        </h2>
      </div>

      {expenses.length === 0 ? (
        <p className="px-4 py-6 text-sm text-slate-600">
          {emptyMessage}
        </p>
      ) : (
        <div className="divide-y divide-slate-100">
          {expenses.map((expense) => (
            <article className="px-4 py-4" key={expense.id}>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 className="font-medium text-slate-950">
                    {expense.description}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    Fecha: {formatDate(expense.expense_date)}
                  </p>
                  {expense.category ? (
                    <p className="mt-1 text-sm text-slate-600">
                      Categoría: {expense.category}
                    </p>
                  ) : null}
                  <p className="mt-1 text-sm text-slate-600">
                    Tipo: {formatExpenseTiming(expense.expense_timing)}
                  </p>
                  {expense.notes ? (
                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      {expense.notes}
                    </p>
                  ) : null}
                </div>
                <p className="text-base font-semibold text-slate-950">
                  {formatMoney(expense.amount)}
                </p>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function formatExpenseTiming(expenseTiming: Expense["expense_timing"]): string {
  if (expenseTiming === "before_count") {
    return "Antes del conteo";
  }

  return "Despues del conteo";
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

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

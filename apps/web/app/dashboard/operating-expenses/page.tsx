"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createExpenseFromRecurringOperatingExpense,
  createOperatingExpense,
  createOperatingExpenseCategory,
  createRecurringOperatingExpense,
  getOperatingExpenseSummary,
  listOperatingExpenseCategories,
  listOperatingExpenses,
  listRecurringOperatingExpenses,
  listSuppliers,
  setOperatingExpenseCategoryActive,
  setRecurringOperatingExpenseActive,
  voidOperatingExpense,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import { isValidMoneyInputDraft, parseMoneyInputToCents } from "@/lib/money";
import {
  OPERATING_EXPENSE_PAYMENT_METHOD_LABELS,
  OPERATING_EXPENSE_PAYMENT_STATUS_LABELS,
  OPERATING_EXPENSE_STATUS_LABELS,
  RECURRING_OPERATING_EXPENSE_FREQUENCY_LABELS,
  type OperatingExpense,
  type OperatingExpenseCategory,
  type OperatingExpenseFilters,
  type OperatingExpensePaymentMethod,
  type OperatingExpensePaymentStatus,
  type OperatingExpenseStatus,
  type OperatingExpenseSummary,
  type RecurringOperatingExpense,
  type RecurringOperatingExpenseFrequency,
} from "@/types/operatingExpense";
import type { Supplier } from "@/types/supplier";

type Section = "expenses" | "categories" | "recurring";

type ExpenseFormValues = {
  expenseDate: string;
  categoryId: string;
  supplierId: string;
  description: string;
  amount: string;
  paymentStatus: OperatingExpensePaymentStatus;
  paymentMethod: OperatingExpensePaymentMethod;
  documentNumber: string;
  dueDate: string;
  paidDate: string;
  notes: string;
};

type ExpenseFilterValues = {
  dateFrom: string;
  dateTo: string;
  status: "" | OperatingExpenseStatus;
  paymentStatus: "" | OperatingExpensePaymentStatus;
  categoryId: string;
  supplierId: string;
  paymentMethod: "" | OperatingExpensePaymentMethod;
  search: string;
};

type TemplateFormValues = {
  name: string;
  categoryId: string;
  supplierId: string;
  description: string;
  amount: string;
  frequency: RecurringOperatingExpenseFrequency;
  startDate: string;
  endDate: string;
  nextDueDate: string;
  paymentMethod: OperatingExpensePaymentMethod;
  notes: string;
};

type GenerateFormValues = {
  expenseDate: string;
  dueDate: string;
  paidDate: string;
  paymentStatus: OperatingExpensePaymentStatus;
  notes: string;
};

const emptyFilters: ExpenseFilterValues = {
  dateFrom: "",
  dateTo: "",
  status: "",
  paymentStatus: "",
  categoryId: "",
  supplierId: "",
  paymentMethod: "",
  search: "",
};

export default function OperatingExpensesPage() {
  const canVoid = useIsAdminAuditor();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [section, setSection] = useState<Section>("expenses");
  const [categories, setCategories] = useState<OperatingExpenseCategory[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [expenses, setExpenses] = useState<OperatingExpense[]>([]);
  const [templates, setTemplates] = useState<RecurringOperatingExpense[]>([]);
  const [summary, setSummary] = useState<OperatingExpenseSummary | null>(null);
  const [filters, setFilters] = useState(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState(emptyFilters);
  const [categoryName, setCategoryName] = useState("");
  const [categoryDescription, setCategoryDescription] = useState("");
  const [expenseForm, setExpenseForm] = useState(createEmptyExpenseForm);
  const [templateForm, setTemplateForm] = useState(createEmptyTemplateForm);
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [selectedExpense, setSelectedExpense] =
    useState<OperatingExpense | null>(null);
  const [voidingExpense, setVoidingExpense] =
    useState<OperatingExpense | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [generatingTemplate, setGeneratingTemplate] =
    useState<RecurringOperatingExpense | null>(null);
  const [generateForm, setGenerateForm] = useState(createEmptyGenerateForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingId, setChangingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    loadAll(storedToken);
  }, [router]);

  async function loadAll(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const [
        loadedCategories,
        loadedSuppliers,
        loadedExpenses,
        loadedTemplates,
        loadedSummary,
      ] = await Promise.all([
        listOperatingExpenseCategories(activeToken),
        listSuppliers(activeToken, { is_active: true }),
        listOperatingExpenses(activeToken),
        listRecurringOperatingExpenses(activeToken),
        getOperatingExpenseSummary(activeToken),
      ]);
      setCategories(loadedCategories);
      setSuppliers(loadedSuppliers);
      setExpenses(loadedExpenses);
      setTemplates(loadedTemplates);
      setSummary(loadedSummary);
      setAppliedFilters(emptyFilters);
    } catch (loadError) {
      handleError(loadError, "No se pudo cargar el módulo.");
    } finally {
      setIsLoading(false);
    }
  }

  async function reloadModule(activeToken: string) {
    const expenseFilters = toExpenseFilters(appliedFilters);
    const [
      loadedCategories,
      loadedExpenses,
      loadedTemplates,
      loadedSummary,
    ] = await Promise.all([
      listOperatingExpenseCategories(activeToken),
      listOperatingExpenses(activeToken, expenseFilters),
      listRecurringOperatingExpenses(activeToken),
      getOperatingExpenseSummary(
        activeToken,
        toSummaryFilters(appliedFilters),
      ),
    ]);
    setCategories(loadedCategories);
    setExpenses(loadedExpenses);
    setTemplates(loadedTemplates);
    setSummary(loadedSummary);
  }

  async function handleFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsLoading(true);
    clearNotices();
    try {
      const [loadedExpenses, loadedSummary] = await Promise.all([
        listOperatingExpenses(token, toExpenseFilters(filters)),
        getOperatingExpenseSummary(token, toSummaryFilters(filters)),
      ]);
      setExpenses(loadedExpenses);
      setSummary(loadedSummary);
      setAppliedFilters({ ...filters });
    } catch (loadError) {
      handleError(loadError, "No se pudieron aplicar los filtros.");
    } finally {
      setIsLoading(false);
    }
  }

  async function clearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    setIsLoading(true);
    clearNotices();
    try {
      const [loadedExpenses, loadedSummary] = await Promise.all([
        listOperatingExpenses(token),
        getOperatingExpenseSummary(token),
      ]);
      setExpenses(loadedExpenses);
      setSummary(loadedSummary);
      setAppliedFilters(emptyFilters);
    } catch (loadError) {
      handleError(loadError, "No se pudieron limpiar los filtros.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    if (!categoryName.trim()) {
      setError("El nombre de la categoría es obligatorio.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createOperatingExpenseCategory(token, {
        name: categoryName.trim(),
        description: optionalText(categoryDescription),
      });
      setCategoryName("");
      setCategoryDescription("");
      setMessage(`Categoría registrada: ${created.name}.`);
      await reloadModule(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo registrar la categoría.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggleCategory(category: OperatingExpenseCategory) {
    if (!token) {
      return;
    }
    if (
      category.is_active &&
      !window.confirm(`¿Desactivar la categoría ${category.name}?`)
    ) {
      return;
    }
    setChangingId(category.id);
    clearNotices();
    try {
      const updated = await setOperatingExpenseCategoryActive(
        token,
        category.id,
        !category.is_active,
      );
      setMessage(
        `Categoría ${updated.is_active ? "activada" : "desactivada"}: ${
          updated.name
        }.`,
      );
      await reloadModule(token);
    } catch (statusError) {
      handleError(statusError, "No se pudo cambiar el estado de la categoría.");
    } finally {
      setChangingId(null);
    }
  }

  async function handleCreateExpense(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    const validationError = validateExpenseForm(expenseForm, categories);
    if (validationError) {
      setError(validationError);
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createOperatingExpense(token, {
        expense_date: expenseForm.expenseDate,
        category_id: Number(expenseForm.categoryId),
        supplier_id: optionalId(expenseForm.supplierId),
        description: expenseForm.description.trim(),
        amount: normalizeMoney(expenseForm.amount),
        payment_status: expenseForm.paymentStatus,
        payment_method: expenseForm.paymentMethod,
        document_number: optionalText(expenseForm.documentNumber),
        due_date: optionalText(expenseForm.dueDate),
        paid_date: optionalText(expenseForm.paidDate),
        notes: optionalText(expenseForm.notes),
      });
      setExpenseForm(createEmptyExpenseForm());
      setShowExpenseForm(false);
      setMessage(`Gasto registrado: ${created.expense_number}.`);
      await reloadModule(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo registrar el gasto.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleVoidExpense(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !voidingExpense) {
      return;
    }
    if (!voidReason.trim()) {
      setError("El motivo de anulación es obligatorio.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const voided = await voidOperatingExpense(
        token,
        voidingExpense.id,
        voidReason.trim(),
      );
      setVoidingExpense(null);
      setVoidReason("");
      setSelectedExpense(voided);
      setMessage(`Gasto anulado: ${voided.expense_number}.`);
      await reloadModule(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo anular el gasto.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleCreateTemplate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    const validationError = validateTemplateForm(templateForm, categories);
    if (validationError) {
      setError(validationError);
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createRecurringOperatingExpense(token, {
        name: templateForm.name.trim(),
        category_id: Number(templateForm.categoryId),
        supplier_id: optionalId(templateForm.supplierId),
        description: templateForm.description.trim(),
        amount: normalizeMoney(templateForm.amount),
        frequency: templateForm.frequency,
        start_date: templateForm.startDate,
        end_date: optionalText(templateForm.endDate),
        next_due_date: optionalText(templateForm.nextDueDate),
        payment_method: templateForm.paymentMethod,
        notes: optionalText(templateForm.notes),
      });
      setTemplateForm(createEmptyTemplateForm());
      setShowTemplateForm(false);
      setMessage(`Plantilla registrada: ${created.name}.`);
      await reloadModule(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo registrar la plantilla.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggleTemplate(template: RecurringOperatingExpense) {
    if (!token) {
      return;
    }
    if (
      template.is_active &&
      !window.confirm(`¿Desactivar la plantilla ${template.name}?`)
    ) {
      return;
    }
    setChangingId(template.id);
    clearNotices();
    try {
      const updated = await setRecurringOperatingExpenseActive(
        token,
        template.id,
        !template.is_active,
      );
      setMessage(
        `Plantilla ${updated.is_active ? "activada" : "desactivada"}: ${
          updated.name
        }.`,
      );
      await reloadModule(token);
    } catch (statusError) {
      handleError(statusError, "No se pudo cambiar el estado de la plantilla.");
    } finally {
      setChangingId(null);
    }
  }

  async function handleGenerateExpense(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !generatingTemplate) {
      return;
    }
    if (!generateForm.expenseDate) {
      setError("La fecha del gasto es obligatoria.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createExpenseFromRecurringOperatingExpense(
        token,
        generatingTemplate.id,
        {
          expense_date: generateForm.expenseDate,
          due_date: optionalText(generateForm.dueDate),
          paid_date: optionalText(generateForm.paidDate),
          payment_status: generateForm.paymentStatus,
          notes: optionalText(generateForm.notes),
        },
      );
      setGeneratingTemplate(null);
      setGenerateForm(createEmptyGenerateForm());
      setSection("expenses");
      setSelectedExpense(created);
      setMessage(
        `Gasto ${created.expense_number} generado manualmente desde la plantilla.`,
      );
      await reloadModule(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo generar el gasto.");
    } finally {
      setIsSaving(false);
    }
  }

  function handleError(possibleError: unknown, fallback: string) {
    if (
      possibleError instanceof ApiError &&
      possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(
      possibleError instanceof Error ? possibleError.message : fallback,
    );
  }

  function clearNotices() {
    setError("");
    setMessage("");
  }

  const activeCategories = categories.filter((category) => category.is_active);

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Gastos operativos
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra gastos generales del negocio fuera del cuadre diario de
              caja. Este módulo no modifica caja ni bancos automáticamente.
            </p>
          </div>
          <LogoutButton />
        </header>

        <section className="rounded-lg border border-sky-200 bg-sky-50 p-4">
          <p className="font-semibold text-sky-950">
            Los gastos del cuadre diario y los gastos operativos generales se
            manejan separados.
          </p>
          <p className="mt-1 text-sm leading-6 text-sky-800">
            Registrar un gasto aquí tampoco crea compras, pagos a proveedores
            ni movimientos de inventario.
          </p>
        </section>

        {summary ? <SummaryPanel summary={summary} /> : null}

        <nav
          aria-label="Secciones de gastos operativos"
          className="grid gap-2 rounded-lg border border-slate-200 bg-white p-2 sm:grid-cols-3"
        >
          <SectionButton
            active={section === "expenses"}
            label="Gastos"
            count={expenses.length}
            onClick={() => setSection("expenses")}
          />
          {canVoid ? <SectionButton
            active={section === "categories"}
            label="Categorías"
            count={categories.length}
            onClick={() => setSection("categories")}
          /> : null}
          {canVoid ? <SectionButton
            active={section === "recurring"}
            label="Plantillas recurrentes"
            count={templates.length}
            onClick={() => setSection("recurring")}
          /> : null}
        </nav>

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando gastos operativos..." />
        ) : section === "categories" ? (
          <CategoriesSection
            categories={categories}
            name={categoryName}
            description={categoryDescription}
            isSaving={isSaving}
            changingId={changingId}
            onNameChange={setCategoryName}
            onDescriptionChange={setCategoryDescription}
            onSubmit={handleCreateCategory}
            onToggle={handleToggleCategory}
          />
        ) : section === "recurring" ? (
          <RecurringSection
            categories={activeCategories}
            suppliers={suppliers}
            templates={templates}
            form={templateForm}
            showForm={showTemplateForm}
            isSaving={isSaving}
            changingId={changingId}
            generatingTemplate={generatingTemplate}
            generateForm={generateForm}
            onFormChange={setTemplateForm}
            onShowForm={() => {
              clearNotices();
              setShowTemplateForm(true);
            }}
            onHideForm={() => setShowTemplateForm(false)}
            onSubmit={handleCreateTemplate}
            onToggle={handleToggleTemplate}
            onStartGenerate={(template) => {
              clearNotices();
              setGeneratingTemplate(template);
              setGenerateForm({
                ...createEmptyGenerateForm(),
                dueDate: template.next_due_date ?? "",
              });
            }}
            onCancelGenerate={() => setGeneratingTemplate(null)}
            onGenerateFormChange={setGenerateForm}
            onGenerate={handleGenerateExpense}
          />
        ) : (
          <ExpensesSection
            canVoid={canVoid}
            categories={activeCategories}
            allCategories={categories}
            suppliers={suppliers}
            expenses={expenses}
            filters={filters}
            form={expenseForm}
            showForm={showExpenseForm}
            selectedExpense={selectedExpense}
            voidingExpense={voidingExpense}
            voidReason={voidReason}
            isSaving={isSaving}
            onFiltersChange={setFilters}
            onApplyFilters={handleFilters}
            onClearFilters={clearFilters}
            onFormChange={setExpenseForm}
            onShowForm={() => {
              clearNotices();
              setShowExpenseForm(true);
            }}
            onHideForm={() => setShowExpenseForm(false)}
            onSubmit={handleCreateExpense}
            onSelectExpense={setSelectedExpense}
            onStartVoid={(expense) => {
              clearNotices();
              setVoidingExpense(expense);
              setVoidReason("");
            }}
            onCancelVoid={() => setVoidingExpense(null)}
            onVoidReasonChange={setVoidReason}
            onVoid={handleVoidExpense}
          />
        )}
      </div>
    </main>
  );
}

function SummaryPanel({ summary }: { summary: OperatingExpenseSummary }) {
  const cards = [
    ["Total activo", summary.total_expenses_amount],
    ["Pagado", summary.paid_amount],
    ["Pendiente", summary.unpaid_amount],
    ["Parcial", summary.partial_amount],
  ] as const;
  return (
    <section aria-labelledby="opex-summary-title" className="space-y-4">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-water-700">Resumen oficial</p>
          <h2
            id="opex-summary-title"
            className="mt-1 text-xl font-semibold text-slate-950"
          >
            Gastos activos del período
          </h2>
        </div>
        <p className="text-sm text-slate-600">
          {summary.expenses_count} activos · {summary.voided_count} anulados
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(([label, amount]) => (
          <article
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
            key={label}
          >
            <p className="text-sm text-slate-600">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-950">
              {formatAmount(amount)}
            </p>
          </article>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <SummaryBreakdown
          title="Por categoría"
          rows={summary.by_category.map((row) => ({
            key: String(row.category_id),
            label: row.category_name,
            amount: row.total_amount,
            count: row.expenses_count,
          }))}
        />
        <SummaryBreakdown
          title="Por proveedor"
          rows={summary.by_supplier.map((row) => ({
            key: String(row.supplier_id ?? "none"),
            label: row.supplier_name,
            amount: row.total_amount,
            count: row.expenses_count,
          }))}
        />
      </div>
    </section>
  );
}

function SummaryBreakdown({
  title,
  rows,
}: {
  title: string;
  rows: Array<{ key: string; label: string; amount: string; count: number }>;
}) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="font-semibold text-slate-950">{title}</h3>
      {rows.length ? (
        <ul className="mt-3 divide-y divide-slate-100">
          {rows.map((row) => (
            <li
              className="flex items-center justify-between gap-3 py-2 text-sm"
              key={row.key}
            >
              <span className="text-slate-700">
                {row.label}{" "}
                <span className="text-slate-400">({row.count})</span>
              </span>
              <span className="font-semibold text-slate-950">
                {formatAmount(row.amount)}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-500">Sin gastos activos.</p>
      )}
    </article>
  );
}

function CategoriesSection({
  categories,
  name,
  description,
  isSaving,
  changingId,
  onNameChange,
  onDescriptionChange,
  onSubmit,
  onToggle,
}: {
  categories: OperatingExpenseCategory[];
  name: string;
  description: string;
  isSaving: boolean;
  changingId: number | null;
  onNameChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggle: (category: OperatingExpenseCategory) => void;
}) {
  return (
    <section className="grid gap-5 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
      <form
        className="h-fit rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
        onSubmit={onSubmit}
      >
        <h2 className="text-lg font-semibold text-slate-950">
          Nueva categoría
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Las categorías se desactivan; no se eliminan físicamente.
        </p>
        <div className="mt-4 space-y-4">
          <InputField
            label="Nombre *"
            value={name}
            required
            disabled={isSaving}
            onChange={onNameChange}
          />
          <TextAreaField
            label="Descripción"
            value={description}
            disabled={isSaving}
            onChange={onDescriptionChange}
          />
        </div>
        <button
          className="mt-4 h-10 w-full rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
          type="submit"
          disabled={isSaving}
        >
          {isSaving ? "Guardando..." : "Guardar categoría"}
        </button>
      </form>
      <div className="space-y-3">
        <div>
          <p className="text-sm font-medium text-water-700">Catálogo</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Categorías registradas
          </h2>
        </div>
        {categories.length ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {categories.map((category) => (
              <article
                className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
                key={category.id}
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold text-slate-950">
                    {category.name}
                  </h3>
                  <StatusBadge active={category.is_active} />
                </div>
                <p className="mt-2 min-h-10 text-sm leading-5 text-slate-600">
                  {category.description ?? "Sin descripción."}
                </p>
                <button
                  className={
                    category.is_active
                      ? "mt-4 h-9 w-full rounded-md border border-red-200 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:bg-slate-100"
                      : "mt-4 h-9 w-full rounded-md border border-emerald-200 text-sm font-semibold text-emerald-700 hover:bg-emerald-50 disabled:bg-slate-100"
                  }
                  type="button"
                  disabled={changingId === category.id}
                  onClick={() => onToggle(category)}
                >
                  {changingId === category.id
                    ? "Guardando..."
                    : category.is_active
                      ? "Desactivar"
                      : "Activar"}
                </button>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState text="Todavía no hay categorías registradas." />
        )}
      </div>
    </section>
  );
}

function ExpensesSection({
  canVoid,
  categories,
  allCategories,
  suppliers,
  expenses,
  filters,
  form,
  showForm,
  selectedExpense,
  voidingExpense,
  voidReason,
  isSaving,
  onFiltersChange,
  onApplyFilters,
  onClearFilters,
  onFormChange,
  onShowForm,
  onHideForm,
  onSubmit,
  onSelectExpense,
  onStartVoid,
  onCancelVoid,
  onVoidReasonChange,
  onVoid,
}: {
  canVoid: boolean;
  categories: OperatingExpenseCategory[];
  allCategories: OperatingExpenseCategory[];
  suppliers: Supplier[];
  expenses: OperatingExpense[];
  filters: ExpenseFilterValues;
  form: ExpenseFormValues;
  showForm: boolean;
  selectedExpense: OperatingExpense | null;
  voidingExpense: OperatingExpense | null;
  voidReason: string;
  isSaving: boolean;
  onFiltersChange: (value: ExpenseFilterValues) => void;
  onApplyFilters: (event: FormEvent<HTMLFormElement>) => void;
  onClearFilters: () => void;
  onFormChange: (value: ExpenseFormValues) => void;
  onShowForm: () => void;
  onHideForm: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onSelectExpense: (expense: OperatingExpense | null) => void;
  onStartVoid: (expense: OperatingExpense) => void;
  onCancelVoid: () => void;
  onVoidReasonChange: (value: string) => void;
  onVoid: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-water-700">Administración</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Gastos registrados
          </h2>
        </div>
        <button
          className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500"
          type="button"
          onClick={onShowForm}
        >
          Nuevo gasto
        </button>
      </div>

      {showForm ? (
        <form
          className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          onSubmit={onSubmit}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">
                Registrar gasto operativo
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                El método de pago es informativo y no mueve dinero.
              </p>
            </div>
            <button
              className="text-sm font-semibold text-slate-600 hover:text-slate-950"
              type="button"
              disabled={isSaving}
              onClick={onHideForm}
            >
              Cerrar
            </button>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <InputField
              label="Fecha *"
              type="date"
              value={form.expenseDate}
              required
              disabled={isSaving}
              onChange={(expenseDate) =>
                onFormChange({ ...form, expenseDate })
              }
            />
            <SelectField
              label="Categoría *"
              value={form.categoryId}
              required
              disabled={isSaving}
              onChange={(categoryId) =>
                onFormChange({ ...form, categoryId })
              }
            >
              <option value="">Selecciona una categoría</option>
              {categories.map((category) => (
                <option value={category.id} key={category.id}>
                  {category.name}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Proveedor"
              value={form.supplierId}
              disabled={isSaving}
              onChange={(supplierId) =>
                onFormChange({ ...form, supplierId })
              }
            >
              <option value="">Sin proveedor</option>
              {suppliers.map((supplier) => (
                <option value={supplier.id} key={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </SelectField>
            <InputField
              label="Descripción *"
              value={form.description}
              required
              disabled={isSaving}
              onChange={(description) =>
                onFormChange({ ...form, description })
              }
            />
            <MoneyField
              label="Monto *"
              value={form.amount}
              disabled={isSaving}
              onChange={(amount) => onFormChange({ ...form, amount })}
            />
            <SelectField
              label="Estado de pago *"
              value={form.paymentStatus}
              disabled={isSaving}
              onChange={(paymentStatus) =>
                onFormChange({
                  ...form,
                  paymentStatus:
                    paymentStatus as OperatingExpensePaymentStatus,
                })
              }
            >
              {paymentStatusOptions()}
            </SelectField>
            <SelectField
              label="Método informativo *"
              value={form.paymentMethod}
              disabled={isSaving}
              onChange={(paymentMethod) =>
                onFormChange({
                  ...form,
                  paymentMethod:
                    paymentMethod as OperatingExpensePaymentMethod,
                })
              }
            >
              {paymentMethodOptions()}
            </SelectField>
            <InputField
              label="Documento"
              value={form.documentNumber}
              disabled={isSaving}
              onChange={(documentNumber) =>
                onFormChange({ ...form, documentNumber })
              }
            />
            <InputField
              label="Vencimiento"
              type="date"
              value={form.dueDate}
              disabled={isSaving}
              onChange={(dueDate) => onFormChange({ ...form, dueDate })}
            />
            <InputField
              label="Fecha de pago"
              type="date"
              value={form.paidDate}
              disabled={isSaving}
              onChange={(paidDate) => onFormChange({ ...form, paidDate })}
            />
          </div>
          <div className="mt-4">
            <TextAreaField
              label="Notas"
              value={form.notes}
              disabled={isSaving}
              onChange={(notes) => onFormChange({ ...form, notes })}
            />
          </div>
          <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-slate-300 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              type="button"
              disabled={isSaving}
              onClick={onHideForm}
            >
              Cancelar
            </button>
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
              type="submit"
              disabled={isSaving}
            >
              {isSaving ? "Guardando..." : "Guardar gasto"}
            </button>
          </div>
        </form>
      ) : null}

      <form
        className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        onSubmit={onApplyFilters}
      >
        <h3 className="font-semibold text-slate-950">Buscar y filtrar</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <InputField
            label="Desde"
            type="date"
            value={filters.dateFrom}
            disabled={false}
            onChange={(dateFrom) =>
              onFiltersChange({ ...filters, dateFrom })
            }
          />
          <InputField
            label="Hasta"
            type="date"
            value={filters.dateTo}
            disabled={false}
            onChange={(dateTo) => onFiltersChange({ ...filters, dateTo })}
          />
          <SelectField
            label="Estado"
            value={filters.status}
            disabled={false}
            onChange={(status) =>
              onFiltersChange({
                ...filters,
                status: status as ExpenseFilterValues["status"],
              })
            }
          >
            <option value="">Todos</option>
            <option value="active">Activos</option>
            <option value="voided">Anulados</option>
          </SelectField>
          <SelectField
            label="Estado de pago"
            value={filters.paymentStatus}
            disabled={false}
            onChange={(paymentStatus) =>
              onFiltersChange({
                ...filters,
                paymentStatus:
                  paymentStatus as ExpenseFilterValues["paymentStatus"],
              })
            }
          >
            <option value="">Todos</option>
            {paymentStatusOptions()}
          </SelectField>
          <SelectField
            label="Categoría"
            value={filters.categoryId}
            disabled={false}
            onChange={(categoryId) =>
              onFiltersChange({ ...filters, categoryId })
            }
          >
            <option value="">Todas</option>
            {allCategories.map((category) => (
              <option value={category.id} key={category.id}>
                {category.name}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Proveedor"
            value={filters.supplierId}
            disabled={false}
            onChange={(supplierId) =>
              onFiltersChange({ ...filters, supplierId })
            }
          >
            <option value="">Todos</option>
            {suppliers.map((supplier) => (
              <option value={supplier.id} key={supplier.id}>
                {supplier.name}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="Método"
            value={filters.paymentMethod}
            disabled={false}
            onChange={(paymentMethod) =>
              onFiltersChange({
                ...filters,
                paymentMethod:
                  paymentMethod as ExpenseFilterValues["paymentMethod"],
              })
            }
          >
            <option value="">Todos</option>
            {paymentMethodOptions()}
          </SelectField>
          <InputField
            label="Buscar"
            value={filters.search}
            placeholder="Número, descripción o documento"
            disabled={false}
            onChange={(search) => onFiltersChange({ ...filters, search })}
          />
        </div>
        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:justify-end">
          <button
            className="h-10 rounded-md border border-slate-300 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            type="button"
            onClick={onClearFilters}
          >
            Limpiar
          </button>
          <button
            className="h-10 rounded-md bg-slate-900 px-4 text-sm font-semibold text-white hover:bg-slate-700"
            type="submit"
          >
            Aplicar filtros
          </button>
        </div>
      </form>

      {canVoid && voidingExpense ? (
        <form
          className="rounded-lg border border-red-200 bg-red-50 p-4"
          onSubmit={onVoid}
        >
          <h3 className="font-semibold text-red-950">
            Anular {voidingExpense.expense_number}
          </h3>
          <p className="mt-1 text-sm text-red-800">
            El registro seguirá visible y no se modificará ningún otro módulo.
          </p>
          <div className="mt-3">
            <TextAreaField
              label="Motivo *"
              value={voidReason}
              disabled={isSaving}
              onChange={onVoidReasonChange}
            />
          </div>
          <div className="mt-3 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-red-200 bg-white px-4 text-sm font-semibold text-red-700"
              type="button"
              disabled={isSaving}
              onClick={onCancelVoid}
            >
              Cancelar
            </button>
            <button
              className="h-10 rounded-md bg-red-700 px-4 text-sm font-semibold text-white disabled:bg-slate-300"
              type="submit"
              disabled={isSaving}
            >
              {isSaving ? "Anulando..." : "Confirmar anulación"}
            </button>
          </div>
        </form>
      ) : null}

      {selectedExpense ? (
        <ExpenseDetail
          expense={selectedExpense}
          onClose={() => onSelectExpense(null)}
        />
      ) : null}

      {expenses.length ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {expenses.map((expense) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={expense.id}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-water-700">
                    {expense.expense_number}
                  </p>
                  <h3 className="mt-1 font-semibold text-slate-950">
                    {expense.description}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    {formatDate(expense.expense_date)} · {expense.category.name}
                  </p>
                </div>
                <p className="text-xl font-semibold text-slate-950">
                  {formatAmount(expense.amount)}
                </p>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <Pill label={OPERATING_EXPENSE_STATUS_LABELS[expense.status]} />
                <Pill
                  label={
                    OPERATING_EXPENSE_PAYMENT_STATUS_LABELS[
                      expense.payment_status
                    ]
                  }
                />
                <Pill
                  label={
                    OPERATING_EXPENSE_PAYMENT_METHOD_LABELS[
                      expense.payment_method
                    ]
                  }
                />
                {expense.recurring_template_id ? (
                  <Pill label="Desde plantilla" />
                ) : null}
              </div>
              <p className="mt-3 text-sm text-slate-600">
                {expense.supplier?.name ?? "Sin proveedor"}
                {expense.document_number
                  ? ` · Documento ${expense.document_number}`
                  : ""}
              </p>
              {expense.status === "voided" ? (
                <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
                  Motivo: {expense.void_reason}
                </p>
              ) : null}
              <div className="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 sm:flex-row sm:justify-end">
                <button
                  className="h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  type="button"
                  onClick={() => onSelectExpense(expense)}
                >
                  Ver detalle
                </button>
                {canVoid && expense.status === "active" ? (
                  <button
                    className="h-9 rounded-md border border-red-200 px-3 text-sm font-semibold text-red-700 hover:bg-red-50"
                    type="button"
                    onClick={() => onStartVoid(expense)}
                  >
                    Anular
                  </button>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState text="No hay gastos que coincidan con los filtros." />
      )}
    </section>
  );
}

function ExpenseDetail({
  expense,
  onClose,
}: {
  expense: OperatingExpense;
  onClose: () => void;
}) {
  const rows = [
    ["Número", expense.expense_number],
    ["Fecha", formatDate(expense.expense_date)],
    ["Categoría", expense.category.name],
    ["Proveedor", expense.supplier?.name ?? "Sin proveedor"],
    ["Monto", formatAmount(expense.amount)],
    [
      "Estado de pago",
      OPERATING_EXPENSE_PAYMENT_STATUS_LABELS[expense.payment_status],
    ],
    [
      "Método",
      OPERATING_EXPENSE_PAYMENT_METHOD_LABELS[expense.payment_method],
    ],
    ["Documento", expense.document_number ?? "No informado"],
    ["Vencimiento", formatOptionalDate(expense.due_date)],
    ["Fecha de pago", formatOptionalDate(expense.paid_date)],
  ] as const;
  return (
    <article className="rounded-lg border border-water-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-water-700">Detalle</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">
            {expense.description}
          </h3>
        </div>
        <button
          className="text-sm font-semibold text-slate-600 hover:text-slate-950"
          type="button"
          onClick={onClose}
        >
          Cerrar
        </button>
      </div>
      <dl className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {label}
            </dt>
            <dd className="mt-1 text-sm text-slate-950">{value}</dd>
          </div>
        ))}
      </dl>
      {expense.notes ? (
        <p className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">
          {expense.notes}
        </p>
      ) : null}
    </article>
  );
}

function RecurringSection({
  categories,
  suppliers,
  templates,
  form,
  showForm,
  isSaving,
  changingId,
  generatingTemplate,
  generateForm,
  onFormChange,
  onShowForm,
  onHideForm,
  onSubmit,
  onToggle,
  onStartGenerate,
  onCancelGenerate,
  onGenerateFormChange,
  onGenerate,
}: {
  categories: OperatingExpenseCategory[];
  suppliers: Supplier[];
  templates: RecurringOperatingExpense[];
  form: TemplateFormValues;
  showForm: boolean;
  isSaving: boolean;
  changingId: number | null;
  generatingTemplate: RecurringOperatingExpense | null;
  generateForm: GenerateFormValues;
  onFormChange: (value: TemplateFormValues) => void;
  onShowForm: () => void;
  onHideForm: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggle: (template: RecurringOperatingExpense) => void;
  onStartGenerate: (template: RecurringOperatingExpense) => void;
  onCancelGenerate: () => void;
  onGenerateFormChange: (value: GenerateFormValues) => void;
  onGenerate: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-water-700">Programación</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Plantillas recurrentes
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Ninguna plantilla crea gastos automáticamente.
          </p>
        </div>
        <button
          className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500"
          type="button"
          onClick={onShowForm}
        >
          Nueva plantilla
        </button>
      </div>

      {showForm ? (
        <form
          className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          onSubmit={onSubmit}
        >
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-lg font-semibold text-slate-950">
              Registrar plantilla
            </h3>
            <button
              className="text-sm font-semibold text-slate-600"
              type="button"
              disabled={isSaving}
              onClick={onHideForm}
            >
              Cerrar
            </button>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <InputField
              label="Nombre *"
              value={form.name}
              required
              disabled={isSaving}
              onChange={(name) => onFormChange({ ...form, name })}
            />
            <SelectField
              label="Categoría *"
              value={form.categoryId}
              required
              disabled={isSaving}
              onChange={(categoryId) =>
                onFormChange({ ...form, categoryId })
              }
            >
              <option value="">Selecciona una categoría</option>
              {categories.map((category) => (
                <option value={category.id} key={category.id}>
                  {category.name}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Proveedor"
              value={form.supplierId}
              disabled={isSaving}
              onChange={(supplierId) =>
                onFormChange({ ...form, supplierId })
              }
            >
              <option value="">Sin proveedor</option>
              {suppliers.map((supplier) => (
                <option value={supplier.id} key={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </SelectField>
            <InputField
              label="Descripción *"
              value={form.description}
              required
              disabled={isSaving}
              onChange={(description) =>
                onFormChange({ ...form, description })
              }
            />
            <MoneyField
              label="Monto *"
              value={form.amount}
              disabled={isSaving}
              onChange={(amount) => onFormChange({ ...form, amount })}
            />
            <SelectField
              label="Frecuencia *"
              value={form.frequency}
              disabled={isSaving}
              onChange={(frequency) =>
                onFormChange({
                  ...form,
                  frequency:
                    frequency as RecurringOperatingExpenseFrequency,
                })
              }
            >
              {frequencyOptions()}
            </SelectField>
            <InputField
              label="Inicio *"
              type="date"
              value={form.startDate}
              required
              disabled={isSaving}
              onChange={(startDate) => onFormChange({ ...form, startDate })}
            />
            <InputField
              label="Fin"
              type="date"
              value={form.endDate}
              disabled={isSaving}
              onChange={(endDate) => onFormChange({ ...form, endDate })}
            />
            <InputField
              label="Próximo vencimiento"
              type="date"
              value={form.nextDueDate}
              disabled={isSaving}
              onChange={(nextDueDate) =>
                onFormChange({ ...form, nextDueDate })
              }
            />
            <SelectField
              label="Método informativo *"
              value={form.paymentMethod}
              disabled={isSaving}
              onChange={(paymentMethod) =>
                onFormChange({
                  ...form,
                  paymentMethod:
                    paymentMethod as OperatingExpensePaymentMethod,
                })
              }
            >
              {paymentMethodOptions()}
            </SelectField>
          </div>
          <div className="mt-4">
            <TextAreaField
              label="Notas"
              value={form.notes}
              disabled={isSaving}
              onChange={(notes) => onFormChange({ ...form, notes })}
            />
          </div>
          <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-slate-300 px-4 text-sm font-semibold text-slate-700"
              type="button"
              disabled={isSaving}
              onClick={onHideForm}
            >
              Cancelar
            </button>
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white hover:bg-water-500 disabled:bg-slate-300"
              type="submit"
              disabled={isSaving}
            >
              {isSaving ? "Guardando..." : "Guardar plantilla"}
            </button>
          </div>
        </form>
      ) : null}

      {generatingTemplate ? (
        <form
          className="rounded-lg border border-amber-200 bg-amber-50 p-5"
          onSubmit={onGenerate}
        >
          <h3 className="font-semibold text-amber-950">
            Generar gasto desde “{generatingTemplate.name}”
          </h3>
          <p className="mt-1 text-sm text-amber-800">
            Se copiarán categoría, proveedor, descripción, monto y método de
            pago. Solo se creará este gasto.
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <InputField
              label="Fecha del gasto *"
              type="date"
              value={generateForm.expenseDate}
              required
              disabled={isSaving}
              onChange={(expenseDate) =>
                onGenerateFormChange({ ...generateForm, expenseDate })
              }
            />
            <InputField
              label="Vencimiento"
              type="date"
              value={generateForm.dueDate}
              disabled={isSaving}
              onChange={(dueDate) =>
                onGenerateFormChange({ ...generateForm, dueDate })
              }
            />
            <InputField
              label="Fecha de pago"
              type="date"
              value={generateForm.paidDate}
              disabled={isSaving}
              onChange={(paidDate) =>
                onGenerateFormChange({ ...generateForm, paidDate })
              }
            />
            <SelectField
              label="Estado de pago"
              value={generateForm.paymentStatus}
              disabled={isSaving}
              onChange={(paymentStatus) =>
                onGenerateFormChange({
                  ...generateForm,
                  paymentStatus:
                    paymentStatus as OperatingExpensePaymentStatus,
                })
              }
            >
              {paymentStatusOptions()}
            </SelectField>
          </div>
          <div className="mt-4">
            <TextAreaField
              label="Notas del gasto"
              value={generateForm.notes}
              disabled={isSaving}
              onChange={(notes) =>
                onGenerateFormChange({ ...generateForm, notes })
              }
            />
          </div>
          <div className="mt-4 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              className="h-10 rounded-md border border-amber-300 bg-white px-4 text-sm font-semibold text-amber-900"
              type="button"
              disabled={isSaving}
              onClick={onCancelGenerate}
            >
              Cancelar
            </button>
            <button
              className="h-10 rounded-md bg-amber-700 px-4 text-sm font-semibold text-white disabled:bg-slate-300"
              type="submit"
              disabled={isSaving}
            >
              {isSaving ? "Generando..." : "Crear gasto manualmente"}
            </button>
          </div>
        </form>
      ) : null}

      {templates.length ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {templates.map((template) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={template.id}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-slate-950">
                    {template.name}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    {template.category.name} ·{" "}
                    {
                      RECURRING_OPERATING_EXPENSE_FREQUENCY_LABELS[
                        template.frequency
                      ]
                    }
                  </p>
                </div>
                <StatusBadge active={template.is_active} />
              </div>
              <p className="mt-3 text-sm text-slate-700">
                {template.description}
              </p>
              <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                <Detail
                  label="Monto"
                  value={formatAmount(template.amount)}
                />
                <Detail
                  label="Proveedor"
                  value={template.supplier?.name ?? "Sin proveedor"}
                />
                <Detail
                  label="Inicio"
                  value={formatDate(template.start_date)}
                />
                <Detail
                  label="Próximo vencimiento"
                  value={formatOptionalDate(template.next_due_date)}
                />
                <Detail
                  label="Método"
                  value={
                    OPERATING_EXPENSE_PAYMENT_METHOD_LABELS[
                      template.payment_method
                    ]
                  }
                />
              </dl>
              <div className="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 sm:flex-row sm:justify-end">
                {template.is_active ? (
                  <button
                    className="h-9 rounded-md bg-water-700 px-3 text-sm font-semibold text-white hover:bg-water-500"
                    type="button"
                    onClick={() => onStartGenerate(template)}
                  >
                    Generar gasto
                  </button>
                ) : null}
                <button
                  className={
                    template.is_active
                      ? "h-9 rounded-md border border-red-200 px-3 text-sm font-semibold text-red-700 hover:bg-red-50"
                      : "h-9 rounded-md border border-emerald-200 px-3 text-sm font-semibold text-emerald-700 hover:bg-emerald-50"
                  }
                  type="button"
                  disabled={changingId === template.id}
                  onClick={() => onToggle(template)}
                >
                  {changingId === template.id
                    ? "Guardando..."
                    : template.is_active
                      ? "Desactivar"
                      : "Activar"}
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState text="Todavía no hay plantillas recurrentes." />
      )}
    </section>
  );
}

function SectionButton({
  active,
  label,
  count,
  onClick,
}: {
  active: boolean;
  label: string;
  count: number;
  onClick: () => void;
}) {
  return (
    <button
      className={
        active
          ? "rounded-md bg-water-700 px-4 py-3 text-left text-sm font-semibold text-white"
          : "rounded-md px-4 py-3 text-left text-sm font-semibold text-slate-700 hover:bg-slate-50"
      }
      type="button"
      onClick={onClick}
    >
      {label} <span className="ml-1 opacity-70">({count})</span>
    </button>
  );
}

function InputField({
  label,
  value,
  onChange,
  disabled,
  required = false,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
  required?: boolean;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        type={type}
        value={value}
        required={required}
        placeholder={placeholder}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function MoneyField({
  label,
  value,
  onChange,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        inputMode="decimal"
        value={value}
        required
        placeholder="0.00"
        disabled={disabled}
        onChange={(event) => {
          if (isValidMoneyInputDraft(event.target.value)) {
            onChange(event.target.value);
          }
        }}
      />
    </label>
  );
}

function TextAreaField({
  label,
  value,
  onChange,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <textarea
        className="mt-1 min-h-20 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  disabled,
  required = false,
  children,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <select
        className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:bg-slate-100"
        value={value}
        required={required}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      >
        {children}
      </select>
    </label>
  );
}

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={
        active
          ? "shrink-0 rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700"
          : "shrink-0 rounded-full bg-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700"
      }
    >
      {active ? "Activa" : "Inactiva"}
    </span>
  );
}

function Pill({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
      {label}
    </span>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </dt>
      <dd className="mt-1 text-slate-950">{value}</dd>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <p className="rounded-lg border border-dashed border-slate-300 bg-white px-5 py-8 text-center text-sm text-slate-600">
      {text}
    </p>
  );
}

function paymentStatusOptions() {
  return (
    <>
      {(
        Object.entries(OPERATING_EXPENSE_PAYMENT_STATUS_LABELS) as Array<
          [OperatingExpensePaymentStatus, string]
        >
      ).map(([value, label]) => (
        <option value={value} key={value}>
          {label}
        </option>
      ))}
    </>
  );
}

function paymentMethodOptions() {
  return (
    <>
      {(
        Object.entries(OPERATING_EXPENSE_PAYMENT_METHOD_LABELS) as Array<
          [OperatingExpensePaymentMethod, string]
        >
      ).map(([value, label]) => (
        <option value={value} key={value}>
          {label}
        </option>
      ))}
    </>
  );
}

function frequencyOptions() {
  return (
    <>
      {(
        Object.entries(
          RECURRING_OPERATING_EXPENSE_FREQUENCY_LABELS,
        ) as Array<[RecurringOperatingExpenseFrequency, string]>
      ).map(([value, label]) => (
        <option value={value} key={value}>
          {label}
        </option>
      ))}
    </>
  );
}

function createEmptyExpenseForm(): ExpenseFormValues {
  return {
    expenseDate: todayISODate(),
    categoryId: "",
    supplierId: "",
    description: "",
    amount: "",
    paymentStatus: "unpaid",
    paymentMethod: "unknown",
    documentNumber: "",
    dueDate: "",
    paidDate: "",
    notes: "",
  };
}

function createEmptyTemplateForm(): TemplateFormValues {
  return {
    name: "",
    categoryId: "",
    supplierId: "",
    description: "",
    amount: "",
    frequency: "monthly",
    startDate: todayISODate(),
    endDate: "",
    nextDueDate: "",
    paymentMethod: "unknown",
    notes: "",
  };
}

function createEmptyGenerateForm(): GenerateFormValues {
  return {
    expenseDate: todayISODate(),
    dueDate: "",
    paidDate: "",
    paymentStatus: "unpaid",
    notes: "",
  };
}

function validateExpenseForm(
  form: ExpenseFormValues,
  categories: OperatingExpenseCategory[],
): string {
  if (!form.expenseDate) {
    return "La fecha del gasto es obligatoria.";
  }
  const category = categories.find(
    (item) => item.id === Number(form.categoryId),
  );
  if (!category || !category.is_active) {
    return "Selecciona una categoría activa.";
  }
  if (!form.description.trim()) {
    return "La descripción del gasto es obligatoria.";
  }
  const amountCents = parseMoneyInputToCents(form.amount);
  if (amountCents === null || amountCents <= 0) {
    return "El monto debe ser mayor a cero y tener hasta dos decimales.";
  }
  return "";
}

function validateTemplateForm(
  form: TemplateFormValues,
  categories: OperatingExpenseCategory[],
): string {
  if (!form.name.trim()) {
    return "El nombre de la plantilla es obligatorio.";
  }
  const category = categories.find(
    (item) => item.id === Number(form.categoryId),
  );
  if (!category || !category.is_active) {
    return "Selecciona una categoría activa.";
  }
  if (!form.description.trim()) {
    return "La descripción de la plantilla es obligatoria.";
  }
  const amountCents = parseMoneyInputToCents(form.amount);
  if (amountCents === null || amountCents <= 0) {
    return "El monto debe ser mayor a cero y tener hasta dos decimales.";
  }
  if (!form.startDate) {
    return "La fecha de inicio es obligatoria.";
  }
  if (form.endDate && form.startDate > form.endDate) {
    return "La fecha final no puede ser anterior al inicio.";
  }
  if (form.nextDueDate && form.nextDueDate < form.startDate) {
    return "El próximo vencimiento no puede ser anterior al inicio.";
  }
  if (
    form.nextDueDate &&
    form.endDate &&
    form.nextDueDate > form.endDate
  ) {
    return "El próximo vencimiento no puede ser posterior a la fecha final.";
  }
  return "";
}

function toExpenseFilters(
  filters: ExpenseFilterValues,
): OperatingExpenseFilters {
  return {
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.paymentStatus
      ? { payment_status: filters.paymentStatus }
      : {}),
    ...(filters.categoryId
      ? { category_id: Number(filters.categoryId) }
      : {}),
    ...(filters.supplierId
      ? { supplier_id: Number(filters.supplierId) }
      : {}),
    ...(filters.paymentMethod
      ? { payment_method: filters.paymentMethod }
      : {}),
    ...(filters.search.trim() ? { search: filters.search.trim() } : {}),
  };
}

function toSummaryFilters(filters: ExpenseFilterValues) {
  return {
    ...(filters.dateFrom ? { date_from: filters.dateFrom } : {}),
    ...(filters.dateTo ? { date_to: filters.dateTo } : {}),
    ...(filters.categoryId
      ? { category_id: Number(filters.categoryId) }
      : {}),
    ...(filters.supplierId
      ? { supplier_id: Number(filters.supplierId) }
      : {}),
  };
}

function normalizeMoney(value: string): string {
  return value.trim().replace(",", ".");
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function optionalId(value: string): number | null {
  return value ? Number(value) : null;
}

function todayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function formatAmount(value: string): string {
  return `$${value}`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC").format(
    new Date(`${value}T00:00:00`),
  );
}

function formatOptionalDate(value: string | null): string {
  return value ? formatDate(value) : "No informado";
}

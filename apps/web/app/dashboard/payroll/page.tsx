"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  addPayrollItem,
  approvePayrollRun,
  cancelPayrollRun,
  createPayrollRun,
  getPayrollRun,
  listEmployeeAdvances,
  listEmployeeLoans,
  listEmployees,
  listPayrollRuns,
  markPayrollRunPaid,
  previewPayrollRun,
  updatePayrollItem,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import {
  isValidMoneyInputDraft,
  parseMoneyInputToCents,
} from "@/lib/money";
import { getPayrollRunActions } from "@/lib/payrollWorkflow";
import type { Employee } from "@/types/employee";
import type { EmployeeAdvance, EmployeeLoan } from "@/types/employeeControls";
import {
  PAYROLL_STATUS_LABELS,
  type PayrollCalculatedItem,
  type PayrollItemPayload,
  type PayrollPreview,
  type PayrollRun,
  type PayrollRunFilters,
  type PayrollRunSummary,
  type PayrollStatus,
} from "@/types/payroll";

type EmployeeDraft = {
  selected: boolean;
  baseSalary: string;
  bonusAmount: string;
  otherIncomeAmount: string;
  otherDeductionsAmount: string;
  advanceIds: number[];
  loanAmounts: Record<number, string>;
  notes: string;
};

type PayrollPeriod = {
  periodStart: string;
  periodEnd: string;
  payrollDate: string;
  label: string;
  notes: string;
};

type FilterDraft = {
  dateFrom: string;
  dateTo: string;
  status: "" | PayrollStatus;
  employeeId: string;
  search: string;
};

const emptyFilters: FilterDraft = {
  dateFrom: "",
  dateTo: "",
  status: "",
  employeeId: "",
  search: "",
};

export default function PayrollPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [advances, setAdvances] = useState<EmployeeAdvance[]>([]);
  const [loans, setLoans] = useState<EmployeeLoan[]>([]);
  const [runs, setRuns] = useState<PayrollRunSummary[]>([]);
  const [drafts, setDrafts] = useState<Record<number, EmployeeDraft>>({});
  const [period, setPeriod] = useState<PayrollPeriod>(createDefaultPeriod);
  const [preview, setPreview] = useState<PayrollPreview | null>(null);
  const [selectedRun, setSelectedRun] = useState<PayrollRun | null>(null);
  const [filters, setFilters] = useState<FilterDraft>(emptyFilters);
  const [cancelReason, setCancelReason] = useState("");
  const [addEmployeeId, setAddEmployeeId] = useState("");
  const [editingItemId, setEditingItemId] = useState<number | null>(null);
  const [editDraft, setEditDraft] = useState<EmployeeDraft | null>(null);
  const [correctionReason, setCorrectionReason] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const selectedEmployees = useMemo(
    () => employees.filter((employee) => drafts[employee.id]?.selected),
    [drafts, employees],
  );

  const employeesAvailableForRun = useMemo(() => {
    if (!selectedRun) {
      return [];
    }
    const existingIds = new Set(
      selectedRun.items.map((item) => item.employee_id),
    );
    return employees.filter((employee) => !existingIds.has(employee.id));
  }, [employees, selectedRun]);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    void loadInitial(storedToken);
  }, [router]);

  async function loadInitial(activeToken: string) {
    setIsLoading(true);
    clearNotices();
    try {
      const [loadedEmployees, loadedAdvances, loadedLoans, loadedRuns] =
        await Promise.all([
          listEmployees(activeToken, { is_active: true }),
          listEmployeeAdvances(activeToken, { status: "active" }),
          listEmployeeLoans(activeToken, { status: "active" }),
          listPayrollRuns(activeToken),
        ]);
      setEmployees(loadedEmployees);
      setAdvances(loadedAdvances);
      setLoans(loadedLoans);
      setRuns(loadedRuns);
      setDrafts(createDrafts(loadedEmployees));
    } catch (loadError) {
      handleError(loadError, "No se pudo cargar el módulo de roles de pago.");
    } finally {
      setIsLoading(false);
    }
  }

  async function refreshFinancialSources(activeToken: string) {
    const [loadedAdvances, loadedLoans] = await Promise.all([
      listEmployeeAdvances(activeToken, { status: "active" }),
      listEmployeeLoans(activeToken, { status: "active" }),
    ]);
    setAdvances(loadedAdvances);
    setLoans(loadedLoans);
  }

  function updatePeriod(field: keyof PayrollPeriod, value: string) {
    setPeriod((current) => ({ ...current, [field]: value }));
    setPreview(null);
  }

  function updateDraft(
    employeeId: number,
    updater: (draft: EmployeeDraft) => EmployeeDraft,
  ) {
    setDrafts((current) => ({
      ...current,
      [employeeId]: updater(
        current[employeeId] ??
          createEmployeeDraft(
            employees.find((employee) => employee.id === employeeId)
              ?.base_salary ?? "0.00",
          ),
      ),
    }));
    setPreview(null);
  }

  function updateMoneyField(
    employeeId: number,
    field:
      | "baseSalary"
      | "bonusAmount"
      | "otherIncomeAmount"
      | "otherDeductionsAmount",
    value: string,
  ) {
    if (!isValidMoneyInputDraft(value)) {
      return;
    }
    updateDraft(employeeId, (draft) => ({ ...draft, [field]: value }));
  }

  function toggleEmployee(employee: Employee) {
    updateDraft(employee.id, (draft) => ({
      ...draft,
      selected: !draft.selected,
      baseSalary: draft.baseSalary || employee.base_salary,
    }));
  }

  function toggleAdvance(employeeId: number, advanceId: number) {
    updateDraft(employeeId, (draft) => ({
      ...draft,
      advanceIds: draft.advanceIds.includes(advanceId)
        ? draft.advanceIds.filter((id) => id !== advanceId)
        : [...draft.advanceIds, advanceId],
    }));
  }

  function updateLoanAmount(
    employeeId: number,
    loanId: number,
    value: string,
  ) {
    if (!isValidMoneyInputDraft(value)) {
      return;
    }
    updateDraft(employeeId, (draft) => ({
      ...draft,
      loanAmounts: { ...draft.loanAmounts, [loanId]: value },
    }));
  }

  async function handlePreview() {
    if (!token) {
      return;
    }
    clearNotices();
    let items: PayrollItemPayload[];
    try {
      validatePeriod(period);
      items = buildItems(
        selectedEmployees,
        drafts,
        advances,
        loans,
      );
    } catch (validationError) {
      setError(getErrorMessage(validationError));
      return;
    }
    setIsSaving(true);
    try {
      const calculated = await previewPayrollRun(token, {
        period_start: period.periodStart,
        period_end: period.periodEnd,
        employee_ids: selectedEmployees.map((employee) => employee.id),
        items,
      });
      setPreview(calculated);
      setMessage(
        "Vista previa calculada por el backend. El neto no se captura manualmente.",
      );
    } catch (previewError) {
      handleError(previewError, "No se pudo generar la vista previa.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleCreate() {
    if (!token) {
      return;
    }
    clearNotices();
    let items: PayrollItemPayload[] = [];
    try {
      validatePeriod(period);
      if (!period.label.trim()) {
        throw new Error("La etiqueta del período es obligatoria.");
      }
      if (selectedEmployees.length > 0) {
        if (!preview) {
          throw new Error(
            "Genera la vista previa antes de crear un borrador con empleados.",
          );
        }
        items = buildItems(
          selectedEmployees,
          drafts,
          advances,
          loans,
        );
      }
    } catch (validationError) {
      setError(getErrorMessage(validationError));
      return;
    }
    setIsSaving(true);
    try {
      const created = await createPayrollRun(token, {
        period_start: period.periodStart,
        period_end: period.periodEnd,
        payroll_date: period.payrollDate,
        label: period.label.trim(),
        notes: optionalText(period.notes),
        employee_ids: selectedEmployees.map((employee) => employee.id),
        items,
      });
      setRuns(await listPayrollRuns(token, toFilters(filters)));
      setSelectedRun(created);
      setPreview(null);
      setDrafts(createDrafts(employees));
      setMessage(`Borrador creado: ${created.payroll_number}.`);
    } catch (createError) {
      handleError(createError, "No se pudo crear el rol de pago.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    if (
      filters.dateFrom &&
      filters.dateTo &&
      filters.dateTo < filters.dateFrom
    ) {
      setError("La fecha final no puede ser menor que la fecha inicial.");
      return;
    }
    setIsLoading(true);
    clearNotices();
    try {
      setRuns(await listPayrollRuns(token, toFilters(filters)));
    } catch (filterError) {
      handleError(filterError, "No se pudieron aplicar los filtros.");
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
      setRuns(await listPayrollRuns(token));
    } catch (filterError) {
      handleError(filterError, "No se pudieron limpiar los filtros.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleOpenDetail(payrollRunId: number) {
    if (!token) {
      return;
    }
    setIsLoadingDetail(true);
    clearNotices();
    try {
      setSelectedRun(await getPayrollRun(token, payrollRunId));
      resetDetailForms();
    } catch (detailError) {
      handleError(detailError, "No se pudo cargar el detalle del rol.");
    } finally {
      setIsLoadingDetail(false);
    }
  }

  async function updateSelectedRun(
    operation: () => Promise<PayrollRun>,
    successMessage: string,
    refreshSources = false,
  ) {
    if (!token) {
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const updated = await operation();
      setSelectedRun(updated);
      setRuns(await listPayrollRuns(token, toFilters(filters)));
      if (refreshSources) {
        await refreshFinancialSources(token);
      }
      resetDetailForms();
      setMessage(successMessage);
    } catch (operationError) {
      handleError(operationError, "No se pudo completar la acción.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleAddEmployee() {
    if (!token || !selectedRun || !addEmployeeId) {
      setError("Selecciona el empleado que deseas agregar.");
      return;
    }
    const employee = employees.find(
      (candidate) => candidate.id === Number(addEmployeeId),
    );
    if (!employee) {
      setError("El empleado seleccionado no está disponible.");
      return;
    }
    await updateSelectedRun(
      () =>
        addPayrollItem(
          token,
          selectedRun.id,
          draftToPayload(
            employee.id,
            createEmployeeDraft(employee.base_salary),
            loans,
          ),
        ),
      "Empleado agregado al borrador.",
    );
  }

  function startEditing(item: PayrollCalculatedItem) {
    setEditingItemId(item.id ?? null);
    setEditDraft(itemToDraft(item));
    setCorrectionReason("");
    clearNotices();
  }

  async function handleUpdateItem(item: PayrollCalculatedItem) {
    if (!token || item.id === undefined || !editDraft) {
      return;
    }
    if (!correctionReason.trim()) {
      setError("El motivo de corrección es obligatorio.");
      return;
    }
    let payload: PayrollItemPayload;
    try {
      payload = draftToPayload(item.employee_id, editDraft, loans);
    } catch (validationError) {
      setError(getErrorMessage(validationError));
      return;
    }
    await updateSelectedRun(
      () =>
        updatePayrollItem(token, item.id!, {
          ...withoutEmployeeId(payload),
          correction_reason: correctionReason.trim(),
        }),
      "Ítem actualizado y auditado.",
    );
  }

  async function handleApprove() {
    if (!token || !selectedRun) {
      return;
    }
    await updateSelectedRun(
      () => approvePayrollRun(token, selectedRun.id),
      "Rol de pago aprobado correctamente.",
    );
  }

  async function handleMarkPaid() {
    if (!token || !selectedRun) {
      return;
    }
    const confirmed = window.confirm(
      "Esta acción aplicará los anticipos y abonos de préstamos. Confirma solo si George autorizó marcar este rol como pagado.",
    );
    if (!confirmed) {
      return;
    }
    await updateSelectedRun(
      () => markPayrollRunPaid(token, selectedRun.id),
      "Rol de pago marcado como pagado correctamente.",
      true,
    );
  }

  async function handleCancel() {
    if (!token || !selectedRun) {
      return;
    }
    if (!cancelReason.trim()) {
      setError("El motivo de cancelación es obligatorio.");
      return;
    }
    await updateSelectedRun(
      () => cancelPayrollRun(token, selectedRun.id, cancelReason.trim()),
      "Rol de pago cancelado correctamente.",
      true,
    );
  }

  function resetDetailForms() {
    setCancelReason("");
    setAddEmployeeId("");
    setEditingItemId(null);
    setEditDraft(null);
    setCorrectionReason("");
  }

  function clearNotices() {
    setError("");
    setMessage("");
  }

  function handleError(possibleError: unknown, fallback: string) {
    if (possibleError instanceof ApiError && possibleError.status === 401) {
      removeToken();
      router.replace("/login");
      return;
    }
    setError(getErrorMessage(possibleError, fallback));
  }

  if (isLoading && employees.length === 0 && runs.length === 0) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6">
        <div className="mx-auto w-full max-w-7xl">
          <LoadingState label="Cargando roles de pago..." />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Link className="text-sm font-medium text-water-700" href="/dashboard">
              ← Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Roles de pago
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Nómina interna base con sueldo, ingresos, anticipos, préstamos,
              descuentos y neto calculado por el backend.
            </p>
          </div>
          <LogoutButton />
        </header>

        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
          Este bloque no calcula IESS, décimos, vacaciones, fondos de reserva,
          horas extra ni liquidaciones. Marcar pagado no mueve caja o banco,
          pero sí aplica los descuentos internos vinculados.
        </div>
        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            {message}
          </p>
        ) : null}

        <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-medium text-water-700">Nuevo período</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Crear rol en borrador
            </h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <TextField
              label="Etiqueta"
              onChange={(value) => updatePeriod("label", value)}
              placeholder="Ej. Julio 2026"
              value={period.label}
            />
            <DateField
              label="Período desde"
              onChange={(value) => updatePeriod("periodStart", value)}
              value={period.periodStart}
            />
            <DateField
              label="Período hasta"
              onChange={(value) => updatePeriod("periodEnd", value)}
              value={period.periodEnd}
            />
            <DateField
              label="Fecha del rol"
              onChange={(value) => updatePeriod("payrollDate", value)}
              value={period.payrollDate}
            />
            <TextField
              label="Notas generales"
              onChange={(value) => updatePeriod("notes", value)}
              value={period.notes}
            />
          </div>

          {employees.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">
              No hay empleados activos. También puedes crear el período vacío
              y agregar empleados después.
            </p>
          ) : (
            <div className="space-y-3">
              {employees.map((employee) => {
                const draft =
                  drafts[employee.id] ??
                  createEmployeeDraft(employee.base_salary);
                return (
                  <EmployeeDraftCard
                    advances={advances.filter(
                      (advance) => advance.employee_id === employee.id,
                    )}
                    draft={draft}
                    employee={employee}
                    key={employee.id}
                    loans={loans.filter(
                      (loan) => loan.employee_id === employee.id,
                    )}
                    onMoneyChange={(field, value) =>
                      updateMoneyField(employee.id, field, value)
                    }
                    onNotesChange={(value) =>
                      updateDraft(employee.id, (current) => ({
                        ...current,
                        notes: value,
                      }))
                    }
                    onToggle={() => toggleEmployee(employee)}
                    onToggleAdvance={(advanceId) =>
                      toggleAdvance(employee.id, advanceId)
                    }
                    onUpdateLoan={(loanId, value) =>
                      updateLoanAmount(employee.id, loanId, value)
                    }
                  />
                );
              })}
            </div>
          )}

          <p className="text-xs text-slate-500">
            El neto a pagar se calcula automáticamente. Puedes crear un período
            vacío o agregar empleados antes de guardarlo.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              className={secondaryButtonClass}
              disabled={isSaving || selectedEmployees.length === 0}
              onClick={handlePreview}
              type="button"
            >
              {isSaving ? "Calculando..." : "Calcular vista previa"}
            </button>
            <button
              className={primaryButtonClass}
              disabled={isSaving}
              onClick={handleCreate}
              type="button"
            >
              Crear borrador
            </button>
          </div>
        </section>

        {preview ? <PayrollPreviewCard preview={preview} /> : null}

        <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-medium text-water-700">Historial</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Roles registrados
            </h2>
          </div>
          <form
            className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6"
            onSubmit={handleFilters}
          >
            <DateField
              label="Desde"
              onChange={(value) =>
                setFilters((current) => ({ ...current, dateFrom: value }))
              }
              value={filters.dateFrom}
            />
            <DateField
              label="Hasta"
              onChange={(value) =>
                setFilters((current) => ({ ...current, dateTo: value }))
              }
              value={filters.dateTo}
            />
            <label className="text-sm font-medium text-slate-700">
              Estado
              <select
                className={inputClass}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    status: event.target.value as "" | PayrollStatus,
                  }))
                }
                value={filters.status}
              >
                <option value="">Todos</option>
                {Object.entries(PAYROLL_STATUS_LABELS).map(
                  ([status, label]) => (
                    <option key={status} value={status}>
                      {label}
                    </option>
                  ),
                )}
              </select>
            </label>
            <label className="text-sm font-medium text-slate-700">
              Empleado
              <select
                className={inputClass}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    employeeId: event.target.value,
                  }))
                }
                value={filters.employeeId}
              >
                <option value="">Todos</option>
                {employees.map((employee) => (
                  <option key={employee.id} value={employee.id}>
                    {employee.first_name} {employee.last_name}
                  </option>
                ))}
              </select>
            </label>
            <TextField
              label="Buscar"
              onChange={(value) =>
                setFilters((current) => ({ ...current, search: value }))
              }
              placeholder="Número, etiqueta o empleado"
              value={filters.search}
            />
            <div className="flex items-end gap-2">
              <button className={secondaryButtonClass} type="submit">
                Filtrar
              </button>
              <button
                className={plainButtonClass}
                onClick={clearFilters}
                type="button"
              >
                Limpiar
              </button>
            </div>
          </form>

          {isLoading ? (
            <LoadingState label="Cargando roles..." />
          ) : runs.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">
              No hay roles para los filtros seleccionados.
            </p>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {runs.map((run) => (
                <article
                  className="rounded-lg border border-slate-200 p-4"
                  key={run.id}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-semibold text-slate-950">
                        {run.label}
                      </h3>
                      <p className="mt-1 text-xs text-slate-500">
                        {run.payroll_number}
                      </p>
                      <p className="mt-1 text-sm text-slate-500">
                        {run.period_start} a {run.period_end}
                      </p>
                    </div>
                    <PayrollStatusBadge status={run.status} />
                  </div>
                  <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <TotalCell
                      label="Empleados"
                      value={String(run.employees_count)}
                    />
                    <TotalCell label="Fecha" value={run.payroll_date} />
                    <TotalCell
                      label="Descuentos"
                      value={money(run.total_deductions)}
                    />
                    <TotalCell label="Neto" value={money(run.net_pay_total)} />
                  </dl>
                  <button
                    className={`${secondaryButtonClass} mt-4 w-full`}
                    disabled={isLoadingDetail}
                    onClick={() => handleOpenDetail(run.id)}
                    type="button"
                  >
                    Ver detalle
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>

        {selectedRun ? (
          <PayrollDetail
            addEmployeeId={addEmployeeId}
            advances={advances}
            cancelReason={cancelReason}
            correctionReason={correctionReason}
            editDraft={editDraft}
            editingItemId={editingItemId}
            employeesAvailable={employeesAvailableForRun}
            isSaving={isSaving}
            loans={loans}
            onAddEmployee={handleAddEmployee}
            onApprove={handleApprove}
            onCancel={handleCancel}
            onClose={() => {
              setSelectedRun(null);
              resetDetailForms();
            }}
            onEditDraftChange={setEditDraft}
            onEditItem={startEditing}
            onMarkPaid={handleMarkPaid}
            onSaveItem={handleUpdateItem}
            run={selectedRun}
            setAddEmployeeId={setAddEmployeeId}
            setCancelReason={setCancelReason}
            setCorrectionReason={setCorrectionReason}
          />
        ) : null}
      </div>
    </main>
  );
}

function EmployeeDraftCard({
  employee,
  draft,
  advances,
  loans,
  onToggle,
  onMoneyChange,
  onNotesChange,
  onToggleAdvance,
  onUpdateLoan,
}: {
  employee: Employee;
  draft: EmployeeDraft;
  advances: EmployeeAdvance[];
  loans: EmployeeLoan[];
  onToggle: () => void;
  onMoneyChange: (
    field:
      | "baseSalary"
      | "bonusAmount"
      | "otherIncomeAmount"
      | "otherDeductionsAmount",
    value: string,
  ) => void;
  onNotesChange: (value: string) => void;
  onToggleAdvance: (advanceId: number) => void;
  onUpdateLoan: (loanId: number, value: string) => void;
}) {
  return (
    <article
      className={`rounded-lg border p-4 ${
        draft.selected
          ? "border-water-500 bg-water-50/40"
          : "border-slate-200"
      }`}
    >
      <label className="flex cursor-pointer items-start gap-3">
        <input
          checked={draft.selected}
          className="mt-1 h-4 w-4"
          onChange={onToggle}
          type="checkbox"
        />
        <span>
          <span className="block font-semibold text-slate-950">
            {employee.first_name} {employee.last_name}
          </span>
          <span className="mt-1 block text-sm text-slate-600">
            {employee.job_position ?? "Sin cargo"} · Sueldo registrado{" "}
            {money(employee.base_salary)} · {employee.payment_frequency}
          </span>
        </span>
      </label>
      {draft.selected ? (
        <div className="mt-4 space-y-4 border-t border-slate-200 pt-4">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <MoneyField
              label="Sueldo base"
              onChange={(value) => onMoneyChange("baseSalary", value)}
              value={draft.baseSalary}
            />
            <MoneyField
              label="Bonos"
              onChange={(value) => onMoneyChange("bonusAmount", value)}
              value={draft.bonusAmount}
            />
            <MoneyField
              label="Otros ingresos"
              onChange={(value) => onMoneyChange("otherIncomeAmount", value)}
              value={draft.otherIncomeAmount}
            />
            <MoneyField
              label="Otros descuentos"
              onChange={(value) =>
                onMoneyChange("otherDeductionsAmount", value)
              }
              value={draft.otherDeductionsAmount}
            />
            <TextField
              label="Observación"
              onChange={onNotesChange}
              value={draft.notes}
            />
          </div>
          <DeductionInputs
            advances={advances}
            draft={draft}
            loans={loans}
            onToggleAdvance={onToggleAdvance}
            onUpdateLoan={onUpdateLoan}
          />
        </div>
      ) : null}
    </article>
  );
}

function DeductionInputs({
  advances,
  loans,
  draft,
  onToggleAdvance,
  onUpdateLoan,
}: {
  advances: EmployeeAdvance[];
  loans: EmployeeLoan[];
  draft: EmployeeDraft;
  onToggleAdvance: (advanceId: number) => void;
  onUpdateLoan: (loanId: number, value: string) => void;
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-md border border-slate-200 bg-white p-3">
        <p className="text-sm font-semibold text-slate-900">
          Anticipos activos
        </p>
        {advances.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">Sin anticipos activos.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {advances.map((advance) => (
              <label
                className="flex items-start justify-between gap-3 text-sm"
                key={advance.id}
              >
                <span>
                  {advance.advance_number} · {money(advance.amount)}
                </span>
                <input
                  checked={draft.advanceIds.includes(advance.id)}
                  onChange={() => onToggleAdvance(advance.id)}
                  type="checkbox"
                />
              </label>
            ))}
          </div>
        )}
      </div>
      <div className="rounded-md border border-slate-200 bg-white p-3">
        <p className="text-sm font-semibold text-slate-900">
          Préstamos activos
        </p>
        {loans.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">Sin préstamos activos.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {loans.map((loan) => (
              <label
                className="grid grid-cols-[1fr_8rem] items-center gap-3 text-sm"
                key={loan.id}
              >
                <span>
                  {loan.loan_number} · saldo {money(loan.balance_amount)}
                </span>
                <input
                  className={compactInputClass}
                  inputMode="decimal"
                  onChange={(event) =>
                    onUpdateLoan(loan.id, event.target.value)
                  }
                  placeholder="0.00"
                  value={draft.loanAmounts[loan.id] ?? ""}
                />
              </label>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function PayrollPreviewCard({ preview }: { preview: PayrollPreview }) {
  return (
    <section className="space-y-4 rounded-lg border border-water-200 bg-white p-4 shadow-sm">
      <div>
        <p className="text-sm font-medium text-water-700">Vista previa oficial</p>
        <h2 className="mt-1 text-lg font-semibold text-slate-950">
          Totales calculados por backend
        </h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        <TotalCard label="Empleados" value={String(preview.employees_count)} />
        <TotalCard label="Ingresos" value={money(preview.gross_total)} />
        <TotalCard label="Bonos" value={money(preview.bonuses_total)} />
        <TotalCard
          label="Anticipos"
          value={money(preview.advances_deducted_total)}
        />
        <TotalCard
          label="Préstamos"
          value={money(preview.loan_deductions_total)}
        />
        <TotalCard
          label="Descuentos"
          value={money(preview.total_deductions)}
        />
        <TotalCard label="Neto a pagar" value={money(preview.net_pay_total)} />
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">Empleado</th>
              <th className="px-3 py-2">Sueldo</th>
              <th className="px-3 py-2">Ingresos</th>
              <th className="px-3 py-2">Anticipos</th>
              <th className="px-3 py-2">Préstamos</th>
              <th className="px-3 py-2">Descuentos</th>
              <th className="px-3 py-2">Neto</th>
            </tr>
          </thead>
          <tbody>
            {preview.items.map((item) => (
              <tr className="border-b border-slate-100" key={item.employee_id}>
                <td className="px-3 py-3 font-medium text-slate-900">
                  {item.employee_name_snapshot}
                </td>
                <td className="px-3 py-3">{money(item.base_salary_amount)}</td>
                <td className="px-3 py-3">{money(item.gross_amount)}</td>
                <td className="px-3 py-3">
                  {money(item.advances_deducted_amount)}
                </td>
                <td className="px-3 py-3">
                  {money(item.loan_deductions_amount)}
                </td>
                <td className="px-3 py-3">
                  {money(item.total_deductions_amount)}
                </td>
                <td className="px-3 py-3 font-semibold text-water-700">
                  {money(item.net_pay_amount)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PayrollDetail({
  run,
  employeesAvailable,
  advances,
  loans,
  addEmployeeId,
  setAddEmployeeId,
  cancelReason,
  setCancelReason,
  editingItemId,
  editDraft,
  onEditDraftChange,
  correctionReason,
  setCorrectionReason,
  isSaving,
  onAddEmployee,
  onEditItem,
  onSaveItem,
  onApprove,
  onMarkPaid,
  onCancel,
  onClose,
}: {
  run: PayrollRun;
  employeesAvailable: Employee[];
  advances: EmployeeAdvance[];
  loans: EmployeeLoan[];
  addEmployeeId: string;
  setAddEmployeeId: (value: string) => void;
  cancelReason: string;
  setCancelReason: (value: string) => void;
  editingItemId: number | null;
  editDraft: EmployeeDraft | null;
  onEditDraftChange: (value: EmployeeDraft | null) => void;
  correctionReason: string;
  setCorrectionReason: (value: string) => void;
  isSaving: boolean;
  onAddEmployee: () => void;
  onEditItem: (item: PayrollCalculatedItem) => void;
  onSaveItem: (item: PayrollCalculatedItem) => void;
  onApprove: () => void;
  onMarkPaid: () => void;
  onCancel: () => void;
  onClose: () => void;
}) {
  const actions = getPayrollRunActions(run.status, run.items.length);

  return (
    <section className="space-y-5 rounded-lg border border-slate-300 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-water-700">Detalle del rol</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            {run.label}
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            {run.payroll_number} · {run.period_start} a {run.period_end}
          </p>
        </div>
        <button className={plainButtonClass} onClick={onClose} type="button">
          Cerrar
        </button>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <TotalCard label="Estado" value={PAYROLL_STATUS_LABELS[run.status]} />
        <TotalCard label="Empleados" value={String(run.employees_count)} />
        <TotalCard label="Ingresos" value={money(run.gross_total)} />
        <TotalCard label="Descuentos" value={money(run.total_deductions)} />
        <TotalCard label="Neto" value={money(run.net_pay_total)} />
      </div>

      {actions.canAddEmployee ? (
        <div className="rounded-lg border border-water-200 bg-water-50/40 p-4">
          <p className="text-sm font-semibold text-slate-900">
            Agregar empleado al borrador
          </p>
          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <select
              className={`${inputClass} mt-0 flex-1`}
              onChange={(event) => setAddEmployeeId(event.target.value)}
              value={addEmployeeId}
            >
              <option value="">Selecciona un empleado</option>
              {employeesAvailable.map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {employee.first_name} {employee.last_name} ·{" "}
                  {money(employee.base_salary)}
                </option>
              ))}
            </select>
            <button
              className={secondaryButtonClass}
              disabled={isSaving || !addEmployeeId}
              onClick={onAddEmployee}
              type="button"
            >
              Agregar
            </button>
          </div>
        </div>
      ) : null}

      <div className="space-y-3">
        {run.items.length === 0 ? (
          <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">
            Este borrador todavía no tiene empleados.
          </p>
        ) : (
          run.items.map((item) => {
            const isEditing = editingItemId === item.id && editDraft;
            const employeeAdvances = advances.filter(
              (advance) => advance.employee_id === item.employee_id,
            );
            const employeeLoans = loans.filter(
              (loan) => loan.employee_id === item.employee_id,
            );
            return (
              <article
                className="rounded-lg border border-slate-200 p-4"
                key={item.id}
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-950">
                      {item.employee_name_snapshot}
                    </h3>
                    <p className="text-sm text-slate-500">
                      {item.employee_identification_snapshot ??
                        "Sin identificación"}{" "}
                      · {item.job_position_snapshot ?? "Sin cargo"}
                    </p>
                  </div>
                  <div className="text-left sm:text-right">
                    <p className="font-semibold text-water-700">
                      Neto {money(item.net_pay_amount)}
                    </p>
                    {actions.canEditItems ? (
                      <button
                        className="mt-1 text-sm font-medium text-water-700 underline"
                        onClick={() => onEditItem(item)}
                        type="button"
                      >
                        Editar ítem
                      </button>
                    ) : null}
                  </div>
                </div>
                <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-7">
                  <TotalCell
                    label="Sueldo"
                    value={money(item.base_salary_amount)}
                  />
                  <TotalCell label="Bonos" value={money(item.bonus_amount)} />
                  <TotalCell
                    label="Otros ingresos"
                    value={money(item.other_income_amount)}
                  />
                  <TotalCell
                    label="Anticipos"
                    value={money(item.advances_deducted_amount)}
                  />
                  <TotalCell
                    label="Préstamos"
                    value={money(item.loan_deductions_amount)}
                  />
                  <TotalCell
                    label="Otros descuentos"
                    value={money(item.other_deductions_amount)}
                  />
                  <TotalCell
                    label="Descuentos"
                    value={money(item.total_deductions_amount)}
                  />
                </div>
                {isEditing ? (
                  <div className="mt-4 space-y-4 border-t border-slate-200 pt-4">
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                      <EditableMoney
                        draft={editDraft}
                        field="baseSalary"
                        label="Sueldo base"
                        onChange={onEditDraftChange}
                      />
                      <EditableMoney
                        draft={editDraft}
                        field="bonusAmount"
                        label="Bonos"
                        onChange={onEditDraftChange}
                      />
                      <EditableMoney
                        draft={editDraft}
                        field="otherIncomeAmount"
                        label="Otros ingresos"
                        onChange={onEditDraftChange}
                      />
                      <EditableMoney
                        draft={editDraft}
                        field="otherDeductionsAmount"
                        label="Otros descuentos"
                        onChange={onEditDraftChange}
                      />
                      <TextField
                        label="Observación"
                        onChange={(value) =>
                          onEditDraftChange({ ...editDraft, notes: value })
                        }
                        value={editDraft.notes}
                      />
                    </div>
                    <DeductionInputs
                      advances={employeeAdvances}
                      draft={editDraft}
                      loans={employeeLoans}
                      onToggleAdvance={(advanceId) =>
                        onEditDraftChange({
                          ...editDraft,
                          advanceIds: editDraft.advanceIds.includes(advanceId)
                            ? editDraft.advanceIds.filter(
                                (id) => id !== advanceId,
                              )
                            : [...editDraft.advanceIds, advanceId],
                        })
                      }
                      onUpdateLoan={(loanId, value) => {
                        if (!isValidMoneyInputDraft(value)) {
                          return;
                        }
                        onEditDraftChange({
                          ...editDraft,
                          loanAmounts: {
                            ...editDraft.loanAmounts,
                            [loanId]: value,
                          },
                        });
                      }}
                    />
                    <TextField
                      label="Motivo de corrección"
                      onChange={setCorrectionReason}
                      placeholder="Obligatorio para auditoría"
                      value={correctionReason}
                    />
                    <button
                      className={primaryButtonClass}
                      disabled={isSaving}
                      onClick={() => onSaveItem(item)}
                      type="button"
                    >
                      Guardar corrección
                    </button>
                  </div>
                ) : null}
              </article>
            );
          })
        )}
      </div>

      <div className="grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 lg:grid-cols-4">
        <AuditValue label="Creado por" value={run.created_by} at={run.created_at} />
        <AuditValue
          label="Aprobado por"
          value={run.approved_by}
          at={run.approved_at}
        />
        <AuditValue label="Pagado por" value={run.paid_by} at={run.paid_at} />
        <AuditValue
          label="Cancelado por"
          value={run.cancelled_by}
          at={run.cancelled_at}
        />
      </div>

      {run.audit_logs.length > 0 ? (
        <details className="rounded-lg border border-slate-200 p-4">
          <summary className="cursor-pointer text-sm font-semibold text-slate-900">
            Ver trazabilidad ({run.audit_logs.length})
          </summary>
          <ol className="mt-3 space-y-2 text-sm text-slate-600">
            {run.audit_logs.map((log) => (
              <li key={log.id}>
                {auditActionLabel(log.action)} · usuario {log.actor_id} ·{" "}
                {formatTimestamp(log.created_at)}
                {log.reason ? ` · ${log.reason}` : ""}
              </li>
            ))}
          </ol>
        </details>
      ) : null}

      {run.status === "cancelled" ? (
        <p className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
          Motivo de cancelación: {run.cancellation_reason}
        </p>
      ) : null}

      {actions.canCancel ? (
        <div className="space-y-3 rounded-lg border border-red-200 bg-red-50 p-4">
          <TextField
            label="Motivo de cancelación"
            onChange={setCancelReason}
            placeholder="Obligatorio"
            value={cancelReason}
          />
          <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
            <button
              className={dangerButtonClass}
              disabled={isSaving}
              onClick={onCancel}
              type="button"
            >
              Cancelar rol
            </button>
            {actions.canApprove ? (
              <button
                className={primaryButtonClass}
                disabled={isSaving}
                onClick={onApprove}
                type="button"
              >
                Aprobar rol
              </button>
            ) : actions.canMarkPaid ? (
              <button
                className={primaryButtonClass}
                disabled={isSaving}
                onClick={onMarkPaid}
                type="button"
              >
                Marcar como pagado
              </button>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function EditableMoney({
  label,
  field,
  draft,
  onChange,
}: {
  label: string;
  field:
    | "baseSalary"
    | "bonusAmount"
    | "otherIncomeAmount"
    | "otherDeductionsAmount";
  draft: EmployeeDraft;
  onChange: (draft: EmployeeDraft) => void;
}) {
  return (
    <MoneyField
      label={label}
      onChange={(value) => {
        if (isValidMoneyInputDraft(value)) {
          onChange({ ...draft, [field]: value });
        }
      }}
      value={draft[field]}
    />
  );
}

function AuditValue({
  label,
  value,
  at,
}: {
  label: string;
  value: number | null;
  at: string | null;
}) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-sm text-slate-800">
        {value ? `Usuario ${value}` : "—"}
      </p>
      <p className="mt-1 text-xs text-slate-500">
        {at ? formatTimestamp(at) : "Sin registro"}
      </p>
    </div>
  );
}

function DateField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="text-sm font-medium text-slate-700">
      {label}
      <input
        className={inputClass}
        onChange={(event) => onChange(event.target.value)}
        type="date"
        value={value}
      />
    </label>
  );
}

function TextField({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <label className="text-sm font-medium text-slate-700">
      {label}
      <input
        className={inputClass}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        value={value}
      />
    </label>
  );
}

function MoneyField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="text-sm font-medium text-slate-700">
      {label}
      <input
        className={inputClass}
        inputMode="decimal"
        onChange={(event) => onChange(event.target.value)}
        value={value}
      />
    </label>
  );
}

function PayrollStatusBadge({ status }: { status: PayrollStatus }) {
  const classes: Record<PayrollStatus, string> = {
    draft: "bg-amber-100 text-amber-800",
    approved: "bg-blue-100 text-blue-800",
    paid: "bg-emerald-100 text-emerald-800",
    cancelled: "bg-slate-200 text-slate-700",
  };
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${classes[status]}`}>
      {PAYROLL_STATUS_LABELS[status]}
    </span>
  );
}

function TotalCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function TotalCell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="font-medium text-slate-900">{value}</dd>
    </div>
  );
}

function buildItems(
  selectedEmployees: Employee[],
  drafts: Record<number, EmployeeDraft>,
  _advances: EmployeeAdvance[],
  loans: EmployeeLoan[],
): PayrollItemPayload[] {
  if (selectedEmployees.length === 0) {
    throw new Error("Selecciona al menos un empleado activo.");
  }
  return selectedEmployees.map((employee) =>
    draftToPayload(
      employee.id,
      drafts[employee.id] ?? createEmployeeDraft(employee.base_salary),
      loans,
    ),
  );
}

function draftToPayload(
  employeeId: number,
  draft: EmployeeDraft,
  loans: EmployeeLoan[],
): PayrollItemPayload {
  const moneyFields = [
    ["sueldo base", draft.baseSalary],
    ["bonos", draft.bonusAmount],
    ["otros ingresos", draft.otherIncomeAmount],
    ["otros descuentos", draft.otherDeductionsAmount],
  ] as const;
  for (const [label, value] of moneyFields) {
    if (parseMoneyInputToCents(value) === null) {
      throw new Error(`Ingresa un valor válido para ${label}.`);
    }
  }
  const employeeLoans = loans.filter(
    (loan) => loan.employee_id === employeeId,
  );
  const loanDeductions = employeeLoans.flatMap((loan) => {
    const amount = draft.loanAmounts[loan.id]?.trim() ?? "";
    if (!amount) {
      return [];
    }
    const amountCents = parseMoneyInputToCents(amount);
    if (amountCents === null || amountCents <= 0) {
      throw new Error(
        `El descuento del préstamo ${loan.loan_number} debe ser mayor a cero.`,
      );
    }
    const balanceCents = parseMoneyInputToCents(loan.balance_amount);
    if (balanceCents !== null && amountCents > balanceCents) {
      throw new Error("El descuento supera el saldo disponible.");
    }
    return [
      {
        employee_loan_id: loan.id,
        amount_deducted: normalizeMoney(amount),
      },
    ];
  });
  return {
    employee_id: employeeId,
    base_salary_amount: normalizeMoney(draft.baseSalary),
    bonus_amount: normalizeMoney(draft.bonusAmount),
    other_income_amount: normalizeMoney(draft.otherIncomeAmount),
    other_deductions_amount: normalizeMoney(draft.otherDeductionsAmount),
    advance_ids: draft.advanceIds,
    loan_deductions: loanDeductions,
    notes: optionalText(draft.notes),
  };
}

function withoutEmployeeId(payload: PayrollItemPayload) {
  const { employee_id: _employeeId, ...values } = payload;
  return values;
}

function itemToDraft(item: PayrollCalculatedItem): EmployeeDraft {
  return {
    selected: true,
    baseSalary: item.base_salary_amount,
    bonusAmount: item.bonus_amount,
    otherIncomeAmount: item.other_income_amount,
    otherDeductionsAmount: item.other_deductions_amount,
    advanceIds: item.advance_deductions.map(
      (deduction) => deduction.employee_advance_id,
    ),
    loanAmounts: Object.fromEntries(
      item.loan_deductions.map((deduction) => [
        deduction.employee_loan_id,
        deduction.amount_deducted,
      ]),
    ),
    notes: item.notes ?? "",
  };
}

function createDefaultPeriod(): PayrollPeriod {
  const today = getTodayISODate();
  return {
    periodStart: `${today.slice(0, 8)}01`,
    periodEnd: today,
    payrollDate: today,
    label: `Rol ${today.slice(0, 7)}`,
    notes: "",
  };
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function createEmployeeDraft(baseSalary: string): EmployeeDraft {
  return {
    selected: false,
    baseSalary,
    bonusAmount: "0.00",
    otherIncomeAmount: "0.00",
    otherDeductionsAmount: "0.00",
    advanceIds: [],
    loanAmounts: {},
    notes: "",
  };
}

function createDrafts(employees: Employee[]): Record<number, EmployeeDraft> {
  return Object.fromEntries(
    employees.map((employee) => [
      employee.id,
      createEmployeeDraft(employee.base_salary),
    ]),
  );
}

function validatePeriod(period: PayrollPeriod) {
  if (!period.periodStart || !period.periodEnd) {
    throw new Error("Selecciona la fecha inicial y final del período.");
  }
  if (period.periodEnd < period.periodStart) {
    throw new Error("La fecha final no puede ser menor que la fecha inicial.");
  }
  if (!period.payrollDate) {
    throw new Error("La fecha del rol es obligatoria.");
  }
}

function toFilters(filters: FilterDraft): PayrollRunFilters {
  return {
    date_from: filters.dateFrom || undefined,
    date_to: filters.dateTo || undefined,
    status: filters.status,
    employee_id: filters.employeeId
      ? Number(filters.employeeId)
      : undefined,
    search: filters.search.trim() || undefined,
  };
}

function normalizeMoney(value: string): string {
  const normalized = value.trim().replace(",", ".");
  const [dollars, cents = ""] = normalized.split(".");
  return `${dollars || "0"}.${cents.padEnd(2, "0").slice(0, 2)}`;
}

function money(value: string): string {
  return `$${value}`;
}

function optionalText(value: string): string | null {
  return value.trim() || null;
}

function formatTimestamp(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function auditActionLabel(action: string): string {
  const labels: Record<string, string> = {
    run_created: "Rol creado",
    item_added: "Empleado agregado",
    item_updated: "Ítem corregido",
    approved: "Rol aprobado",
    paid: "Rol marcado como pagado",
    cancelled: "Rol cancelado",
  };
  return labels[action] ?? action;
}

function getErrorMessage(
  possibleError: unknown,
  fallback = "Ocurrió un error inesperado.",
): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return fallback;
}

const inputClass =
  "mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-950 outline-none focus:border-water-500 focus:ring-1 focus:ring-water-500";
const compactInputClass =
  "block w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-950 outline-none focus:border-water-500";
const primaryButtonClass =
  "rounded-md bg-water-700 px-4 py-2 text-sm font-semibold text-white hover:bg-water-800 disabled:cursor-not-allowed disabled:opacity-50";
const secondaryButtonClass =
  "rounded-md border border-water-700 bg-white px-4 py-2 text-sm font-semibold text-water-700 hover:bg-water-50 disabled:cursor-not-allowed disabled:opacity-50";
const plainButtonClass =
  "rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50";
const dangerButtonClass =
  "rounded-md bg-red-700 px-4 py-2 text-sm font-semibold text-white hover:bg-red-800 disabled:cursor-not-allowed disabled:opacity-50";

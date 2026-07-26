"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createPayrollRun,
  getPayrollRun,
  listEmployeeAdvances,
  listEmployeeLoans,
  listEmployees,
  listPayrollRuns,
  previewPayrollRun,
  voidPayrollRun,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import { useIsAdminAuditor } from "@/lib/useCurrentRole";
import {
  isValidMoneyInputDraft,
  parseMoneyInputToCents,
} from "@/lib/money";
import type { Employee } from "@/types/employee";
import type { EmployeeAdvance, EmployeeLoan } from "@/types/employeeControls";
import {
  PAYROLL_STATUS_LABELS,
  type PayrollItemPayload,
  type PayrollPreview,
  type PayrollRun,
  type PayrollRunFilters,
  type PayrollRunSummary,
  type PayrollStatus,
} from "@/types/payroll";

type EmployeeDraft = {
  selected: boolean;
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
  const canVoid = useIsAdminAuditor();
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
  const [voidReason, setVoidReason] = useState("");
  const [filters, setFilters] = useState<FilterDraft>(emptyFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const selectedEmployees = useMemo(
    () => employees.filter((employee) => drafts[employee.id]?.selected),
    [drafts, employees],
  );

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    setToken(storedToken);
    loadInitial(storedToken);
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
      [employeeId]: updater(current[employeeId] ?? createEmployeeDraft()),
    }));
    setPreview(null);
  }

  function toggleEmployee(employeeId: number) {
    updateDraft(employeeId, (draft) => ({
      ...draft,
      selected: !draft.selected,
    }));
  }

  function updateMoneyField(
    employeeId: number,
    field:
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
      items = buildItems();
      validatePeriod();
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
      setMessage("Vista previa calculada oficialmente por el backend.");
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
    if (!preview) {
      setError("Genera una vista previa antes de crear el rol.");
      return;
    }
    clearNotices();
    let items: PayrollItemPayload[];
    try {
      items = buildItems();
      validatePeriod();
      if (!period.payrollDate) {
        throw new Error("La fecha del rol es obligatoria.");
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
        notes: optionalText(period.notes),
        employee_ids: selectedEmployees.map((employee) => employee.id),
        items,
      });
      setRuns(await listPayrollRuns(token, toFilters(filters)));
      setSelectedRun(created);
      setPreview(null);
      setDrafts(createDrafts(employees));
      setMessage(`Rol creado: ${created.payroll_number}.`);
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
      setVoidReason("");
    } catch (detailError) {
      handleError(detailError, "No se pudo cargar el detalle del rol.");
    } finally {
      setIsLoadingDetail(false);
    }
  }

  async function handleVoid() {
    if (!token || !selectedRun) {
      return;
    }
    if (!voidReason.trim()) {
      setError("El motivo de anulación es obligatorio.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const updated = await voidPayrollRun(
        token,
        selectedRun.id,
        voidReason.trim(),
      );
      setSelectedRun(updated);
      setRuns(await listPayrollRuns(token, toFilters(filters)));
      setVoidReason("");
      setMessage(`Rol anulado: ${updated.payroll_number}.`);
    } catch (voidError) {
      handleError(voidError, "No se pudo anular el rol.");
    } finally {
      setIsSaving(false);
    }
  }

  function validatePeriod() {
    if (!period.periodStart || !period.periodEnd) {
      throw new Error("Selecciona la fecha inicial y final del período.");
    }
    if (period.periodEnd < period.periodStart) {
      throw new Error("La fecha final no puede ser menor que la fecha inicial.");
    }
  }

  function buildItems(): PayrollItemPayload[] {
    if (selectedEmployees.length === 0) {
      throw new Error("Selecciona al menos un empleado activo.");
    }
    return selectedEmployees.map((employee) => {
      const draft = drafts[employee.id];
      const moneyFields = [
        ["bonos", draft.bonusAmount],
        ["otros ingresos", draft.otherIncomeAmount],
        ["otros descuentos", draft.otherDeductionsAmount],
      ] as const;
      for (const [label, value] of moneyFields) {
        if (parseMoneyInputToCents(value) === null) {
          throw new Error(
            `Ingresa un valor válido para ${label} de ${employee.first_name}.`,
          );
        }
      }
      const employeeLoans = loans.filter(
        (loan) => loan.employee_id === employee.id,
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
          throw new Error(
            `El descuento del préstamo ${loan.loan_number} supera su saldo.`,
          );
        }
        return [
          {
            employee_loan_id: loan.id,
            amount_deducted: normalizeMoney(amount),
          },
        ];
      });
      return {
        employee_id: employee.id,
        bonus_amount: normalizeMoney(draft.bonusAmount),
        other_income_amount: normalizeMoney(draft.otherIncomeAmount),
        other_deductions_amount: normalizeMoney(
          draft.otherDeductionsAmount,
        ),
        advance_ids: draft.advanceIds,
        loan_deductions: loanDeductions,
        notes: optionalText(draft.notes),
      };
    });
  }

  function clearNotices() {
    setError("");
    setMessage("");
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
              Calcula y congela roles de pago de empleados. Este módulo no paga
              automáticamente, no modifica caja y no crea gastos operativos.
            </p>
          </div>
          <LogoutButton />
        </header>

        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Los pagos reales de nómina y movimientos de caja/banco se
          implementarán en un bloque posterior.
        </div>
        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            {message}
          </p>
        ) : null}

        <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-medium text-water-700">Nuevo rol</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Período y empleados
            </h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <DateField
              label="Período desde"
              value={period.periodStart}
              onChange={(value) => updatePeriod("periodStart", value)}
            />
            <DateField
              label="Período hasta"
              value={period.periodEnd}
              onChange={(value) => updatePeriod("periodEnd", value)}
            />
            <DateField
              label="Fecha del rol"
              value={period.payrollDate}
              onChange={(value) => updatePeriod("payrollDate", value)}
            />
            <label className="text-sm font-medium text-slate-700">
              Notas generales
              <input
                className={inputClass}
                onChange={(event) => updatePeriod("notes", event.target.value)}
                value={period.notes}
              />
            </label>
          </div>

          {employees.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">
              No hay empleados activos. Registra o activa un empleado antes de
              crear un rol.
            </p>
          ) : (
            <div className="space-y-3">
              {employees.map((employee) => {
                const draft =
                  drafts[employee.id] ?? createEmployeeDraft();
                const employeeAdvances = advances.filter(
                  (advance) => advance.employee_id === employee.id,
                );
                const employeeLoans = loans.filter(
                  (loan) => loan.employee_id === employee.id,
                );
                return (
                  <article
                    className={`rounded-lg border p-4 ${
                      draft.selected
                        ? "border-water-500 bg-water-50/40"
                        : "border-slate-200"
                    }`}
                    key={employee.id}
                  >
                    <label className="flex cursor-pointer items-start gap-3">
                      <input
                        checked={draft.selected}
                        className="mt-1 h-4 w-4"
                        onChange={() => toggleEmployee(employee.id)}
                        type="checkbox"
                      />
                      <span>
                        <span className="block font-semibold text-slate-950">
                          {employee.first_name} {employee.last_name}
                        </span>
                        <span className="mt-1 block text-sm text-slate-600">
                          {employee.job_position ?? "Sin cargo"} · Sueldo base{" "}
                          {money(employee.base_salary)} ·{" "}
                          {employee.payment_frequency}
                        </span>
                      </span>
                    </label>

                    {draft.selected ? (
                      <div className="mt-4 space-y-4 border-t border-slate-200 pt-4">
                        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                          <MoneyField
                            label="Bonos"
                            value={draft.bonusAmount}
                            onChange={(value) =>
                              updateMoneyField(
                                employee.id,
                                "bonusAmount",
                                value,
                              )
                            }
                          />
                          <MoneyField
                            label="Otros ingresos"
                            value={draft.otherIncomeAmount}
                            onChange={(value) =>
                              updateMoneyField(
                                employee.id,
                                "otherIncomeAmount",
                                value,
                              )
                            }
                          />
                          <MoneyField
                            label="Otros descuentos"
                            value={draft.otherDeductionsAmount}
                            onChange={(value) =>
                              updateMoneyField(
                                employee.id,
                                "otherDeductionsAmount",
                                value,
                              )
                            }
                          />
                          <label className="text-sm font-medium text-slate-700">
                            Notas del empleado
                            <input
                              className={inputClass}
                              onChange={(event) =>
                                updateDraft(employee.id, (current) => ({
                                  ...current,
                                  notes: event.target.value,
                                }))
                              }
                              value={draft.notes}
                            />
                          </label>
                        </div>

                        <div className="grid gap-4 lg:grid-cols-2">
                          <div>
                            <h3 className="text-sm font-semibold text-slate-900">
                              Anticipos activos
                            </h3>
                            {employeeAdvances.length === 0 ? (
                              <p className="mt-2 text-sm text-slate-500">
                                Sin anticipos activos.
                              </p>
                            ) : (
                              <div className="mt-2 space-y-2">
                                {employeeAdvances.map((advance) => (
                                  <label
                                    className="flex items-start gap-2 rounded-md border border-slate-200 p-3 text-sm"
                                    key={advance.id}
                                  >
                                    <input
                                      checked={draft.advanceIds.includes(
                                        advance.id,
                                      )}
                                      className="mt-1"
                                      onChange={() =>
                                        toggleAdvance(employee.id, advance.id)
                                      }
                                      type="checkbox"
                                    />
                                    <span>
                                      <span className="font-medium">
                                        {advance.advance_number} ·{" "}
                                        {money(advance.amount)}
                                      </span>
                                      <span className="block text-slate-500">
                                        {advance.reason}
                                      </span>
                                    </span>
                                  </label>
                                ))}
                              </div>
                            )}
                          </div>
                          <div>
                            <h3 className="text-sm font-semibold text-slate-900">
                              Préstamos activos
                            </h3>
                            {employeeLoans.length === 0 ? (
                              <p className="mt-2 text-sm text-slate-500">
                                Sin préstamos activos.
                              </p>
                            ) : (
                              <div className="mt-2 space-y-2">
                                {employeeLoans.map((loan) => (
                                  <label
                                    className="block rounded-md border border-slate-200 p-3 text-sm"
                                    key={loan.id}
                                  >
                                    <span className="font-medium text-slate-900">
                                      {loan.loan_number} · saldo{" "}
                                      {money(loan.balance_amount)}
                                    </span>
                                    <span className="mt-2 block text-slate-600">
                                      Monto a descontar
                                    </span>
                                    <input
                                      className={inputClass}
                                      inputMode="decimal"
                                      onChange={(event) =>
                                        updateLoanAmount(
                                          employee.id,
                                          loan.id,
                                          event.target.value,
                                        )
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
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </div>
          )}

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              className={secondaryButtonClass}
              disabled={isSaving || employees.length === 0}
              onClick={handlePreview}
              type="button"
            >
              {isSaving ? "Calculando..." : "Generar vista previa"}
            </button>
            <button
              className={primaryButtonClass}
              disabled={isSaving || !preview}
              onClick={handleCreate}
              type="button"
            >
              Crear rol
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
              value={filters.dateFrom}
              onChange={(value) =>
                setFilters((current) => ({ ...current, dateFrom: value }))
              }
            />
            <DateField
              label="Hasta"
              value={filters.dateTo}
              onChange={(value) =>
                setFilters((current) => ({ ...current, dateTo: value }))
              }
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
                <option value="active">Activo</option>
                <option value="voided">Anulado</option>
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
            <label className="text-sm font-medium text-slate-700">
              Buscar
              <input
                className={inputClass}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    search: event.target.value,
                  }))
                }
                placeholder="Número o empleado"
                value={filters.search}
              />
            </label>
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
                        {run.payroll_number}
                      </h3>
                      <p className="mt-1 text-sm text-slate-500">
                        {run.period_start} a {run.period_end}
                      </p>
                    </div>
                    <StatusBadge status={run.status} />
                  </div>
                  <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <TotalCell label="Empleados" value={String(run.employees_count)} />
                    <TotalCell label="Fecha" value={run.payroll_date} />
                    <TotalCell label="Ingresos" value={money(run.gross_total)} />
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
            canVoid={canVoid}
            isSaving={isSaving}
            onClose={() => setSelectedRun(null)}
            onVoid={handleVoid}
            run={selectedRun}
            setVoidReason={setVoidReason}
            voidReason={voidReason}
          />
        ) : null}
      </div>
    </main>
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
      <div className="space-y-3">
        {preview.items.map((item) => (
          <article
            className="rounded-lg border border-slate-200 p-4"
            key={item.employee_id}
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h3 className="font-semibold text-slate-950">
                  {item.employee_name_snapshot}
                </h3>
                <p className="text-sm text-slate-500">
                  Sueldo base {money(item.base_salary_amount)} · Horas{" "}
                  {item.hours_worked}
                </p>
              </div>
              <p className="text-lg font-semibold text-water-700">
                Neto {money(item.net_pay_amount)}
              </p>
            </div>
            <div className="mt-3 grid gap-2 text-sm sm:grid-cols-3 lg:grid-cols-6">
              <TotalCell label="Asistencia" value={String(item.attendance_days)} />
              <TotalCell label="Ausencias" value={String(item.absent_days)} />
              <TotalCell label="Atrasos" value={String(item.late_days)} />
              <TotalCell label="Permisos" value={String(item.permission_days)} />
              <TotalCell label="Vacaciones" value={String(item.vacation_days)} />
              <TotalCell label="Enfermedad" value={String(item.sick_days)} />
            </div>
            <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <TotalCell label="Ingresos" value={money(item.gross_amount)} />
              <TotalCell
                label="Anticipos"
                value={money(item.advances_deducted_amount)}
              />
              <TotalCell
                label="Préstamos"
                value={money(item.loan_deductions_amount)}
              />
              <TotalCell
                label="Descuentos totales"
                value={money(item.total_deductions_amount)}
              />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function PayrollDetail({
  canVoid,
  run,
  voidReason,
  setVoidReason,
  onVoid,
  onClose,
  isSaving,
}: {
  canVoid: boolean;
  run: PayrollRun;
  voidReason: string;
  setVoidReason: (value: string) => void;
  onVoid: () => void;
  onClose: () => void;
  isSaving: boolean;
}) {
  return (
    <section className="space-y-4 rounded-lg border border-slate-300 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-water-700">Detalle del rol</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            {run.payroll_number}
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            {run.period_start} a {run.period_end} · {run.payroll_date}
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
      <div className="space-y-3">
        {run.items.map((item) => (
          <article className="rounded-lg border border-slate-200 p-4" key={item.id}>
            <div className="flex flex-col gap-1 sm:flex-row sm:justify-between">
              <div>
                <h3 className="font-semibold text-slate-950">
                  {item.employee_name_snapshot}
                </h3>
                <p className="text-sm text-slate-500">
                  {item.employee_identification_snapshot ?? "Sin identificación"} ·{" "}
                  {item.job_position_snapshot ?? "Sin cargo"}
                </p>
              </div>
              <p className="font-semibold text-water-700">
                Neto {money(item.net_pay_amount)}
              </p>
            </div>
            <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-5">
              <TotalCell label="Sueldo" value={money(item.base_salary_amount)} />
              <TotalCell label="Bonos" value={money(item.bonus_amount)} />
              <TotalCell
                label="Otros ingresos"
                value={money(item.other_income_amount)}
              />
              <TotalCell label="Ingresos" value={money(item.gross_amount)} />
              <TotalCell
                label="Descuentos"
                value={money(item.total_deductions_amount)}
              />
            </div>
            <p className="mt-3 text-sm text-slate-600">
              Asistencia: {item.attendance_days}; ausencias: {item.absent_days};
              atrasos: {item.late_days}; permisos: {item.permission_days};
              vacaciones: {item.vacation_days}; enfermedad: {item.sick_days};
              horas: {item.hours_worked}.
            </p>
            {item.advance_deductions.length > 0 ? (
              <div className="mt-3 text-sm text-slate-600">
                <span className="font-medium text-slate-900">Anticipos: </span>
                {item.advance_deductions
                  .map(
                    (deduction) =>
                      `${deduction.advance_number_snapshot} (${money(
                        deduction.amount_deducted,
                      )})`,
                  )
                  .join(", ")}
              </div>
            ) : null}
            {item.loan_deductions.length > 0 ? (
              <div className="mt-2 text-sm text-slate-600">
                <span className="font-medium text-slate-900">Préstamos: </span>
                {item.loan_deductions
                  .map(
                    (deduction) =>
                      `${deduction.loan_number_snapshot} (${money(
                        deduction.amount_deducted,
                      )})`,
                  )
                  .join(", ")}
              </div>
            ) : null}
          </article>
        ))}
      </div>
      {run.status === "active" && canVoid ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <label className="text-sm font-medium text-red-900">
            Motivo de anulación
            <textarea
              className={`${inputClass} min-h-20 bg-white`}
              onChange={(event) => setVoidReason(event.target.value)}
              value={voidReason}
            />
          </label>
          <button
            className="mt-3 rounded-md bg-red-700 px-4 py-2 text-sm font-semibold text-white hover:bg-red-800 disabled:opacity-50"
            disabled={isSaving}
            onClick={onVoid}
            type="button"
          >
            Anular rol
          </button>
        </div>
      ) : run.status === "voided" ? (
        <p className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
          Motivo de anulación: {run.void_reason}
        </p>
      ) : null}
    </section>
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

function StatusBadge({ status }: { status: PayrollStatus }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
        status === "active"
          ? "bg-emerald-100 text-emerald-800"
          : "bg-slate-200 text-slate-700"
      }`}
    >
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

function createDefaultPeriod(): PayrollPeriod {
  const today = getTodayISODate();
  return {
    periodStart: `${today.slice(0, 8)}01`,
    periodEnd: today,
    payrollDate: today,
    notes: "",
  };
}

function getTodayISODate(): string {
  const now = new Date();
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 10);
}

function createEmployeeDraft(): EmployeeDraft {
  return {
    selected: false,
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
    employees.map((employee) => [employee.id, createEmployeeDraft()]),
  );
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
const primaryButtonClass =
  "rounded-md bg-water-700 px-4 py-2 text-sm font-semibold text-white hover:bg-water-800 disabled:cursor-not-allowed disabled:opacity-50";
const secondaryButtonClass =
  "rounded-md border border-water-700 bg-white px-4 py-2 text-sm font-semibold text-water-700 hover:bg-water-50 disabled:cursor-not-allowed disabled:opacity-50";
const plainButtonClass =
  "rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50";

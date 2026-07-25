"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createEmployeeAdvance,
  createEmployeeAttendance,
  createEmployeeLoan,
  createEmployeeLoanPayment,
  getEmployeeAccountSummary,
  listEmployeeAdvances,
  listEmployeeAttendance,
  listEmployeeLoanPayments,
  listEmployeeLoans,
  listEmployees,
  updateEmployeeAttendance,
  voidEmployeeAdvance,
  voidEmployeeLoan,
  voidEmployeeLoanPayment,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import {
  formatCentsAsMoneyInput,
  isValidMoneyInputDraft,
  parseMoneyInputToCents,
} from "@/lib/money";
import type { Employee } from "@/types/employee";
import {
  ATTENDANCE_STATUS_LABELS,
  EMPLOYEE_CONTROL_STATUS_LABELS,
  type AttendanceStatus,
  type EmployeeAccountSummary,
  type EmployeeAdvance,
  type EmployeeAttendance,
  type EmployeeControlFilters,
  type EmployeeLoan,
  type EmployeeLoanPayment,
} from "@/types/employeeControls";

type Section = "attendance" | "advances" | "loans" | "payments";

type PeriodFilters = {
  dateFrom: string;
  dateTo: string;
};

type AttendanceForm = {
  attendanceDate: string;
  status: AttendanceStatus;
  checkInTime: string;
  checkOutTime: string;
  hoursWorked: string;
  notes: string;
};

type AdvanceForm = {
  advanceDate: string;
  amount: string;
  reason: string;
  notes: string;
};

type LoanForm = {
  loanDate: string;
  principalAmount: string;
  reason: string;
  notes: string;
};

type PaymentForm = {
  loanId: string;
  paymentDate: string;
  amount: string;
  notes: string;
};

const emptyPeriod: PeriodFilters = { dateFrom: "", dateTo: "" };

export default function EmployeeControlPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState("");
  const [section, setSection] = useState<Section>("attendance");
  const [summary, setSummary] = useState<EmployeeAccountSummary | null>(null);
  const [attendance, setAttendance] = useState<EmployeeAttendance[]>([]);
  const [advances, setAdvances] = useState<EmployeeAdvance[]>([]);
  const [loans, setLoans] = useState<EmployeeLoan[]>([]);
  const [payments, setPayments] = useState<EmployeeLoanPayment[]>([]);
  const [period, setPeriod] = useState<PeriodFilters>(emptyPeriod);
  const [appliedPeriod, setAppliedPeriod] =
    useState<PeriodFilters>(emptyPeriod);
  const [attendanceForm, setAttendanceForm] =
    useState<AttendanceForm>(createAttendanceForm);
  const [advanceForm, setAdvanceForm] =
    useState<AdvanceForm>(createAdvanceForm);
  const [loanForm, setLoanForm] = useState<LoanForm>(createLoanForm);
  const [paymentForm, setPaymentForm] =
    useState<PaymentForm>(createPaymentForm);
  const [editingAttendanceId, setEditingAttendanceId] =
    useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingId, setChangingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const selectedEmployee = useMemo(
    () =>
      employees.find(
        (employee) => employee.id === Number(selectedEmployeeId),
      ) ?? null,
    [employees, selectedEmployeeId],
  );
  const payableLoans = loans.filter(
    (loan) => loan.status === "active" && Number(loan.balance_amount) > 0,
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
    setError("");
    try {
      const loadedEmployees = await listEmployees(activeToken);
      setEmployees(loadedEmployees);
      const initialEmployee =
        loadedEmployees.find((employee) => employee.is_active) ??
        loadedEmployees[0];
      if (initialEmployee) {
        setSelectedEmployeeId(String(initialEmployee.id));
        await loadEmployeeData(
          activeToken,
          initialEmployee.id,
          emptyPeriod,
        );
      } else {
        clearEmployeeData();
      }
    } catch (loadError) {
      handleError(loadError, "No se pudo cargar el control de empleados.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadEmployeeData(
    activeToken: string,
    employeeId: number,
    activePeriod: PeriodFilters,
  ) {
    const filters = toApiFilters(employeeId, activePeriod);
    const [
      loadedSummary,
      loadedAttendance,
      loadedAdvances,
      loadedLoans,
      loadedPayments,
    ] = await Promise.all([
      getEmployeeAccountSummary(activeToken, employeeId, filters),
      listEmployeeAttendance(activeToken, filters),
      listEmployeeAdvances(activeToken, filters),
      listEmployeeLoans(activeToken, filters),
      listEmployeeLoanPayments(activeToken, filters),
    ]);
    setSummary(loadedSummary);
    setAttendance(loadedAttendance);
    setAdvances(loadedAdvances);
    setLoans(loadedLoans);
    setPayments(loadedPayments);
    setAppliedPeriod({ ...activePeriod });
    setPaymentForm((current) => {
      const selectedStillPayable = loadedLoans.some(
        (loan) =>
          String(loan.id) === current.loanId && loan.status === "active",
      );
      return {
        ...current,
        loanId: selectedStillPayable ? current.loanId : "",
      };
    });
  }

  async function handleEmployeeChange(employeeIdValue: string) {
    setSelectedEmployeeId(employeeIdValue);
    resetForms();
    clearNotices();
    if (!token || !employeeIdValue) {
      clearEmployeeData();
      return;
    }
    setIsLoading(true);
    try {
      await loadEmployeeData(token, Number(employeeIdValue), appliedPeriod);
    } catch (loadError) {
      handleError(loadError, "No se pudo cargar el empleado.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handlePeriodSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedEmployee) {
      setError("Selecciona un empleado.");
      return;
    }
    if (period.dateFrom && period.dateTo && period.dateFrom > period.dateTo) {
      setError("La fecha desde no puede ser posterior a la fecha hasta.");
      return;
    }
    setIsLoading(true);
    clearNotices();
    try {
      await loadEmployeeData(token, selectedEmployee.id, period);
    } catch (loadError) {
      handleError(loadError, "No se pudo aplicar el período.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleClearPeriod() {
    setPeriod(emptyPeriod);
    if (!token || !selectedEmployee) {
      return;
    }
    setIsLoading(true);
    clearNotices();
    try {
      await loadEmployeeData(token, selectedEmployee.id, emptyPeriod);
    } catch (loadError) {
      handleError(loadError, "No se pudo limpiar el período.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAttendanceSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedEmployee) {
      setError("Selecciona un empleado.");
      return;
    }
    const validationError = validateAttendance(attendanceForm);
    if (validationError) {
      setError(validationError);
      return;
    }
    setIsSaving(true);
    clearNotices();
    const values = {
      attendance_date: attendanceForm.attendanceDate,
      status: attendanceForm.status,
      check_in_time: optionalText(attendanceForm.checkInTime),
      check_out_time: optionalText(attendanceForm.checkOutTime),
      hours_worked: normalizeOptionalDecimal(attendanceForm.hoursWorked),
      notes: optionalText(attendanceForm.notes),
    };
    try {
      if (editingAttendanceId) {
        await updateEmployeeAttendance(token, editingAttendanceId, values);
        setMessage("Asistencia actualizada.");
      } else {
        await createEmployeeAttendance(token, {
          employee_id: selectedEmployee.id,
          ...values,
        });
        setMessage("Asistencia registrada.");
      }
      setAttendanceForm(createAttendanceForm());
      setEditingAttendanceId(null);
      await reloadSelectedEmployee(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo guardar la asistencia.");
    } finally {
      setIsSaving(false);
    }
  }

  function handleEditAttendance(item: EmployeeAttendance) {
    setEditingAttendanceId(item.id);
    setAttendanceForm({
      attendanceDate: item.attendance_date,
      status: item.status,
      checkInTime: item.check_in_time?.slice(0, 5) ?? "",
      checkOutTime: item.check_out_time?.slice(0, 5) ?? "",
      hoursWorked: item.hours_worked ?? "",
      notes: item.notes ?? "",
    });
    setSection("attendance");
    clearNotices();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleAdvanceSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedEmployee) {
      setError("Selecciona un empleado.");
      return;
    }
    const amount = validatedPositiveMoney(
      advanceForm.amount,
      "El monto del anticipo",
    );
    if (!amount) {
      return;
    }
    if (!advanceForm.reason.trim()) {
      setError("El motivo del anticipo es obligatorio.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createEmployeeAdvance(token, {
        employee_id: selectedEmployee.id,
        advance_date: advanceForm.advanceDate,
        amount,
        reason: advanceForm.reason.trim(),
        notes: optionalText(advanceForm.notes),
      });
      setAdvanceForm(createAdvanceForm());
      setMessage(`Anticipo registrado: ${created.advance_number}.`);
      await reloadSelectedEmployee(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo registrar el anticipo.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleLoanSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedEmployee) {
      setError("Selecciona un empleado.");
      return;
    }
    const amount = validatedPositiveMoney(
      loanForm.principalAmount,
      "El monto del préstamo",
    );
    if (!amount) {
      return;
    }
    if (!loanForm.reason.trim()) {
      setError("El motivo del préstamo es obligatorio.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createEmployeeLoan(token, {
        employee_id: selectedEmployee.id,
        loan_date: loanForm.loanDate,
        principal_amount: amount,
        reason: loanForm.reason.trim(),
        notes: optionalText(loanForm.notes),
      });
      setLoanForm(createLoanForm());
      setMessage(`Préstamo registrado: ${created.loan_number}.`);
      await reloadSelectedEmployee(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo registrar el préstamo.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handlePaymentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedEmployee) {
      setError("Selecciona un empleado.");
      return;
    }
    if (!paymentForm.loanId) {
      setError("Selecciona un préstamo activo.");
      return;
    }
    const amount = validatedPositiveMoney(
      paymentForm.amount,
      "El monto del abono",
    );
    if (!amount) {
      return;
    }
    const selectedLoan = loans.find(
      (loan) => loan.id === Number(paymentForm.loanId),
    );
    if (
      selectedLoan &&
      (parseMoneyInputToCents(amount) ?? 0) >
        (parseMoneyInputToCents(selectedLoan.balance_amount) ?? 0)
    ) {
      setError("El monto del abono no puede superar el saldo del préstamo.");
      return;
    }
    setIsSaving(true);
    clearNotices();
    try {
      const created = await createEmployeeLoanPayment(
        token,
        Number(paymentForm.loanId),
        {
          payment_date: paymentForm.paymentDate,
          amount,
          notes: optionalText(paymentForm.notes),
        },
      );
      setPaymentForm(createPaymentForm());
      setMessage(`Abono registrado: ${created.payment_number}.`);
      await reloadSelectedEmployee(token);
    } catch (saveError) {
      handleError(saveError, "No se pudo registrar el abono.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleVoidAdvance(advance: EmployeeAdvance) {
    const reason = requestVoidReason("anticipo");
    if (!token || !reason) {
      return;
    }
    setChangingId(advance.id);
    clearNotices();
    try {
      await voidEmployeeAdvance(token, advance.id, reason);
      setMessage(`Anticipo anulado: ${advance.advance_number}.`);
      await reloadSelectedEmployee(token);
    } catch (voidError) {
      handleError(voidError, "No se pudo anular el anticipo.");
    } finally {
      setChangingId(null);
    }
  }

  async function handleVoidLoan(loan: EmployeeLoan) {
    const reason = requestVoidReason("préstamo");
    if (!token || !reason) {
      return;
    }
    setChangingId(loan.id);
    clearNotices();
    try {
      await voidEmployeeLoan(token, loan.id, reason);
      setMessage(`Préstamo anulado: ${loan.loan_number}.`);
      await reloadSelectedEmployee(token);
    } catch (voidError) {
      handleError(voidError, "No se pudo anular el préstamo.");
    } finally {
      setChangingId(null);
    }
  }

  async function handleVoidPayment(payment: EmployeeLoanPayment) {
    const reason = requestVoidReason("abono");
    if (!token || !reason) {
      return;
    }
    setChangingId(payment.id);
    clearNotices();
    try {
      await voidEmployeeLoanPayment(token, payment.id, reason);
      setMessage(`Abono anulado: ${payment.payment_number}.`);
      await reloadSelectedEmployee(token);
    } catch (voidError) {
      handleError(voidError, "No se pudo anular el abono.");
    } finally {
      setChangingId(null);
    }
  }

  function startPayment(loan: EmployeeLoan) {
    setPaymentForm({
      ...createPaymentForm(),
      loanId: String(loan.id),
    });
    setSection("payments");
    clearNotices();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function reloadSelectedEmployee(activeToken: string) {
    if (selectedEmployee) {
      await loadEmployeeData(
        activeToken,
        selectedEmployee.id,
        appliedPeriod,
      );
    }
  }

  function validatedPositiveMoney(
    value: string,
    fieldLabel: string,
  ): string | null {
    const cents = parseMoneyInputToCents(value);
    if (cents === null || cents <= 0) {
      setError(`${fieldLabel} debe ser mayor a cero y tener hasta 2 decimales.`);
      return null;
    }
    return formatCentsAsMoneyInput(cents);
  }

  function requestVoidReason(itemLabel: string): string | null {
    const response = window.prompt(
      `Escribe el motivo de anulación del ${itemLabel}:`,
    );
    if (response === null) {
      return null;
    }
    const reason = response.trim();
    if (!reason) {
      setError("El motivo de anulación es obligatorio.");
      return null;
    }
    return reason;
  }

  function handleError(possibleError: unknown, fallback: string) {
    if (
      possibleError instanceof ApiError &&
      (possibleError.status === 401 || possibleError.status === 403)
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

  function clearEmployeeData() {
    setSummary(null);
    setAttendance([]);
    setAdvances([]);
    setLoans([]);
    setPayments([]);
  }

  function resetForms() {
    setAttendanceForm(createAttendanceForm());
    setAdvanceForm(createAdvanceForm());
    setLoanForm(createLoanForm());
    setPaymentForm(createPaymentForm());
    setEditingAttendanceId(null);
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-slate-950">
              Control de empleados
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Registra asistencia, anticipos y préstamos de empleados. Este
              módulo no modifica caja ni genera roles de pago automáticamente.
            </p>
            <p className="mt-2 text-sm font-semibold text-amber-700">
              Los roles de pago se implementarán en un bloque posterior.
            </p>
          </div>
          <LogoutButton />
        </header>

        <section className="grid gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
          <label className="text-sm font-medium text-slate-700">
            Empleado
            <select
              className={inputClassName}
              value={selectedEmployeeId}
              onChange={(event) => handleEmployeeChange(event.target.value)}
            >
              <option value="">Selecciona un empleado</option>
              {employees.map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {employee.first_name} {employee.last_name}
                  {employee.is_active ? "" : " (inactivo)"}
                </option>
              ))}
            </select>
          </label>

          <form
            className="grid gap-3 sm:grid-cols-[1fr_1fr_auto_auto] sm:items-end"
            onSubmit={handlePeriodSubmit}
          >
            <label className="text-sm font-medium text-slate-700">
              Desde
              <input
                className={inputClassName}
                type="date"
                value={period.dateFrom}
                onChange={(event) =>
                  setPeriod((current) => ({
                    ...current,
                    dateFrom: event.target.value,
                  }))
                }
              />
            </label>
            <label className="text-sm font-medium text-slate-700">
              Hasta
              <input
                className={inputClassName}
                type="date"
                value={period.dateTo}
                onChange={(event) =>
                  setPeriod((current) => ({
                    ...current,
                    dateTo: event.target.value,
                  }))
                }
              />
            </label>
            <button className={secondaryButtonClassName} type="submit">
              Aplicar
            </button>
            <button
              className={secondaryButtonClassName}
              type="button"
              onClick={handleClearPeriod}
            >
              Limpiar
            </button>
          </form>
        </section>

        {!employees.length && !isLoading ? (
          <p className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            No existen empleados. Registra primero un empleado en el módulo
            base.
          </p>
        ) : null}

        {selectedEmployee && !selectedEmployee.is_active ? (
          <p className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            Este empleado está inactivo. Puedes consultar su historial, pero no
            crear nuevos registros.
          </p>
        ) : null}

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando control de empleados..." />
        ) : selectedEmployee ? (
          <>
            {summary ? <SummaryCards summary={summary} /> : null}

            <nav
              aria-label="Secciones del control de empleados"
              className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4"
            >
              {(
                [
                  ["attendance", "Asistencia"],
                  ["advances", "Anticipos"],
                  ["loans", "Préstamos"],
                  ["payments", "Abonos"],
                ] as const
              ).map(([value, label]) => (
                <button
                  className={
                    section === value
                      ? primaryButtonClassName
                      : secondaryButtonClassName
                  }
                  key={value}
                  type="button"
                  onClick={() => setSection(value)}
                >
                  {label}
                </button>
              ))}
            </nav>

            {section === "attendance" ? (
              <AttendanceSection
                attendance={attendance}
                disabled={!selectedEmployee.is_active || isSaving}
                editingId={editingAttendanceId}
                form={attendanceForm}
                onFormChange={setAttendanceForm}
                onSubmit={handleAttendanceSubmit}
                onCancelEdit={() => {
                  setEditingAttendanceId(null);
                  setAttendanceForm(createAttendanceForm());
                }}
                onEdit={handleEditAttendance}
              />
            ) : null}

            {section === "advances" ? (
              <AdvancesSection
                advances={advances}
                disabled={!selectedEmployee.is_active || isSaving}
                changingId={changingId}
                form={advanceForm}
                onFormChange={setAdvanceForm}
                onSubmit={handleAdvanceSubmit}
                onVoid={handleVoidAdvance}
              />
            ) : null}

            {section === "loans" ? (
              <LoansSection
                loans={loans}
                disabled={!selectedEmployee.is_active || isSaving}
                changingId={changingId}
                form={loanForm}
                onFormChange={setLoanForm}
                onSubmit={handleLoanSubmit}
                onVoid={handleVoidLoan}
                onStartPayment={startPayment}
              />
            ) : null}

            {section === "payments" ? (
              <PaymentsSection
                payments={payments}
                payableLoans={payableLoans}
                disabled={!selectedEmployee.is_active || isSaving}
                changingId={changingId}
                form={paymentForm}
                onFormChange={setPaymentForm}
                onSubmit={handlePaymentSubmit}
                onVoid={handleVoidPayment}
              />
            ) : null}
          </>
        ) : null}
      </div>
    </main>
  );
}

function SummaryCards({ summary }: { summary: EmployeeAccountSummary }) {
  const items = [
    ["Anticipos activos", formatMoney(summary.advances_total_active)],
    ["Capital prestado", formatMoney(summary.loans_principal_total)],
    ["Total abonado", formatMoney(summary.loans_paid_total)],
    ["Saldo pendiente", formatMoney(summary.loans_balance_total)],
    ["Préstamos activos", String(summary.active_loans_count)],
    ["Préstamos pagados", String(summary.paid_loans_count)],
    ["Asistencias del período", String(summary.attendance_count_period)],
  ];
  return (
    <section aria-labelledby="employee-summary-title">
      <h2
        className="mb-3 text-lg font-semibold text-slate-950"
        id="employee-summary-title"
      >
        Resumen de {summary.employee_name}
      </h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {items.map(([label, value]) => (
          <div
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
            key={label}
          >
            <p className="text-sm text-slate-600">{label}</p>
            <p className="mt-1 text-xl font-semibold text-slate-950">{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

type AttendanceSectionProps = {
  attendance: EmployeeAttendance[];
  disabled: boolean;
  editingId: number | null;
  form: AttendanceForm;
  onFormChange: (value: AttendanceForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancelEdit: () => void;
  onEdit: (item: EmployeeAttendance) => void;
};

function AttendanceSection({
  attendance,
  disabled,
  editingId,
  form,
  onFormChange,
  onSubmit,
  onCancelEdit,
  onEdit,
}: AttendanceSectionProps) {
  return (
    <section className="space-y-4">
      <ControlForm
        description="Un empleado solo puede tener un registro por fecha."
        title={editingId ? "Editar asistencia" : "Registrar asistencia"}
      >
        <form className="grid gap-3 md:grid-cols-3" onSubmit={onSubmit}>
          <label className={labelClassName}>
            Fecha
            <input
              className={inputClassName}
              disabled={disabled}
              required
              type="date"
              value={form.attendanceDate}
              onChange={(event) =>
                onFormChange({
                  ...form,
                  attendanceDate: event.target.value,
                })
              }
            />
          </label>
          <label className={labelClassName}>
            Estado
            <select
              className={inputClassName}
              disabled={disabled}
              value={form.status}
              onChange={(event) =>
                onFormChange({
                  ...form,
                  status: event.target.value as AttendanceStatus,
                })
              }
            >
              {Object.entries(ATTENDANCE_STATUS_LABELS).map(
                ([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ),
              )}
            </select>
          </label>
          <label className={labelClassName}>
            Horas trabajadas
            <input
              className={inputClassName}
              disabled={disabled}
              inputMode="decimal"
              placeholder="8.00"
              value={form.hoursWorked}
              onChange={(event) =>
                onFormChange({
                  ...form,
                  hoursWorked: event.target.value,
                })
              }
            />
          </label>
          <label className={labelClassName}>
            Entrada
            <input
              className={inputClassName}
              disabled={disabled}
              type="time"
              value={form.checkInTime}
              onChange={(event) =>
                onFormChange({ ...form, checkInTime: event.target.value })
              }
            />
          </label>
          <label className={labelClassName}>
            Salida
            <input
              className={inputClassName}
              disabled={disabled}
              type="time"
              value={form.checkOutTime}
              onChange={(event) =>
                onFormChange({ ...form, checkOutTime: event.target.value })
              }
            />
          </label>
          <label className={labelClassName}>
            Notas
            <input
              className={inputClassName}
              disabled={disabled}
              value={form.notes}
              onChange={(event) =>
                onFormChange({ ...form, notes: event.target.value })
              }
            />
          </label>
          <div className="flex gap-2 md:col-span-3">
            <button
              className={primaryButtonClassName}
              disabled={disabled}
              type="submit"
            >
              {editingId ? "Guardar cambios" : "Registrar asistencia"}
            </button>
            {editingId ? (
              <button
                className={secondaryButtonClassName}
                type="button"
                onClick={onCancelEdit}
              >
                Cancelar
              </button>
            ) : null}
          </div>
        </form>
      </ControlForm>

      <DataTable
        emptyMessage="No hay asistencias en el período."
        headers={["Fecha", "Estado", "Horario", "Horas", "Notas", "Acción"]}
      >
        {attendance.map((item) => (
          <tr className="border-t border-slate-100" key={item.id}>
            <TableCell>{formatDate(item.attendance_date)}</TableCell>
            <TableCell>{ATTENDANCE_STATUS_LABELS[item.status]}</TableCell>
            <TableCell>
              {formatTime(item.check_in_time)} – {formatTime(item.check_out_time)}
            </TableCell>
            <TableCell>{item.hours_worked ?? "—"}</TableCell>
            <TableCell>{item.notes ?? "—"}</TableCell>
            <TableCell>
              <button
                className={linkButtonClassName}
                type="button"
                onClick={() => onEdit(item)}
              >
                Editar
              </button>
            </TableCell>
          </tr>
        ))}
      </DataTable>
    </section>
  );
}

type AdvancesSectionProps = {
  advances: EmployeeAdvance[];
  disabled: boolean;
  changingId: number | null;
  form: AdvanceForm;
  onFormChange: (value: AdvanceForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onVoid: (advance: EmployeeAdvance) => void;
};

function AdvancesSection({
  advances,
  disabled,
  changingId,
  form,
  onFormChange,
  onSubmit,
  onVoid,
}: AdvancesSectionProps) {
  return (
    <section className="space-y-4">
      <ControlForm
        description="El registro es administrativo y no genera movimientos de caja."
        title="Registrar anticipo"
      >
        <form className="grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
          <label className={labelClassName}>
            Fecha
            <input
              className={inputClassName}
              disabled={disabled}
              required
              type="date"
              value={form.advanceDate}
              onChange={(event) =>
                onFormChange({ ...form, advanceDate: event.target.value })
              }
            />
          </label>
          <MoneyInput
            disabled={disabled}
            label="Monto"
            value={form.amount}
            onChange={(amount) => onFormChange({ ...form, amount })}
          />
          <label className={labelClassName}>
            Motivo
            <input
              className={inputClassName}
              disabled={disabled}
              required
              value={form.reason}
              onChange={(event) =>
                onFormChange({ ...form, reason: event.target.value })
              }
            />
          </label>
          <label className={labelClassName}>
            Notas
            <input
              className={inputClassName}
              disabled={disabled}
              value={form.notes}
              onChange={(event) =>
                onFormChange({ ...form, notes: event.target.value })
              }
            />
          </label>
          <button
            className={`${primaryButtonClassName} md:col-span-2 md:w-fit`}
            disabled={disabled}
            type="submit"
          >
            Registrar anticipo
          </button>
        </form>
      </ControlForm>

      <DataTable
        emptyMessage="No hay anticipos en el período."
        headers={["Número", "Fecha", "Monto", "Motivo", "Estado", "Acción"]}
      >
        {advances.map((advance) => (
          <tr className="border-t border-slate-100" key={advance.id}>
            <TableCell>{advance.advance_number}</TableCell>
            <TableCell>{formatDate(advance.advance_date)}</TableCell>
            <TableCell>{formatMoney(advance.amount)}</TableCell>
            <TableCell>
              {advance.reason}
              {advance.void_reason ? (
                <span className="block text-xs text-rose-700">
                  Anulación: {advance.void_reason}
                </span>
              ) : null}
            </TableCell>
            <TableCell>
              <StatusBadge status={advance.status} />
            </TableCell>
            <TableCell>
              {advance.status === "active" ? (
                <button
                  className={dangerButtonClassName}
                  disabled={changingId === advance.id}
                  type="button"
                  onClick={() => onVoid(advance)}
                >
                  Anular
                </button>
              ) : (
                "—"
              )}
            </TableCell>
          </tr>
        ))}
      </DataTable>
    </section>
  );
}

type LoansSectionProps = {
  loans: EmployeeLoan[];
  disabled: boolean;
  changingId: number | null;
  form: LoanForm;
  onFormChange: (value: LoanForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onVoid: (loan: EmployeeLoan) => void;
  onStartPayment: (loan: EmployeeLoan) => void;
};

function LoansSection({
  loans,
  disabled,
  changingId,
  form,
  onFormChange,
  onSubmit,
  onVoid,
  onStartPayment,
}: LoansSectionProps) {
  return (
    <section className="space-y-4">
      <ControlForm
        description="El saldo se actualiza únicamente con abonos registrados en este módulo."
        title="Registrar préstamo"
      >
        <form className="grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
          <label className={labelClassName}>
            Fecha
            <input
              className={inputClassName}
              disabled={disabled}
              required
              type="date"
              value={form.loanDate}
              onChange={(event) =>
                onFormChange({ ...form, loanDate: event.target.value })
              }
            />
          </label>
          <MoneyInput
            disabled={disabled}
            label="Monto principal"
            value={form.principalAmount}
            onChange={(principalAmount) =>
              onFormChange({ ...form, principalAmount })
            }
          />
          <label className={labelClassName}>
            Motivo
            <input
              className={inputClassName}
              disabled={disabled}
              required
              value={form.reason}
              onChange={(event) =>
                onFormChange({ ...form, reason: event.target.value })
              }
            />
          </label>
          <label className={labelClassName}>
            Notas
            <input
              className={inputClassName}
              disabled={disabled}
              value={form.notes}
              onChange={(event) =>
                onFormChange({ ...form, notes: event.target.value })
              }
            />
          </label>
          <button
            className={`${primaryButtonClassName} md:col-span-2 md:w-fit`}
            disabled={disabled}
            type="submit"
          >
            Registrar préstamo
          </button>
        </form>
      </ControlForm>

      <DataTable
        emptyMessage="No hay préstamos en el período."
        headers={[
          "Número",
          "Fecha",
          "Principal",
          "Abonado",
          "Saldo",
          "Estado",
          "Acciones",
        ]}
      >
        {loans.map((loan) => (
          <tr className="border-t border-slate-100" key={loan.id}>
            <TableCell>
              {loan.loan_number}
              <span className="block text-xs text-slate-500">
                {loan.reason}
              </span>
              {loan.void_reason ? (
                <span className="block text-xs text-rose-700">
                  Anulación: {loan.void_reason}
                </span>
              ) : null}
            </TableCell>
            <TableCell>{formatDate(loan.loan_date)}</TableCell>
            <TableCell>{formatMoney(loan.principal_amount)}</TableCell>
            <TableCell>{formatMoney(loan.paid_amount)}</TableCell>
            <TableCell>{formatMoney(loan.balance_amount)}</TableCell>
            <TableCell>
              <StatusBadge status={loan.status} />
            </TableCell>
            <TableCell>
              <div className="flex flex-wrap gap-2">
                {loan.status === "active" ? (
                  <button
                    className={linkButtonClassName}
                    type="button"
                    onClick={() => onStartPayment(loan)}
                  >
                    Abonar
                  </button>
                ) : null}
                {loan.status === "active" ? (
                  <button
                    className={dangerButtonClassName}
                    disabled={changingId === loan.id}
                    type="button"
                    onClick={() => onVoid(loan)}
                  >
                    Anular
                  </button>
                ) : null}
                {loan.status !== "active" ? "—" : null}
              </div>
            </TableCell>
          </tr>
        ))}
      </DataTable>
    </section>
  );
}

type PaymentsSectionProps = {
  payments: EmployeeLoanPayment[];
  payableLoans: EmployeeLoan[];
  disabled: boolean;
  changingId: number | null;
  form: PaymentForm;
  onFormChange: (value: PaymentForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onVoid: (payment: EmployeeLoanPayment) => void;
};

function PaymentsSection({
  payments,
  payableLoans,
  disabled,
  changingId,
  form,
  onFormChange,
  onSubmit,
  onVoid,
}: PaymentsSectionProps) {
  return (
    <section className="space-y-4">
      <ControlForm
        description="El abono reduce el saldo del préstamo, sin modificar caja ni bancos."
        title="Registrar abono"
      >
        <form className="grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
          <label className={labelClassName}>
            Préstamo activo
            <select
              className={inputClassName}
              disabled={disabled}
              required
              value={form.loanId}
              onChange={(event) =>
                onFormChange({ ...form, loanId: event.target.value })
              }
            >
              <option value="">Selecciona un préstamo</option>
              {payableLoans.map((loan) => (
                <option key={loan.id} value={loan.id}>
                  {loan.loan_number} · saldo {formatMoney(loan.balance_amount)}
                </option>
              ))}
            </select>
          </label>
          <label className={labelClassName}>
            Fecha
            <input
              className={inputClassName}
              disabled={disabled}
              required
              type="date"
              value={form.paymentDate}
              onChange={(event) =>
                onFormChange({ ...form, paymentDate: event.target.value })
              }
            />
          </label>
          <MoneyInput
            disabled={disabled}
            label="Monto"
            value={form.amount}
            onChange={(amount) => onFormChange({ ...form, amount })}
          />
          <label className={labelClassName}>
            Notas
            <input
              className={inputClassName}
              disabled={disabled}
              value={form.notes}
              onChange={(event) =>
                onFormChange({ ...form, notes: event.target.value })
              }
            />
          </label>
          <button
            className={`${primaryButtonClassName} md:col-span-2 md:w-fit`}
            disabled={disabled || payableLoans.length === 0}
            type="submit"
          >
            Registrar abono
          </button>
        </form>
      </ControlForm>

      <DataTable
        emptyMessage="No hay abonos en el período."
        headers={["Número", "Préstamo", "Fecha", "Monto", "Estado", "Acción"]}
      >
        {payments.map((payment) => (
          <tr className="border-t border-slate-100" key={payment.id}>
            <TableCell>{payment.payment_number}</TableCell>
            <TableCell>{payment.loan_number}</TableCell>
            <TableCell>{formatDate(payment.payment_date)}</TableCell>
            <TableCell>{formatMoney(payment.amount)}</TableCell>
            <TableCell>
              <StatusBadge status={payment.status} />
              {payment.void_reason ? (
                <span className="mt-1 block text-xs text-rose-700">
                  {payment.void_reason}
                </span>
              ) : null}
            </TableCell>
            <TableCell>
              {payment.status === "active" ? (
                <button
                  className={dangerButtonClassName}
                  disabled={changingId === payment.id}
                  type="button"
                  onClick={() => onVoid(payment)}
                >
                  Anular
                </button>
              ) : (
                "—"
              )}
            </TableCell>
          </tr>
        ))}
      </DataTable>
    </section>
  );
}

function ControlForm({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      <p className="mb-4 mt-1 text-sm text-slate-600">{description}</p>
      {children}
    </div>
  );
}

function MoneyInput({
  label,
  value,
  disabled,
  onChange,
}: {
  label: string;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className={labelClassName}>
      {label}
      <input
        className={inputClassName}
        disabled={disabled}
        inputMode="decimal"
        placeholder="0.00"
        required
        value={value}
        onChange={(event) => {
          if (isValidMoneyInputDraft(event.target.value)) {
            onChange(event.target.value);
          }
        }}
      />
    </label>
  );
}

function DataTable({
  headers,
  emptyMessage,
  children,
}: {
  headers: string[];
  emptyMessage: string;
  children: React.ReactNode;
}) {
  const hasRows = Array.isArray(children) ? children.length > 0 : Boolean(children);
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
      {hasRows ? (
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-600">
            <tr>
              {headers.map((header) => (
                <th className="px-4 py-3 font-semibold" key={header}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>{children}</tbody>
        </table>
      ) : (
        <p className="p-5 text-sm text-slate-600">{emptyMessage}</p>
      )}
    </div>
  );
}

function TableCell({ children }: { children: React.ReactNode }) {
  return (
    <td className="whitespace-nowrap px-4 py-3 align-top text-slate-700">
      {children}
    </td>
  );
}

function StatusBadge({
  status,
}: {
  status: keyof typeof EMPLOYEE_CONTROL_STATUS_LABELS;
}) {
  const styles =
    status === "voided"
      ? "bg-rose-100 text-rose-700"
      : status === "paid"
        ? "bg-emerald-100 text-emerald-700"
        : "bg-sky-100 text-sky-700";
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-semibold ${styles}`}>
      {EMPLOYEE_CONTROL_STATUS_LABELS[status]}
    </span>
  );
}

function validateAttendance(form: AttendanceForm): string | null {
  if (!form.attendanceDate) {
    return "La fecha de asistencia es obligatoria.";
  }
  if (
    form.hoursWorked &&
    !/^\d+(?:[.,]\d{0,2})?$/.test(form.hoursWorked.trim())
  ) {
    return "Las horas trabajadas deben ser un número no negativo con hasta 2 decimales.";
  }
  return null;
}

function toApiFilters(
  employeeId: number,
  period: PeriodFilters,
): EmployeeControlFilters {
  return {
    employee_id: employeeId,
    ...(period.dateFrom ? { date_from: period.dateFrom } : {}),
    ...(period.dateTo ? { date_to: period.dateTo } : {}),
  };
}

function normalizeOptionalDecimal(value: string): string | null {
  const normalized = value.trim().replace(",", ".");
  return normalized || null;
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function createAttendanceForm(): AttendanceForm {
  return {
    attendanceDate: getToday(),
    status: "present",
    checkInTime: "",
    checkOutTime: "",
    hoursWorked: "",
    notes: "",
  };
}

function createAdvanceForm(): AdvanceForm {
  return {
    advanceDate: getToday(),
    amount: "",
    reason: "",
    notes: "",
  };
}

function createLoanForm(): LoanForm {
  return {
    loanDate: getToday(),
    principalAmount: "",
    reason: "",
    notes: "",
  };
}

function createPaymentForm(): PaymentForm {
  return {
    loanId: "",
    paymentDate: getToday(),
    amount: "",
    notes: "",
  };
}

function getToday(): string {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 10);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function formatTime(value: string | null): string {
  return value ? value.slice(0, 5) : "—";
}

function formatMoney(value: string): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(Number(value));
}

const inputClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none transition focus:border-water-500 focus:ring-2 focus:ring-water-100 disabled:cursor-not-allowed disabled:bg-slate-100";
const labelClassName = "text-sm font-medium text-slate-700";
const primaryButtonClassName =
  "h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300";
const secondaryButtonClassName =
  "h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700";
const linkButtonClassName =
  "text-sm font-semibold text-water-700 hover:text-water-500";
const dangerButtonClassName =
  "text-sm font-semibold text-rose-700 hover:text-rose-500 disabled:cursor-not-allowed disabled:text-slate-400";

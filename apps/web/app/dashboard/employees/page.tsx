"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  EmployeeFilters,
  type EmployeeFilterValues,
} from "@/components/EmployeeFilters";
import { EmployeeForm } from "@/components/EmployeeForm";
import { EmployeeList } from "@/components/EmployeeList";
import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  activateEmployee,
  ApiError,
  createEmployee,
  deactivateEmployee,
  listEmployees,
  updateEmployee,
} from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { Employee, EmployeePayload } from "@/types/employee";

const emptyFilters: EmployeeFilterValues = {
  search: "",
  isActive: "",
  employeeType: "",
  jobPosition: "",
};

export default function EmployeesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [filters, setFilters] = useState<EmployeeFilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<EmployeeFilterValues>(emptyFilters);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingEmployeeId, setChangingEmployeeId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadEmployees(storedToken);
  }, [router]);

  async function loadEmployees(
    activeToken: string,
    activeFilters: EmployeeFilterValues = emptyFilters,
  ) {
    setIsLoading(true);
    setError("");

    try {
      const loadedEmployees = await listEmployees(activeToken, {
        ...(activeFilters.search ? { search: activeFilters.search } : {}),
        ...(activeFilters.isActive
          ? { is_active: activeFilters.isActive === "active" }
          : {}),
        ...(activeFilters.employeeType
          ? { employee_type: activeFilters.employeeType }
          : {}),
        ...(activeFilters.jobPosition
          ? { job_position: activeFilters.jobPosition }
          : {}),
      });
      setEmployees(loadedEmployees);
      setAppliedFilters({ ...activeFilters });
    } catch (loadError) {
      if (redirectIfUnauthorized(loadError)) {
        return;
      }
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  function handleShowCreateForm() {
    setEditingEmployee(null);
    setIsFormVisible(true);
    setError("");
    setMessage("");
  }

  function handleEdit(employee: Employee) {
    setEditingEmployee(employee);
    setIsFormVisible(true);
    setError("");
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelForm() {
    setEditingEmployee(null);
    setIsFormVisible(false);
  }

  async function handleSaveEmployee(payload: EmployeePayload): Promise<boolean> {
    if (!token) {
      return false;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const savedEmployee = editingEmployee
        ? await updateEmployee(token, editingEmployee.id, payload)
        : await createEmployee(token, payload);
      const action = editingEmployee ? "actualizado" : "registrado";

      setEditingEmployee(null);
      setIsFormVisible(false);
      setMessage(
        `Empleado ${action}: ${savedEmployee.first_name} ${savedEmployee.last_name}.`,
      );
      await loadEmployees(token, appliedFilters);
      return true;
    } catch (saveError) {
      if (redirectIfUnauthorized(saveError)) {
        return false;
      }
      setError(getErrorMessage(saveError));
      return false;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggleActive(employee: Employee) {
    if (!token) {
      return;
    }
    const fullName = `${employee.first_name} ${employee.last_name}`;
    if (
      employee.is_active &&
      !window.confirm(`¿Inactivar al empleado ${fullName}?`)
    ) {
      return;
    }

    setChangingEmployeeId(employee.id);
    setError("");
    setMessage("");

    try {
      const updatedEmployee = employee.is_active
        ? await deactivateEmployee(token, employee.id)
        : await activateEmployee(token, employee.id);
      setMessage(
        updatedEmployee.is_active
          ? `Empleado reactivado: ${fullName}.`
          : `Empleado inactivado: ${fullName}.`,
      );
      await loadEmployees(token, appliedFilters);
    } catch (statusError) {
      if (redirectIfUnauthorized(statusError)) {
        return;
      }
      setError(getErrorMessage(statusError));
    } finally {
      setChangingEmployeeId(null);
    }
  }

  function handleFilterSubmit() {
    if (token) {
      loadEmployees(token, filters);
    }
  }

  function handleClearFilters() {
    if (!token) {
      return;
    }
    setFilters(emptyFilters);
    loadEmployees(token, emptyFilters);
  }

  function redirectIfUnauthorized(possibleError: unknown): boolean {
    if (
      possibleError instanceof ApiError &&
      possibleError.status === 401
    ) {
      removeToken();
      router.replace("/login");
      return true;
    }
    return false;
  }

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
              Empleados
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Administra los empleados de Agua Activa. Este módulo será la base
              para anticipos, pagos, roles de pago, rutas y control operativo.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="h-10 rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500 disabled:cursor-not-allowed disabled:bg-slate-300"
              type="button"
              disabled={isSaving}
              onClick={handleShowCreateForm}
            >
              Nuevo empleado
            </button>
            <LogoutButton />
          </div>
        </header>

        {isFormVisible ? (
          <EmployeeForm
            key={editingEmployee?.id ?? "new"}
            employee={editingEmployee}
            isSubmitting={isSaving}
            onSubmit={handleSaveEmployee}
            onCancel={handleCancelForm}
          />
        ) : null}

        <EmployeeFilters
          filters={filters}
          disabled={isLoading}
          onChange={setFilters}
          onSubmit={handleFilterSubmit}
          onClear={handleClearFilters}
        />

        {error ? <ErrorMessage message={error} /> : null}
        {message ? (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </p>
        ) : null}

        {isLoading ? (
          <LoadingState label="Cargando empleados..." />
        ) : (
          <EmployeeList
            employees={employees}
            hasActiveFilters={hasActiveFilters(appliedFilters)}
            changingEmployeeId={changingEmployeeId}
            onEdit={handleEdit}
            onToggleActive={handleToggleActive}
          />
        )}
      </div>
    </main>
  );
}

function hasActiveFilters(filters: EmployeeFilterValues): boolean {
  return Boolean(
    filters.search ||
      filters.isActive ||
      filters.employeeType ||
      filters.jobPosition,
  );
}

function getErrorMessage(possibleError: unknown): string {
  if (possibleError instanceof Error) {
    return possibleError.message;
  }
  return "No se pudo completar la solicitud.";
}

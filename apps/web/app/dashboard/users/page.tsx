"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorMessage } from "@/components/ErrorMessage";
import { LoadingState } from "@/components/LoadingState";
import { LogoutButton } from "@/components/LogoutButton";
import {
  ApiError,
  createUser,
  getCurrentUser,
  listUsers,
  setUserActive,
  updateUser,
  updateUserPassword,
} from "@/lib/api";
import { getToken, removeToken, saveUser } from "@/lib/auth";
import type { UserRole } from "@/types/auth";
import type { User } from "@/types/user";

type CreateForm = {
  username: string;
  password: string;
  role: UserRole;
  isActive: boolean;
};

const emptyForm: CreateForm = {
  username: "",
  password: "",
  role: "operator",
  isActive: true,
};

export default function UsersPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [form, setForm] = useState<CreateForm>(emptyForm);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    const storedToken = getToken();
    if (!storedToken) {
      router.replace("/login");
      return;
    }
    void loadPage(storedToken);
  }, [router]);

  async function loadPage(activeToken: string) {
    setIsLoading(true);
    setError("");
    try {
      const currentUser = await getCurrentUser(activeToken);
      saveUser(currentUser);
      if (currentUser.role !== "admin_auditor") {
        setForbidden(true);
        return;
      }

      setToken(activeToken);
      setUsers(await listUsers(activeToken));
    } catch (loadError) {
      handleApiError(loadError, "No se pudieron cargar los usuarios.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsSaving(true);
    setError("");
    setMessage("");
    try {
      const created = await createUser(token, {
        username: form.username,
        password: form.password,
        role: form.role,
        is_active: form.isActive,
      });
      setUsers((current) =>
        [...current, created].sort((first, second) =>
          first.username.localeCompare(second.username),
        ),
      );
      setForm(emptyForm);
      setMessage(`Usuario creado: ${created.username}.`);
    } catch (saveError) {
      handleApiError(saveError, "No se pudo crear el usuario.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRoleChange(user: User, role: UserRole) {
    if (!token || role === user.role) {
      return;
    }
    setError("");
    setMessage("");
    try {
      const updated = await updateUser(token, user.id, { role });
      replaceUser(updated);
      setMessage(`Rol actualizado para ${updated.username}.`);
    } catch (saveError) {
      handleApiError(saveError, "No se pudo cambiar el rol.");
    }
  }

  async function handleToggleActive(user: User) {
    if (!token) {
      return;
    }
    const nextActive = !user.is_active;
    if (
      !window.confirm(
        `${nextActive ? "¿Activar" : "¿Desactivar"} a ${user.username}?`,
      )
    ) {
      return;
    }
    setError("");
    setMessage("");
    try {
      const updated = await setUserActive(token, user.id, nextActive);
      replaceUser(updated);
      setMessage(
        `${updated.username} quedó ${updated.is_active ? "activo" : "inactivo"}.`,
      );
    } catch (saveError) {
      handleApiError(saveError, "No se pudo cambiar el estado del usuario.");
    }
  }

  async function handlePasswordChange(user: User) {
    if (!token) {
      return;
    }
    const newPassword = window.prompt(
      `Nueva contraseña para ${user.username} (mínimo 8 caracteres):`,
    );
    if (newPassword === null) {
      return;
    }
    if (newPassword.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    setError("");
    setMessage("");
    try {
      await updateUserPassword(token, user.id, newPassword);
      setMessage(`Contraseña actualizada para ${user.username}.`);
    } catch (saveError) {
      handleApiError(saveError, "No se pudo cambiar la contraseña.");
    }
  }

  function replaceUser(updated: User) {
    setUsers((current) =>
      current.map((user) => (user.id === updated.id ? updated : user)),
    );
  }

  function handleApiError(possibleError: unknown, fallback: string) {
    if (possibleError instanceof ApiError) {
      if (possibleError.status === 401) {
        removeToken();
        router.replace("/login");
        return;
      }
      if (possibleError.status === 403) {
        setForbidden(true);
        return;
      }
    }
    setError(possibleError instanceof Error ? possibleError.message : fallback);
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Link
              className="text-sm font-semibold text-water-700 hover:text-water-500"
              href="/dashboard"
            >
              Volver al dashboard
            </Link>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Usuarios y permisos
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Administra las cuentas del ERP. Cada persona debe usar su propia
              cuenta.
            </p>
          </div>
          <LogoutButton />
        </header>

        {isLoading ? <LoadingState label="Cargando usuarios..." /> : null}

        {forbidden && !isLoading ? (
          <section className="rounded-xl border border-amber-200 bg-amber-50 p-5">
            <h2 className="text-lg font-semibold text-amber-950">
              No tienes permisos
            </h2>
            <p className="mt-2 text-sm leading-6 text-amber-900">
              Esta pantalla está disponible solo para el administrador/auditor.
            </p>
          </section>
        ) : null}

        {!forbidden && !isLoading ? (
          <>
            <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-950">
              No compartas la cuenta admin. La secretaria debe usar una cuenta
              operator.
            </p>

            {error ? <ErrorMessage message={error} /> : null}
            {message ? (
              <p className="rounded-md border border-water-100 bg-water-50 px-3 py-2 text-sm text-water-800">
                {message}
              </p>
            ) : null}

            <form
              className="grid gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-2"
              onSubmit={handleCreate}
            >
              <div className="md:col-span-2">
                <h2 className="text-xl font-semibold text-slate-950">
                  Crear usuario
                </h2>
              </div>
              <Field label="Usuario">
                <input
                  className={inputClassName}
                  autoComplete="off"
                  maxLength={100}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      username: event.target.value,
                    }))
                  }
                  required
                  value={form.username}
                />
              </Field>
              <Field label="Contraseña temporal">
                <input
                  className={inputClassName}
                  autoComplete="new-password"
                  minLength={8}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      password: event.target.value,
                    }))
                  }
                  required
                  type="password"
                  value={form.password}
                />
              </Field>
              <Field label="Rol">
                <select
                  className={inputClassName}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      role: event.target.value as UserRole,
                    }))
                  }
                  value={form.role}
                >
                  <option value="operator">operator</option>
                  <option value="admin_auditor">admin_auditor</option>
                </select>
              </Field>
              <label className="flex items-center gap-3 self-end pb-2 text-sm font-medium text-slate-700">
                <input
                  checked={form.isActive}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      isActive: event.target.checked,
                    }))
                  }
                  type="checkbox"
                />
                Usuario activo
              </label>
              <div className="md:col-span-2">
                <button
                  className="h-10 rounded-md bg-water-700 px-5 text-sm font-semibold text-white transition hover:bg-water-500 disabled:bg-slate-300"
                  disabled={isSaving}
                  type="submit"
                >
                  {isSaving ? "Creando..." : "Crear usuario"}
                </button>
              </div>
            </form>

            <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 px-5 py-4">
                <h2 className="text-xl font-semibold text-slate-950">
                  Cuentas registradas
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-left text-slate-600">
                    <tr>
                      <th className="px-5 py-3 font-semibold">Usuario</th>
                      <th className="px-5 py-3 font-semibold">Rol</th>
                      <th className="px-5 py-3 font-semibold">Estado</th>
                      <th className="px-5 py-3 font-semibold">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td className="px-5 py-4 font-medium text-slate-950">
                          {user.username}
                        </td>
                        <td className="px-5 py-4">
                          <select
                            aria-label={`Rol de ${user.username}`}
                            className="h-9 rounded-md border border-slate-300 bg-white px-2 text-slate-800"
                            onChange={(event) =>
                              void handleRoleChange(
                                user,
                                event.target.value as UserRole,
                              )
                            }
                            value={user.role}
                          >
                            <option value="operator">operator</option>
                            <option value="admin_auditor">
                              admin_auditor
                            </option>
                          </select>
                        </td>
                        <td className="px-5 py-4">
                          <span
                            className={
                              user.is_active
                                ? "rounded-full bg-emerald-100 px-2.5 py-1 font-medium text-emerald-800"
                                : "rounded-full bg-slate-200 px-2.5 py-1 font-medium text-slate-700"
                            }
                          >
                            {user.is_active ? "Activo" : "Inactivo"}
                          </span>
                        </td>
                        <td className="px-5 py-4">
                          <div className="flex flex-wrap gap-2">
                            <button
                              className="rounded-md border border-slate-300 px-3 py-1.5 font-semibold text-slate-700 hover:border-water-500 hover:text-water-700"
                              onClick={() => void handleToggleActive(user)}
                              type="button"
                            >
                              {user.is_active ? "Desactivar" : "Activar"}
                            </button>
                            <button
                              className="rounded-md border border-slate-300 px-3 py-1.5 font-semibold text-slate-700 hover:border-water-500 hover:text-water-700"
                              onClick={() => void handlePasswordChange(user)}
                              type="button"
                            >
                              Cambiar contraseña
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}

function Field({
  children,
  label,
}: {
  children: React.ReactNode;
  label: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

const inputClassName =
  "mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none focus:border-water-500 focus:ring-2 focus:ring-water-100";

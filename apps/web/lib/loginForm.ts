import type { LoginCredentials } from "@/types/auth";

const LOGIN_CONNECTIVITY_ERROR =
  "No se pudo iniciar sesión. Verifica la conexión o avisa a George.";

export function readLoginCredentials(formData: FormData): LoginCredentials {
  return {
    username: readTextField(formData, "username").trim(),
    password: readTextField(formData, "password"),
  };
}

export function getLoginErrorMessage(error: unknown): string {
  const status = getErrorStatus(error);

  if (status === 401) {
    return "Usuario o contraseña incorrectos.";
  }
  if (status === 403) {
    return "La cuenta está inactiva. Solicita ayuda a George.";
  }
  if (status === 0) {
    return LOGIN_CONNECTIVITY_ERROR;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return LOGIN_CONNECTIVITY_ERROR;
}

function readTextField(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

function getErrorStatus(error: unknown): number | undefined {
  if (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    typeof error.status === "number"
  ) {
    return error.status;
  }
  return undefined;
}

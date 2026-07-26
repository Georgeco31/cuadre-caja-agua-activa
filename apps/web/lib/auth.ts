import type { CurrentUser, UserRole } from "@/types/auth";

const TOKEN_KEY = "cuadre_caja_access_token";
const USER_KEY = "cuadre_caja_current_user";

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function getStoredUser(): CurrentUser | null {
  if (typeof window === "undefined") {
    return null;
  }

  const value = window.localStorage.getItem(USER_KEY);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as CurrentUser;
  } catch {
    window.localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function saveUser(user: CurrentUser): void {
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getStoredRole(): UserRole | null {
  const storedUser = getStoredUser();
  if (storedUser?.role) {
    return storedUser.role;
  }

  const token = getToken();
  if (!token) {
    return null;
  }
  try {
    const encodedPayload = token
      .split(".")[1]
      .replace(/-/g, "+")
      .replace(/_/g, "/");
    const paddedPayload = encodedPayload.padEnd(
      Math.ceil(encodedPayload.length / 4) * 4,
      "=",
    );
    const payload = JSON.parse(
      window.atob(paddedPayload),
    ) as { role?: UserRole };
    return payload.role ?? null;
  } catch {
    return null;
  }
}

export function isAdminAuditor(): boolean {
  return getStoredRole() === "admin_auditor";
}

export function removeToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

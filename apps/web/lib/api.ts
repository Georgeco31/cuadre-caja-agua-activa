import type { CurrentUser, LoginCredentials, TokenResponse } from "@/types/auth";
import type {
  CashCountItem,
  CashCountItemPayload,
  CashSession,
  CashSessionPayload,
} from "@/types/cashSession";
import type { Denomination } from "@/types/denomination";
import type { Expense, ExpensePayload } from "@/types/expense";
import type { CashSessionSummary } from "@/types/summary";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function login(
  credentials: LoginCredentials,
): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function getCurrentUser(token: string): Promise<CurrentUser> {
  return request<CurrentUser>("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function listDenominations(token: string): Promise<Denomination[]> {
  return request<Denomination[]>("/denominations", {
    headers: authHeaders(token),
  });
}

export async function getCashSessionByDate(
  token: string,
  sessionDate: string,
): Promise<CashSession> {
  return request<CashSession>(`/cash-sessions/by-date/${sessionDate}`, {
    headers: authHeaders(token),
  });
}

export async function createCashSession(
  token: string,
  payload: CashSessionPayload,
): Promise<CashSession> {
  return request<CashSession>("/cash-sessions", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function setCashCountItem(
  token: string,
  cashSessionId: number,
  payload: CashCountItemPayload,
): Promise<CashCountItem> {
  return request<CashCountItem>(
    `/cash-sessions/${cashSessionId}/count-items`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function getCashSessionSummary(
  token: string,
  cashSessionId: number,
): Promise<CashSessionSummary> {
  return request<CashSessionSummary>(
    `/cash-sessions/${cashSessionId}/summary`,
    {
      headers: authHeaders(token),
    },
  );
}

export async function closeCashSession(
  token: string,
  cashSessionId: number,
): Promise<CashSession> {
  return request<CashSession>(`/cash-sessions/${cashSessionId}/close`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function listExpenses(
  token: string,
  cashSessionId: number,
): Promise<Expense[]> {
  return request<Expense[]>(`/cash-sessions/${cashSessionId}/expenses`, {
    headers: authHeaders(token),
  });
}

export async function createExpense(
  token: string,
  cashSessionId: number,
  payload: ExpensePayload,
): Promise<Expense> {
  return request<Expense>(`/cash-sessions/${cashSessionId}/expenses`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const message = await getErrorMessage(response);
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
  };
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string | unknown[] };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    return "No se pudo completar la solicitud.";
  }

  return "No se pudo completar la solicitud.";
}

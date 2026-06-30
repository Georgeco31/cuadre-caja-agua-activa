import type { CurrentUser, LoginCredentials, TokenResponse } from "@/types/auth";
import type {
  CashCountItem,
  CashCountItemPayload,
  CashSession,
  CashSessionFilters,
  CashSessionPayload,
} from "@/types/cashSession";
import type { CountItemDetail } from "@/types/countItem";
import type {
  CorrectionCountItemPayload,
  CorrectionCountItemResponse,
  CorrectionExpensePayload,
  CorrectionExpenseResponse,
  CorrectionLog,
} from "@/types/correction";
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

export async function getCashSession(
  token: string,
  cashSessionId: number,
): Promise<CashSession> {
  return request<CashSession>(`/cash-sessions/${cashSessionId}`, {
    headers: authHeaders(token),
  });
}

export async function listCashSessions(
  token: string,
  filters: CashSessionFilters = {},
): Promise<CashSession[]> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  if (filters.status) {
    searchParams.set("status", filters.status);
  }

  const query = searchParams.toString();
  return request<CashSession[]>(`/cash-sessions${query ? `?${query}` : ""}`, {
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

export async function listCashCountItems(
  token: string,
  cashSessionId: number,
): Promise<CountItemDetail[]> {
  return request<CountItemDetail[]>(
    `/cash-sessions/${cashSessionId}/count-items`,
    {
      headers: authHeaders(token),
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

export async function listCorrections(
  token: string,
  cashSessionId: number,
): Promise<CorrectionLog[]> {
  return request<CorrectionLog[]>(
    `/cash-sessions/${cashSessionId}/corrections`,
    {
      headers: authHeaders(token),
    },
  );
}

export async function correctCashCountItem(
  token: string,
  cashSessionId: number,
  payload: CorrectionCountItemPayload,
): Promise<CorrectionCountItemResponse> {
  return request<CorrectionCountItemResponse>(
    `/cash-sessions/${cashSessionId}/corrections/count-items`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function createCorrectiveExpense(
  token: string,
  cashSessionId: number,
  payload: CorrectionExpensePayload,
): Promise<CorrectionExpenseResponse> {
  return request<CorrectionExpenseResponse>(
    `/cash-sessions/${cashSessionId}/corrections/expenses`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
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

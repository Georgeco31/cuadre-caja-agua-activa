import type { CurrentUser, LoginCredentials, TokenResponse } from "@/types/auth";
import type {
  CashCountItem,
  CashCountItemPayload,
  CashSession,
  CashSessionFilters,
  CashSessionPayload,
} from "@/types/cashSession";
import type { CountItemDetail } from "@/types/countItem";
import type { DailyOperationalSummary } from "@/types/dailyOperationalSummary";
import type { MonthlyOperationalSummary } from "@/types/monthlyOperationalSummary";
import type {
  ManagementDashboard,
  ManagementDashboardFilters,
} from "@/types/managementDashboard";
import type {
  CreditPayment,
  CreditPaymentFilters,
  CreditPaymentPayload,
} from "@/types/creditPayment";
import type {
  Customer,
  CustomerFilters,
  CustomerPayload,
  CustomerUpdatePayload,
} from "@/types/customer";
import type {
  CorrectionCountItemPayload,
  CorrectionCountItemResponse,
  CorrectionExpensePayload,
  CorrectionExpenseResponse,
  CorrectionLog,
} from "@/types/correction";
import type { Denomination } from "@/types/denomination";
import type {
  DeliveryRoute,
  DeliveryRouteFilters,
  DeliveryRoutePayload,
  DeliveryRouteUpdatePayload,
} from "@/types/deliveryRoute";
import type {
  Employee,
  EmployeeFilters,
  EmployeePayload,
  EmployeeUpdatePayload,
} from "@/types/employee";
import type {
  EmployeeAccountSummary,
  EmployeeAdvance,
  EmployeeAdvancePayload,
  EmployeeAttendance,
  EmployeeAttendancePayload,
  EmployeeAttendanceUpdatePayload,
  EmployeeControlFilters,
  EmployeeLoan,
  EmployeeLoanPayment,
  EmployeeLoanPaymentFilters,
  EmployeeLoanPaymentPayload,
  EmployeeLoanPayload,
} from "@/types/employeeControls";
import type { Expense, ExpensePayload } from "@/types/expense";
import type {
  InventoryLocation,
  InventoryLocationFilters,
  InventoryLocationPayload,
  InventoryLocationUpdatePayload,
  InventoryMovement,
  InventoryMovementFilters,
  InventoryMovementPayload,
  InventoryStock,
  InventoryStockFilters,
} from "@/types/inventory";
import type {
  OperatingExpense,
  OperatingExpenseCategory,
  OperatingExpenseCategoryFilters,
  OperatingExpenseCategoryPayload,
  OperatingExpenseCategoryUpdatePayload,
  OperatingExpenseFilters,
  OperatingExpensePayload,
  OperatingExpenseSummary,
  OperatingExpenseSummaryFilters,
  OperatingExpenseUpdatePayload,
  RecurringOperatingExpense,
  RecurringOperatingExpenseCreateExpensePayload,
  RecurringOperatingExpenseFilters,
  RecurringOperatingExpensePayload,
  RecurringOperatingExpenseUpdatePayload,
} from "@/types/operatingExpense";
import type {
  EmployeePayrollSummary,
  PayrollPreview,
  PayrollPreviewPayload,
  PayrollRun,
  PayrollRunFilters,
  PayrollRunPayload,
  PayrollRunSummary,
} from "@/types/payroll";
import type {
  Product,
  ProductFilters,
  ProductPayload,
  ProductProductionClassificationPayload,
  ProductUpdatePayload,
} from "@/types/product";
import type {
  ProductionRecipe,
  ProductionRecipeCostEstimate,
  ProductionRecipeFilters,
  ProductionRecipeItem,
  ProductionRecipeItemPayload,
  ProductionRecipeItemUpdatePayload,
  ProductionRecipePayload,
  ProductionRecipeUpdatePayload,
} from "@/types/productionRecipe";
import type {
  ProductionBatchMaterialConsumption,
  ProductionMaterialConsumption,
  ProductionMaterialConsumptionFilters,
  ProductionMaterialConsumptionPayload,
  ProductionMaterialConsumptionPreview,
  ProductionMaterialConsumptionPreviewPayload,
} from "@/types/productionMaterialConsumption";
import type {
  PriceList,
  PriceListFilters,
  PriceListItem,
  PriceListItemPayload,
  PriceListItemUpdatePayload,
  PriceListPayload,
  PriceListUpdatePayload,
  PriceResolution,
  PriceResolutionParams,
} from "@/types/pricing";
import type {
  Purchase,
  PurchaseFilters,
  PurchasePayload,
} from "@/types/purchase";
import type {
  ProductionBatch,
  ProductionBatchFilters,
  ProductionBatchPayload,
  ProductionInventoryApplication,
  ProductionInventoryApplyPayload,
} from "@/types/production";
import type {
  CashSummaryReport,
  CashSummaryReportFilters,
} from "@/types/report";
import type {
  RouteLoad,
  RouteLoadFilters,
  RouteLoadPayload,
} from "@/types/routeLoad";
import type { RouteCommercialActivity } from "@/types/routeActivity";
import type {
  RouteClosure,
  RouteClosureFilters,
  RouteClosurePayload,
  RouteLoadFinancialClosure,
} from "@/types/routeClosure";
import type {
  RouteCashComparisonFilters,
  RouteCashComparisonReport,
} from "@/types/routeCashComparison";
import type {
  CashSessionRouteCashReceipts,
  RouteCashReceipt,
  RouteCashReceiptFilters,
  RouteCashReceiptPayload,
  RouteClosureCashReceipt,
} from "@/types/routeCashReceipt";
import type {
  RouteReturn,
  RouteReturnFilters,
  RouteReturnPayload,
} from "@/types/routeReturn";
import type { RouteSettlement } from "@/types/routeSettlement";
import type {
  CustomerStatement,
  CustomerStatementFilters,
  OverdueReceivable,
  ReceivableCustomer,
  ReceivableCustomerFilters,
  ReceivablesSummary,
  ReceivablesSummaryFilters,
} from "@/types/receivable";
import type {
  CashSale,
  CashSaleFilters,
  CashSalePayload,
  CreditSalePayload,
  CustomerCreditBalance,
  SaleDateCorrectionPayload,
  SaleDateCorrectionResponse,
} from "@/types/sale";
import type { CashSessionSummary } from "@/types/summary";
import type {
  Supplier,
  SupplierFilters,
  SupplierPayload,
  SupplierUpdatePayload,
} from "@/types/supplier";
import type {
  Vehicle,
  VehicleFilters,
  VehiclePayload,
  VehicleUpdatePayload,
} from "@/types/vehicle";
import type {
  User,
  UserCreatePayload,
  UserUpdatePayload,
} from "@/types/user";
import { buildApiUrl } from "@/lib/apiUrl";

export {
  buildApiUrl,
  getApiBaseUrl,
  resolveApiBaseUrl,
} from "@/lib/apiUrl";

export class ApiError extends Error {
  status: number;
  cause?: unknown;

  constructor(message: string, status: number, cause?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.cause = cause;
  }
}

const AUTH_REQUEST_TIMEOUT_MS = 15_000;

export async function login(
  credentials: LoginCredentials,
): Promise<TokenResponse> {
  return requestWithTimeout<TokenResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify(credentials),
    },
    AUTH_REQUEST_TIMEOUT_MS,
  );
}

export async function getCurrentUser(token: string): Promise<CurrentUser> {
  return requestWithTimeout<CurrentUser>(
    "/auth/me",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
    AUTH_REQUEST_TIMEOUT_MS,
  );
}

export async function listUsers(token: string): Promise<User[]> {
  return request<User[]>("/users", {
    headers: authHeaders(token),
  });
}

export async function createUser(
  token: string,
  payload: UserCreatePayload,
): Promise<User> {
  return request<User>("/users", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateUser(
  token: string,
  userId: number,
  payload: UserUpdatePayload,
): Promise<User> {
  return request<User>(`/users/${userId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function setUserActive(
  token: string,
  userId: number,
  isActive: boolean,
): Promise<User> {
  return request<User>(`/users/${userId}/${isActive ? "activate" : "deactivate"}`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function updateUserPassword(
  token: string,
  userId: number,
  newPassword: string,
): Promise<User> {
  return request<User>(`/users/${userId}/password`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify({ new_password: newPassword }),
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

export async function getCashSummaryReport(
  token: string,
  filters: CashSummaryReportFilters = {},
): Promise<CashSummaryReport> {
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
  return request<CashSummaryReport>(
    `/reports/cash-summary${query ? `?${query}` : ""}`,
    {
      headers: authHeaders(token),
    },
  );
}

export async function getRouteCashComparisonReport(
  token: string,
  filters: RouteCashComparisonFilters = {},
): Promise<RouteCashComparisonReport> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }

  const query = searchParams.toString();
  return request<RouteCashComparisonReport>(
    `/reports/route-cash-comparison${query ? `?${query}` : ""}`,
    {
      headers: authHeaders(token),
    },
  );
}

export async function getDailyOperationalSummary(
  token: string,
  date?: string,
): Promise<DailyOperationalSummary> {
  const searchParams = new URLSearchParams();
  if (date) {
    searchParams.set("date", date);
  }
  const query = searchParams.toString();
  return request<DailyOperationalSummary>(
    `/reports/daily-operational-summary${query ? `?${query}` : ""}`,
    {
      headers: authHeaders(token),
    },
  );
}

export async function getMonthlyOperationalSummary(
  token: string,
  year?: number,
  month?: number,
): Promise<MonthlyOperationalSummary> {
  const searchParams = new URLSearchParams();
  if (year !== undefined) {
    searchParams.set("year", String(year));
  }
  if (month !== undefined) {
    searchParams.set("month", String(month));
  }
  const query = searchParams.toString();
  return request<MonthlyOperationalSummary>(
    `/reports/monthly-operational-summary${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getManagementDashboard(
  token: string,
  filters: ManagementDashboardFilters = {},
): Promise<ManagementDashboard> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  const query = searchParams.toString();
  return request<ManagementDashboard>(
    `/reports/management-dashboard${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function downloadFile(
  token: string,
  endpoint: string,
  filename: string,
): Promise<void> {
  const response = await apiFetch(endpoint, {
    headers: authHeaders(token),
  });
  if (!response.ok) {
    const message = await getErrorMessage(response);
    throw new ApiError(message, response.status);
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  link.hidden = true;
  document.body.appendChild(link);
  try {
    link.click();
  } finally {
    link.remove();
    URL.revokeObjectURL(objectUrl);
  }
}

export async function listCustomers(
  token: string,
  filters: CustomerFilters = {},
): Promise<Customer[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.customer_type) {
    searchParams.set("customer_type", filters.customer_type);
  }
  if (filters.sector) {
    searchParams.set("sector", filters.sector);
  }

  const query = searchParams.toString();
  return request<Customer[]>(`/customers${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getCustomer(
  token: string,
  customerId: number,
): Promise<Customer> {
  return request<Customer>(`/customers/${customerId}`, {
    headers: authHeaders(token),
  });
}

export async function createCustomer(
  token: string,
  payload: CustomerPayload,
): Promise<Customer> {
  return request<Customer>("/customers", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateCustomer(
  token: string,
  customerId: number,
  payload: CustomerUpdatePayload,
): Promise<Customer> {
  return request<Customer>(`/customers/${customerId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function deactivateCustomer(
  token: string,
  customerId: number,
): Promise<Customer> {
  return request<Customer>(`/customers/${customerId}/deactivate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function activateCustomer(
  token: string,
  customerId: number,
): Promise<Customer> {
  return request<Customer>(`/customers/${customerId}/activate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function listEmployees(
  token: string,
  filters: EmployeeFilters = {},
): Promise<Employee[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.employee_type) {
    searchParams.set("employee_type", filters.employee_type);
  }
  if (filters.job_position) {
    searchParams.set("job_position", filters.job_position);
  }

  const query = searchParams.toString();
  return request<Employee[]>(`/employees${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getEmployee(
  token: string,
  employeeId: number,
): Promise<Employee> {
  return request<Employee>(`/employees/${employeeId}`, {
    headers: authHeaders(token),
  });
}

export async function createEmployee(
  token: string,
  payload: EmployeePayload,
): Promise<Employee> {
  return request<Employee>("/employees", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateEmployee(
  token: string,
  employeeId: number,
  payload: EmployeeUpdatePayload,
): Promise<Employee> {
  return request<Employee>(`/employees/${employeeId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function deactivateEmployee(
  token: string,
  employeeId: number,
  terminationDate?: string,
): Promise<Employee> {
  return request<Employee>(`/employees/${employeeId}/deactivate`, {
    method: "PATCH",
    headers: authHeaders(token),
    ...(terminationDate
      ? { body: JSON.stringify({ termination_date: terminationDate }) }
      : {}),
  });
}

export async function activateEmployee(
  token: string,
  employeeId: number,
): Promise<Employee> {
  return request<Employee>(`/employees/${employeeId}/activate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function listEmployeeAttendance(
  token: string,
  filters: EmployeeControlFilters = {},
): Promise<EmployeeAttendance[]> {
  return request<EmployeeAttendance[]>(
    `/employees/attendance${buildEmployeeControlQuery(filters)}`,
    { headers: authHeaders(token) },
  );
}

export async function createEmployeeAttendance(
  token: string,
  payload: EmployeeAttendancePayload,
): Promise<EmployeeAttendance> {
  return request<EmployeeAttendance>("/employees/attendance", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateEmployeeAttendance(
  token: string,
  attendanceId: number,
  payload: EmployeeAttendanceUpdatePayload,
): Promise<EmployeeAttendance> {
  return request<EmployeeAttendance>(
    `/employees/attendance/${attendanceId}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function listEmployeeAdvances(
  token: string,
  filters: EmployeeControlFilters = {},
): Promise<EmployeeAdvance[]> {
  return request<EmployeeAdvance[]>(
    `/employees/advances${buildEmployeeControlQuery(filters)}`,
    { headers: authHeaders(token) },
  );
}

export async function createEmployeeAdvance(
  token: string,
  payload: EmployeeAdvancePayload,
): Promise<EmployeeAdvance> {
  return request<EmployeeAdvance>("/employees/advances", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function voidEmployeeAdvance(
  token: string,
  advanceId: number,
  reason: string,
): Promise<EmployeeAdvance> {
  return request<EmployeeAdvance>(`/employees/advances/${advanceId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function listEmployeeLoans(
  token: string,
  filters: EmployeeControlFilters = {},
): Promise<EmployeeLoan[]> {
  return request<EmployeeLoan[]>(
    `/employees/loans${buildEmployeeControlQuery(filters)}`,
    { headers: authHeaders(token) },
  );
}

export async function createEmployeeLoan(
  token: string,
  payload: EmployeeLoanPayload,
): Promise<EmployeeLoan> {
  return request<EmployeeLoan>("/employees/loans", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function voidEmployeeLoan(
  token: string,
  loanId: number,
  reason: string,
): Promise<EmployeeLoan> {
  return request<EmployeeLoan>(`/employees/loans/${loanId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function listEmployeeLoanPayments(
  token: string,
  filters: EmployeeLoanPaymentFilters = {},
): Promise<EmployeeLoanPayment[]> {
  return request<EmployeeLoanPayment[]>(
    `/employees/loan-payments${buildEmployeeControlQuery(filters)}`,
    { headers: authHeaders(token) },
  );
}

export async function createEmployeeLoanPayment(
  token: string,
  loanId: number,
  payload: EmployeeLoanPaymentPayload,
): Promise<EmployeeLoanPayment> {
  return request<EmployeeLoanPayment>(
    `/employees/loans/${loanId}/payments`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function voidEmployeeLoanPayment(
  token: string,
  paymentId: number,
  reason: string,
): Promise<EmployeeLoanPayment> {
  return request<EmployeeLoanPayment>(
    `/employees/loan-payments/${paymentId}/void`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ reason }),
    },
  );
}

export async function getEmployeeAccountSummary(
  token: string,
  employeeId: number,
  filters: Pick<EmployeeControlFilters, "date_from" | "date_to"> = {},
): Promise<EmployeeAccountSummary> {
  return request<EmployeeAccountSummary>(
    `/employees/${employeeId}/account-summary${buildEmployeeControlQuery(
      filters,
    )}`,
    { headers: authHeaders(token) },
  );
}

export async function previewPayrollRun(
  token: string,
  payload: PayrollPreviewPayload,
): Promise<PayrollPreview> {
  return request<PayrollPreview>("/payroll/runs/preview", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function createPayrollRun(
  token: string,
  payload: PayrollRunPayload,
): Promise<PayrollRun> {
  return request<PayrollRun>("/payroll/runs", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listPayrollRuns(
  token: string,
  filters: PayrollRunFilters = {},
): Promise<PayrollRunSummary[]> {
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
  if (filters.employee_id !== undefined) {
    searchParams.set("employee_id", String(filters.employee_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<PayrollRunSummary[]>(
    `/payroll/runs${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getPayrollRun(
  token: string,
  payrollRunId: number,
): Promise<PayrollRun> {
  return request<PayrollRun>(`/payroll/runs/${payrollRunId}`, {
    headers: authHeaders(token),
  });
}

export async function voidPayrollRun(
  token: string,
  payrollRunId: number,
  reason: string,
): Promise<PayrollRun> {
  return request<PayrollRun>(`/payroll/runs/${payrollRunId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function getEmployeePayrollSummary(
  token: string,
  employeeId: number,
  filters: Pick<PayrollRunFilters, "date_from" | "date_to"> = {},
): Promise<EmployeePayrollSummary> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  const query = searchParams.toString();
  return request<EmployeePayrollSummary>(
    `/employees/${employeeId}/payroll-summary${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function listDeliveryRoutes(
  token: string,
  filters: DeliveryRouteFilters = {},
): Promise<DeliveryRoute[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.zone) {
    searchParams.set("zone", filters.zone);
  }
  if (filters.sector) {
    searchParams.set("sector", filters.sector);
  }

  const query = searchParams.toString();
  return request<DeliveryRoute[]>(
    `/delivery-routes${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getDeliveryRoute(
  token: string,
  routeId: number,
): Promise<DeliveryRoute> {
  return request<DeliveryRoute>(`/delivery-routes/${routeId}`, {
    headers: authHeaders(token),
  });
}

export async function createDeliveryRoute(
  token: string,
  payload: DeliveryRoutePayload,
): Promise<DeliveryRoute> {
  return request<DeliveryRoute>("/delivery-routes", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateDeliveryRoute(
  token: string,
  routeId: number,
  payload: DeliveryRouteUpdatePayload,
): Promise<DeliveryRoute> {
  return request<DeliveryRoute>(`/delivery-routes/${routeId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function deactivateDeliveryRoute(
  token: string,
  routeId: number,
): Promise<DeliveryRoute> {
  return request<DeliveryRoute>(`/delivery-routes/${routeId}/deactivate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function activateDeliveryRoute(
  token: string,
  routeId: number,
): Promise<DeliveryRoute> {
  return request<DeliveryRoute>(`/delivery-routes/${routeId}/activate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function listVehicles(
  token: string,
  filters: VehicleFilters = {},
): Promise<Vehicle[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.vehicle_type) {
    searchParams.set("vehicle_type", filters.vehicle_type);
  }
  if (filters.fuel_type) {
    searchParams.set("fuel_type", filters.fuel_type);
  }

  const query = searchParams.toString();
  return request<Vehicle[]>(`/vehicles${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getVehicle(
  token: string,
  vehicleId: number,
): Promise<Vehicle> {
  return request<Vehicle>(`/vehicles/${vehicleId}`, {
    headers: authHeaders(token),
  });
}

export async function createVehicle(
  token: string,
  payload: VehiclePayload,
): Promise<Vehicle> {
  return request<Vehicle>("/vehicles", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateVehicle(
  token: string,
  vehicleId: number,
  payload: VehicleUpdatePayload,
): Promise<Vehicle> {
  return request<Vehicle>(`/vehicles/${vehicleId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function deactivateVehicle(
  token: string,
  vehicleId: number,
): Promise<Vehicle> {
  return request<Vehicle>(`/vehicles/${vehicleId}/deactivate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function activateVehicle(
  token: string,
  vehicleId: number,
): Promise<Vehicle> {
  return request<Vehicle>(`/vehicles/${vehicleId}/activate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function listProducts(
  token: string,
  filters: ProductFilters = {},
): Promise<Product[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.category) {
    searchParams.set("category", filters.category);
  }
  if (filters.unit) {
    searchParams.set("unit", filters.unit);
  }
  if (filters.product_kind) {
    searchParams.set("product_kind", filters.product_kind);
  }

  const query = searchParams.toString();
  return request<Product[]>(`/products${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getProduct(
  token: string,
  productId: number,
): Promise<Product> {
  return request<Product>(`/products/${productId}`, {
    headers: authHeaders(token),
  });
}

export async function createProduct(
  token: string,
  payload: ProductPayload,
): Promise<Product> {
  return request<Product>("/products", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateProduct(
  token: string,
  productId: number,
  payload: ProductUpdatePayload,
): Promise<Product> {
  return request<Product>(`/products/${productId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateProductProductionClassification(
  token: string,
  productId: number,
  payload: ProductProductionClassificationPayload,
): Promise<Product> {
  return request<Product>(
    `/products/${productId}/production-classification`,
    {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function listProductionRecipes(
  token: string,
  filters: ProductionRecipeFilters = {},
): Promise<ProductionRecipe[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.status) {
    searchParams.set("status", filters.status);
  }
  if (filters.output_product_id !== undefined) {
    searchParams.set(
      "output_product_id",
      String(filters.output_product_id),
    );
  }
  if (filters.product_kind) {
    searchParams.set("product_kind", filters.product_kind);
  }
  if (filters.is_valid_today !== undefined) {
    searchParams.set("is_valid_today", String(filters.is_valid_today));
  }
  const query = searchParams.toString();
  return request<ProductionRecipe[]>(
    `/production/recipes${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getProductionRecipe(
  token: string,
  recipeId: number,
): Promise<ProductionRecipe> {
  return request<ProductionRecipe>(`/production/recipes/${recipeId}`, {
    headers: authHeaders(token),
  });
}

export async function createProductionRecipe(
  token: string,
  payload: ProductionRecipePayload,
): Promise<ProductionRecipe> {
  return request<ProductionRecipe>("/production/recipes", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateProductionRecipe(
  token: string,
  recipeId: number,
  payload: ProductionRecipeUpdatePayload,
): Promise<ProductionRecipe> {
  return request<ProductionRecipe>(`/production/recipes/${recipeId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function setProductionRecipeActive(
  token: string,
  recipeId: number,
  isActive: boolean,
): Promise<ProductionRecipe> {
  return request<ProductionRecipe>(
    `/production/recipes/${recipeId}/${
      isActive ? "activate" : "deactivate"
    }`,
    { method: "PATCH", headers: authHeaders(token) },
  );
}

export async function voidProductionRecipe(
  token: string,
  recipeId: number,
  reason: string,
): Promise<ProductionRecipe> {
  return request<ProductionRecipe>(
    `/production/recipes/${recipeId}/void`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ reason }),
    },
  );
}

export async function createProductionRecipeItem(
  token: string,
  recipeId: number,
  payload: ProductionRecipeItemPayload,
): Promise<ProductionRecipeItem> {
  return request<ProductionRecipeItem>(
    `/production/recipes/${recipeId}/items`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function updateProductionRecipeItem(
  token: string,
  itemId: number,
  payload: ProductionRecipeItemUpdatePayload,
): Promise<ProductionRecipeItem> {
  return request<ProductionRecipeItem>(
    `/production/recipe-items/${itemId}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function setProductionRecipeItemActive(
  token: string,
  itemId: number,
  isActive: boolean,
): Promise<ProductionRecipeItem> {
  return request<ProductionRecipeItem>(
    `/production/recipe-items/${itemId}/${
      isActive ? "activate" : "deactivate"
    }`,
    { method: "PATCH", headers: authHeaders(token) },
  );
}

export async function getProductionRecipeCostEstimate(
  token: string,
  recipeId: number,
  outputQuantity?: string,
): Promise<ProductionRecipeCostEstimate> {
  const searchParams = new URLSearchParams();
  if (outputQuantity) {
    searchParams.set("output_quantity", outputQuantity);
  }
  const query = searchParams.toString();
  return request<ProductionRecipeCostEstimate>(
    `/production/recipes/${recipeId}/cost-estimate${
      query ? `?${query}` : ""
    }`,
    { headers: authHeaders(token) },
  );
}

export async function deactivateProduct(
  token: string,
  productId: number,
): Promise<Product> {
  return request<Product>(`/products/${productId}/deactivate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function activateProduct(
  token: string,
  productId: number,
): Promise<Product> {
  return request<Product>(`/products/${productId}/activate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function listSuppliers(
  token: string,
  filters: SupplierFilters = {},
): Promise<Supplier[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.supplier_type) {
    searchParams.set("supplier_type", filters.supplier_type);
  }

  const query = searchParams.toString();
  return request<Supplier[]>(`/suppliers${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getSupplier(
  token: string,
  supplierId: number,
): Promise<Supplier> {
  return request<Supplier>(`/suppliers/${supplierId}`, {
    headers: authHeaders(token),
  });
}

export async function createSupplier(
  token: string,
  payload: SupplierPayload,
): Promise<Supplier> {
  return request<Supplier>("/suppliers", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateSupplier(
  token: string,
  supplierId: number,
  payload: SupplierUpdatePayload,
): Promise<Supplier> {
  return request<Supplier>(`/suppliers/${supplierId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function deactivateSupplier(
  token: string,
  supplierId: number,
): Promise<Supplier> {
  return request<Supplier>(`/suppliers/${supplierId}/deactivate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function activateSupplier(
  token: string,
  supplierId: number,
): Promise<Supplier> {
  return request<Supplier>(`/suppliers/${supplierId}/activate`, {
    method: "PATCH",
    headers: authHeaders(token),
  });
}

export async function listPurchases(
  token: string,
  filters: PurchaseFilters = {},
): Promise<Purchase[]> {
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
  if (filters.payment_status) {
    searchParams.set("payment_status", filters.payment_status);
  }
  if (filters.supplier_id !== undefined) {
    searchParams.set("supplier_id", String(filters.supplier_id));
  }
  if (filters.product_id !== undefined) {
    searchParams.set("product_id", String(filters.product_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }

  const query = searchParams.toString();
  return request<Purchase[]>(`/purchases${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getPurchase(
  token: string,
  purchaseId: number,
): Promise<Purchase> {
  return request<Purchase>(`/purchases/${purchaseId}`, {
    headers: authHeaders(token),
  });
}

export async function createPurchase(
  token: string,
  payload: PurchasePayload,
): Promise<Purchase> {
  return request<Purchase>("/purchases", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function voidPurchase(
  token: string,
  purchaseId: number,
  reason: string,
): Promise<Purchase> {
  return request<Purchase>(`/purchases/${purchaseId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function listOperatingExpenseCategories(
  token: string,
  filters: OperatingExpenseCategoryFilters = {},
): Promise<OperatingExpenseCategory[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  const query = searchParams.toString();
  return request<OperatingExpenseCategory[]>(
    `/operating-expenses/categories${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getOperatingExpenseCategory(
  token: string,
  categoryId: number,
): Promise<OperatingExpenseCategory> {
  return request<OperatingExpenseCategory>(
    `/operating-expenses/categories/${categoryId}`,
    { headers: authHeaders(token) },
  );
}

export async function createOperatingExpenseCategory(
  token: string,
  payload: OperatingExpenseCategoryPayload,
): Promise<OperatingExpenseCategory> {
  return request<OperatingExpenseCategory>("/operating-expenses/categories", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateOperatingExpenseCategory(
  token: string,
  categoryId: number,
  payload: OperatingExpenseCategoryUpdatePayload,
): Promise<OperatingExpenseCategory> {
  return request<OperatingExpenseCategory>(
    `/operating-expenses/categories/${categoryId}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function setOperatingExpenseCategoryActive(
  token: string,
  categoryId: number,
  isActive: boolean,
): Promise<OperatingExpenseCategory> {
  return request<OperatingExpenseCategory>(
    `/operating-expenses/categories/${categoryId}/${
      isActive ? "activate" : "deactivate"
    }`,
    { method: "PATCH", headers: authHeaders(token) },
  );
}

export async function listOperatingExpenses(
  token: string,
  filters: OperatingExpenseFilters = {},
): Promise<OperatingExpense[]> {
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
  if (filters.payment_status) {
    searchParams.set("payment_status", filters.payment_status);
  }
  if (filters.category_id !== undefined) {
    searchParams.set("category_id", String(filters.category_id));
  }
  if (filters.supplier_id !== undefined) {
    searchParams.set("supplier_id", String(filters.supplier_id));
  }
  if (filters.payment_method) {
    searchParams.set("payment_method", filters.payment_method);
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<OperatingExpense[]>(
    `/operating-expenses${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getOperatingExpense(
  token: string,
  expenseId: number,
): Promise<OperatingExpense> {
  return request<OperatingExpense>(`/operating-expenses/${expenseId}`, {
    headers: authHeaders(token),
  });
}

export async function createOperatingExpense(
  token: string,
  payload: OperatingExpensePayload,
): Promise<OperatingExpense> {
  return request<OperatingExpense>("/operating-expenses", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateOperatingExpense(
  token: string,
  expenseId: number,
  payload: OperatingExpenseUpdatePayload,
): Promise<OperatingExpense> {
  return request<OperatingExpense>(`/operating-expenses/${expenseId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function voidOperatingExpense(
  token: string,
  expenseId: number,
  reason: string,
): Promise<OperatingExpense> {
  return request<OperatingExpense>(
    `/operating-expenses/${expenseId}/void`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ reason }),
    },
  );
}

export async function listRecurringOperatingExpenses(
  token: string,
  filters: RecurringOperatingExpenseFilters = {},
): Promise<RecurringOperatingExpense[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.category_id !== undefined) {
    searchParams.set("category_id", String(filters.category_id));
  }
  if (filters.supplier_id !== undefined) {
    searchParams.set("supplier_id", String(filters.supplier_id));
  }
  if (filters.frequency) {
    searchParams.set("frequency", filters.frequency);
  }
  const query = searchParams.toString();
  return request<RecurringOperatingExpense[]>(
    `/operating-expenses/recurring${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getRecurringOperatingExpense(
  token: string,
  templateId: number,
): Promise<RecurringOperatingExpense> {
  return request<RecurringOperatingExpense>(
    `/operating-expenses/recurring/${templateId}`,
    { headers: authHeaders(token) },
  );
}

export async function createRecurringOperatingExpense(
  token: string,
  payload: RecurringOperatingExpensePayload,
): Promise<RecurringOperatingExpense> {
  return request<RecurringOperatingExpense>(
    "/operating-expenses/recurring",
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function updateRecurringOperatingExpense(
  token: string,
  templateId: number,
  payload: RecurringOperatingExpenseUpdatePayload,
): Promise<RecurringOperatingExpense> {
  return request<RecurringOperatingExpense>(
    `/operating-expenses/recurring/${templateId}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function setRecurringOperatingExpenseActive(
  token: string,
  templateId: number,
  isActive: boolean,
): Promise<RecurringOperatingExpense> {
  return request<RecurringOperatingExpense>(
    `/operating-expenses/recurring/${templateId}/${
      isActive ? "activate" : "deactivate"
    }`,
    { method: "PATCH", headers: authHeaders(token) },
  );
}

export async function createExpenseFromRecurringOperatingExpense(
  token: string,
  templateId: number,
  payload: RecurringOperatingExpenseCreateExpensePayload,
): Promise<OperatingExpense> {
  return request<OperatingExpense>(
    `/operating-expenses/recurring/${templateId}/create-expense`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function getOperatingExpenseSummary(
  token: string,
  filters: OperatingExpenseSummaryFilters = {},
): Promise<OperatingExpenseSummary> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  if (filters.category_id !== undefined) {
    searchParams.set("category_id", String(filters.category_id));
  }
  if (filters.supplier_id !== undefined) {
    searchParams.set("supplier_id", String(filters.supplier_id));
  }
  const query = searchParams.toString();
  return request<OperatingExpenseSummary>(
    `/operating-expenses/summary${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function listCashSales(
  token: string,
  filters: CashSaleFilters = {},
): Promise<CashSale[]> {
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
  if (filters.customer_id !== undefined) {
    searchParams.set("customer_id", String(filters.customer_id));
  }
  if (filters.payment_method) {
    searchParams.set("payment_method", filters.payment_method);
  }
  if (filters.sale_type) {
    searchParams.set("sale_type", filters.sale_type);
  }
  if (filters.route_load_id !== undefined) {
    searchParams.set("route_load_id", String(filters.route_load_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }

  const query = searchParams.toString();
  return request<CashSale[]>(`/sales${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getCashSale(
  token: string,
  saleId: number,
): Promise<CashSale> {
  return request<CashSale>(`/sales/${saleId}`, {
    headers: authHeaders(token),
  });
}

export async function createCashSale(
  token: string,
  payload: CashSalePayload,
): Promise<CashSale> {
  return request<CashSale>("/sales/cash", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function createCreditSale(
  token: string,
  payload: CreditSalePayload,
): Promise<CashSale> {
  return request<CashSale>("/sales/credit", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listPriceLists(
  token: string,
  filters: PriceListFilters = {},
): Promise<PriceList[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.list_type) {
    searchParams.set("list_type", filters.list_type);
  }
  if (filters.customer_id !== undefined) {
    searchParams.set("customer_id", String(filters.customer_id));
  }
  if (filters.route_id !== undefined) {
    searchParams.set("route_id", String(filters.route_id));
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  const query = searchParams.toString();
  return request<PriceList[]>(
    `/pricing/price-lists${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getPriceList(
  token: string,
  priceListId: number,
): Promise<PriceList> {
  return request<PriceList>(`/pricing/price-lists/${priceListId}`, {
    headers: authHeaders(token),
  });
}

export async function createPriceList(
  token: string,
  payload: PriceListPayload,
): Promise<PriceList> {
  return request<PriceList>("/pricing/price-lists", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updatePriceList(
  token: string,
  priceListId: number,
  payload: PriceListUpdatePayload,
): Promise<PriceList> {
  return request<PriceList>(`/pricing/price-lists/${priceListId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function setPriceListActive(
  token: string,
  priceListId: number,
  isActive: boolean,
): Promise<PriceList> {
  return request<PriceList>(
    `/pricing/price-lists/${priceListId}/${isActive ? "activate" : "deactivate"}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
    },
  );
}

export async function createPriceListItem(
  token: string,
  priceListId: number,
  payload: PriceListItemPayload,
): Promise<PriceListItem> {
  return request<PriceListItem>(
    `/pricing/price-lists/${priceListId}/items`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function updatePriceListItem(
  token: string,
  itemId: number,
  payload: PriceListItemUpdatePayload,
): Promise<PriceListItem> {
  return request<PriceListItem>(`/pricing/price-list-items/${itemId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function setPriceListItemActive(
  token: string,
  itemId: number,
  isActive: boolean,
): Promise<PriceListItem> {
  return request<PriceListItem>(
    `/pricing/price-list-items/${itemId}/${isActive ? "activate" : "deactivate"}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
    },
  );
}

export async function resolveProductPrice(
  token: string,
  params: PriceResolutionParams,
): Promise<PriceResolution> {
  const searchParams = new URLSearchParams();
  searchParams.set("product_id", String(params.product_id));
  if (params.customer_id !== undefined) {
    searchParams.set("customer_id", String(params.customer_id));
  }
  if (params.route_id !== undefined) {
    searchParams.set("route_id", String(params.route_id));
  }
  if (params.route_load_id !== undefined) {
    searchParams.set("route_load_id", String(params.route_load_id));
  }
  if (params.quantity) {
    searchParams.set("quantity", params.quantity);
  }
  if (params.price_date) {
    searchParams.set("price_date", params.price_date);
  }
  return request<PriceResolution>(
    `/pricing/resolve?${searchParams.toString()}`,
    { headers: authHeaders(token) },
  );
}

export async function getCustomerCreditBalance(
  token: string,
  customerId: number,
): Promise<CustomerCreditBalance> {
  return request<CustomerCreditBalance>(
    `/sales/credit/customer/${customerId}/balance`,
    { headers: authHeaders(token) },
  );
}

export async function voidCashSale(
  token: string,
  saleId: number,
  reason: string,
): Promise<CashSale> {
  return request<CashSale>(`/sales/${saleId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function correctSaleDate(
  token: string,
  saleId: number,
  payload: SaleDateCorrectionPayload,
): Promise<SaleDateCorrectionResponse> {
  return request<SaleDateCorrectionResponse>(`/sales/${saleId}/date`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function createCreditPayment(
  token: string,
  saleId: number,
  payload: CreditPaymentPayload,
): Promise<CreditPayment> {
  return request<CreditPayment>(`/sales/${saleId}/payments`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listSaleCreditPayments(
  token: string,
  saleId: number,
): Promise<CreditPayment[]> {
  return request<CreditPayment[]>(`/sales/${saleId}/payments`, {
    headers: authHeaders(token),
  });
}

export async function listCreditPayments(
  token: string,
  filters: CreditPaymentFilters = {},
): Promise<CreditPayment[]> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  if (filters.customer_id !== undefined) {
    searchParams.set("customer_id", String(filters.customer_id));
  }
  if (filters.sale_id !== undefined) {
    searchParams.set("sale_id", String(filters.sale_id));
  }
  if (filters.route_load_id !== undefined) {
    searchParams.set("route_load_id", String(filters.route_load_id));
  }
  if (filters.status) {
    searchParams.set("status", filters.status);
  }
  if (filters.payment_method) {
    searchParams.set("payment_method", filters.payment_method);
  }

  const query = searchParams.toString();
  return request<CreditPayment[]>(
    `/credit-payments${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function voidCreditPayment(
  token: string,
  paymentId: number,
  reason: string,
): Promise<CreditPayment> {
  return request<CreditPayment>(`/credit-payments/${paymentId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function getReceivablesSummary(
  token: string,
  filters: ReceivablesSummaryFilters = {},
): Promise<ReceivablesSummary> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  const query = searchParams.toString();
  return request<ReceivablesSummary>(
    `/receivables/summary${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function listReceivableCustomers(
  token: string,
  filters: ReceivableCustomerFilters = {},
): Promise<ReceivableCustomer[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.only_with_balance !== undefined) {
    searchParams.set(
      "only_with_balance",
      String(filters.only_with_balance),
    );
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  const query = searchParams.toString();
  return request<ReceivableCustomer[]>(
    `/receivables/customers${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getCustomerStatement(
  token: string,
  customerId: number,
  filters: CustomerStatementFilters = {},
): Promise<CustomerStatement> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  if (filters.include_paid !== undefined) {
    searchParams.set("include_paid", String(filters.include_paid));
  }
  const query = searchParams.toString();
  return request<CustomerStatement>(
    `/receivables/customers/${customerId}/statement${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function listOverdueReceivables(
  token: string,
): Promise<OverdueReceivable[]> {
  return request<OverdueReceivable[]>("/receivables/overdue", {
    headers: authHeaders(token),
  });
}

export async function listInventoryLocations(
  token: string,
  filters: InventoryLocationFilters = {},
): Promise<InventoryLocation[]> {
  const searchParams = new URLSearchParams();
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  if (filters.is_active !== undefined && filters.is_active !== "") {
    searchParams.set("is_active", String(filters.is_active));
  }
  if (filters.location_type) {
    searchParams.set("location_type", filters.location_type);
  }
  const query = searchParams.toString();
  return request<InventoryLocation[]>(
    `/inventory/locations${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function createInventoryLocation(
  token: string,
  payload: InventoryLocationPayload,
): Promise<InventoryLocation> {
  return request<InventoryLocation>("/inventory/locations", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateInventoryLocation(
  token: string,
  locationId: number,
  payload: InventoryLocationUpdatePayload,
): Promise<InventoryLocation> {
  return request<InventoryLocation>(`/inventory/locations/${locationId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function deactivateInventoryLocation(
  token: string,
  locationId: number,
): Promise<InventoryLocation> {
  return request<InventoryLocation>(
    `/inventory/locations/${locationId}/deactivate`,
    { method: "PATCH", headers: authHeaders(token) },
  );
}

export async function activateInventoryLocation(
  token: string,
  locationId: number,
): Promise<InventoryLocation> {
  return request<InventoryLocation>(
    `/inventory/locations/${locationId}/activate`,
    { method: "PATCH", headers: authHeaders(token) },
  );
}

export async function listInventoryStocks(
  token: string,
  filters: InventoryStockFilters = {},
): Promise<InventoryStock[]> {
  const searchParams = new URLSearchParams();
  if (filters.product_id !== undefined) {
    searchParams.set("product_id", String(filters.product_id));
  }
  if (filters.location_id !== undefined) {
    searchParams.set("location_id", String(filters.location_id));
  }
  if (filters.only_positive !== undefined) {
    searchParams.set("only_positive", String(filters.only_positive));
  }
  const query = searchParams.toString();
  return request<InventoryStock[]>(
    `/inventory/stocks${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function createInventoryMovement(
  token: string,
  payload: InventoryMovementPayload,
): Promise<InventoryMovement> {
  return request<InventoryMovement>("/inventory/movements", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listInventoryMovements(
  token: string,
  filters: InventoryMovementFilters = {},
): Promise<InventoryMovement[]> {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  if (filters.product_id !== undefined) {
    searchParams.set("product_id", String(filters.product_id));
  }
  if (filters.location_id !== undefined) {
    searchParams.set("location_id", String(filters.location_id));
  }
  if (filters.movement_type) {
    searchParams.set("movement_type", filters.movement_type);
  }
  if (filters.status) {
    searchParams.set("status", filters.status);
  }
  const query = searchParams.toString();
  return request<InventoryMovement[]>(
    `/inventory/movements${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function voidInventoryMovement(
  token: string,
  movementId: number,
  reason: string,
): Promise<InventoryMovement> {
  return request<InventoryMovement>(
    `/inventory/movements/${movementId}/void`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ reason }),
    },
  );
}

export async function createProductionBatch(
  token: string,
  payload: ProductionBatchPayload,
): Promise<ProductionBatch> {
  return request<ProductionBatch>("/production/batches", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listProductionBatches(
  token: string,
  filters: ProductionBatchFilters = {},
): Promise<ProductionBatch[]> {
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
  if (filters.product_id !== undefined) {
    searchParams.set("product_id", String(filters.product_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<ProductionBatch[]>(
    `/production/batches${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getProductionBatch(
  token: string,
  batchId: number,
): Promise<ProductionBatch> {
  return request<ProductionBatch>(`/production/batches/${batchId}`, {
    headers: authHeaders(token),
  });
}

export async function voidProductionBatch(
  token: string,
  batchId: number,
  reason: string,
): Promise<ProductionBatch> {
  return request<ProductionBatch>(`/production/batches/${batchId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function applyProductionToInventory(
  token: string,
  batchId: number,
  payload: ProductionInventoryApplyPayload,
): Promise<ProductionInventoryApplication> {
  return request<ProductionInventoryApplication>(
    `/production/batches/${batchId}/apply-inventory`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function getProductionInventoryApplication(
  token: string,
  batchId: number,
): Promise<ProductionInventoryApplication> {
  return request<ProductionInventoryApplication>(
    `/production/batches/${batchId}/inventory-application`,
    { headers: authHeaders(token) },
  );
}

export async function voidProductionInventoryApplication(
  token: string,
  applicationId: number,
  reason: string,
): Promise<ProductionInventoryApplication> {
  return request<ProductionInventoryApplication>(
    `/production/inventory-applications/${applicationId}/void`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ reason }),
    },
  );
}

export async function previewProductionMaterialConsumption(
  token: string,
  batchId: number,
  payload: ProductionMaterialConsumptionPreviewPayload,
): Promise<ProductionMaterialConsumptionPreview> {
  return request<ProductionMaterialConsumptionPreview>(
    `/production/batches/${batchId}/material-consumption/preview`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function createProductionMaterialConsumption(
  token: string,
  batchId: number,
  payload: ProductionMaterialConsumptionPayload,
): Promise<ProductionMaterialConsumption> {
  return request<ProductionMaterialConsumption>(
    `/production/batches/${batchId}/material-consumption`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function getProductionMaterialConsumptionForBatch(
  token: string,
  batchId: number,
): Promise<ProductionBatchMaterialConsumption> {
  return request<ProductionBatchMaterialConsumption>(
    `/production/batches/${batchId}/material-consumption`,
    { headers: authHeaders(token) },
  );
}

export async function listProductionMaterialConsumptions(
  token: string,
  filters: ProductionMaterialConsumptionFilters = {},
): Promise<ProductionMaterialConsumption[]> {
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
  if (filters.production_batch_id !== undefined) {
    searchParams.set(
      "production_batch_id",
      String(filters.production_batch_id),
    );
  }
  if (filters.source_location_id !== undefined) {
    searchParams.set(
      "source_location_id",
      String(filters.source_location_id),
    );
  }
  if (filters.input_product_id !== undefined) {
    searchParams.set("input_product_id", String(filters.input_product_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<ProductionMaterialConsumption[]>(
    `/production/material-consumptions${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getProductionMaterialConsumption(
  token: string,
  consumptionId: number,
): Promise<ProductionMaterialConsumption> {
  return request<ProductionMaterialConsumption>(
    `/production/material-consumptions/${consumptionId}`,
    { headers: authHeaders(token) },
  );
}

export async function voidProductionMaterialConsumption(
  token: string,
  consumptionId: number,
  reason: string,
): Promise<ProductionMaterialConsumption> {
  return request<ProductionMaterialConsumption>(
    `/production/material-consumptions/${consumptionId}/void`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ reason }),
    },
  );
}

export async function createRouteLoad(
  token: string,
  payload: RouteLoadPayload,
): Promise<RouteLoad> {
  return request<RouteLoad>("/route-loads", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listRouteLoads(
  token: string,
  filters: RouteLoadFilters = {},
): Promise<RouteLoad[]> {
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
  if (filters.route_id !== undefined) {
    searchParams.set("route_id", String(filters.route_id));
  }
  if (filters.vehicle_id !== undefined) {
    searchParams.set("vehicle_id", String(filters.vehicle_id));
  }
  if (filters.product_id !== undefined) {
    searchParams.set("product_id", String(filters.product_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<RouteLoad[]>(`/route-loads${query ? `?${query}` : ""}`, {
    headers: authHeaders(token),
  });
}

export async function getRouteLoad(
  token: string,
  loadId: number,
): Promise<RouteLoad> {
  return request<RouteLoad>(`/route-loads/${loadId}`, {
    headers: authHeaders(token),
  });
}

export async function getRouteCommercialActivity(
  token: string,
  loadId: number,
): Promise<RouteCommercialActivity> {
  return request<RouteCommercialActivity>(
    `/route-loads/${loadId}/commercial-activity`,
    { headers: authHeaders(token) },
  );
}

export async function getRouteLoadFinancialClosure(
  token: string,
  loadId: number,
): Promise<RouteLoadFinancialClosure> {
  return request<RouteLoadFinancialClosure>(
    `/route-loads/${loadId}/financial-closure`,
    { headers: authHeaders(token) },
  );
}

export async function getRouteSettlementSummary(
  token: string,
  loadId: number,
): Promise<RouteSettlement> {
  return request<RouteSettlement>(
    `/route-loads/${loadId}/settlement-summary`,
    { headers: authHeaders(token) },
  );
}

export async function createRouteClosure(
  token: string,
  payload: RouteClosurePayload,
): Promise<RouteClosure> {
  return request<RouteClosure>("/route-closures", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listRouteClosures(
  token: string,
  filters: RouteClosureFilters = {},
): Promise<RouteClosure[]> {
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
  if (filters.route_id !== undefined) {
    searchParams.set("route_id", String(filters.route_id));
  }
  if (filters.vehicle_id !== undefined) {
    searchParams.set("vehicle_id", String(filters.vehicle_id));
  }
  if (filters.route_load_id !== undefined) {
    searchParams.set("route_load_id", String(filters.route_load_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<RouteClosure[]>(
    `/route-closures${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getRouteClosure(
  token: string,
  closureId: number,
): Promise<RouteClosure> {
  return request<RouteClosure>(`/route-closures/${closureId}`, {
    headers: authHeaders(token),
  });
}

export async function voidRouteClosure(
  token: string,
  closureId: number,
  reason: string,
): Promise<RouteClosure> {
  return request<RouteClosure>(`/route-closures/${closureId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function createRouteCashReceipt(
  token: string,
  payload: RouteCashReceiptPayload,
): Promise<RouteCashReceipt> {
  return request<RouteCashReceipt>("/route-cash-receipts", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listRouteCashReceipts(
  token: string,
  filters: RouteCashReceiptFilters = {},
): Promise<RouteCashReceipt[]> {
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
  if (filters.route_id !== undefined) {
    searchParams.set("route_id", String(filters.route_id));
  }
  if (filters.vehicle_id !== undefined) {
    searchParams.set("vehicle_id", String(filters.vehicle_id));
  }
  if (filters.route_closure_id !== undefined) {
    searchParams.set("route_closure_id", String(filters.route_closure_id));
  }
  if (filters.cash_session_id !== undefined) {
    searchParams.set("cash_session_id", String(filters.cash_session_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<RouteCashReceipt[]>(
    `/route-cash-receipts${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getRouteCashReceipt(
  token: string,
  receiptId: number,
): Promise<RouteCashReceipt> {
  return request<RouteCashReceipt>(`/route-cash-receipts/${receiptId}`, {
    headers: authHeaders(token),
  });
}

export async function getRouteClosureCashReceipt(
  token: string,
  closureId: number,
): Promise<RouteClosureCashReceipt> {
  return request<RouteClosureCashReceipt>(
    `/route-closures/${closureId}/cash-receipt`,
    { headers: authHeaders(token) },
  );
}

export async function getCashSessionRouteCashReceipts(
  token: string,
  cashSessionId: number,
): Promise<CashSessionRouteCashReceipts> {
  return request<CashSessionRouteCashReceipts>(
    `/cash-sessions/${cashSessionId}/route-cash-receipts`,
    { headers: authHeaders(token) },
  );
}

export async function voidRouteCashReceipt(
  token: string,
  receiptId: number,
  reason: string,
): Promise<RouteCashReceipt> {
  return request<RouteCashReceipt>(`/route-cash-receipts/${receiptId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function voidRouteLoad(
  token: string,
  loadId: number,
  reason: string,
): Promise<RouteLoad> {
  return request<RouteLoad>(`/route-loads/${loadId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

export async function createRouteReturn(
  token: string,
  payload: RouteReturnPayload,
): Promise<RouteReturn> {
  return request<RouteReturn>("/route-returns", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function listRouteReturns(
  token: string,
  filters: RouteReturnFilters = {},
): Promise<RouteReturn[]> {
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
  if (filters.route_id !== undefined) {
    searchParams.set("route_id", String(filters.route_id));
  }
  if (filters.vehicle_id !== undefined) {
    searchParams.set("vehicle_id", String(filters.vehicle_id));
  }
  if (filters.route_load_id !== undefined) {
    searchParams.set("route_load_id", String(filters.route_load_id));
  }
  if (filters.product_id !== undefined) {
    searchParams.set("product_id", String(filters.product_id));
  }
  if (filters.search) {
    searchParams.set("search", filters.search);
  }
  const query = searchParams.toString();
  return request<RouteReturn[]>(
    `/route-returns${query ? `?${query}` : ""}`,
    { headers: authHeaders(token) },
  );
}

export async function getRouteReturn(
  token: string,
  returnId: number,
): Promise<RouteReturn> {
  return request<RouteReturn>(`/route-returns/${returnId}`, {
    headers: authHeaders(token),
  });
}

export async function voidRouteReturn(
  token: string,
  returnId: number,
  reason: string,
): Promise<RouteReturn> {
  return request<RouteReturn>(`/route-returns/${returnId}/void`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ reason }),
  });
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await apiFetch(path, {
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

  try {
    return (await response.json()) as T;
  } catch (error) {
    throw new ApiError(
      "El servidor devolvió una respuesta inválida.",
      response.status,
      error,
    );
  }
}

async function requestWithTimeout<T>(
  path: string,
  options: RequestInit,
  timeoutMs: number,
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await request<T>(path, {
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (controller.signal.aborted) {
      throw new ApiError(
        "La autenticación tardó demasiado en responder.",
        0,
        error,
      );
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function apiFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  try {
    return await fetch(buildApiUrl(path), options);
  } catch (error) {
    throw new ApiError(
      "No se pudo contactar al servidor. Verifica la conexión e inténtalo nuevamente; si continúa, usa el método manual y avisa a George.",
      0,
      error,
    );
  }
}

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
  };
}

function buildEmployeeControlQuery(
  filters: EmployeeLoanPaymentFilters,
): string {
  const searchParams = new URLSearchParams();
  if (filters.date_from) {
    searchParams.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    searchParams.set("date_to", filters.date_to);
  }
  if (filters.employee_id !== undefined) {
    searchParams.set("employee_id", String(filters.employee_id));
  }
  if (filters.loan_id !== undefined) {
    searchParams.set("loan_id", String(filters.loan_id));
  }
  if (filters.status) {
    searchParams.set("status", filters.status);
  }
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as {
      detail?: string | Array<{ msg?: string }>;
    };
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((item) => item.msg)
        .filter((message): message is string => Boolean(message));
      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  } catch {
    return getFallbackErrorMessage(response.status);
  }

  return getFallbackErrorMessage(response.status);
}

function getFallbackErrorMessage(status: number): string {
  if (status >= 500) {
    return "El servidor no pudo completar la solicitud. Inténtalo nuevamente y, si continúa, avisa a George.";
  }
  return "No se pudo completar la solicitud.";
}

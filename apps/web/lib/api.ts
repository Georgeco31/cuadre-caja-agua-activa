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
  Product,
  ProductFilters,
  ProductPayload,
  ProductUpdatePayload,
} from "@/types/product";
import type {
  ProductionBatch,
  ProductionBatchFilters,
  ProductionBatchPayload,
} from "@/types/production";
import type {
  CashSummaryReport,
  CashSummaryReportFilters,
} from "@/types/report";
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
} from "@/types/sale";
import type { CashSessionSummary } from "@/types/summary";
import type {
  Vehicle,
  VehicleFilters,
  VehiclePayload,
  VehicleUpdatePayload,
} from "@/types/vehicle";

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

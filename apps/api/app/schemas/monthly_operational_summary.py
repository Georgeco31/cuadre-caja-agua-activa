from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class MonthlyOperationalPeriod(BaseModel):
    year: int
    month: int
    date_from: date
    date_to: date
    days_in_month: int


class MonthlyCashSummary(BaseModel):
    cash_sessions_count: int
    open_cash_sessions_count: int
    closed_cash_sessions_count: int
    total_coins: Decimal
    total_bills: Decimal
    total_counted: Decimal
    total_expenses: Decimal
    total_final: Decimal
    average_daily_counted: Decimal
    days_with_cash_session: int
    days_without_cash_session: int


class MonthlyProductionProduct(BaseModel):
    product_id: int
    product_name_snapshot: str
    quantity_produced: Decimal
    quantity_waste: Decimal
    quantity_net: Decimal


class MonthlyProductionSummary(BaseModel):
    production_batches_count: int
    active_production_batches_count: int
    voided_production_batches_count: int
    total_quantity_produced: Decimal
    total_quantity_waste: Decimal
    total_quantity_net: Decimal
    products: list[MonthlyProductionProduct]


class MonthlyProductSold(BaseModel):
    product_id: int
    product_name_snapshot: str
    quantity: Decimal
    amount: Decimal


class MonthlySalesSummary(BaseModel):
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    total_sales_amount: Decimal
    cash_sales_count: int
    credit_sales_count: int
    voided_sales_count: int
    products_sold: list[MonthlyProductSold]


class MonthlyReceivablesSummary(BaseModel):
    payments_total: Decimal
    payments_count: int
    voided_payments_count: int
    credit_sales_created_total: Decimal
    pending_credit_total: Decimal
    customers_with_credit_sales_count: int


class MonthlyRouteOperationsSummary(BaseModel):
    route_loads_count: int
    active_route_loads_count: int
    voided_route_loads_count: int
    route_returns_count: int
    active_route_returns_count: int
    voided_route_returns_count: int
    total_quantity_loaded: Decimal
    total_quantity_returned: Decimal


class MonthlyRouteFinancialSummary(BaseModel):
    route_closures_count: int
    active_route_closures_count: int
    voided_route_closures_count: int
    expected_cash_total: Decimal
    delivered_cash_total: Decimal
    difference_total: Decimal
    closures_with_shortage_count: int
    closures_with_surplus_count: int
    closures_balanced_count: int


class MonthlyRouteCashReceiptsSummary(BaseModel):
    receipts_count: int
    active_receipts_count: int
    voided_receipts_count: int
    delivered_cash_total: Decimal
    received_amount_total: Decimal
    difference_total: Decimal


class MonthlyOperationalDailyRow(BaseModel):
    date: date
    cash_session_exists: bool
    cash_total_counted: Decimal
    cash_total_expenses: Decimal
    cash_total_final: Decimal
    production_quantity_net: Decimal
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    payments_total: Decimal
    route_delivered_cash_total: Decimal
    route_cash_registered_total: Decimal
    alerts_count: int
    alert_codes: list[str]


class MonthlyOperationalAlertByCode(BaseModel):
    code: str
    count: int
    message: str


class MonthlyOperationalAlertsSummary(BaseModel):
    total_alerts: int
    days_with_alerts_count: int
    alerts_by_code: list[MonthlyOperationalAlertByCode]


class MonthlyOperationalTotals(BaseModel):
    total_business_cash_inflow_reference: Decimal


class MonthlyOperationalSummary(BaseModel):
    period: MonthlyOperationalPeriod
    cash_summary: MonthlyCashSummary
    production_summary: MonthlyProductionSummary
    sales_summary: MonthlySalesSummary
    receivables_summary: MonthlyReceivablesSummary
    route_operations_summary: MonthlyRouteOperationsSummary
    route_financial_summary: MonthlyRouteFinancialSummary
    route_cash_receipts_summary: MonthlyRouteCashReceiptsSummary
    daily_rows: list[MonthlyOperationalDailyRow]
    alerts_summary: MonthlyOperationalAlertsSummary
    totals: MonthlyOperationalTotals

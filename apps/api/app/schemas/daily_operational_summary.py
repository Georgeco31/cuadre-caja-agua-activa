from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class DailyCashSummary(BaseModel):
    cash_session_exists: bool
    cash_session_id: int | None
    cash_session_status: str | None
    total_coins: Decimal
    total_bills: Decimal
    total_counted: Decimal
    total_expenses: Decimal
    total_final: Decimal
    pre_count_expenses_total: Decimal
    post_count_expenses_total: Decimal
    expenses_count: int
    route_cash_receipts_total: Decimal
    route_cash_receipts_count: int


class DailyProductionProduct(BaseModel):
    product_id: int
    product_name_snapshot: str
    quantity_produced: Decimal
    quantity_waste: Decimal
    quantity_net: Decimal


class DailyProductionSummary(BaseModel):
    production_batches_count: int
    active_production_batches_count: int
    voided_production_batches_count: int
    total_quantity_produced: Decimal
    total_quantity_waste: Decimal
    total_quantity_net: Decimal
    products: list[DailyProductionProduct]


class DailyRouteLoad(BaseModel):
    id: int
    load_number: str
    route_name: str
    vehicle_name: str
    status: str
    total_quantity_loaded: Decimal


class DailyRouteLoadsSummary(BaseModel):
    route_loads_count: int
    active_route_loads_count: int
    voided_route_loads_count: int
    total_items_loaded: int
    total_quantity_loaded: Decimal
    loads: list[DailyRouteLoad]


class DailyRouteReturn(BaseModel):
    id: int
    return_number: str
    route_name: str
    vehicle_name: str
    status: str
    total_quantity_returned: Decimal


class DailyRouteReturnsSummary(BaseModel):
    route_returns_count: int
    active_route_returns_count: int
    voided_route_returns_count: int
    total_quantity_returned: Decimal
    returns: list[DailyRouteReturn]


class DailyRouteClosure(BaseModel):
    id: int
    closure_number: str
    route_name_snapshot: str
    vehicle_name_snapshot: str
    expected_cash_total: Decimal
    delivered_cash_total: Decimal
    difference_amount: Decimal
    status: str


class DailyRouteClosuresSummary(BaseModel):
    route_closures_count: int
    active_route_closures_count: int
    voided_route_closures_count: int
    expected_cash_total: Decimal
    delivered_cash_total: Decimal
    difference_total: Decimal
    closures_with_shortage_count: int
    closures_with_surplus_count: int
    closures_balanced_count: int
    closures: list[DailyRouteClosure]


class DailyRouteCashReceipt(BaseModel):
    id: int
    receipt_number: str
    closure_number_snapshot: str
    route_name_snapshot: str
    vehicle_name_snapshot: str
    delivered_cash_total: Decimal
    received_amount: Decimal
    difference_amount: Decimal
    status: str


class DailyRouteCashReceiptsSummary(BaseModel):
    receipts_count: int
    active_receipts_count: int
    voided_receipts_count: int
    delivered_cash_total: Decimal
    received_amount_total: Decimal
    difference_total: Decimal
    receipts: list[DailyRouteCashReceipt]


class DailyProductSold(BaseModel):
    product_id: int
    product_name_snapshot: str
    quantity: Decimal
    amount: Decimal


class DailySalesSummary(BaseModel):
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    total_sales_amount: Decimal
    cash_sales_count: int
    credit_sales_count: int
    voided_sales_count: int
    products_sold: list[DailyProductSold]


class DailyReceivablesSummary(BaseModel):
    payments_total: Decimal
    payments_count: int
    voided_payments_count: int
    credit_sales_created_total: Decimal
    outstanding_balance_created_today: Decimal
    customers_with_credit_sales_count: int


class DailyOperationalAlert(BaseModel):
    type: Literal["warning", "info", "success"]
    code: str
    message: str


class DailyOperationalTotals(BaseModel):
    total_business_cash_inflow_reference: Decimal
    total_route_delivered_cash: Decimal
    total_route_cash_registered: Decimal
    total_cash_counted: Decimal
    total_cash_final: Decimal


class DailyOperationalSummary(BaseModel):
    date: date
    cash_summary: DailyCashSummary
    production_summary: DailyProductionSummary
    route_loads_summary: DailyRouteLoadsSummary
    route_returns_summary: DailyRouteReturnsSummary
    route_closures_summary: DailyRouteClosuresSummary
    route_cash_receipts_summary: DailyRouteCashReceiptsSummary
    sales_summary: DailySalesSummary
    receivables_summary: DailyReceivablesSummary
    alerts: list[DailyOperationalAlert]
    totals: DailyOperationalTotals

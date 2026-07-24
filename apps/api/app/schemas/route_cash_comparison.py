from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

RouteCashComparisonStatus = Literal[
    "no_cash_session",
    "no_route_closures",
    "matched",
    "cash_higher_than_routes",
    "routes_higher_than_cash",
]


class RouteCashComparisonClosure(BaseModel):
    id: int
    closure_number: str
    route_name_snapshot: str
    vehicle_name_snapshot: str
    expected_cash_total: Decimal
    delivered_cash_total: Decimal
    difference_amount: Decimal


class RouteCashComparisonTotals(BaseModel):
    route_closures_count: int
    route_expected_cash_total: Decimal
    route_delivered_cash_total: Decimal
    route_difference_total: Decimal
    cash_total_counted: Decimal
    cash_total_expenses: Decimal
    cash_total_final: Decimal
    cash_vs_route_delivered_difference: Decimal


class RouteCashComparisonRow(BaseModel):
    date: date
    route_closures_count: int
    route_expected_cash_total: Decimal
    route_delivered_cash_total: Decimal
    route_difference_total: Decimal
    cash_session_exists: bool
    has_cash_session: bool
    has_route_closures: bool
    cash_session_id: int | None
    cash_session_status: str | None
    cash_total_coins: Decimal
    cash_total_bills: Decimal
    cash_total_counted: Decimal
    cash_total_expenses: Decimal
    cash_total_final: Decimal
    cash_vs_route_delivered_difference: Decimal
    comparison_status: RouteCashComparisonStatus
    route_closures: list[RouteCashComparisonClosure]


class RouteCashComparisonReport(BaseModel):
    date_from: date
    date_to: date
    totals: RouteCashComparisonTotals
    rows: list[RouteCashComparisonRow]

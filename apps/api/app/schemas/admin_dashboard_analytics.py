from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class AdminBestSalesDay(BaseModel):
    date: date
    amount: Decimal


class AdminTopCustomer(BaseModel):
    customer_id: int
    customer_name: str
    sales_count: int
    total_amount: Decimal


class AdminDailySalesPoint(BaseModel):
    date: date
    cash_sales_amount: Decimal
    credit_sales_amount: Decimal
    total_sales_amount: Decimal


class AdminSalesMixPoint(BaseModel):
    sale_type: Literal["cash", "credit"]
    amount: Decimal
    percentage: Decimal


class AdminSimpleRouteDailySalesPoint(BaseModel):
    date: date
    amount: Decimal


class AdminSimpleRouteRanking(BaseModel):
    label: str
    amount: Decimal
    count: int


class AdminDashboardAnalytics(BaseModel):
    period_start: date
    period_end: date
    official_sales_amount: Decimal
    official_cash_sales_amount: Decimal
    official_credit_sales_amount: Decimal
    simple_route_sales_amount: Decimal
    total_sales_with_routes_amount: Decimal
    official_credit_collections_amount: Decimal
    official_credit_pending_amount: Decimal
    simple_route_cash_sales_amount: Decimal
    simple_route_credit_sales_amount: Decimal
    simple_route_partial_sales_amount: Decimal
    simple_route_paid_amount: Decimal
    simple_route_pending_amount: Decimal
    simple_route_collections_amount: Decimal
    simple_route_expenses_amount: Decimal
    simple_route_expected_cash_amount: Decimal
    simple_route_cash_delivered_amount: Decimal
    simple_route_cash_difference_amount: Decimal
    simple_route_best_day: AdminBestSalesDay | None
    simple_route_daily_sales: list[AdminSimpleRouteDailySalesPoint]
    simple_route_top_routes: list[AdminSimpleRouteRanking]
    simple_route_top_sellers: list[AdminSimpleRouteRanking]
    simple_route_sheets_count: int
    simple_route_sheets_with_difference: int

    # Campos 62A conservados para clientes existentes. Todos representan solo
    # el dominio oficial y nunca incluyen Rutas Simples.
    total_sales_amount: Decimal
    cash_sales_amount: Decimal
    credit_sales_amount: Decimal
    collections_amount: Decimal
    pending_credit_amount: Decimal
    expenses_amount: Decimal
    net_amount: Decimal | None
    net_amount_note: str
    best_sales_day: AdminBestSalesDay | None
    average_daily_sales: Decimal
    customers_served_count: int
    top_customers: list[AdminTopCustomer]
    daily_sales: list[AdminDailySalesPoint]
    sales_mix: list[AdminSalesMixPoint]

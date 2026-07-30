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


class AdminDashboardAnalytics(BaseModel):
    period_start: date
    period_end: date
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

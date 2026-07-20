from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.credit_payment import CreditPaymentRead
from app.schemas.sale import SaleRead


class RouteActivityProductRead(BaseModel):
    product_id: int
    product_name_snapshot: str
    total_quantity: Decimal
    total_amount: Decimal


class RouteCommercialActivityRead(BaseModel):
    load_id: int
    load_number: str
    load_date: date
    route_id: int
    route_name: str
    vehicle_id: int
    vehicle_name: str
    status: Literal["active", "voided"]
    cash_sales: list[SaleRead]
    credit_sales: list[SaleRead]
    payments: list[CreditPaymentRead]
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    payments_total: Decimal
    expected_cash_total: Decimal
    products_sold: list[RouteActivityProductRead]

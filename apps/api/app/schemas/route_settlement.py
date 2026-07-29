from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

RouteLoadStatus = Literal["active", "voided"]
RouteSettlementStatus = Literal["pending", "balanced", "with_difference"]


class RouteSettlementItemRead(BaseModel):
    product_id: int
    product_name_snapshot: str
    product_presentation_snapshot: str | None
    loaded_quantity: Decimal
    returned_quantity: Decimal | None
    physical_sold_quantity: Decimal | None
    registered_sold_quantity: Decimal
    physical_vs_registered_difference: Decimal | None


class RouteSettlementRead(BaseModel):
    route_load_id: int
    load_number: str
    load_date: date
    route_load_status: RouteLoadStatus
    route_id: int
    route_name: str
    vehicle_id: int
    vehicle_name: str
    responsible_name: str | None
    route_return_id: int | None
    return_number: str | None
    return_date: date | None
    route_closure_id: int | None
    closure_number: str | None
    closure_date: date | None
    total_loaded_quantity: Decimal
    total_returned_quantity: Decimal | None
    physical_sold_quantity: Decimal | None
    registered_sold_quantity: Decimal
    physical_vs_registered_difference: Decimal | None
    cash_sales_amount: Decimal
    credit_sales_amount: Decimal
    registered_sales_amount: Decimal
    registered_payments_amount: Decimal
    expected_cash_amount: Decimal
    delivered_cash_amount: Decimal | None
    cash_difference: Decimal | None
    status: RouteSettlementStatus
    return_observation: str | None
    settlement_observation: str | None
    difference_reason: str | None
    messages: list[str]
    items: list[RouteSettlementItemRead]

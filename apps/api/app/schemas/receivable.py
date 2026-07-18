from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

CreditStatus = Literal["pending", "paid"]
PaymentMethod = Literal["cash", "transfer", "card", "other"]
PaymentStatus = Literal["active", "voided"]


class ReceivablesSummary(BaseModel):
    total_customers_with_balance: int
    total_credit_sales: Decimal
    total_paid: Decimal
    total_balance: Decimal


class ReceivableCustomerRead(BaseModel):
    customer_id: int
    customer_name: str
    primary_phone: str | None
    sector: str | None
    is_active: bool
    total_credit_sales: Decimal
    total_paid: Decimal
    total_balance: Decimal
    pending_sales_count: int


class ReceivableSaleRead(BaseModel):
    sale_id: int
    sale_number: str
    sale_date: date
    due_date: date | None
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    credit_status: CreditStatus
    status: Literal["active"]


class ReceivablePaymentRead(BaseModel):
    payment_id: int
    sale_id: int
    sale_number: str
    payment_date: date
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    notes: str | None
    void_reason: str | None


class CustomerStatement(BaseModel):
    customer_id: int
    customer_name: str
    primary_phone: str | None
    sector: str | None
    is_active: bool
    total_credit_sales: Decimal
    total_paid: Decimal
    total_balance: Decimal
    credit_sales: list[ReceivableSaleRead]
    payments: list[ReceivablePaymentRead]


class OverdueReceivableRead(BaseModel):
    sale_id: int
    sale_number: str
    customer_id: int
    customer_name: str
    primary_phone: str | None
    sector: str | None
    sale_date: date
    due_date: date
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal

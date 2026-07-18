from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories import customers
from app.repositories import receivables as receivable_repository
from app.schemas.receivable import (
    CustomerStatement,
    OverdueReceivableRead,
    ReceivableCustomerRead,
    ReceivablePaymentRead,
    ReceivableSaleRead,
    ReceivablesSummary,
)


def get_receivables_summary(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
) -> ReceivablesSummary:
    _validate_date_range(date_from, date_to)
    return _build_summary(
        receivable_repository.get_receivables_summary(
            db,
            date_from=date_from,
            date_to=date_to,
        )
    )


def list_receivable_customers(
    db: Session,
    search: str | None = None,
    only_with_balance: bool = False,
    is_active: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[ReceivableCustomerRead]:
    _validate_date_range(date_from, date_to)
    rows = receivable_repository.list_receivable_customers(
        db=db,
        search=_normalize_filter(search),
        only_with_balance=only_with_balance,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
    )
    return [
        ReceivableCustomerRead(
            customer_id=row[0],
            customer_name=row[1],
            primary_phone=row[2],
            sector=row[3],
            is_active=row[4],
            total_credit_sales=Decimal(row[5]),
            total_paid=Decimal(row[6]),
            total_balance=Decimal(row[7]),
            pending_sales_count=int(row[8]),
        )
        for row in rows
    ]


def get_customer_statement(
    db: Session,
    customer_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    include_paid: bool = False,
) -> CustomerStatement:
    _validate_date_range(date_from, date_to)
    customer = customers.get_customer(db, customer_id)
    if customer is None:
        raise ValueError("El cliente no existe.")

    summary = _build_summary(
        receivable_repository.get_receivables_summary(
            db,
            date_from=date_from,
            date_to=date_to,
            customer_id=customer_id,
        )
    )
    sales = receivable_repository.list_customer_credit_sales(
        db=db,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
        include_paid=include_paid,
    )
    payment_rows = receivable_repository.list_customer_payments(
        db=db,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
    )
    return CustomerStatement(
        customer_id=customer.id,
        customer_name=customer.name,
        primary_phone=customer.primary_phone,
        sector=customer.sector,
        is_active=customer.is_active,
        total_credit_sales=summary.total_credit_sales,
        total_paid=summary.total_paid,
        total_balance=summary.total_balance,
        credit_sales=[
            ReceivableSaleRead(
                sale_id=sale.id,
                sale_number=sale.sale_number,
                sale_date=sale.sale_date,
                due_date=sale.due_date,
                total_amount=sale.total_amount,
                paid_amount=sale.paid_amount,
                balance_amount=sale.balance_amount,
                credit_status=sale.credit_status,
                status=sale.status,
            )
            for sale in sales
        ],
        payments=[
            ReceivablePaymentRead(
                payment_id=payment.id,
                sale_id=payment.sale_id,
                sale_number=sale_number,
                payment_date=payment.payment_date,
                amount=payment.amount,
                payment_method=payment.payment_method,
                status=payment.status,
                notes=payment.notes,
                void_reason=payment.void_reason,
            )
            for payment, sale_number in payment_rows
        ],
    )


def list_overdue_receivables(db: Session) -> list[OverdueReceivableRead]:
    return [
        OverdueReceivableRead(
            sale_id=sale.id,
            sale_number=sale.sale_number,
            customer_id=sale.customer_id,
            customer_name=customer_name,
            primary_phone=primary_phone,
            sector=sector,
            sale_date=sale.sale_date,
            due_date=sale.due_date,
            total_amount=sale.total_amount,
            paid_amount=sale.paid_amount,
            balance_amount=sale.balance_amount,
        )
        for sale, customer_name, primary_phone, sector in (
            receivable_repository.list_overdue_receivables(db, date.today())
        )
    ]


def _build_summary(
    values: tuple[int, Decimal, Decimal, Decimal],
) -> ReceivablesSummary:
    return ReceivablesSummary(
        total_customers_with_balance=values[0],
        total_credit_sales=values[1],
        total_paid=values[2],
        total_balance=values[3],
    )


def _validate_date_range(date_from: date | None, date_to: date | None) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.schemas.customer import CustomerSalesSummary
from app.services import customers as customer_service
from app.services import sales as sale_service

MONEY_ZERO = Decimal("0.00")
MONEY_QUANTUM = Decimal("0.01")


def get_customer_sales_summary(
    db: Session,
    *,
    customer_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    sale_type: str = "all",
    status: str | None = None,
) -> CustomerSalesSummary:
    resolved_start, resolved_end = _resolve_period(start_date, end_date)
    customer = customer_service.get_customer(db, customer_id)
    sales = list_customer_sales(
        db,
        customer_id=customer_id,
        start_date=resolved_start,
        end_date=resolved_end,
        sale_type=sale_type,
        status=status,
    )
    active_sales = [sale for sale in sales if sale.status == "active"]
    cash_sales = [sale for sale in active_sales if sale.sale_type == "cash"]
    credit_sales = [sale for sale in active_sales if sale.sale_type == "credit"]
    cancelled_sales = [sale for sale in sales if sale.status == "voided"]

    cash_total = _sum_money(sale.total_amount for sale in cash_sales)
    credit_total = _sum_money(sale.total_amount for sale in credit_sales)
    return CustomerSalesSummary(
        customer_id=customer.id,
        customer_name=customer.name,
        period_start=resolved_start,
        period_end=resolved_end,
        cash_sales_count=len(cash_sales),
        cash_sales_total=cash_total,
        credit_sales_count=len(credit_sales),
        credit_sales_total=credit_total,
        total_sales_count=len(active_sales),
        total_sales_amount=_money(cash_total + credit_total),
        total_collected_amount=_sum_money(
            sale.paid_amount for sale in credit_sales
        ),
        pending_credit_amount=_sum_money(
            sale.balance_amount for sale in credit_sales
        ),
        last_sale_date=max(
            (sale.sale_date for sale in active_sales),
            default=None,
        ),
        cancelled_sales_count=len(cancelled_sales),
        cancelled_sales_total=_sum_money(
            sale.total_amount for sale in cancelled_sales
        ),
    )


def list_customer_sales(
    db: Session,
    *,
    customer_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    sale_type: str = "all",
    status: str | None = None,
) -> list[Sale]:
    resolved_start, resolved_end = _resolve_period(start_date, end_date)
    customer_service.get_customer(db, customer_id)
    return sale_service.list_sales(
        db=db,
        date_from=resolved_start,
        date_to=resolved_end,
        customer_id=customer_id,
        sale_type=None if sale_type == "all" else sale_type,
        status=status,
    )


def _resolve_period(
    start_date: date | None,
    end_date: date | None,
) -> tuple[date | None, date | None]:
    if start_date is None and end_date is None:
        return None, None
    if start_date is None:
        start_date = end_date
    if end_date is None:
        end_date = start_date
    if start_date is None or end_date is None:
        raise ValueError("No se pudo resolver el rango de fechas.")
    if end_date < start_date:
        raise ValueError("La fecha hasta no puede ser menor que la fecha desde.")
    return start_date, end_date


def _sum_money(values) -> Decimal:
    return _money(sum(values, MONEY_ZERO))


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.repositories import customers, products
from app.repositories import sales as sale_repository
from app.schemas.sale import (
    CashSaleCreate,
    CreditSaleCreate,
    CustomerCreditBalance,
    SaleItemCreate,
)

MONEY_QUANTUM = Decimal("0.01")


def create_cash_sale(
    db: Session,
    payload: CashSaleCreate,
    created_by: int,
) -> Sale:
    customer_id = payload.customer_id
    customer_name_snapshot = "Consumidor final"
    if customer_id is not None:
        customer = customers.get_customer(db, customer_id)
        if customer is None:
            raise ValueError("El cliente no existe.")
        customer_name_snapshot = customer.name

    item_values, total_amount = _build_sale_items(db, payload.items)
    return _persist_sale(
        db,
        {
            "sale_number": f"PENDING-{uuid4().hex}",
            "sale_date": payload.sale_date,
            "customer_id": customer_id,
            "customer_name_snapshot": customer_name_snapshot,
            "sale_type": "cash",
            "payment_method": payload.payment_method,
            "status": "active",
            "total_amount": total_amount,
            "paid_amount": total_amount,
            "balance_amount": Decimal("0.00"),
            "credit_status": "none",
            "due_date": None,
            "notes": payload.notes,
            "created_by": created_by,
        },
        item_values,
    )


def create_credit_sale(
    db: Session,
    payload: CreditSaleCreate,
    created_by: int,
) -> Sale:
    customer = sale_repository.get_customer_for_credit(db, payload.customer_id)
    if customer is None:
        raise ValueError("El cliente no existe.")
    if not customer.is_active:
        raise ValueError("El cliente esta inactivo.")
    if not customer.credit_allowed:
        raise ValueError("El cliente no tiene credito permitido.")

    item_values, total_amount = _build_sale_items(db, payload.items)
    active_balance = sale_repository.get_active_credit_balance(db, customer.id)
    if (
        customer.credit_limit > 0
        and active_balance + total_amount > customer.credit_limit
    ):
        available_credit = max(
            customer.credit_limit - active_balance,
            Decimal("0.00"),
        )
        raise ValueError(
            "La venta supera el limite de credito del cliente. "
            f"Credito disponible: {available_credit.quantize(MONEY_QUANTUM)}."
        )

    return _persist_sale(
        db,
        {
            "sale_number": f"PENDING-{uuid4().hex}",
            "sale_date": payload.sale_date,
            "customer_id": customer.id,
            "customer_name_snapshot": customer.name,
            "sale_type": "credit",
            "payment_method": "other",
            "status": "active",
            "total_amount": total_amount,
            "paid_amount": Decimal("0.00"),
            "balance_amount": total_amount,
            "credit_status": "pending",
            "due_date": payload.due_date,
            "notes": payload.notes,
            "created_by": created_by,
        },
        item_values,
    )


def list_sales(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    customer_id: int | None = None,
    payment_method: str | None = None,
    sale_type: str | None = None,
    search: str | None = None,
) -> list[Sale]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return sale_repository.list_sales(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        customer_id=customer_id,
        payment_method=payment_method,
        sale_type=sale_type,
        search=_normalize_filter(search),
    )


def get_sale(db: Session, sale_id: int) -> Sale:
    sale = sale_repository.get_sale(db, sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    return sale


def void_sale(db: Session, sale_id: int, reason: str) -> Sale:
    sale = get_sale(db, sale_id)
    if sale.status == "voided":
        raise ValueError("La venta ya esta anulada.")

    sale_repository.mark_sale_voided(
        db,
        sale,
        reason,
        datetime.now(timezone.utc),
    )
    db.commit()
    voided_sale = sale_repository.get_sale(db, sale.id)
    if voided_sale is None:
        raise RuntimeError("La venta anulada no pudo recuperarse.")
    return voided_sale


def get_customer_credit_balance(
    db: Session,
    customer_id: int,
) -> CustomerCreditBalance:
    customer = customers.get_customer(db, customer_id)
    if customer is None:
        raise ValueError("El cliente no existe.")
    total_sales, total_paid, total_balance = (
        sale_repository.get_credit_balance_totals(db, customer_id)
    )
    return CustomerCreditBalance(
        customer_id=customer.id,
        customer_name=customer.name,
        total_credit_sales=total_sales,
        total_paid=total_paid,
        total_balance=total_balance,
    )


def _build_sale_items(
    db: Session,
    items: list[SaleItemCreate],
) -> tuple[list[dict[str, object]], Decimal]:
    item_values: list[dict[str, object]] = []
    total_amount = Decimal("0.00")
    for item in items:
        product = products.get_product(db, item.product_id)
        if product is None:
            raise ValueError(f"El producto {item.product_id} no existe.")
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")

        unit_price = item.unit_price
        if unit_price is None:
            unit_price = product.default_price
        subtotal = (item.quantity * unit_price).quantize(
            MONEY_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
        total_amount += subtotal
        item_values.append(
            {
                "product_id": product.id,
                "product_sku_snapshot": product.sku,
                "product_name_snapshot": product.name,
                "product_presentation_snapshot": product.presentation,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )
    return item_values, total_amount.quantize(MONEY_QUANTUM)


def _persist_sale(
    db: Session,
    sale_values: dict[str, object],
    item_values: list[dict[str, object]],
) -> Sale:
    sale = sale_repository.create_sale(db, sale_values)
    try:
        db.flush()
        sale.sale_number = f"SALE-{sale.sale_date:%Y%m%d}-{sale.id:06d}"
        for values in item_values:
            sale_repository.create_sale_item(
                db,
                {"sale_id": sale.id, **values},
            )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar la venta.") from error

    created_sale = sale_repository.get_sale(db, sale.id)
    if created_sale is None:
        raise RuntimeError("La venta registrada no pudo recuperarse.")
    return created_sale


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

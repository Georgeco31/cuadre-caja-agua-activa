from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.repositories import cash_sessions, customers, products
from app.repositories import sale_date_corrections
from app.repositories import sales as sale_repository
from app.schemas.sale import (
    CashSaleCreate,
    CreditSaleCreate,
    CustomerCreditBalance,
    SaleDateCorrectionResponse,
    SaleItemCreate,
)
from app.services import route_loads as route_load_service
from app.services import pricing as pricing_service

MONEY_QUANTUM = Decimal("0.01")


def create_cash_sale(
    db: Session,
    payload: CashSaleCreate,
    created_by: int,
) -> Sale:
    route_load_id = _validate_route_load(db, payload.route_load_id)
    customer_id = payload.customer_id
    customer_name_snapshot = "Consumidor final"
    if customer_id is not None:
        customer = customers.get_customer(db, customer_id)
        if customer is None:
            raise ValueError("El cliente no existe.")
        customer_name_snapshot = customer.name

    item_values, total_amount = _build_sale_items(
        db,
        payload.items,
        customer_id=customer_id,
        route_load_id=route_load_id,
        price_date=payload.sale_date,
    )
    return _persist_sale(
        db,
        {
            "sale_number": f"PENDING-{uuid4().hex}",
            "sale_date": payload.sale_date,
            "customer_id": customer_id,
            "customer_name_snapshot": customer_name_snapshot,
            "route_load_id": route_load_id,
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
    route_load_id = _validate_route_load(db, payload.route_load_id)
    customer = sale_repository.get_customer_for_credit(db, payload.customer_id)
    if customer is None:
        raise ValueError("El cliente no existe.")
    if not customer.is_active:
        raise ValueError("El cliente esta inactivo.")
    if not customer.credit_allowed:
        raise ValueError("El cliente no tiene credito permitido.")

    item_values, total_amount = _build_sale_items(
        db,
        payload.items,
        customer_id=customer.id,
        route_load_id=route_load_id,
        price_date=payload.sale_date,
    )
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
            "route_load_id": route_load_id,
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
    route_load_id: int | None = None,
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
        route_load_id=route_load_id,
        search=_normalize_filter(search),
    )


def get_sale(db: Session, sale_id: int) -> Sale:
    sale = sale_repository.get_sale(db, sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    return sale


def void_sale(db: Session, sale_id: int, reason: str) -> Sale:
    sale = sale_repository.get_sale_for_update(db, sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    if sale.status == "voided":
        raise ValueError("La venta ya esta anulada.")
    if sale.route_load_id is not None:
        route_load_service.ensure_route_load_is_financially_open(
            db,
            sale.route_load_id,
        )
    if (
        sale.sale_type == "credit"
        and sale_repository.has_active_credit_payments(db, sale.id)
    ):
        raise ValueError(
            "La venta tiene abonos activos. Anule primero los abonos."
        )

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


def correct_sale_date(
    db: Session,
    *,
    sale_id: int,
    new_sale_date: date,
    reason: str,
    corrected_by: int,
) -> SaleDateCorrectionResponse:
    sale = sale_repository.get_sale_for_update(db, sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    if sale.status == "voided":
        raise ValueError("La venta anulada no puede corregirse.")

    previous_sale_date = sale.sale_date
    if previous_sale_date == new_sale_date:
        raise ValueError("La nueva fecha debe ser diferente de la fecha actual.")

    if sale.route_load_id is not None:
        try:
            route_load_service.ensure_route_load_is_financially_open(
                db,
                sale.route_load_id,
            )
        except ValueError as error:
            if "cierre financiero activo" in str(error):
                raise ValueError(
                    "La fecha no puede corregirse porque la venta está "
                    "ligada a un cierre.",
                ) from error
            raise

    for affected_date in sorted({previous_sale_date, new_sale_date}):
        cash_session = cash_sessions.get_cash_session_by_date(
            db,
            affected_date,
            for_update=True,
        )
        if cash_session is not None and cash_session.status in {
            "closed",
            "corrected",
        }:
            raise ValueError(
                "La fecha no puede corregirse porque la venta está ligada "
                "a un cierre de caja.",
            )

    corrected_at = datetime.now(timezone.utc)
    correction = sale_date_corrections.create_sale_date_correction(
        db,
        sale_id=sale.id,
        previous_sale_date=previous_sale_date,
        new_sale_date=new_sale_date,
        reason=reason,
        created_by=corrected_by,
        created_at=corrected_at,
    )
    sale_repository.update_sale_date(db, sale, new_sale_date)
    try:
        db.flush()
        correction_id = correction.id
        db.commit()
    except Exception:
        db.rollback()
        raise

    corrected_sale = sale_repository.get_sale(db, sale.id)
    if corrected_sale is None:
        raise RuntimeError("La venta corregida no pudo recuperarse.")
    return SaleDateCorrectionResponse(
        sale=corrected_sale,
        correction_id=correction_id,
        correction_type="date_change",
        previous_sale_date=previous_sale_date,
        new_sale_date=new_sale_date,
        reason=reason,
        corrected_by=corrected_by,
        corrected_at=corrected_at,
    )


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
    customer_id: int | None,
    route_load_id: int | None,
    price_date: date,
) -> tuple[list[dict[str, object]], Decimal]:
    item_values: list[dict[str, object]] = []
    total_amount = Decimal("0.00")
    for item in items:
        product = products.get_product(db, item.product_id)
        if product is None:
            raise ValueError(f"El producto {item.product_id} no existe.")
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")

        if item.unit_price is None:
            resolution = pricing_service.resolve_price(
                db=db,
                product_id=product.id,
                customer_id=customer_id,
                route_load_id=route_load_id,
                quantity=item.quantity,
                price_date=price_date,
            )
            unit_price = resolution.resolved_price
            price_source = resolution.price_source
            price_list_id = resolution.price_list_id
            price_list_name = resolution.price_list_name
            pricing_note = resolution.pricing_note
        else:
            unit_price = item.unit_price
            price_source = "manual"
            price_list_id = None
            price_list_name = None
            pricing_note = "Precio ingresado manualmente"
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
                "price_source": price_source,
                "price_list_id": price_list_id,
                "price_list_name_snapshot": price_list_name,
                "pricing_note": pricing_note,
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


def _validate_route_load(db: Session, route_load_id: int | None) -> int | None:
    if route_load_id is None:
        return None
    return route_load_service.get_active_route_load_for_link(db, route_load_id).id

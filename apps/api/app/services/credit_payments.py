from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.credit_payment import CreditPayment
from app.repositories import credit_payments as payment_repository
from app.repositories import sales as sale_repository
from app.schemas.credit_payment import CreditPaymentCreate

MONEY_QUANTUM = Decimal("0.01")


def create_credit_payment(
    db: Session,
    sale_id: int,
    payload: CreditPaymentCreate,
    created_by: int,
) -> CreditPayment:
    sale = payment_repository.get_sale_for_update(db, sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    if sale.sale_type != "credit":
        raise ValueError("Solo se pueden registrar abonos sobre ventas a credito.")
    if sale.status != "active":
        raise ValueError("No se pueden registrar abonos sobre una venta anulada.")
    if sale.customer_id is None:
        raise ValueError("La venta a credito no tiene cliente.")
    if sale.balance_amount <= 0 or sale.credit_status == "paid":
        raise ValueError("La venta a credito ya esta pagada.")

    amount = payload.amount.quantize(MONEY_QUANTUM)
    if amount > sale.balance_amount:
        raise ValueError(
            "El monto del abono no puede ser mayor al saldo pendiente."
        )

    payment = payment_repository.create_credit_payment(
        db,
        {
            "sale_id": sale.id,
            "customer_id": sale.customer_id,
            "payment_date": payload.payment_date,
            "amount": amount,
            "payment_method": payload.payment_method,
            "status": "active",
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    sale.paid_amount = (sale.paid_amount + amount).quantize(MONEY_QUANTUM)
    sale.balance_amount = (sale.balance_amount - amount).quantize(MONEY_QUANTUM)
    sale.credit_status = "paid" if sale.balance_amount == 0 else "pending"
    db.add(sale)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar el abono.") from error

    created_payment = payment_repository.get_credit_payment(db, payment.id)
    if created_payment is None:
        raise RuntimeError("El abono registrado no pudo recuperarse.")
    return created_payment


def list_credit_payments(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = None,
    sale_id: int | None = None,
    status: str | None = None,
    payment_method: str | None = None,
) -> list[CreditPayment]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return payment_repository.list_credit_payments(
        db=db,
        date_from=date_from,
        date_to=date_to,
        customer_id=customer_id,
        sale_id=sale_id,
        status=status,
        payment_method=payment_method,
    )


def list_sale_payments(db: Session, sale_id: int) -> list[CreditPayment]:
    sale = sale_repository.get_sale(db, sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    return payment_repository.list_credit_payments(db=db, sale_id=sale_id)


def void_credit_payment(
    db: Session,
    payment_id: int,
    reason: str,
) -> CreditPayment:
    payment = payment_repository.get_credit_payment(
        db,
        payment_id,
        for_update=True,
    )
    if payment is None:
        raise ValueError("El abono no existe.")
    if payment.status == "voided":
        raise ValueError("El abono ya esta anulado.")

    sale = payment_repository.get_sale_for_update(db, payment.sale_id)
    if sale is None:
        raise ValueError("La venta no existe.")
    if sale.status != "active":
        raise ValueError("No se puede anular un abono de una venta anulada.")
    if sale.customer_id != payment.customer_id:
        raise RuntimeError("El cliente del abono no coincide con la venta.")
    if payment.amount > sale.paid_amount:
        raise RuntimeError("El abono no coincide con el monto pagado de la venta.")

    sale.paid_amount = (sale.paid_amount - payment.amount).quantize(MONEY_QUANTUM)
    sale.balance_amount = (sale.balance_amount + payment.amount).quantize(
        MONEY_QUANTUM
    )
    sale.credit_status = "pending"
    db.add(sale)
    payment_repository.mark_credit_payment_voided(
        db,
        payment,
        reason,
        datetime.now(timezone.utc),
    )

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular el abono.") from error

    voided_payment = payment_repository.get_credit_payment(db, payment.id)
    if voided_payment is None:
        raise RuntimeError("El abono anulado no pudo recuperarse.")
    return voided_payment

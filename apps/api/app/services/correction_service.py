from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cash_count_item import CashCountItem
from app.models.expense import Expense
from app.repositories import (
    cash_count_items,
    cash_sessions,
    correction_logs,
    denominations,
    expenses,
)
from app.schemas.correction import CorrectionLogRead
from app.services.summary_service import get_cash_session_summary

MONEY_QUANT = Decimal("0.01")


def correct_count_item(
    db: Session,
    cash_session_id: int,
    denomination_id: int,
    quantity: int,
    reason: str,
    created_by: int | None,
) -> tuple[CashCountItem, CorrectionLogRead]:
    normalized_reason = _normalize_required_text(reason, "El motivo es obligatorio.")
    if quantity < 0:
        raise ValueError("La cantidad debe ser mayor o igual a cero.")

    cash_session = _get_closed_cash_session(db, cash_session_id)
    denomination = denominations.get_denomination(db, denomination_id)
    if denomination is None:
        raise ValueError("La denominacion no existe.")

    previous_total = get_cash_session_summary(db, cash_session.id).final_total
    subtotal = (denomination.value * Decimal(quantity)).quantize(MONEY_QUANT)
    count_item = cash_count_items.get_count_item(
        db=db,
        cash_session_id=cash_session.id,
        denomination_id=denomination_id,
    )

    if count_item is None:
        count_item = cash_count_items.create_count_item(
            db=db,
            cash_session_id=cash_session.id,
            denomination_id=denomination_id,
            quantity=quantity,
            subtotal=subtotal,
        )
    else:
        count_item = cash_count_items.update_count_item(
            db=db,
            count_item=count_item,
            quantity=quantity,
            subtotal=subtotal,
        )

    db.flush()
    new_total = get_cash_session_summary(db, cash_session.id).final_total
    correction_log = correction_logs.create_correction_log(
        db=db,
        cash_session_id=cash_session.id,
        reason=normalized_reason,
        previous_total=previous_total,
        new_total=new_total,
        created_by=created_by,
    )
    db.commit()
    db.refresh(count_item)
    db.refresh(correction_log)
    return count_item, CorrectionLogRead.model_validate(correction_log)


def create_corrective_expense(
    db: Session,
    cash_session_id: int,
    description: str,
    amount: Decimal | str | int,
    reason: str,
    created_by: int | None,
    category: str | None = None,
    expense_date: date | None = None,
    notes: str | None = None,
) -> tuple[Expense, CorrectionLogRead]:
    cash_session = _get_closed_cash_session(db, cash_session_id)
    normalized_reason = _normalize_required_text(reason, "El motivo es obligatorio.")
    normalized_description = _normalize_required_text(
        description,
        "La descripcion del gasto es obligatoria.",
    )
    decimal_amount = _to_money_decimal(amount)
    if decimal_amount <= 0:
        raise ValueError("El monto del gasto debe ser mayor a cero.")

    previous_total = get_cash_session_summary(db, cash_session.id).final_total
    expense = expenses.create_expense(
        db=db,
        cash_session_id=cash_session.id,
        description=normalized_description,
        amount=decimal_amount,
        category=_normalize_optional_text(category),
        expense_timing="after_count",
        expense_date=expense_date or cash_session.session_date,
        notes=_normalize_optional_text(notes),
    )
    db.flush()

    new_total = get_cash_session_summary(db, cash_session.id).final_total
    correction_log = correction_logs.create_correction_log(
        db=db,
        cash_session_id=cash_session.id,
        reason=normalized_reason,
        previous_total=previous_total,
        new_total=new_total,
        created_by=created_by,
    )
    db.commit()
    db.refresh(expense)
    db.refresh(correction_log)
    return expense, CorrectionLogRead.model_validate(correction_log)


def list_corrections(db: Session, cash_session_id: int) -> list[CorrectionLogRead]:
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")

    return [
        CorrectionLogRead.model_validate(correction_log)
        for correction_log in correction_logs.list_correction_logs_by_cash_session(
            db=db,
            cash_session_id=cash_session_id,
        )
    ]


def _get_closed_cash_session(db: Session, cash_session_id: int):
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")
    if cash_session.status != "closed":
        raise ValueError("Las correcciones solo se permiten en cuadres cerrados.")
    return cash_session


def _normalize_required_text(value: str, message: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(message)
    return normalized_value


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None


def _to_money_decimal(amount: Decimal | str | int) -> Decimal:
    if isinstance(amount, float):
        raise ValueError("No usar float para valores monetarios.")
    return Decimal(amount).quantize(MONEY_QUANT)

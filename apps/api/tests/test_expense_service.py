from decimal import Decimal

import pytest

from app.services.cash_session_service import close_cash_session
from app.services.expense_service import create_expense


def test_create_expense_with_valid_amount(db, cash_session) -> None:
    expense = create_expense(
        db,
        cash_session_id=cash_session.id,
        description="Compra de suministros",
        amount=Decimal("8.50"),
        category="operativo",
    )

    assert expense.id is not None
    assert expense.amount == Decimal("8.50")
    assert expense.expense_timing == "after_count"
    assert expense.expense_date == cash_session.session_date


def test_create_expense_with_before_count_timing(db, cash_session) -> None:
    expense = create_expense(
        db,
        cash_session_id=cash_session.id,
        description="Compra antes del conteo",
        amount=Decimal("4.00"),
        category="operativo",
        expense_timing="before_count",
    )

    assert expense.expense_timing == "before_count"


def test_create_expense_rejects_invalid_expense_timing(db, cash_session) -> None:
    with pytest.raises(ValueError, match="tipo de gasto"):
        create_expense(
            db,
            cash_session_id=cash_session.id,
            description="Gasto invalido",
            amount=Decimal("4.00"),
            expense_timing="during_count",
        )


@pytest.mark.parametrize("amount", [Decimal("0.00"), Decimal("-1.00")])
def test_create_expense_rejects_non_positive_amount(
    db,
    cash_session,
    amount,
) -> None:
    with pytest.raises(ValueError, match="mayor a cero"):
        create_expense(
            db,
            cash_session_id=cash_session.id,
            description="Gasto invalido",
            amount=amount,
        )


def test_create_expense_rejects_float_amount(db, cash_session) -> None:
    with pytest.raises(ValueError, match="float"):
        create_expense(
            db,
            cash_session_id=cash_session.id,
            description="Gasto invalido",
            amount=8.5,
        )


def test_create_expense_blocks_closed_cash_session(db, cash_session) -> None:
    close_cash_session(db, cash_session.id)

    with pytest.raises(ValueError, match="cerrado"):
        create_expense(
            db,
            cash_session_id=cash_session.id,
            description="Compra de suministros",
            amount=Decimal("8.50"),
        )

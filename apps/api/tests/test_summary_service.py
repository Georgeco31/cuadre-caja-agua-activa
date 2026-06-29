from decimal import Decimal

from app.services.cash_count_service import set_count_item
from app.services.expense_service import create_expense
from app.services.summary_service import get_cash_session_summary


def test_get_cash_session_summary_calculates_daily_totals(
    db,
    cash_session,
    sample_denominations,
) -> None:
    set_count_item(db, cash_session.id, sample_denominations["coin_025"].id, 10)
    set_count_item(db, cash_session.id, sample_denominations["coin_100"].id, 5)
    set_count_item(db, cash_session.id, sample_denominations["bill_1000"].id, 3)
    set_count_item(db, cash_session.id, sample_denominations["bill_2000"].id, 2)
    create_expense(
        db,
        cash_session_id=cash_session.id,
        description="Gasto 1",
        amount=Decimal("8.50"),
    )
    create_expense(
        db,
        cash_session_id=cash_session.id,
        description="Gasto 2",
        amount=Decimal("2.00"),
    )

    summary = get_cash_session_summary(db, cash_session.id)

    assert summary.cash_session_id == cash_session.id
    assert summary.session_date == cash_session.session_date
    assert summary.status == "open"
    assert summary.total_coins == Decimal("7.50")
    assert summary.total_bills == Decimal("70.00")
    assert summary.total_counted == Decimal("77.50")
    assert summary.total_expenses == Decimal("10.50")
    assert summary.final_total == Decimal("67.00")

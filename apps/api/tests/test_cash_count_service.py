from decimal import Decimal

import pytest

from app.services.cash_count_service import set_count_item
from app.services.cash_session_service import close_cash_session


def test_set_count_item_with_valid_quantity(
    db,
    cash_session,
    sample_denominations,
) -> None:
    denomination = sample_denominations["coin_025"]

    item = set_count_item(db, cash_session.id, denomination.id, 10)

    assert item.quantity == 10
    assert item.subtotal == Decimal("2.50")


def test_set_count_item_rejects_negative_quantity(
    db,
    cash_session,
    sample_denominations,
) -> None:
    denomination = sample_denominations["coin_025"]

    with pytest.raises(ValueError, match="cantidad"):
        set_count_item(db, cash_session.id, denomination.id, -1)


def test_set_count_item_updates_existing_item(
    db,
    cash_session,
    sample_denominations,
) -> None:
    denomination = sample_denominations["bill_1000"]
    first_item = set_count_item(db, cash_session.id, denomination.id, 3)

    updated_item = set_count_item(db, cash_session.id, denomination.id, 4)

    assert updated_item.id == first_item.id
    assert updated_item.quantity == 4
    assert updated_item.subtotal == Decimal("40.00")


def test_set_count_item_blocks_closed_cash_session(
    db,
    cash_session,
    sample_denominations,
) -> None:
    denomination = sample_denominations["coin_100"]
    close_cash_session(db, cash_session.id)

    with pytest.raises(ValueError, match="cerrado"):
        set_count_item(db, cash_session.id, denomination.id, 5)

from decimal import Decimal

from sqlalchemy import select

from app.models.denomination import Denomination
from app.seeds.denominations import INITIAL_DENOMINATIONS, seed_denominations


def test_seed_denominations_creates_expected_initial_catalog(db) -> None:
    denominations = seed_denominations(db)

    assert len(denominations) == len(INITIAL_DENOMINATIONS)
    assert _count_denominations(db) == len(INITIAL_DENOMINATIONS)
    assert {
        (denomination.type, denomination.value, denomination.label)
        for denomination in denominations
    } == {
        (str(item["type"]), item["value"], str(item["label"]))
        for item in INITIAL_DENOMINATIONS
    }


def test_seed_denominations_is_idempotent(db) -> None:
    first_run = seed_denominations(db)
    second_run = seed_denominations(db)

    assert _count_denominations(db) == len(INITIAL_DENOMINATIONS)
    assert {denomination.id for denomination in first_run} == {
        denomination.id for denomination in second_run
    }


def test_seed_denominations_keeps_all_items_active(db) -> None:
    seed_denominations(db)

    denominations = db.scalars(select(Denomination)).all()

    assert denominations
    assert all(denomination.is_active is True for denomination in denominations)


def test_seed_denominations_uses_decimal_values(db) -> None:
    seed_denominations(db)

    denominations = db.scalars(select(Denomination)).all()

    assert denominations
    assert all(isinstance(denomination.value, Decimal) for denomination in denominations)


def _count_denominations(db) -> int:
    return len(db.scalars(select(Denomination)).all())

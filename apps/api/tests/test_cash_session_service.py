from datetime import date

import pytest

from app.services.cash_session_service import (
    close_cash_session,
    create_cash_session,
    get_cash_session_by_date,
)


def test_create_cash_session_with_valid_date(db) -> None:
    session_date = date(2026, 6, 29)

    cash_session = create_cash_session(db, session_date, notes="Caja principal")

    assert cash_session.id is not None
    assert cash_session.session_date == session_date
    assert cash_session.status == "open"
    assert cash_session.notes == "Caja principal"


def test_get_cash_session_by_date(db) -> None:
    session_date = date(2026, 6, 29)
    create_cash_session(db, session_date)

    cash_session = get_cash_session_by_date(db, session_date)

    assert cash_session is not None
    assert cash_session.session_date == session_date


def test_create_cash_session_rejects_duplicate_date(db) -> None:
    session_date = date(2026, 6, 29)
    create_cash_session(db, session_date)

    with pytest.raises(ValueError, match="Ya existe un cuadre"):
        create_cash_session(db, session_date)


def test_close_cash_session_sets_closed_status_and_timestamp(db, cash_session) -> None:
    closed_session = close_cash_session(db, cash_session.id)

    assert closed_session.status == "closed"
    assert closed_session.closed_at is not None

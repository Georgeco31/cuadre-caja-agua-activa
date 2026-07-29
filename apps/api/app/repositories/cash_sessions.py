from datetime import date, datetime, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash_session import CashSession


def get_cash_session(
    db: Session,
    cash_session_id: int,
    *,
    for_update: bool = False,
) -> CashSession | None:
    statement = select(CashSession).where(CashSession.id == cash_session_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_cash_session_by_date(
    db: Session,
    session_date: date,
    *,
    for_update: bool = False,
) -> CashSession | None:
    statement = select(CashSession).where(CashSession.session_date == session_date)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_cash_sessions(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
) -> list[CashSession]:
    statement = select(CashSession).order_by(CashSession.session_date)

    if date_from is not None:
        statement = statement.where(CashSession.session_date >= date_from)
    if date_to is not None:
        statement = statement.where(CashSession.session_date <= date_to)
    if status is not None:
        statement = statement.where(CashSession.status == status)

    return list(db.scalars(statement))


def create_cash_session(
    db: Session,
    session_date: date,
    created_by: int | None = None,
    notes: str | None = None,
) -> CashSession:
    cash_session = CashSession(
        session_date=session_date,
        created_by=created_by,
        notes=notes,
        status="open",
    )
    db.add(cash_session)
    return cash_session


def close_cash_session(db: Session, cash_session: CashSession) -> CashSession:
    cash_session.status = "closed"
    cash_session.closed_at = datetime.now(UTC)
    db.add(cash_session)
    return cash_session

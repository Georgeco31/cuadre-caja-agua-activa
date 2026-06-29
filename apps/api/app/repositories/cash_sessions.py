from datetime import date, datetime, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash_session import CashSession


def get_cash_session(db: Session, cash_session_id: int) -> CashSession | None:
    return db.get(CashSession, cash_session_id)


def get_cash_session_by_date(
    db: Session,
    session_date: date,
) -> CashSession | None:
    statement = select(CashSession).where(CashSession.session_date == session_date)
    return db.scalar(statement)


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

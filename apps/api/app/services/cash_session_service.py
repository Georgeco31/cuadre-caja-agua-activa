from datetime import date

from sqlalchemy.orm import Session

from app.models.cash_session import CashSession
from app.repositories import cash_sessions


def create_cash_session(
    db: Session,
    session_date: date,
    created_by: int | None = None,
    notes: str | None = None,
) -> CashSession:
    existing_session = cash_sessions.get_cash_session_by_date(db, session_date)
    if existing_session is not None:
        raise ValueError("Ya existe un cuadre para esta fecha.")

    cash_session = cash_sessions.create_cash_session(
        db=db,
        session_date=session_date,
        created_by=created_by,
        notes=notes,
    )
    db.commit()
    db.refresh(cash_session)
    return cash_session


def get_cash_session_by_date(
    db: Session,
    session_date: date,
) -> CashSession | None:
    return cash_sessions.get_cash_session_by_date(db, session_date)


def close_cash_session(db: Session, cash_session_id: int) -> CashSession:
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre no existe.")

    if cash_session.status == "closed":
        return cash_session

    cash_sessions.close_cash_session(db, cash_session)
    db.commit()
    db.refresh(cash_session)
    return cash_session


def ensure_cash_session_is_open(cash_session: CashSession) -> None:
    if cash_session.status != "open":
        raise ValueError("El cuadre esta cerrado y no permite cambios directos.")

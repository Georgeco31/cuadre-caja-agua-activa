from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.correction_log import CorrectionLog


def create_correction_log(
    db: Session,
    cash_session_id: int,
    reason: str,
    previous_total: Decimal,
    new_total: Decimal,
    created_by: int | None,
) -> CorrectionLog:
    correction_log = CorrectionLog(
        cash_session_id=cash_session_id,
        reason=reason,
        previous_total=previous_total,
        new_total=new_total,
        created_by=created_by,
    )
    db.add(correction_log)
    return correction_log


def list_correction_logs_by_cash_session(
    db: Session,
    cash_session_id: int,
) -> list[CorrectionLog]:
    statement = (
        select(CorrectionLog)
        .where(CorrectionLog.cash_session_id == cash_session_id)
        .order_by(CorrectionLog.created_at, CorrectionLog.id)
    )
    return list(db.scalars(statement))

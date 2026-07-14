from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories import cash_sessions
from app.schemas.report import CashSummaryReport
from app.services.summary_service import get_cash_session_summary

MONEY_ZERO = Decimal("0.00")


def get_cash_summary_report(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
) -> CashSummaryReport:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser mayor que la fecha hasta.")

    sessions = cash_sessions.list_cash_sessions(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
    )
    summaries = [
        get_cash_session_summary(db=db, cash_session_id=cash_session.id)
        for cash_session in sessions
    ]

    return CashSummaryReport(
        date_from=date_from,
        date_to=date_to,
        status=status,
        total_sessions=len(sessions),
        open_sessions=sum(
            1 for cash_session in sessions if cash_session.status == "open"
        ),
        closed_sessions=sum(
            1 for cash_session in sessions if cash_session.status == "closed"
        ),
        total_counted=sum(
            (summary.total_counted for summary in summaries),
            MONEY_ZERO,
        ),
        total_pre_count_expenses=sum(
            (summary.total_pre_count_expenses for summary in summaries),
            MONEY_ZERO,
        ),
        total_post_count_expenses=sum(
            (summary.total_post_count_expenses for summary in summaries),
            MONEY_ZERO,
        ),
        total_expenses=sum(
            (summary.total_expenses for summary in summaries),
            MONEY_ZERO,
        ),
        final_total=sum(
            (summary.final_total for summary in summaries),
            MONEY_ZERO,
        ),
    )

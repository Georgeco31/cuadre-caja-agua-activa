from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cash_session import CashSession
from app.models.route_closure import RouteClosure
from app.repositories import cash_sessions, route_closures
from app.schemas.report import CashSummaryReport
from app.schemas.route_cash_comparison import (
    RouteCashComparisonClosure,
    RouteCashComparisonReport,
    RouteCashComparisonRow,
    RouteCashComparisonStatus,
    RouteCashComparisonTotals,
)
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
    total_coins = sum(
        (summary.total_coins for summary in summaries),
        MONEY_ZERO,
    )
    total_bills = sum(
        (summary.total_bills for summary in summaries),
        MONEY_ZERO,
    )

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
        total_coins=total_coins,
        total_bills=total_bills,
        total_counted=total_coins + total_bills,
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


def get_route_cash_comparison_report(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
) -> RouteCashComparisonReport:
    resolved_date_from, resolved_date_to = _resolve_comparison_dates(
        date_from,
        date_to,
    )
    closures = route_closures.list_route_closures(
        db=db,
        date_from=resolved_date_from,
        date_to=resolved_date_to,
        status="active",
    )
    sessions = cash_sessions.list_cash_sessions(
        db=db,
        date_from=resolved_date_from,
        date_to=resolved_date_to,
    )

    closures_by_date: defaultdict[date, list[RouteClosure]] = defaultdict(list)
    for closure in closures:
        closures_by_date[closure.closure_date].append(closure)
    sessions_by_date = {
        cash_session.session_date: cash_session for cash_session in sessions
    }
    dates_with_information = sorted(set(closures_by_date) | set(sessions_by_date))
    rows = [
        _build_route_cash_comparison_row(
            db=db,
            comparison_date=comparison_date,
            closures=closures_by_date[comparison_date],
            cash_session=sessions_by_date.get(comparison_date),
        )
        for comparison_date in dates_with_information
    ]

    return RouteCashComparisonReport(
        date_from=resolved_date_from,
        date_to=resolved_date_to,
        totals=RouteCashComparisonTotals(
            route_closures_count=sum(row.route_closures_count for row in rows),
            route_expected_cash_total=sum(
                (row.route_expected_cash_total for row in rows),
                MONEY_ZERO,
            ),
            route_delivered_cash_total=sum(
                (row.route_delivered_cash_total for row in rows),
                MONEY_ZERO,
            ),
            route_difference_total=sum(
                (row.route_difference_total for row in rows),
                MONEY_ZERO,
            ),
            cash_total_counted=sum(
                (row.cash_total_counted for row in rows),
                MONEY_ZERO,
            ),
            cash_total_expenses=sum(
                (row.cash_total_expenses for row in rows),
                MONEY_ZERO,
            ),
            cash_total_final=sum(
                (row.cash_total_final for row in rows),
                MONEY_ZERO,
            ),
            cash_vs_route_delivered_difference=sum(
                (row.cash_vs_route_delivered_difference for row in rows),
                MONEY_ZERO,
            ),
        ),
        rows=rows,
    )


def _resolve_comparison_dates(
    date_from: date | None,
    date_to: date | None,
) -> tuple[date, date]:
    if date_from is None and date_to is None:
        today = date.today()
        return today, today
    if date_from is None:
        date_from = date_to
    if date_to is None:
        date_to = date_from
    if date_from is None or date_to is None:
        raise ValueError("No se pudo resolver el rango de fechas.")
    if date_from > date_to:
        raise ValueError("La fecha desde no puede ser mayor que la fecha hasta.")
    return date_from, date_to


def _build_route_cash_comparison_row(
    db: Session,
    comparison_date: date,
    closures: list[RouteClosure],
    cash_session: CashSession | None,
) -> RouteCashComparisonRow:
    route_expected_cash_total = sum(
        (closure.expected_cash_total for closure in closures),
        MONEY_ZERO,
    )
    route_delivered_cash_total = sum(
        (closure.delivered_cash_total for closure in closures),
        MONEY_ZERO,
    )
    route_difference_total = sum(
        (closure.difference_amount for closure in closures),
        MONEY_ZERO,
    )

    cash_total_coins = MONEY_ZERO
    cash_total_bills = MONEY_ZERO
    cash_total_counted = MONEY_ZERO
    cash_total_expenses = MONEY_ZERO
    cash_total_final = MONEY_ZERO
    if cash_session is not None:
        cash_summary = get_cash_session_summary(db, cash_session.id)
        cash_total_coins = cash_summary.total_coins
        cash_total_bills = cash_summary.total_bills
        cash_total_counted = cash_summary.total_counted
        cash_total_expenses = cash_summary.total_expenses
        cash_total_final = cash_summary.final_total

    has_cash_session = cash_session is not None
    has_route_closures = bool(closures)
    cash_vs_route_delivered_difference = (
        cash_total_counted - route_delivered_cash_total
    )

    return RouteCashComparisonRow(
        date=comparison_date,
        route_closures_count=len(closures),
        route_expected_cash_total=route_expected_cash_total,
        route_delivered_cash_total=route_delivered_cash_total,
        route_difference_total=route_difference_total,
        cash_session_exists=has_cash_session,
        has_cash_session=has_cash_session,
        has_route_closures=has_route_closures,
        cash_session_id=cash_session.id if cash_session is not None else None,
        cash_session_status=cash_session.status if cash_session is not None else None,
        cash_total_coins=cash_total_coins,
        cash_total_bills=cash_total_bills,
        cash_total_counted=cash_total_counted,
        cash_total_expenses=cash_total_expenses,
        cash_total_final=cash_total_final,
        cash_vs_route_delivered_difference=cash_vs_route_delivered_difference,
        comparison_status=_get_route_cash_comparison_status(
            has_cash_session=has_cash_session,
            has_route_closures=has_route_closures,
            difference=cash_vs_route_delivered_difference,
        ),
        route_closures=[
            RouteCashComparisonClosure(
                id=closure.id,
                closure_number=closure.closure_number,
                route_name_snapshot=closure.route_name_snapshot,
                vehicle_name_snapshot=closure.vehicle_name_snapshot,
                expected_cash_total=closure.expected_cash_total,
                delivered_cash_total=closure.delivered_cash_total,
                difference_amount=closure.difference_amount,
            )
            for closure in sorted(closures, key=lambda item: item.id)
        ],
    )


def _get_route_cash_comparison_status(
    *,
    has_cash_session: bool,
    has_route_closures: bool,
    difference: Decimal,
) -> RouteCashComparisonStatus:
    if not has_cash_session:
        return "no_cash_session"
    if not has_route_closures:
        return "no_route_closures"
    if difference == MONEY_ZERO:
        return "matched"
    if difference > MONEY_ZERO:
        return "cash_higher_than_routes"
    return "routes_higher_than_cash"

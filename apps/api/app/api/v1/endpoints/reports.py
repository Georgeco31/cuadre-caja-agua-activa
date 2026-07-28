from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.schemas.daily_operational_summary import DailyOperationalSummary
from app.schemas.monthly_operational_summary import MonthlyOperationalSummary
from app.schemas.report import CashSummaryReport
from app.schemas.route_cash_comparison import RouteCashComparisonReport
from app.services.daily_operational_summary import (
    get_daily_operational_summary as build_daily_operational_summary,
)
from app.services.monthly_operational_summary import (
    get_monthly_operational_summary as build_monthly_operational_summary,
)
from app.services.report_service import (
    get_cash_summary_report,
    get_route_cash_comparison_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/cash-summary",
    response_model=CashSummaryReport,
    dependencies=[Depends(require_admin_auditor)],
)
def get_cash_summary(
    date_from: Date | None = None,
    date_to: Date | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return get_cash_summary_report(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=status,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/route-cash-comparison",
    response_model=RouteCashComparisonReport,
)
def get_route_cash_comparison(
    date_from: Date | None = None,
    date_to: Date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return get_route_cash_comparison_report(
            db=db,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/daily-operational-summary",
    response_model=DailyOperationalSummary,
)
def get_daily_operational_summary(
    date: Date | None = None,
    db: Session = Depends(get_db),
):
    return build_daily_operational_summary(db=db, report_date=date)


@router.get(
    "/monthly-operational-summary",
    response_model=MonthlyOperationalSummary,
    dependencies=[Depends(require_admin_auditor)],
)
def get_monthly_operational_summary(
    year: int | None = Query(default=None, ge=1, le=9999),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    return build_monthly_operational_summary(
        db=db,
        year=year,
        month=month,
    )

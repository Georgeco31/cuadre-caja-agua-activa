from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.report import CashSummaryReport
from app.services.report_service import get_cash_summary_report

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/cash-summary", response_model=CashSummaryReport)
def get_cash_summary(
    date_from: date | None = None,
    date_to: date | None = None,
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

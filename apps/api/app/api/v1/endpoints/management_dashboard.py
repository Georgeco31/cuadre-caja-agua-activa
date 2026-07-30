from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_auditor
from app.schemas.admin_dashboard_analytics import AdminDashboardAnalytics
from app.schemas.management_dashboard import ManagementDashboard
from app.services.admin_dashboard_analytics import get_admin_dashboard_analytics
from app.services.management_dashboard import get_management_dashboard

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(require_admin_auditor)],
)


@router.get(
    "/management-dashboard",
    response_model=ManagementDashboard,
)
def read_management_dashboard(
    date_from: Date | None = None,
    date_to: Date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return get_management_dashboard(
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
    "/admin-dashboard-analytics",
    response_model=AdminDashboardAnalytics,
)
def read_admin_dashboard_analytics(
    start_date: Date | None = None,
    end_date: Date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return get_admin_dashboard_analytics(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

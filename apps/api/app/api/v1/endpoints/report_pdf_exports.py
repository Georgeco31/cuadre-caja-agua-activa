from collections.abc import Callable
from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.services.pdf_export import (
    build_daily_operational_summary_pdf,
    build_management_dashboard_pdf,
    build_monthly_summary_pdf,
    build_payroll_pdf,
    build_pdf_response,
    build_receivables_pdf,
)

router = APIRouter(
    prefix="/reports/exports",
    tags=["report-pdf-exports"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/management-dashboard.pdf")
def export_management_dashboard_pdf(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_management_dashboard_pdf(
            db,
            date_from=date_from,
            date_to=date_to,
        ),
        "panel-gerencial.pdf",
    )


@router.get("/monthly-summary.pdf")
def export_monthly_summary_pdf(
    year: int = Query(ge=1, le=9999),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_monthly_summary_pdf(db, year=year, month=month),
        f"resumen-mensual-{year:04d}-{month:02d}.pdf",
    )


@router.get("/daily-operational-summary.pdf")
def export_daily_operational_summary_pdf(
    report_date: date = Query(alias="date"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_daily_operational_summary_pdf(
            db,
            report_date=report_date,
        ),
        f"resumen-operativo-{report_date.isoformat()}.pdf",
    )


@router.get("/receivables.pdf")
def export_receivables_pdf(
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_receivables_pdf(
            db,
            date_from=date_from,
            date_to=date_to,
            customer_id=customer_id,
        ),
        "cartera.pdf",
    )


@router.get("/payroll.pdf")
def export_payroll_pdf(
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = Query(default=None, gt=0),
    payroll_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_payroll_pdf(
            db,
            date_from=date_from,
            date_to=date_to,
            employee_id=employee_id,
            status=payroll_status,
        ),
        "nomina-base.pdf",
    )


def _build_response(
    pdf_builder: Callable[[], BytesIO],
    filename: str,
) -> StreamingResponse:
    try:
        return build_pdf_response(pdf_builder(), filename)
    except ValueError as error:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

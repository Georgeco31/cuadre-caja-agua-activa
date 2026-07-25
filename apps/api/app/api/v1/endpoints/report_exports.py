from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.services.excel_export import (
    build_excel_response,
    build_inventory_workbook,
    build_management_dashboard_workbook,
    build_monthly_summary_workbook,
    build_operating_expenses_workbook,
    build_payroll_workbook,
    build_production_workbook,
    build_purchases_workbook,
    build_receivables_workbook,
    build_routes_workbook,
    build_sales_workbook,
)

router = APIRouter(
    prefix="/reports/exports",
    tags=["report-exports"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/management-dashboard.xlsx")
def export_management_dashboard(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_management_dashboard_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
        ),
        "panel-gerencial.xlsx",
    )


@router.get("/monthly-summary.xlsx")
def export_monthly_summary(
    year: int = Query(ge=1, le=9999),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_monthly_summary_workbook(db, year=year, month=month),
        f"resumen-mensual-{year:04d}-{month:02d}.xlsx",
    )


@router.get("/sales.xlsx")
def export_sales(
    date_from: date | None = None,
    date_to: date | None = None,
    sale_type: str | None = None,
    sale_status: str | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None, gt=0),
    route_load_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_sales_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            sale_type=sale_type,
            status=sale_status,
            customer_id=customer_id,
            route_load_id=route_load_id,
        ),
        "ventas.xlsx",
    )


@router.get("/receivables.xlsx")
def export_receivables(
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_receivables_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            customer_id=customer_id,
        ),
        "cartera.xlsx",
    )


@router.get("/operating-expenses.xlsx")
def export_operating_expenses(
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = Query(default=None, gt=0),
    supplier_id: int | None = Query(default=None, gt=0),
    payment_status: str | None = None,
    expense_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_operating_expenses_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            supplier_id=supplier_id,
            payment_status=payment_status,
            status=expense_status,
        ),
        "gastos-operativos.xlsx",
    )


@router.get("/purchases.xlsx")
def export_purchases(
    date_from: date | None = None,
    date_to: date | None = None,
    supplier_id: int | None = Query(default=None, gt=0),
    payment_status: str | None = None,
    purchase_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_purchases_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            supplier_id=supplier_id,
            payment_status=payment_status,
            status=purchase_status,
        ),
        "compras.xlsx",
    )


@router.get("/inventory.xlsx")
def export_inventory(
    location_id: int | None = Query(default=None, gt=0),
    product_id: int | None = Query(default=None, gt=0),
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_inventory_workbook(
            db,
            location_id=location_id,
            product_id=product_id,
            low_stock_only=low_stock_only,
        ),
        "inventario.xlsx",
    )


@router.get("/production.xlsx")
def export_production(
    date_from: date | None = None,
    date_to: date | None = None,
    production_status: str | None = Query(default=None, alias="status"),
    product_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_production_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            status=production_status,
            product_id=product_id,
        ),
        "produccion.xlsx",
    )


@router.get("/routes.xlsx")
def export_routes(
    date_from: date | None = None,
    date_to: date | None = None,
    route_load_id: int | None = Query(default=None, gt=0),
    route_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_routes_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            route_load_id=route_load_id,
            status=route_status,
        ),
        "rutas.xlsx",
    )


@router.get("/payroll.xlsx")
def export_payroll(
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = Query(default=None, gt=0),
    payroll_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return _build_response(
        lambda: build_payroll_workbook(
            db,
            date_from=date_from,
            date_to=date_to,
            employee_id=employee_id,
            status=payroll_status,
        ),
        "nomina-base.xlsx",
    )


def _build_response(workbook_builder, filename: str) -> StreamingResponse:
    try:
        return build_excel_response(workbook_builder(), filename)
    except ValueError as error:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

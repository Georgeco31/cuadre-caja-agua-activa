from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.schemas.customer import (
    CustomerCreate,
    CustomerRead,
    CustomerSalesSummary,
    CustomerType,
    CustomerUpdate,
)
from app.schemas.sale import SaleRead, SaleStatus
from app.services import customers as customer_service
from app.services import customer_sales as customer_sales_service

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        return customer_service.create_customer(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[CustomerRead])
def list_customers(
    search: str | None = None,
    is_active: bool | None = None,
    customer_type: CustomerType | None = None,
    sector: str | None = None,
    db: Session = Depends(get_db),
):
    return customer_service.list_customers(
        db=db,
        search=search,
        is_active=is_active,
        customer_type=customer_type,
        sector=sector,
    )


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        return customer_service.get_customer(db, customer_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/{customer_id}/sales-summary",
    response_model=CustomerSalesSummary,
)
def get_customer_sales_summary(
    customer_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    sale_type: str = Query(default="all", pattern="^(cash|credit|all)$"),
    sale_status: SaleStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    try:
        return customer_sales_service.get_customer_sales_summary(
            db,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            sale_type=sale_type,
            status=sale_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{customer_id}/sales", response_model=list[SaleRead])
def list_customer_sales(
    customer_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    sale_type: str = Query(default="all", pattern="^(cash|credit|all)$"),
    sale_status: SaleStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    try:
        return customer_sales_service.list_customer_sales(
            db,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            sale_type=sale_type,
            status=sale_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    try:
        return customer_service.update_customer(db, customer_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{customer_id}/deactivate",
    response_model=CustomerRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        return customer_service.deactivate_customer(db, customer_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{customer_id}/activate",
    response_model=CustomerRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        return customer_service.activate_customer(db, customer_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta registrado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

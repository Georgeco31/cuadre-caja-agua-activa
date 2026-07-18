from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.sale import (
    CashSaleCreate,
    CreditSaleCreate,
    CustomerCreditBalance,
    SalePaymentMethod,
    SaleRead,
    SaleStatus,
    SaleType,
    SaleVoid,
)
from app.services import sales as sale_service

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/cash", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_cash_sale(
    payload: CashSaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return sale_service.create_cash_sale(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/credit", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_credit_sale(
    payload: CreditSaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return sale_service.create_credit_sale(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[SaleRead])
def list_sales(
    date_from: date | None = None,
    date_to: date | None = None,
    sale_status: SaleStatus | None = Query(default=None, alias="status"),
    customer_id: int | None = None,
    payment_method: SalePaymentMethod | None = None,
    sale_type: SaleType | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return sale_service.list_sales(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=sale_status,
            customer_id=customer_id,
            payment_method=payment_method,
            sale_type=sale_type,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/credit/customer/{customer_id}/balance",
    response_model=CustomerCreditBalance,
)
def get_customer_credit_balance(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return sale_service.get_customer_credit_balance(db, customer_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    try:
        return sale_service.get_sale(db, sale_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/{sale_id}/void", response_model=SaleRead)
def void_sale(
    sale_id: int,
    payload: SaleVoid,
    db: Session = Depends(get_db),
):
    try:
        return sale_service.void_sale(db, sale_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta anulada" in detail or "tiene abonos activos" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

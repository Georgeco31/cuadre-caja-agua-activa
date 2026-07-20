from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.credit_payment import (
    CreditPaymentCreate,
    CreditPaymentMethod,
    CreditPaymentRead,
    CreditPaymentStatus,
    CreditPaymentVoid,
)
from app.services import credit_payments as payment_service

router = APIRouter(
    tags=["credit-payments"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/sales/{sale_id}/payments",
    response_model=CreditPaymentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_credit_payment(
    sale_id: int,
    payload: CreditPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payment_service.create_credit_payment(
            db,
            sale_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/sales/{sale_id}/payments",
    response_model=list[CreditPaymentRead],
)
def list_sale_payments(sale_id: int, db: Session = Depends(get_db)):
    try:
        return payment_service.list_sale_payments(db, sale_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/credit-payments", response_model=list[CreditPaymentRead])
def list_credit_payments(
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = None,
    sale_id: int | None = None,
    payment_status: CreditPaymentStatus | None = Query(
        default=None,
        alias="status",
    ),
    payment_method: CreditPaymentMethod | None = None,
    route_load_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    try:
        return payment_service.list_credit_payments(
            db=db,
            date_from=date_from,
            date_to=date_to,
            customer_id=customer_id,
            sale_id=sale_id,
            status=payment_status,
            payment_method=payment_method,
            route_load_id=route_load_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/credit-payments/{payment_id}/void",
    response_model=CreditPaymentRead,
)
def void_credit_payment(
    payment_id: int,
    payload: CreditPaymentVoid,
    db: Session = Depends(get_db),
):
    try:
        return payment_service.void_credit_payment(db, payment_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if (
        "ya esta" in detail
        or "tiene abonos activos" in detail
        or "cierre financiero activo" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

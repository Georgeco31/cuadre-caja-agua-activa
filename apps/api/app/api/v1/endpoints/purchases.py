from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.purchase import (
    PurchaseCreate,
    PurchasePaymentStatus,
    PurchaseRead,
    PurchaseStatus,
    PurchaseVoid,
)
from app.services import purchases as purchase_service

router = APIRouter(
    prefix="/purchases",
    tags=["purchases"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(
    payload: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return purchase_service.create_purchase(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[PurchaseRead])
def list_purchases(
    date_from: date | None = None,
    date_to: date | None = None,
    purchase_status: PurchaseStatus | None = Query(default=None, alias="status"),
    payment_status: PurchasePaymentStatus | None = None,
    supplier_id: int | None = Query(default=None, gt=0),
    product_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return purchase_service.list_purchases(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=purchase_status,
            payment_status=payment_status,
            supplier_id=supplier_id,
            product_id=product_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{purchase_id}", response_model=PurchaseRead)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    try:
        return purchase_service.get_purchase(db, purchase_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/{purchase_id}/void", response_model=PurchaseRead)
def void_purchase(
    purchase_id: int,
    payload: PurchaseVoid,
    db: Session = Depends(get_db),
):
    try:
        return purchase_service.void_purchase(db, purchase_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if "ya esta anulada" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

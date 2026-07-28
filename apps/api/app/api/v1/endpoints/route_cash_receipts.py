from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.models.user import User
from app.schemas.route_cash_receipt import (
    RouteCashReceiptCreate,
    RouteCashReceiptRead,
    RouteCashReceiptStatus,
    RouteCashReceiptVoid,
)
from app.services import route_cash_receipts as receipts_service

router = APIRouter(
    prefix="/route-cash-receipts",
    tags=["route-cash-receipts"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=RouteCashReceiptRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_route_cash_receipt(
    payload: RouteCashReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return receipts_service.create_route_cash_receipt(
            db,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[RouteCashReceiptRead])
def list_route_cash_receipts(
    date_from: date | None = None,
    date_to: date | None = None,
    receipt_status: RouteCashReceiptStatus | None = Query(
        default=None,
        alias="status",
    ),
    route_id: int | None = Query(default=None, gt=0),
    vehicle_id: int | None = Query(default=None, gt=0),
    route_closure_id: int | None = Query(default=None, gt=0),
    cash_session_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return receipts_service.list_route_cash_receipts(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=receipt_status,
            route_id=route_id,
            vehicle_id=vehicle_id,
            route_closure_id=route_closure_id,
            cash_session_id=cash_session_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{receipt_id}", response_model=RouteCashReceiptRead)
def get_route_cash_receipt(receipt_id: int, db: Session = Depends(get_db)):
    try:
        return receipts_service.get_route_cash_receipt(db, receipt_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{receipt_id}/void",
    response_model=RouteCashReceiptRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_route_cash_receipt(
    receipt_id: int,
    payload: RouteCashReceiptVoid,
    db: Session = Depends(get_db),
):
    try:
        return receipts_service.void_route_cash_receipt(
            db,
            receipt_id,
            payload.reason,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if (
        "ya tiene" in detail
        or "otro recibo activo" in detail
        or "ya esta anulado" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

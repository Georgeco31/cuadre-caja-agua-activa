from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.receivable import (
    CustomerStatement,
    OverdueReceivableRead,
    ReceivableCustomerRead,
    ReceivablesSummary,
)
from app.services import receivables as receivable_service

router = APIRouter(
    prefix="/receivables",
    tags=["receivables"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/summary", response_model=ReceivablesSummary)
def get_receivables_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return receivable_service.get_receivables_summary(
            db,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/customers", response_model=list[ReceivableCustomerRead])
def list_receivable_customers(
    search: str | None = None,
    only_with_balance: bool = False,
    is_active: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return receivable_service.list_receivable_customers(
            db=db,
            search=search,
            only_with_balance=only_with_balance,
            is_active=is_active,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/overdue", response_model=list[OverdueReceivableRead])
def list_overdue_receivables(db: Session = Depends(get_db)):
    return receivable_service.list_overdue_receivables(db)


@router.get(
    "/customers/{customer_id}/statement",
    response_model=CustomerStatement,
)
def get_customer_statement(
    customer_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    include_paid: bool = False,
    db: Session = Depends(get_db),
):
    try:
        return receivable_service.get_customer_statement(
            db=db,
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to,
            include_paid=include_paid,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

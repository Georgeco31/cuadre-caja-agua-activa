from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories import cash_sessions
from app.schemas.cash_count_item import (
    CashCountItemDetailRead,
    CashCountItemRead,
    CashCountItemSet,
)
from app.schemas.cash_session import CashSessionCreate, CashSessionRead
from app.schemas.correction import (
    CorrectionCountItemCreate,
    CorrectionCountItemResponse,
    CorrectionExpenseCreate,
    CorrectionExpenseResponse,
    CorrectionLogRead,
)
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.schemas.summary import CashSessionSummary
from app.schemas.route_cash_receipt import CashSessionRouteCashReceiptsRead
from app.services import (
    cash_count_service,
    cash_session_service,
    correction_service,
    expense_service,
    route_cash_receipts,
)
from app.services.summary_service import get_cash_session_summary

router = APIRouter(
    prefix="/cash-sessions",
    tags=["cash-sessions"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=CashSessionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_cash_session(
    payload: CashSessionCreate,
    db: Session = Depends(get_db),
):
    try:
        return cash_session_service.create_cash_session(
            db=db,
            session_date=payload.session_date,
            created_by=payload.created_by,
            notes=payload.notes,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[CashSessionRead])
def list_cash_sessions(
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return cash_sessions.list_cash_sessions(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
    )


@router.get("/by-date/{session_date}", response_model=CashSessionRead)
def get_cash_session_by_date(
    session_date: date,
    db: Session = Depends(get_db),
):
    cash_session = cash_session_service.get_cash_session_by_date(db, session_date)
    if cash_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El cuadre no existe.",
        )
    return cash_session


@router.get("/{cash_session_id}", response_model=CashSessionRead)
def get_cash_session(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    cash_session = cash_sessions.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El cuadre no existe.",
        )
    return cash_session


@router.post("/{cash_session_id}/count-items", response_model=CashCountItemRead)
def set_count_item(
    cash_session_id: int,
    payload: CashCountItemSet,
    db: Session = Depends(get_db),
):
    try:
        return cash_count_service.set_count_item(
            db=db,
            cash_session_id=cash_session_id,
            denomination_id=payload.denomination_id,
            quantity=payload.quantity,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/{cash_session_id}/count-items",
    response_model=list[CashCountItemDetailRead],
)
def list_count_items(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return cash_count_service.list_count_items(
            db=db,
            cash_session_id=cash_session_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{cash_session_id}/expenses",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    cash_session_id: int,
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.create_expense(
            db=db,
            cash_session_id=cash_session_id,
            description=payload.description,
            amount=payload.amount,
            category=payload.category,
            expense_timing=payload.expense_timing,
            expense_date=payload.expense_date,
            notes=payload.notes,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{cash_session_id}/expenses", response_model=list[ExpenseRead])
def list_expenses(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.list_expenses(
            db=db,
            cash_session_id=cash_session_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{cash_session_id}/corrections/count-items",
    response_model=CorrectionCountItemResponse,
)
def correct_count_item(
    cash_session_id: int,
    payload: CorrectionCountItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        count_item, correction_log = correction_service.correct_count_item(
            db=db,
            cash_session_id=cash_session_id,
            denomination_id=payload.denomination_id,
            quantity=payload.quantity,
            reason=payload.reason,
            created_by=current_user.id,
        )
        return CorrectionCountItemResponse(
            count_item=count_item,
            summary=get_cash_session_summary(db, cash_session_id),
            correction_log=correction_log,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{cash_session_id}/corrections/expenses",
    response_model=CorrectionExpenseResponse,
)
def create_corrective_expense(
    cash_session_id: int,
    payload: CorrectionExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        expense, correction_log = correction_service.create_corrective_expense(
            db=db,
            cash_session_id=cash_session_id,
            description=payload.description,
            amount=payload.amount,
            category=payload.category,
            expense_date=payload.expense_date,
            notes=payload.notes,
            reason=payload.reason,
            created_by=current_user.id,
        )
        return CorrectionExpenseResponse(
            expense=expense,
            summary=get_cash_session_summary(db, cash_session_id),
            correction_log=correction_log,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/{cash_session_id}/corrections",
    response_model=list[CorrectionLogRead],
)
def list_corrections(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return correction_service.list_corrections(
            db=db,
            cash_session_id=cash_session_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{cash_session_id}/summary", response_model=CashSessionSummary)
def get_summary(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_cash_session_summary(db, cash_session_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/{cash_session_id}/route-cash-receipts",
    response_model=CashSessionRouteCashReceiptsRead,
)
def get_route_cash_receipts(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return route_cash_receipts.get_receipts_for_cash_session(
            db,
            cash_session_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/{cash_session_id}/close", response_model=CashSessionRead)
def close_cash_session(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return cash_session_service.close_cash_session(
            db=db,
            cash_session_id=cash_session_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)

    if "Ya existe" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.models.user import User
from app.schemas.operating_expense import (
    OperatingExpenseCategoryCreate,
    OperatingExpenseCategoryRead,
    OperatingExpenseCategoryUpdate,
    OperatingExpenseCreate,
    OperatingExpensePaymentMethod,
    OperatingExpensePaymentStatus,
    OperatingExpenseRead,
    OperatingExpenseStatus,
    OperatingExpenseSummary,
    OperatingExpenseUpdate,
    OperatingExpenseVoid,
    RecurringOperatingExpenseCreate,
    RecurringOperatingExpenseCreateExpense,
    RecurringOperatingExpenseFrequency,
    RecurringOperatingExpenseRead,
    RecurringOperatingExpenseUpdate,
)
from app.services import operating_expenses as expense_service

router = APIRouter(
    prefix="/operating-expenses",
    tags=["operating-expenses"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/categories",
    response_model=OperatingExpenseCategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_category(
    payload: OperatingExpenseCategoryCreate,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.create_category(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/categories",
    response_model=list[OperatingExpenseCategoryRead],
)
def list_categories(
    search: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    return expense_service.list_categories(
        db,
        search=search,
        is_active=is_active,
    )


@router.get(
    "/categories/{category_id}",
    response_model=OperatingExpenseCategoryRead,
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        return expense_service.get_category(db, category_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/categories/{category_id}",
    response_model=OperatingExpenseCategoryRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_category(
    category_id: int,
    payload: OperatingExpenseCategoryUpdate,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.update_category(db, category_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/categories/{category_id}/deactivate",
    response_model=OperatingExpenseCategoryRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_category(category_id: int, db: Session = Depends(get_db)):
    try:
        return expense_service.deactivate_category(db, category_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/categories/{category_id}/activate",
    response_model=OperatingExpenseCategoryRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_category(category_id: int, db: Session = Depends(get_db)):
    try:
        return expense_service.activate_category(db, category_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/recurring",
    response_model=RecurringOperatingExpenseRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_recurring_template(
    payload: RecurringOperatingExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return expense_service.create_recurring_template(
            db,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/recurring",
    response_model=list[RecurringOperatingExpenseRead],
)
def list_recurring_templates(
    search: str | None = None,
    is_active: bool | None = None,
    category_id: int | None = Query(default=None, gt=0),
    supplier_id: int | None = Query(default=None, gt=0),
    frequency: RecurringOperatingExpenseFrequency | None = None,
    db: Session = Depends(get_db),
):
    return expense_service.list_recurring_templates(
        db=db,
        search=search,
        is_active=is_active,
        category_id=category_id,
        supplier_id=supplier_id,
        frequency=frequency,
    )


@router.get(
    "/recurring/{template_id}",
    response_model=RecurringOperatingExpenseRead,
)
def get_recurring_template(template_id: int, db: Session = Depends(get_db)):
    try:
        return expense_service.get_recurring_template(db, template_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recurring/{template_id}",
    response_model=RecurringOperatingExpenseRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_recurring_template(
    template_id: int,
    payload: RecurringOperatingExpenseUpdate,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.update_recurring_template(
            db,
            template_id,
            payload,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recurring/{template_id}/deactivate",
    response_model=RecurringOperatingExpenseRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_recurring_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.deactivate_recurring_template(db, template_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recurring/{template_id}/activate",
    response_model=RecurringOperatingExpenseRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_recurring_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.activate_recurring_template(db, template_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/recurring/{template_id}/create-expense",
    response_model=OperatingExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_from_template(
    template_id: int,
    payload: RecurringOperatingExpenseCreateExpense,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return expense_service.create_expense_from_template(
            db,
            template_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/summary", response_model=OperatingExpenseSummary)
def get_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = Query(default=None, gt=0),
    supplier_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    try:
        return expense_service.get_summary(
            db=db,
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            supplier_id=supplier_id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "",
    response_model=OperatingExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    payload: OperatingExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return expense_service.create_expense(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[OperatingExpenseRead])
def list_expenses(
    date_from: date | None = None,
    date_to: date | None = None,
    expense_status: OperatingExpenseStatus | None = Query(
        default=None,
        alias="status",
    ),
    payment_status: OperatingExpensePaymentStatus | None = None,
    category_id: int | None = Query(default=None, gt=0),
    supplier_id: int | None = Query(default=None, gt=0),
    payment_method: OperatingExpensePaymentMethod | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.list_expenses(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=expense_status,
            payment_status=payment_status,
            category_id=category_id,
            supplier_id=supplier_id,
            payment_method=payment_method,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{expense_id}", response_model=OperatingExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    try:
        return expense_service.get_expense(db, expense_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{expense_id}", response_model=OperatingExpenseRead)
def update_expense(
    expense_id: int,
    payload: OperatingExpenseUpdate,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.update_expense(db, expense_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{expense_id}/void",
    response_model=OperatingExpenseRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_expense(
    expense_id: int,
    payload: OperatingExpenseVoid,
    db: Session = Depends(get_db),
):
    try:
        return expense_service.void_expense(db, expense_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if "ya esta registrada" in detail or "ya esta anulado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "anulado no se puede editar" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

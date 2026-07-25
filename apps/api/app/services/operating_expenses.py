from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.operating_expense import OperatingExpense
from app.models.operating_expense_category import OperatingExpenseCategory
from app.models.recurring_operating_expense import RecurringOperatingExpense
from app.repositories import operating_expenses as expense_repository
from app.repositories import suppliers
from app.schemas.operating_expense import (
    OperatingExpenseCategoryCreate,
    OperatingExpenseCategoryUpdate,
    OperatingExpenseCreate,
    OperatingExpenseUpdate,
    RecurringOperatingExpenseCreate,
    RecurringOperatingExpenseCreateExpense,
    RecurringOperatingExpenseUpdate,
)

MONEY_QUANTUM = Decimal("0.01")


def create_category(
    db: Session,
    payload: OperatingExpenseCategoryCreate,
) -> OperatingExpenseCategory:
    _ensure_category_name_available(db, payload.name)
    category = expense_repository.create_category(db, payload.model_dump())
    _commit(db, "No se pudo registrar la categoria.")
    db.refresh(category)
    return category


def list_categories(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[OperatingExpenseCategory]:
    return expense_repository.list_categories(
        db,
        search=_normalize_filter(search),
        is_active=is_active,
    )


def get_category(db: Session, category_id: int) -> OperatingExpenseCategory:
    category = expense_repository.get_category(db, category_id)
    if category is None:
        raise ValueError("La categoria de gasto no existe.")
    return category


def update_category(
    db: Session,
    category_id: int,
    payload: OperatingExpenseCategoryUpdate,
) -> OperatingExpenseCategory:
    category = get_category(db, category_id)
    values = payload.model_dump(exclude_unset=True)
    if "name" in values:
        _ensure_category_name_available(
            db,
            str(values["name"]),
            exclude_category_id=category.id,
        )
    expense_repository.update_category(db, category, values)
    _commit(db, "No se pudo actualizar la categoria.")
    db.refresh(category)
    return category


def deactivate_category(
    db: Session,
    category_id: int,
) -> OperatingExpenseCategory:
    return _set_category_active(db, category_id, False)


def activate_category(
    db: Session,
    category_id: int,
) -> OperatingExpenseCategory:
    return _set_category_active(db, category_id, True)


def create_expense(
    db: Session,
    payload: OperatingExpenseCreate,
    created_by: int,
) -> OperatingExpense:
    _validate_category(db, payload.category_id)
    _validate_supplier(db, payload.supplier_id)
    return _create_expense(
        db,
        {
            **payload.model_dump(),
            "amount": payload.amount.quantize(MONEY_QUANTUM),
            "recurring_template_id": None,
            "created_by": created_by,
        },
    )


def list_expenses(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    payment_method: str | None = None,
    search: str | None = None,
) -> list[OperatingExpense]:
    _validate_date_range(date_from, date_to)
    return expense_repository.list_expenses(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        payment_status=payment_status,
        category_id=category_id,
        supplier_id=supplier_id,
        payment_method=payment_method,
        search=_normalize_filter(search),
    )


def get_expense(db: Session, expense_id: int) -> OperatingExpense:
    expense = expense_repository.get_expense(db, expense_id)
    if expense is None:
        raise ValueError("El gasto operativo no existe.")
    return expense


def update_expense(
    db: Session,
    expense_id: int,
    payload: OperatingExpenseUpdate,
) -> OperatingExpense:
    expense = get_expense(db, expense_id)
    if expense.status == "voided":
        raise ValueError("El gasto operativo anulado no se puede editar.")

    values = payload.model_dump(exclude_unset=True)
    if "category_id" in values:
        _validate_category(db, int(values["category_id"]))
    if "supplier_id" in values:
        _validate_supplier(db, values["supplier_id"])
    if "amount" in values:
        values["amount"] = values["amount"].quantize(MONEY_QUANTUM)

    expense_repository.update_expense(db, expense, values)
    _commit(db, "No se pudo actualizar el gasto operativo.")
    return _require_expense(db, expense.id)


def void_expense(
    db: Session,
    expense_id: int,
    reason: str,
) -> OperatingExpense:
    expense = expense_repository.get_expense(db, expense_id, for_update=True)
    if expense is None:
        raise ValueError("El gasto operativo no existe.")
    if expense.status == "voided":
        raise ValueError("El gasto operativo ya esta anulado.")

    expense_repository.mark_expense_voided(
        db,
        expense,
        reason,
        datetime.now(timezone.utc),
    )
    _commit(db, "No se pudo anular el gasto operativo.")
    return _require_expense(db, expense.id)


def create_recurring_template(
    db: Session,
    payload: RecurringOperatingExpenseCreate,
    created_by: int,
) -> RecurringOperatingExpense:
    _validate_category(db, payload.category_id)
    _validate_supplier(db, payload.supplier_id)
    _validate_recurring_dates(
        payload.start_date,
        payload.end_date,
        payload.next_due_date,
    )
    template = expense_repository.create_recurring_template(
        db,
        {
            **payload.model_dump(),
            "amount": payload.amount.quantize(MONEY_QUANTUM),
            "created_by": created_by,
        },
    )
    _commit(db, "No se pudo registrar la plantilla recurrente.")
    return _require_recurring_template(db, template.id)


def list_recurring_templates(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    frequency: str | None = None,
) -> list[RecurringOperatingExpense]:
    return expense_repository.list_recurring_templates(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        category_id=category_id,
        supplier_id=supplier_id,
        frequency=frequency,
    )


def get_recurring_template(
    db: Session,
    template_id: int,
) -> RecurringOperatingExpense:
    template = expense_repository.get_recurring_template(db, template_id)
    if template is None:
        raise ValueError("La plantilla recurrente no existe.")
    return template


def update_recurring_template(
    db: Session,
    template_id: int,
    payload: RecurringOperatingExpenseUpdate,
) -> RecurringOperatingExpense:
    template = get_recurring_template(db, template_id)
    values = payload.model_dump(exclude_unset=True)
    if "category_id" in values:
        _validate_category(db, int(values["category_id"]))
    if "supplier_id" in values:
        _validate_supplier(db, values["supplier_id"])
    if "amount" in values:
        values["amount"] = values["amount"].quantize(MONEY_QUANTUM)

    _validate_recurring_dates(
        values.get("start_date", template.start_date),
        values.get("end_date", template.end_date),
        values.get("next_due_date", template.next_due_date),
    )
    expense_repository.update_recurring_template(db, template, values)
    _commit(db, "No se pudo actualizar la plantilla recurrente.")
    return _require_recurring_template(db, template.id)


def deactivate_recurring_template(
    db: Session,
    template_id: int,
) -> RecurringOperatingExpense:
    return _set_recurring_template_active(db, template_id, False)


def activate_recurring_template(
    db: Session,
    template_id: int,
) -> RecurringOperatingExpense:
    return _set_recurring_template_active(db, template_id, True)


def create_expense_from_template(
    db: Session,
    template_id: int,
    payload: RecurringOperatingExpenseCreateExpense,
    created_by: int,
) -> OperatingExpense:
    template = get_recurring_template(db, template_id)
    if not template.is_active:
        raise ValueError("La plantilla recurrente esta inactiva.")
    _validate_category(db, template.category_id)
    _validate_supplier(db, template.supplier_id)

    return _create_expense(
        db,
        {
            "expense_date": payload.expense_date,
            "category_id": template.category_id,
            "supplier_id": template.supplier_id,
            "description": template.description,
            "amount": template.amount.quantize(MONEY_QUANTUM),
            "payment_status": payload.payment_status,
            "payment_method": template.payment_method,
            "document_number": None,
            "due_date": payload.due_date,
            "paid_date": payload.paid_date,
            "recurring_template_id": template.id,
            "notes": payload.notes,
            "created_by": created_by,
        },
    )


def get_summary(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
) -> dict[str, object]:
    _validate_date_range(date_from, date_to)
    return expense_repository.get_summary(
        db=db,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        supplier_id=supplier_id,
    )


def _create_expense(
    db: Session,
    values: dict[str, object],
) -> OperatingExpense:
    expense_date = values["expense_date"]
    expense = expense_repository.create_expense(
        db,
        {
            **values,
            "expense_number": f"PENDING-{uuid4().hex}",
            "status": "active",
        },
    )
    try:
        db.flush()
        expense.expense_number = (
            f"OPEX-{expense_date:%Y%m%d}-{expense.id:04d}"
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar el gasto operativo.") from error
    return _require_expense(db, expense.id)


def _set_category_active(
    db: Session,
    category_id: int,
    is_active: bool,
) -> OperatingExpenseCategory:
    category = get_category(db, category_id)
    expense_repository.set_category_active(db, category, is_active)
    _commit(db, "No se pudo cambiar el estado de la categoria.")
    db.refresh(category)
    return category


def _set_recurring_template_active(
    db: Session,
    template_id: int,
    is_active: bool,
) -> RecurringOperatingExpense:
    template = get_recurring_template(db, template_id)
    expense_repository.set_recurring_template_active(
        db,
        template,
        is_active,
    )
    _commit(db, "No se pudo cambiar el estado de la plantilla recurrente.")
    return _require_recurring_template(db, template.id)


def _validate_category(
    db: Session,
    category_id: int,
) -> OperatingExpenseCategory:
    category = get_category(db, category_id)
    if not category.is_active:
        raise ValueError("La categoria de gasto esta inactiva.")
    return category


def _validate_supplier(db: Session, supplier_id: object) -> None:
    if supplier_id is None:
        return
    supplier = suppliers.get_supplier(db, int(supplier_id))
    if supplier is None:
        raise ValueError("El proveedor no existe.")
    if not supplier.is_active:
        raise ValueError("El proveedor esta inactivo.")


def _ensure_category_name_available(
    db: Session,
    name: str,
    exclude_category_id: int | None = None,
) -> None:
    existing = expense_repository.get_category_by_name(
        db,
        name,
        exclude_category_id=exclude_category_id,
    )
    if existing is not None:
        raise ValueError("La categoria de gasto ya esta registrada.")


def _require_expense(db: Session, expense_id: int) -> OperatingExpense:
    expense = expense_repository.get_expense(db, expense_id)
    if expense is None:
        raise RuntimeError("El gasto operativo registrado no pudo recuperarse.")
    return expense


def _require_recurring_template(
    db: Session,
    template_id: int,
) -> RecurringOperatingExpense:
    template = expense_repository.get_recurring_template(db, template_id)
    if template is None:
        raise RuntimeError(
            "La plantilla recurrente registrada no pudo recuperarse.",
        )
    return template


def _validate_date_range(
    date_from: date | None,
    date_to: date | None,
) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _validate_recurring_dates(
    start_date: date,
    end_date: date | None,
    next_due_date: date | None,
) -> None:
    if end_date is not None and start_date > end_date:
        raise ValueError(
            "La fecha de inicio no puede ser posterior a la fecha final.",
        )
    if next_due_date is not None and next_due_date < start_date:
        raise ValueError(
            "El proximo vencimiento no puede ser anterior al inicio.",
        )
    if (
        next_due_date is not None
        and end_date is not None
        and next_due_date > end_date
    ):
        raise ValueError(
            "El proximo vencimiento no puede ser posterior a la fecha final.",
        )


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(message) from error


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

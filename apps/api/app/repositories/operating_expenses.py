from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.operating_expense import OperatingExpense
from app.models.operating_expense_category import OperatingExpenseCategory
from app.models.recurring_operating_expense import RecurringOperatingExpense
from app.models.supplier import Supplier


def get_category(
    db: Session,
    category_id: int,
) -> OperatingExpenseCategory | None:
    return db.get(OperatingExpenseCategory, category_id)


def get_category_by_name(
    db: Session,
    name: str,
    exclude_category_id: int | None = None,
) -> OperatingExpenseCategory | None:
    statement = select(OperatingExpenseCategory).where(
        func.lower(OperatingExpenseCategory.name) == name.lower(),
    )
    if exclude_category_id is not None:
        statement = statement.where(
            OperatingExpenseCategory.id != exclude_category_id,
        )
    return db.scalar(statement)


def list_categories(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[OperatingExpenseCategory]:
    statement = select(OperatingExpenseCategory)
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                OperatingExpenseCategory.name.ilike(search_pattern),
                OperatingExpenseCategory.description.ilike(search_pattern),
            ),
        )
    if is_active is not None:
        statement = statement.where(
            OperatingExpenseCategory.is_active == is_active,
        )
    statement = statement.order_by(
        func.lower(OperatingExpenseCategory.name),
        OperatingExpenseCategory.id,
    )
    return list(db.scalars(statement))


def create_category(
    db: Session,
    values: dict[str, object],
) -> OperatingExpenseCategory:
    category = OperatingExpenseCategory(**values)
    db.add(category)
    return category


def update_category(
    db: Session,
    category: OperatingExpenseCategory,
    values: dict[str, object],
) -> OperatingExpenseCategory:
    _set_values(category, values)
    db.add(category)
    return category


def set_category_active(
    db: Session,
    category: OperatingExpenseCategory,
    is_active: bool,
) -> OperatingExpenseCategory:
    category.is_active = is_active
    db.add(category)
    return category


def get_expense(
    db: Session,
    expense_id: int,
    *,
    for_update: bool = False,
) -> OperatingExpense | None:
    statement = (
        select(OperatingExpense)
        .options(*_expense_options())
        .where(OperatingExpense.id == expense_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


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
    statement = (
        select(OperatingExpense)
        .join(OperatingExpense.category)
        .outerjoin(OperatingExpense.supplier)
        .options(*_expense_options())
    )
    statement = _filter_expenses(
        statement,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        supplier_id=supplier_id,
    )
    if status is not None:
        statement = statement.where(OperatingExpense.status == status)
    if payment_status is not None:
        statement = statement.where(
            OperatingExpense.payment_status == payment_status,
        )
    if payment_method is not None:
        statement = statement.where(
            OperatingExpense.payment_method == payment_method,
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                OperatingExpense.expense_number.ilike(search_pattern),
                OperatingExpense.description.ilike(search_pattern),
                OperatingExpense.document_number.ilike(search_pattern),
                OperatingExpense.notes.ilike(search_pattern),
                OperatingExpenseCategory.name.ilike(search_pattern),
                Supplier.name.ilike(search_pattern),
            ),
        )
    statement = statement.order_by(
        OperatingExpense.expense_date.desc(),
        OperatingExpense.id.desc(),
    )
    return list(db.scalars(statement).unique())


def create_expense(
    db: Session,
    values: dict[str, object],
) -> OperatingExpense:
    expense = OperatingExpense(**values)
    db.add(expense)
    return expense


def update_expense(
    db: Session,
    expense: OperatingExpense,
    values: dict[str, object],
) -> OperatingExpense:
    _set_values(expense, values)
    db.add(expense)
    return expense


def mark_expense_voided(
    db: Session,
    expense: OperatingExpense,
    reason: str,
    voided_at: datetime,
) -> OperatingExpense:
    expense.status = "voided"
    expense.void_reason = reason
    expense.voided_at = voided_at
    db.add(expense)
    return expense


def get_recurring_template(
    db: Session,
    template_id: int,
) -> RecurringOperatingExpense | None:
    statement = (
        select(RecurringOperatingExpense)
        .options(*_recurring_options())
        .where(RecurringOperatingExpense.id == template_id)
    )
    return db.scalar(statement)


def list_recurring_templates(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    frequency: str | None = None,
) -> list[RecurringOperatingExpense]:
    statement = (
        select(RecurringOperatingExpense)
        .join(RecurringOperatingExpense.category)
        .outerjoin(RecurringOperatingExpense.supplier)
        .options(*_recurring_options())
    )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                RecurringOperatingExpense.name.ilike(search_pattern),
                RecurringOperatingExpense.description.ilike(search_pattern),
                RecurringOperatingExpense.notes.ilike(search_pattern),
                OperatingExpenseCategory.name.ilike(search_pattern),
                Supplier.name.ilike(search_pattern),
            ),
        )
    if is_active is not None:
        statement = statement.where(
            RecurringOperatingExpense.is_active == is_active,
        )
    if category_id is not None:
        statement = statement.where(
            RecurringOperatingExpense.category_id == category_id,
        )
    if supplier_id is not None:
        statement = statement.where(
            RecurringOperatingExpense.supplier_id == supplier_id,
        )
    if frequency is not None:
        statement = statement.where(
            RecurringOperatingExpense.frequency == frequency,
        )
    statement = statement.order_by(
        func.lower(RecurringOperatingExpense.name),
        RecurringOperatingExpense.id,
    )
    return list(db.scalars(statement).unique())


def create_recurring_template(
    db: Session,
    values: dict[str, object],
) -> RecurringOperatingExpense:
    template = RecurringOperatingExpense(**values)
    db.add(template)
    return template


def update_recurring_template(
    db: Session,
    template: RecurringOperatingExpense,
    values: dict[str, object],
) -> RecurringOperatingExpense:
    _set_values(template, values)
    db.add(template)
    return template


def set_recurring_template_active(
    db: Session,
    template: RecurringOperatingExpense,
    is_active: bool,
) -> RecurringOperatingExpense:
    template.is_active = is_active
    db.add(template)
    return template


def get_summary(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
) -> dict[str, object]:
    active_filters = [OperatingExpense.status == "active"]
    active_filters.extend(
        _expense_filter_conditions(
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            supplier_id=supplier_id,
        ),
    )
    all_filters = _expense_filter_conditions(
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        supplier_id=supplier_id,
    )

    totals = db.execute(
        select(
            func.count(OperatingExpense.id),
            func.coalesce(func.sum(OperatingExpense.amount), 0),
        ).where(*active_filters),
    ).one()
    voided_count = db.scalar(
        select(func.count(OperatingExpense.id)).where(
            OperatingExpense.status == "voided",
            *all_filters,
        ),
    )

    payment_rows = db.execute(
        select(
            OperatingExpense.payment_status,
            func.coalesce(func.sum(OperatingExpense.amount), 0),
            func.count(OperatingExpense.id),
        )
        .where(*active_filters)
        .group_by(OperatingExpense.payment_status)
        .order_by(OperatingExpense.payment_status),
    ).all()
    payment_amounts = {
        row.payment_status: _decimal(row[1]) for row in payment_rows
    }

    category_rows = db.execute(
        select(
            OperatingExpense.category_id,
            OperatingExpenseCategory.name,
            func.coalesce(func.sum(OperatingExpense.amount), 0),
            func.count(OperatingExpense.id),
        )
        .join(
            OperatingExpenseCategory,
            OperatingExpense.category_id == OperatingExpenseCategory.id,
        )
        .where(*active_filters)
        .group_by(
            OperatingExpense.category_id,
            OperatingExpenseCategory.name,
        )
        .order_by(func.lower(OperatingExpenseCategory.name)),
    ).all()

    supplier_rows = db.execute(
        select(
            OperatingExpense.supplier_id,
            Supplier.name,
            func.coalesce(func.sum(OperatingExpense.amount), 0),
            func.count(OperatingExpense.id),
        )
        .outerjoin(Supplier, OperatingExpense.supplier_id == Supplier.id)
        .where(*active_filters)
        .group_by(OperatingExpense.supplier_id, Supplier.name)
        .order_by(func.coalesce(func.lower(Supplier.name), "")),
    ).all()

    return {
        "total_expenses_amount": _decimal(totals[1]),
        "paid_amount": payment_amounts.get("paid", Decimal("0.00")),
        "unpaid_amount": payment_amounts.get("unpaid", Decimal("0.00")),
        "partial_amount": payment_amounts.get("partial", Decimal("0.00")),
        "expenses_count": int(totals[0]),
        "voided_count": int(voided_count or 0),
        "by_category": [
            {
                "category_id": row[0],
                "category_name": row[1],
                "total_amount": _decimal(row[2]),
                "expenses_count": int(row[3]),
            }
            for row in category_rows
        ],
        "by_supplier": [
            {
                "supplier_id": row[0],
                "supplier_name": row[1] or "Sin proveedor",
                "total_amount": _decimal(row[2]),
                "expenses_count": int(row[3]),
            }
            for row in supplier_rows
        ],
        "by_payment_status": [
            {
                "payment_status": row[0],
                "total_amount": _decimal(row[1]),
                "expenses_count": int(row[2]),
            }
            for row in payment_rows
        ],
    }


def _filter_expenses(statement, **filters):
    return statement.where(*_expense_filter_conditions(**filters))


def _expense_filter_conditions(
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
):
    conditions = []
    if date_from is not None:
        conditions.append(OperatingExpense.expense_date >= date_from)
    if date_to is not None:
        conditions.append(OperatingExpense.expense_date <= date_to)
    if category_id is not None:
        conditions.append(OperatingExpense.category_id == category_id)
    if supplier_id is not None:
        conditions.append(OperatingExpense.supplier_id == supplier_id)
    return conditions


def _expense_options():
    return (
        joinedload(OperatingExpense.category, innerjoin=True),
        joinedload(OperatingExpense.supplier),
    )


def _recurring_options():
    return (
        joinedload(RecurringOperatingExpense.category, innerjoin=True),
        joinedload(RecurringOperatingExpense.supplier),
    )


def _set_values(instance, values: dict[str, object]) -> None:
    for field_name, value in values.items():
        setattr(instance, field_name, value)


def _decimal(value: object) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"))

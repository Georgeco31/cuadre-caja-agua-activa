from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.cash_session import CashSession
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.product import Product
from app.models.simple_route import (
    SimpleRouteAuditLog,
    SimpleRouteCashReceipt,
    SimpleRouteCollection,
    SimpleRouteExpense,
    SimpleRouteSale,
    SimpleRouteSaleItem,
    SimpleRouteSheet,
    SimpleRouteTrip,
    SimpleRouteTripItem,
)
from app.models.vehicle import Vehicle


def get_sheet(
    db: Session,
    sheet_id: int,
    *,
    for_update: bool = False,
) -> SimpleRouteSheet | None:
    statement = (
        select(SimpleRouteSheet)
        .options(*_sheet_options())
        .where(SimpleRouteSheet.id == sheet_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_sheets(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    employee_id: int | None = None,
    vehicle_id: int | None = None,
    search: str | None = None,
) -> list[SimpleRouteSheet]:
    statement = select(SimpleRouteSheet).options(*_sheet_options())
    if date_from is not None:
        statement = statement.where(SimpleRouteSheet.route_date >= date_from)
    if date_to is not None:
        statement = statement.where(SimpleRouteSheet.route_date <= date_to)
    if status is not None:
        statement = statement.where(SimpleRouteSheet.status == status)
    if employee_id is not None:
        statement = statement.where(SimpleRouteSheet.employee_id == employee_id)
    if vehicle_id is not None:
        statement = statement.where(SimpleRouteSheet.vehicle_id == vehicle_id)
    if search is not None:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                SimpleRouteSheet.seller_name.ilike(pattern),
                SimpleRouteSheet.route_label.ilike(pattern),
                SimpleRouteSheet.notes.ilike(pattern),
            )
        )
    statement = statement.order_by(
        SimpleRouteSheet.route_date.desc(),
        SimpleRouteSheet.id.desc(),
    )
    return list(db.scalars(statement).unique())


def create_sheet(db: Session, values: dict[str, object]) -> SimpleRouteSheet:
    sheet = SimpleRouteSheet(**values)
    db.add(sheet)
    return sheet


def get_trip(
    db: Session,
    sheet_id: int,
    trip_id: int,
) -> SimpleRouteTrip | None:
    return db.scalar(
        select(SimpleRouteTrip)
        .options(selectinload(SimpleRouteTrip.items))
        .where(
            SimpleRouteTrip.id == trip_id,
            SimpleRouteTrip.route_sheet_id == sheet_id,
        )
    )


def create_trip(db: Session, values: dict[str, object]) -> SimpleRouteTrip:
    trip = SimpleRouteTrip(**values)
    db.add(trip)
    return trip


def create_trip_item(
    db: Session,
    values: dict[str, object],
) -> SimpleRouteTripItem:
    item = SimpleRouteTripItem(**values)
    db.add(item)
    return item


def get_sale(db: Session, sale_id: int) -> SimpleRouteSale | None:
    return db.scalar(
        select(SimpleRouteSale)
        .options(
            selectinload(SimpleRouteSale.items),
            selectinload(SimpleRouteSale.linked_collections),
        )
        .where(SimpleRouteSale.id == sale_id)
    )


def create_sale(db: Session, values: dict[str, object]) -> SimpleRouteSale:
    sale = SimpleRouteSale(**values)
    db.add(sale)
    return sale


def create_sale_item(
    db: Session,
    values: dict[str, object],
) -> SimpleRouteSaleItem:
    item = SimpleRouteSaleItem(**values)
    db.add(item)
    return item


def create_collection(
    db: Session,
    values: dict[str, object],
) -> SimpleRouteCollection:
    collection = SimpleRouteCollection(**values)
    db.add(collection)
    return collection


def create_expense(db: Session, values: dict[str, object]) -> SimpleRouteExpense:
    expense = SimpleRouteExpense(**values)
    db.add(expense)
    return expense


def create_audit_log(
    db: Session,
    values: dict[str, object],
) -> SimpleRouteAuditLog:
    log = SimpleRouteAuditLog(**values)
    db.add(log)
    return log


def create_cash_receipt(
    db: Session,
    values: dict[str, object],
) -> SimpleRouteCashReceipt:
    receipt = SimpleRouteCashReceipt(**values)
    db.add(receipt)
    return receipt


def get_cash_receipt_for_sheet(
    db: Session,
    sheet_id: int,
) -> SimpleRouteCashReceipt | None:
    return db.scalar(
        select(SimpleRouteCashReceipt)
        .options(joinedload(SimpleRouteCashReceipt.route_sheet, innerjoin=True))
        .where(SimpleRouteCashReceipt.route_sheet_id == sheet_id)
    )


def list_cash_receipts_for_session(
    db: Session,
    cash_session_id: int,
) -> list[SimpleRouteCashReceipt]:
    statement = (
        select(SimpleRouteCashReceipt)
        .options(joinedload(SimpleRouteCashReceipt.route_sheet, innerjoin=True))
        .where(SimpleRouteCashReceipt.cash_session_id == cash_session_id)
        .order_by(SimpleRouteCashReceipt.received_at, SimpleRouteCashReceipt.id)
    )
    return list(db.scalars(statement))


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.get(Customer, customer_id)


def get_employee(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.get(Vehicle, vehicle_id)


def get_cash_session(
    db: Session,
    cash_session_id: int,
    *,
    for_update: bool = False,
) -> CashSession | None:
    statement = select(CashSession).where(CashSession.id == cash_session_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def _sheet_options():
    return (
        joinedload(SimpleRouteSheet.employee),
        joinedload(SimpleRouteSheet.vehicle),
        joinedload(SimpleRouteSheet.cash_session),
        selectinload(SimpleRouteSheet.trips).selectinload(SimpleRouteTrip.items),
        selectinload(SimpleRouteSheet.sales).selectinload(SimpleRouteSale.items),
        selectinload(SimpleRouteSheet.sales).selectinload(
            SimpleRouteSale.linked_collections
        ),
        selectinload(SimpleRouteSheet.collections),
        selectinload(SimpleRouteSheet.expenses),
        selectinload(SimpleRouteSheet.audit_logs),
        joinedload(SimpleRouteSheet.cash_receipt),
    )

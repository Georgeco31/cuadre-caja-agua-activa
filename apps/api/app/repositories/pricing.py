from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.price_list import PriceList
from app.models.price_list_item import PriceListItem
from app.models.route_load import RouteLoad


def get_price_list(db: Session, price_list_id: int) -> PriceList | None:
    statement = (
        select(PriceList)
        .options(*_price_list_options())
        .where(PriceList.id == price_list_id)
    )
    return db.scalar(statement)


def list_price_lists(
    db: Session,
    search: str | None = None,
    list_type: str | None = None,
    customer_id: int | None = None,
    route_id: int | None = None,
    is_active: bool | None = None,
) -> list[PriceList]:
    statement = select(PriceList).options(*_price_list_options())
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                PriceList.name.ilike(search_pattern),
                PriceList.notes.ilike(search_pattern),
            )
        )
    if list_type is not None:
        statement = statement.where(PriceList.list_type == list_type)
    if customer_id is not None:
        statement = statement.where(PriceList.customer_id == customer_id)
    if route_id is not None:
        statement = statement.where(PriceList.route_id == route_id)
    if is_active is not None:
        statement = statement.where(PriceList.is_active == is_active)
    statement = statement.order_by(
        PriceList.is_active.desc(),
        PriceList.priority.desc(),
        func.lower(PriceList.name),
        PriceList.id.desc(),
    )
    return list(db.scalars(statement))


def create_price_list(db: Session, values: dict[str, object]) -> PriceList:
    price_list = PriceList(**values)
    db.add(price_list)
    return price_list


def update_price_list(
    db: Session,
    price_list: PriceList,
    values: dict[str, object],
) -> PriceList:
    for field_name, value in values.items():
        setattr(price_list, field_name, value)
    db.add(price_list)
    return price_list


def get_price_list_item(db: Session, item_id: int) -> PriceListItem | None:
    statement = (
        select(PriceListItem)
        .options(joinedload(PriceListItem.product))
        .where(PriceListItem.id == item_id)
    )
    return db.scalar(statement)


def create_price_list_item(
    db: Session,
    values: dict[str, object],
) -> PriceListItem:
    item = PriceListItem(**values)
    db.add(item)
    return item


def update_price_list_item(
    db: Session,
    item: PriceListItem,
    values: dict[str, object],
) -> PriceListItem:
    for field_name, value in values.items():
        setattr(item, field_name, value)
    db.add(item)
    return item


def get_route_load(db: Session, route_load_id: int) -> RouteLoad | None:
    return db.get(RouteLoad, route_load_id)


def find_applicable_price(
    db: Session,
    product_id: int,
    customer_id: int | None,
    route_id: int | None,
    quantity: Decimal,
    price_date: date,
) -> tuple[PriceListItem, PriceList] | None:
    applicability = [
        PriceList.list_type.in_(("general", "special")),
    ]
    if customer_id is not None:
        applicability.append(
            (PriceList.list_type == "customer")
            & (PriceList.customer_id == customer_id)
        )
    if route_id is not None:
        applicability.append(
            (PriceList.list_type == "route") & (PriceList.route_id == route_id)
        )
    if customer_id is not None and route_id is not None:
        applicability.append(
            (PriceList.list_type == "customer_route")
            & (PriceList.customer_id == customer_id)
            & (PriceList.route_id == route_id)
        )

    specificity = case(
        (PriceList.list_type == "customer_route", 4),
        (PriceList.list_type == "customer", 3),
        (PriceList.list_type == "route", 2),
        else_=1,
    )
    statement = (
        select(PriceListItem, PriceList)
        .join(PriceList, PriceList.id == PriceListItem.price_list_id)
        .where(
            PriceListItem.product_id == product_id,
            PriceListItem.is_active.is_(True),
            PriceListItem.min_quantity <= quantity,
            PriceList.is_active.is_(True),
            or_(PriceList.valid_from.is_(None), PriceList.valid_from <= price_date),
            or_(PriceList.valid_to.is_(None), PriceList.valid_to >= price_date),
            or_(*applicability),
        )
        .order_by(
            specificity.desc(),
            PriceList.priority.desc(),
            PriceList.created_at.desc(),
            PriceList.id.desc(),
            PriceListItem.min_quantity.desc(),
            PriceListItem.created_at.desc(),
            PriceListItem.id.desc(),
        )
        .limit(1)
    )
    row = db.execute(statement).first()
    if row is None:
        return None
    return row[0], row[1]


def _price_list_options():
    return (
        joinedload(PriceList.customer),
        joinedload(PriceList.route),
        selectinload(PriceList.items).joinedload(PriceListItem.product),
    )

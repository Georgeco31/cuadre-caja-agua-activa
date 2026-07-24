from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories import customers, delivery_routes, products
from app.repositories import pricing as pricing_repository
from app.schemas.pricing import (
    PriceListCreate,
    PriceListItemCreate,
    PriceListItemUpdate,
    PriceListType,
    PriceListUpdate,
    PriceResolution,
)

PRICE_NOTES = {
    "customer_route": "Precio aplicado por lista de cliente y ruta",
    "customer": "Precio aplicado por lista de cliente",
    "route": "Precio aplicado por lista de ruta",
    "general": "Precio aplicado por lista general",
    "special": "Precio aplicado por lista especial",
}


def create_price_list(db: Session, payload: PriceListCreate):
    values = payload.model_dump()
    _validate_price_list_values(db, values)
    price_list = pricing_repository.create_price_list(db, values)
    db.commit()
    return _get_price_list_or_fail(db, price_list.id)


def list_price_lists(
    db: Session,
    search: str | None = None,
    list_type: PriceListType | None = None,
    customer_id: int | None = None,
    route_id: int | None = None,
    is_active: bool | None = None,
):
    return pricing_repository.list_price_lists(
        db=db,
        search=_normalize_filter(search),
        list_type=list_type,
        customer_id=customer_id,
        route_id=route_id,
        is_active=is_active,
    )


def get_price_list(db: Session, price_list_id: int):
    return _get_price_list_or_fail(db, price_list_id)


def update_price_list(
    db: Session,
    price_list_id: int,
    payload: PriceListUpdate,
):
    price_list = _get_price_list_or_fail(db, price_list_id)
    values = payload.model_dump(exclude_unset=True)
    merged_values = {
        "list_type": price_list.list_type,
        "customer_id": price_list.customer_id,
        "route_id": price_list.route_id,
        "valid_from": price_list.valid_from,
        "valid_to": price_list.valid_to,
        **values,
    }
    _validate_price_list_values(db, merged_values)
    pricing_repository.update_price_list(db, price_list, values)
    db.commit()
    return _get_price_list_or_fail(db, price_list.id)


def set_price_list_active(db: Session, price_list_id: int, is_active: bool):
    price_list = _get_price_list_or_fail(db, price_list_id)
    pricing_repository.update_price_list(
        db,
        price_list,
        {"is_active": is_active},
    )
    db.commit()
    return _get_price_list_or_fail(db, price_list.id)


def create_price_list_item(
    db: Session,
    price_list_id: int,
    payload: PriceListItemCreate,
):
    _get_price_list_or_fail(db, price_list_id)
    product = _get_active_product_or_fail(db, payload.product_id)
    values = payload.model_dump()
    values["price_list_id"] = price_list_id
    values["product_id"] = product.id
    item = pricing_repository.create_price_list_item(db, values)
    db.commit()
    return _get_price_list_item_or_fail(db, item.id)


def update_price_list_item(
    db: Session,
    item_id: int,
    payload: PriceListItemUpdate,
):
    item = _get_price_list_item_or_fail(db, item_id)
    values = payload.model_dump(exclude_unset=True)
    if "product_id" in values:
        _get_active_product_or_fail(db, values["product_id"])
    pricing_repository.update_price_list_item(db, item, values)
    db.commit()
    return _get_price_list_item_or_fail(db, item.id)


def set_price_list_item_active(db: Session, item_id: int, is_active: bool):
    item = _get_price_list_item_or_fail(db, item_id)
    if is_active:
        _get_active_product_or_fail(db, item.product_id)
    pricing_repository.update_price_list_item(
        db,
        item,
        {"is_active": is_active},
    )
    db.commit()
    return _get_price_list_item_or_fail(db, item.id)


def resolve_price(
    db: Session,
    product_id: int,
    customer_id: int | None = None,
    route_id: int | None = None,
    route_load_id: int | None = None,
    quantity: Decimal = Decimal("1"),
    price_date: date | None = None,
) -> PriceResolution:
    product = _get_active_product_or_fail(db, product_id)
    if customer_id is not None and customers.get_customer(db, customer_id) is None:
        raise ValueError("El cliente no existe.")
    if route_load_id is not None:
        route_load = pricing_repository.get_route_load(db, route_load_id)
        if route_load is None:
            raise ValueError("La carga de ruta no existe.")
        route_id = route_load.route_id
    elif (
        route_id is not None
        and delivery_routes.get_delivery_route(db, route_id) is None
    ):
        raise ValueError("La ruta no existe.")

    applicable = pricing_repository.find_applicable_price(
        db=db,
        product_id=product.id,
        customer_id=customer_id,
        route_id=route_id,
        quantity=quantity,
        price_date=price_date or date.today(),
    )
    if applicable is None:
        return PriceResolution(
            product_id=product.id,
            default_price=product.default_price,
            resolved_price=product.default_price,
            price_source="default",
            price_list_id=None,
            price_list_name=None,
            pricing_note="Precio normal del producto",
        )

    item, price_list = applicable
    return PriceResolution(
        product_id=product.id,
        default_price=product.default_price,
        resolved_price=item.unit_price,
        price_source=price_list.list_type,
        price_list_id=price_list.id,
        price_list_name=price_list.name,
        pricing_note=PRICE_NOTES[price_list.list_type],
    )


def _get_price_list_or_fail(db: Session, price_list_id: int):
    price_list = pricing_repository.get_price_list(db, price_list_id)
    if price_list is None:
        raise ValueError("La lista de precios no existe.")
    return price_list


def _get_price_list_item_or_fail(db: Session, item_id: int):
    item = pricing_repository.get_price_list_item(db, item_id)
    if item is None:
        raise ValueError("El item de la lista de precios no existe.")
    return item


def _get_active_product_or_fail(db: Session, product_id: int):
    product = products.get_product(db, product_id)
    if product is None:
        raise ValueError("El producto no existe.")
    if not product.is_active:
        raise ValueError(f"El producto {product.name} esta inactivo.")
    return product


def _validate_price_list_values(
    db: Session,
    values: dict[str, object],
) -> None:
    list_type = values["list_type"]
    customer_id = values.get("customer_id")
    route_id = values.get("route_id")
    if list_type == "customer" and customer_id is None:
        raise ValueError("Una lista por cliente requiere customer_id.")
    if list_type == "route" and route_id is None:
        raise ValueError("Una lista por ruta requiere route_id.")
    if list_type == "customer_route" and (
        customer_id is None or route_id is None
    ):
        raise ValueError(
            "Una lista por cliente y ruta requiere customer_id y route_id."
        )
    if (
        customer_id is not None
        and customers.get_customer(db, int(customer_id)) is None
    ):
        raise ValueError("El cliente no existe.")
    if (
        route_id is not None
        and delivery_routes.get_delivery_route(db, int(route_id)) is None
    ):
        raise ValueError("La ruta no existe.")
    valid_from = values.get("valid_from")
    valid_to = values.get("valid_to")
    if valid_from is not None and valid_to is not None and valid_from > valid_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

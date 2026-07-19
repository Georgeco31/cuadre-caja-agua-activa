from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory_location import InventoryLocation
from app.models.product import Product
from app.models.route_load_item import RouteLoadItem
from app.models.route_return import RouteReturn
from app.repositories import inventory as inventory_repository
from app.repositories import route_loads as route_loads_repository
from app.repositories import route_returns as route_returns_repository
from app.schemas.inventory import InventoryMovementCreate
from app.schemas.route_return import RouteReturnCreate
from app.services import inventory as inventory_service

QUANTITY_QUANTUM = Decimal("0.001")


def create_route_return(
    db: Session,
    payload: RouteReturnCreate,
    created_by: int,
) -> RouteReturn:
    route_load = route_loads_repository.get_route_load_for_update(
        db,
        payload.route_load_id,
    )
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")
    if route_load.status != "active":
        raise ValueError("No se puede registrar un retorno sobre una carga anulada.")
    if route_returns_repository.has_active_return_for_load(db, route_load.id):
        raise ValueError("La carga ya tiene un retorno activo.")

    locations = _get_locations_for_update(
        db,
        route_load.destination_location_id,
        payload.destination_location_id,
    )
    source_location = locations.get(route_load.destination_location_id)
    destination_location = locations.get(payload.destination_location_id)
    if source_location is None:
        raise ValueError("La ubicacion de origen del vehiculo no existe.")
    if destination_location is None:
        raise ValueError("La ubicacion de destino no existe.")
    if not source_location.is_active:
        raise ValueError("La ubicacion de origen del vehiculo esta inactiva.")
    if not destination_location.is_active:
        raise ValueError("La ubicacion de destino esta inactiva.")
    if source_location.id == destination_location.id:
        raise ValueError("Las ubicaciones de origen y destino deben ser distintas.")
    if destination_location.location_type == "vehicle":
        raise ValueError("La ubicacion de destino no puede ser de tipo vehiculo.")

    load_items = {item.id: item for item in route_load.items}
    selected_load_items = _validate_return_items(payload, load_items)
    products = _get_products_for_update(
        db,
        [item.product_id for item in selected_load_items],
    )
    route_return = route_returns_repository.create_route_return(
        db,
        {
            "return_number": f"PENDING-{uuid4().hex}",
            "return_date": payload.return_date,
            "route_load_id": route_load.id,
            "route_id": route_load.route_id,
            "vehicle_id": route_load.vehicle_id,
            "source_location_id": source_location.id,
            "destination_location_id": destination_location.id,
            "status": "active",
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        route_return.return_number = (
            f"RETURN-{route_return.return_date:%Y%m%d}-{route_return.id:04d}"
        )
        reason = f"Retorno de ruta {route_return.return_number}"
        for payload_item in payload.items:
            load_item = load_items[payload_item.route_load_item_id]
            product = products[load_item.product_id]
            quantity = payload_item.quantity_returned.quantize(QUANTITY_QUANTUM)
            source_movement = inventory_service.create_movement_in_transaction(
                db,
                InventoryMovementCreate(
                    movement_date=payload.return_date,
                    movement_type="exit",
                    product_id=product.id,
                    location_id=source_location.id,
                    quantity=quantity,
                    unit_cost=product.cost_estimate,
                    reason=reason,
                ),
                created_by,
            )
            db.flush()
            destination_movement = inventory_service.create_movement_in_transaction(
                db,
                InventoryMovementCreate(
                    movement_date=payload.return_date,
                    movement_type="entry",
                    product_id=product.id,
                    location_id=destination_location.id,
                    quantity=quantity,
                    unit_cost=product.cost_estimate,
                    reason=reason,
                ),
                created_by,
            )
            db.flush()
            route_returns_repository.create_route_return_item(
                db,
                {
                    "route_return_id": route_return.id,
                    "route_load_item_id": load_item.id,
                    "product_id": product.id,
                    "product_sku_snapshot": product.sku,
                    "product_name_snapshot": product.name,
                    "product_presentation_snapshot": product.presentation,
                    "quantity_returned": quantity,
                    "source_exit_movement_id": source_movement.id,
                    "destination_entry_movement_id": destination_movement.id,
                },
            )
            db.flush()
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar el retorno de ruta.") from error
    except Exception:
        db.rollback()
        raise

    created_return = route_returns_repository.get_route_return(db, route_return.id)
    if created_return is None:
        raise RuntimeError("El retorno registrado no pudo recuperarse.")
    return created_return


def list_route_returns(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    route_load_id: int | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[RouteReturn]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return route_returns_repository.list_route_returns(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        route_id=route_id,
        vehicle_id=vehicle_id,
        route_load_id=route_load_id,
        product_id=product_id,
        search=_normalize_filter(search),
    )


def get_route_return(db: Session, return_id: int) -> RouteReturn:
    route_return = route_returns_repository.get_route_return(db, return_id)
    if route_return is None:
        raise ValueError("El retorno de ruta no existe.")
    return route_return


def void_route_return(
    db: Session,
    return_id: int,
    reason: str,
) -> RouteReturn:
    route_return = route_returns_repository.get_route_return_for_update(db, return_id)
    if route_return is None:
        raise ValueError("El retorno de ruta no existe.")
    if route_return.status == "voided":
        raise ValueError("El retorno de ruta ya esta anulado.")

    voided_at = datetime.now(timezone.utc)
    movement_reason = (
        f"Retorno de ruta anulado {route_return.return_number}: {reason}"
    )
    try:
        for item in route_return.items:
            inventory_service.void_movement_in_transaction(
                db,
                item.destination_entry_movement_id,
                movement_reason,
                voided_at=voided_at,
                allow_route_return=True,
            )
            db.flush()
            inventory_service.void_movement_in_transaction(
                db,
                item.source_exit_movement_id,
                movement_reason,
                voided_at=voided_at,
                allow_route_return=True,
            )
            db.flush()
        route_returns_repository.mark_route_return_voided(
            db,
            route_return,
            reason,
            voided_at,
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular el retorno de ruta.") from error
    except Exception:
        db.rollback()
        raise

    voided_return = route_returns_repository.get_route_return(db, return_id)
    if voided_return is None:
        raise RuntimeError("El retorno anulado no pudo recuperarse.")
    return voided_return


def _validate_return_items(
    payload: RouteReturnCreate,
    load_items: dict[int, RouteLoadItem],
) -> list[RouteLoadItem]:
    selected_items: list[RouteLoadItem] = []
    for payload_item in payload.items:
        load_item = load_items.get(payload_item.route_load_item_id)
        if load_item is None:
            raise ValueError(
                "El producto seleccionado no pertenece a la carga indicada.",
            )
        quantity = payload_item.quantity_returned.quantize(QUANTITY_QUANTUM)
        if quantity > load_item.quantity_loaded:
            raise ValueError(
                f"La cantidad devuelta de {load_item.product_name_snapshot} "
                "no puede superar la cantidad cargada.",
            )
        selected_items.append(load_item)
    return selected_items


def _get_locations_for_update(
    db: Session,
    source_location_id: int,
    destination_location_id: int,
) -> dict[int, InventoryLocation]:
    locations: dict[int, InventoryLocation] = {}
    for location_id in sorted({source_location_id, destination_location_id}):
        location = inventory_repository.get_location(db, location_id, for_update=True)
        if location is not None:
            locations[location_id] = location
    return locations


def _get_products_for_update(
    db: Session,
    product_ids: list[int],
) -> dict[int, Product]:
    products: dict[int, Product] = {}
    for product_id in sorted(set(product_ids)):
        product = inventory_repository.get_product(db, product_id, for_update=True)
        if product is None:
            raise ValueError(f"El producto {product_id} no existe.")
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")
        products[product_id] = product
    return products


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

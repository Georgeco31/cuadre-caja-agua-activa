from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory_location import InventoryLocation
from app.models.product import Product
from app.models.route_load import RouteLoad
from app.repositories import inventory as inventory_repository
from app.repositories import route_loads as route_loads_repository
from app.repositories import route_returns as route_returns_repository
from app.schemas.inventory import InventoryMovementCreate
from app.schemas.route_load import RouteLoadCreate
from app.services import inventory as inventory_service

QUANTITY_QUANTUM = Decimal("0.001")


def create_route_load(
    db: Session,
    payload: RouteLoadCreate,
    created_by: int,
) -> RouteLoad:
    delivery_route = route_loads_repository.get_delivery_route_for_update(
        db,
        payload.route_id,
    )
    if delivery_route is None:
        raise ValueError("La ruta no existe.")
    if not delivery_route.is_active:
        raise ValueError("No se puede cargar una ruta inactiva.")

    vehicle = route_loads_repository.get_vehicle_for_update(db, payload.vehicle_id)
    if vehicle is None:
        raise ValueError("El vehiculo no existe.")
    if not vehicle.is_active:
        raise ValueError("No se puede cargar un vehiculo inactivo.")

    locations = _get_locations_for_update(
        db,
        payload.source_location_id,
        payload.destination_location_id,
    )
    source_location = locations.get(payload.source_location_id)
    destination_location = locations.get(payload.destination_location_id)
    if source_location is None:
        raise ValueError("La ubicacion de origen no existe.")
    if destination_location is None:
        raise ValueError("La ubicacion de destino no existe.")
    if not source_location.is_active:
        raise ValueError("La ubicacion de origen esta inactiva.")
    if not destination_location.is_active:
        raise ValueError("La ubicacion de destino esta inactiva.")
    if source_location.id == destination_location.id:
        raise ValueError("Las ubicaciones de origen y destino deben ser distintas.")
    if destination_location.location_type != "vehicle":
        raise ValueError("La ubicacion de destino debe ser de tipo vehiculo.")
    if (
        destination_location.vehicle_id is not None
        and destination_location.vehicle_id != vehicle.id
    ):
        raise ValueError(
            "La ubicacion de destino no corresponde al vehiculo seleccionado.",
        )

    products = _get_products_for_update(
        db,
        [item.product_id for item in payload.items],
    )
    route_load = route_loads_repository.create_route_load(
        db,
        {
            "load_number": f"PENDING-{uuid4().hex}",
            "load_date": payload.load_date,
            "route_id": delivery_route.id,
            "vehicle_id": vehicle.id,
            "source_location_id": source_location.id,
            "destination_location_id": destination_location.id,
            "status": "active",
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        route_load.load_number = (
            f"LOAD-{route_load.load_date:%Y%m%d}-{route_load.id:04d}"
        )
        reason = f"Carga de ruta {route_load.load_number}"
        for payload_item in payload.items:
            product = products[payload_item.product_id]
            quantity = payload_item.quantity_loaded.quantize(QUANTITY_QUANTUM)
            source_movement = inventory_service.create_movement_in_transaction(
                db,
                InventoryMovementCreate(
                    movement_date=payload.load_date,
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
                    movement_date=payload.load_date,
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
            route_loads_repository.create_route_load_item(
                db,
                {
                    "route_load_id": route_load.id,
                    "product_id": product.id,
                    "product_sku_snapshot": product.sku,
                    "product_name_snapshot": product.name,
                    "product_presentation_snapshot": product.presentation,
                    "quantity_loaded": quantity,
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
        raise ValueError("No se pudo registrar la carga de ruta.") from error
    except Exception:
        db.rollback()
        raise

    created_load = route_loads_repository.get_route_load(db, route_load.id)
    if created_load is None:
        raise RuntimeError("La carga registrada no pudo recuperarse.")
    return created_load


def list_route_loads(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[RouteLoad]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return route_loads_repository.list_route_loads(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        route_id=route_id,
        vehicle_id=vehicle_id,
        product_id=product_id,
        search=_normalize_filter(search),
    )


def get_route_load(db: Session, load_id: int) -> RouteLoad:
    route_load = route_loads_repository.get_route_load(db, load_id)
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")
    return route_load


def void_route_load(
    db: Session,
    load_id: int,
    reason: str,
) -> RouteLoad:
    route_load = route_loads_repository.get_route_load_for_update(db, load_id)
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")
    if route_load.status == "voided":
        raise ValueError("La carga de ruta ya esta anulada.")
    if route_returns_repository.has_active_return_for_load(db, route_load.id):
        raise ValueError(
            "Primero anule el retorno de ruta antes de anular la carga.",
        )

    voided_at = datetime.now(timezone.utc)
    movement_reason = f"Carga de ruta anulada {route_load.load_number}: {reason}"
    try:
        for item in route_load.items:
            inventory_service.void_movement_in_transaction(
                db,
                item.destination_entry_movement_id,
                movement_reason,
                voided_at=voided_at,
                allow_route_load=True,
            )
            db.flush()
            inventory_service.void_movement_in_transaction(
                db,
                item.source_exit_movement_id,
                movement_reason,
                voided_at=voided_at,
                allow_route_load=True,
            )
            db.flush()
        route_loads_repository.mark_route_load_voided(
            db,
            route_load,
            reason,
            voided_at,
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular la carga de ruta.") from error
    except Exception:
        db.rollback()
        raise

    voided_load = route_loads_repository.get_route_load(db, load_id)
    if voided_load is None:
        raise RuntimeError("La carga anulada no pudo recuperarse.")
    return voided_load


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

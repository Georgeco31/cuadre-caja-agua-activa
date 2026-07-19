from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.production_inventory_application import (
    ProductionInventoryApplication,
)
from app.models.production_item import ProductionItem
from app.repositories import inventory as inventory_repository
from app.repositories import production as production_repository
from app.repositories import production_inventory as application_repository
from app.schemas.inventory import InventoryMovementCreate
from app.schemas.production_inventory import (
    ProductionInventoryApplicationItemRead,
    ProductionInventoryApplicationRead,
    ProductionInventoryApply,
)
from app.services import inventory as inventory_service

QUANTITY_QUANTUM = Decimal("0.001")


def apply_production_to_inventory(
    db: Session,
    batch_id: int,
    payload: ProductionInventoryApply,
    created_by: int,
) -> ProductionInventoryApplicationRead:
    batch = production_repository.get_production_batch_for_update(db, batch_id)
    if batch is None:
        raise ValueError("La produccion no existe.")
    if batch.status != "active":
        raise ValueError("No se puede aplicar una produccion anulada.")
    if application_repository.get_active_application_for_batch(db, batch.id):
        raise ValueError("La produccion ya tiene una aplicacion activa.")

    location = inventory_repository.get_location(
        db,
        payload.location_id,
        for_update=True,
    )
    if location is None:
        raise ValueError("La ubicacion de inventario no existe.")
    if not location.is_active:
        raise ValueError("No se puede aplicar a una ubicacion inactiva.")

    applicable_items: list[tuple[ProductionItem, Decimal]] = []
    for item in batch.items:
        quantity_produced = item.quantity_produced.quantize(QUANTITY_QUANTUM)
        quantity_waste = item.quantity_waste.quantize(QUANTITY_QUANTUM)
        if quantity_waste > quantity_produced:
            raise ValueError(
                "La merma no puede ser mayor que la cantidad producida.",
            )
        quantity_to_inventory = (
            quantity_produced - quantity_waste
        ).quantize(QUANTITY_QUANTUM)
        if quantity_to_inventory > 0:
            applicable_items.append((item, quantity_to_inventory))
    if not applicable_items:
        raise ValueError("La produccion no tiene cantidad neta para inventario.")

    applied_at = datetime.now(timezone.utc)
    application = application_repository.create_application(
        db,
        {
            "production_batch_id": batch.id,
            "location_id": location.id,
            "status": "active",
            "applied_at": applied_at,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        for production_item, quantity_to_inventory in applicable_items:
            product = inventory_repository.get_product(
                db,
                production_item.product_id,
                for_update=True,
            )
            if product is None:
                raise ValueError("El producto no existe.")
            movement = inventory_service.create_movement_in_transaction(
                db,
                InventoryMovementCreate(
                    movement_date=payload.movement_date,
                    movement_type="entry",
                    product_id=production_item.product_id,
                    location_id=location.id,
                    quantity=quantity_to_inventory,
                    unit_cost=product.cost_estimate,
                    reason=_build_movement_reason(
                        batch.production_number,
                        payload.notes,
                    ),
                ),
                created_by,
            )
            db.flush()
            application_repository.create_application_item(
                db,
                {
                    "application_id": application.id,
                    "production_item_id": production_item.id,
                    "product_id": production_item.product_id,
                    "inventory_movement_id": movement.id,
                    "quantity_applied": quantity_to_inventory,
                },
            )
            db.flush()
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "La produccion ya tiene una aplicacion activa.",
        ) from error
    except Exception:
        db.rollback()
        raise

    return get_inventory_application(db, batch.id)


def get_inventory_application(
    db: Session,
    batch_id: int,
) -> ProductionInventoryApplicationRead:
    batch = production_repository.get_production_batch(db, batch_id)
    if batch is None:
        raise ValueError("La produccion no existe.")
    application = application_repository.get_active_application_for_batch(
        db,
        batch.id,
    )
    if application is not None:
        return _build_application_read(batch.id, application, "applied")
    latest_application = application_repository.get_latest_application_for_batch(
        db,
        batch.id,
    )
    if latest_application is not None:
        return _build_application_read(batch.id, latest_application, "voided")
    return _build_application_read(batch.id, None, "not_applied")


def void_inventory_application(
    db: Session,
    application_id: int,
    reason: str,
) -> ProductionInventoryApplicationRead:
    application = application_repository.get_application_for_update(
        db,
        application_id,
    )
    if application is None:
        raise ValueError("La aplicacion a inventario no existe.")
    if application.status == "voided":
        raise ValueError("La aplicacion a inventario ya esta anulada.")

    production_batch_id = application.production_batch_id
    voided_at = datetime.now(timezone.utc)
    try:
        for item in application.items:
            inventory_service.void_movement_in_transaction(
                db,
                item.inventory_movement_id,
                f"Aplicacion de produccion anulada: {reason}",
                voided_at=voided_at,
                allow_production_application=True,
            )
            db.flush()
        application_repository.mark_application_voided(
            db,
            application,
            reason,
            voided_at,
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se pudo anular la aplicacion a inventario.",
        ) from error
    except Exception:
        db.rollback()
        raise

    return get_inventory_application(db, production_batch_id)


def _build_application_read(
    batch_id: int,
    application: ProductionInventoryApplication | None,
    state: str,
) -> ProductionInventoryApplicationRead:
    if application is None:
        return ProductionInventoryApplicationRead(
            state="not_applied",
            application_id=None,
            production_batch_id=batch_id,
            location_id=None,
            location_name=None,
            status=None,
            applied_at=None,
            void_reason=None,
            voided_at=None,
            created_by=None,
            created_at=None,
            updated_at=None,
            items=[],
        )
    return ProductionInventoryApplicationRead(
        state=state,
        application_id=application.id,
        production_batch_id=batch_id,
        location_id=application.location_id,
        location_name=application.location_name,
        status=application.status,
        applied_at=application.applied_at,
        void_reason=application.void_reason,
        voided_at=application.voided_at,
        created_by=application.created_by,
        created_at=application.created_at,
        updated_at=application.updated_at,
        items=[
            ProductionInventoryApplicationItemRead(
                id=item.id,
                application_id=item.application_id,
                production_item_id=item.production_item_id,
                product_id=item.product_id,
                inventory_movement_id=item.inventory_movement_id,
                movement_date=item.inventory_movement.movement_date,
                quantity_applied=item.quantity_applied,
                created_at=item.created_at,
            )
            for item in application.items
        ],
    )


def _build_movement_reason(
    production_number: str,
    notes: str | None,
) -> str:
    reason = f"Produccion {production_number}"
    return f"{reason} - {notes}" if notes is not None else reason

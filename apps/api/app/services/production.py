from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.production_batch import ProductionBatch
from app.repositories import products
from app.repositories import production as production_repository
from app.repositories import production_inventory as application_repository
from app.repositories import (
    production_material_consumptions as material_consumption_repository,
)
from app.schemas.production import ProductionBatchCreate, ProductionItemCreate


def create_production_batch(
    db: Session,
    payload: ProductionBatchCreate,
    created_by: int,
) -> ProductionBatch:
    item_values = _build_production_items(db, payload.items)
    batch = production_repository.create_production_batch(
        db,
        {
            "production_number": f"PENDING-{uuid4().hex}",
            "production_date": payload.production_date,
            "status": "active",
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        batch.production_number = (
            f"PROD-{batch.production_date:%Y%m%d}-{batch.id:04d}"
        )
        for values in item_values:
            production_repository.create_production_item(
                db,
                {"production_batch_id": batch.id, **values},
            )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar la produccion.") from error

    created_batch = production_repository.get_production_batch(db, batch.id)
    if created_batch is None:
        raise RuntimeError("La produccion registrada no pudo recuperarse.")
    return created_batch


def list_production_batches(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[ProductionBatch]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return production_repository.list_production_batches(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        product_id=product_id,
        search=_normalize_filter(search),
    )


def get_production_batch(db: Session, batch_id: int) -> ProductionBatch:
    batch = production_repository.get_production_batch(db, batch_id)
    if batch is None:
        raise ValueError("La produccion no existe.")
    return batch


def void_production_batch(
    db: Session,
    batch_id: int,
    reason: str,
) -> ProductionBatch:
    batch = production_repository.get_production_batch_for_update(db, batch_id)
    if batch is None:
        raise ValueError("La produccion no existe.")
    if batch.status == "voided":
        raise ValueError("La produccion ya esta anulada.")
    if application_repository.get_active_application_for_batch(db, batch.id):
        raise ValueError(
            "Primero anule la aplicacion a inventario antes de anular la produccion.",
        )
    if material_consumption_repository.get_active_consumption_for_batch(
        db,
        batch.id,
    ):
        raise ValueError(
            "Primero anule el consumo de insumos antes de anular la produccion.",
        )

    production_repository.mark_production_batch_voided(
        db,
        batch,
        reason,
        datetime.now(timezone.utc),
    )
    db.commit()
    voided_batch = production_repository.get_production_batch(db, batch.id)
    if voided_batch is None:
        raise RuntimeError("La produccion anulada no pudo recuperarse.")
    return voided_batch


def _build_production_items(
    db: Session,
    items: list[ProductionItemCreate],
) -> list[dict[str, object]]:
    item_values: list[dict[str, object]] = []
    for item in items:
        product = products.get_product(db, item.product_id)
        if product is None:
            raise ValueError(f"El producto {item.product_id} no existe.")
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")
        item_values.append(
            {
                "product_id": product.id,
                "product_sku_snapshot": product.sku,
                "product_name_snapshot": product.name,
                "product_presentation_snapshot": product.presentation,
                "quantity_produced": item.quantity_produced,
                "quantity_waste": item.quantity_waste,
                "notes": item.notes,
            },
        )
    return item_values


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.inventory_location import InventoryLocation
from app.models.production_batch import ProductionBatch
from app.models.production_material_consumption import (
    ProductionMaterialConsumption,
)
from app.models.production_material_consumption_item import (
    ProductionMaterialConsumptionItem,
)


def get_active_consumption_for_batch(
    db: Session,
    production_batch_id: int,
    *,
    for_update: bool = False,
) -> ProductionMaterialConsumption | None:
    statement = (
        select(ProductionMaterialConsumption)
        .options(*_consumption_options())
        .where(
            ProductionMaterialConsumption.production_batch_id
            == production_batch_id,
            ProductionMaterialConsumption.status == "active",
        )
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_consumption(
    db: Session,
    consumption_id: int,
    *,
    for_update: bool = False,
) -> ProductionMaterialConsumption | None:
    statement = (
        select(ProductionMaterialConsumption)
        .options(*_consumption_options())
        .where(ProductionMaterialConsumption.id == consumption_id)
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_consumptions(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    production_batch_id: int | None = None,
    source_location_id: int | None = None,
    input_product_id: int | None = None,
    search: str | None = None,
) -> list[ProductionMaterialConsumption]:
    statement = select(ProductionMaterialConsumption).options(
        *_consumption_options(),
    )
    if date_from is not None:
        statement = statement.where(
            ProductionMaterialConsumption.movement_date >= date_from,
        )
    if date_to is not None:
        statement = statement.where(
            ProductionMaterialConsumption.movement_date <= date_to,
        )
    if status is not None:
        statement = statement.where(ProductionMaterialConsumption.status == status)
    if production_batch_id is not None:
        statement = statement.where(
            ProductionMaterialConsumption.production_batch_id
            == production_batch_id,
        )
    if source_location_id is not None:
        statement = statement.where(
            ProductionMaterialConsumption.source_location_id
            == source_location_id,
        )
    if input_product_id is not None:
        statement = statement.where(
            ProductionMaterialConsumption.items.any(
                ProductionMaterialConsumptionItem.input_product_id
                == input_product_id,
            ),
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = (
            statement.join(ProductionMaterialConsumption.production_batch)
            .join(ProductionMaterialConsumption.source_location)
            .where(
                or_(
                    ProductionMaterialConsumption.consumption_number.ilike(
                        search_pattern,
                    ),
                    ProductionBatch.production_number.ilike(search_pattern),
                    InventoryLocation.name.ilike(search_pattern),
                    ProductionMaterialConsumption.items.any(
                        ProductionMaterialConsumptionItem.input_product_name_snapshot.ilike(
                            search_pattern,
                        ),
                    ),
                ),
            )
        )
    statement = statement.order_by(
        ProductionMaterialConsumption.movement_date.desc(),
        ProductionMaterialConsumption.id.desc(),
    )
    return list(db.scalars(statement).unique())


def has_active_consumption_for_movement(
    db: Session,
    inventory_movement_id: int,
) -> bool:
    statement = (
        select(ProductionMaterialConsumptionItem.id)
        .join(ProductionMaterialConsumption)
        .where(
            ProductionMaterialConsumptionItem.inventory_movement_id
            == inventory_movement_id,
            ProductionMaterialConsumption.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def create_consumption(
    db: Session,
    values: dict[str, object],
) -> ProductionMaterialConsumption:
    consumption = ProductionMaterialConsumption(**values)
    db.add(consumption)
    return consumption


def create_consumption_item(
    db: Session,
    values: dict[str, object],
) -> ProductionMaterialConsumptionItem:
    item = ProductionMaterialConsumptionItem(**values)
    db.add(item)
    return item


def mark_consumption_voided(
    db: Session,
    consumption: ProductionMaterialConsumption,
    reason: str,
    voided_at: datetime,
) -> ProductionMaterialConsumption:
    consumption.status = "voided"
    consumption.void_reason = reason
    consumption.voided_at = voided_at
    db.add(consumption)
    return consumption


def _consumption_options():
    return (
        joinedload(
            ProductionMaterialConsumption.production_batch,
            innerjoin=True,
        ),
        joinedload(
            ProductionMaterialConsumption.source_location,
            innerjoin=True,
        ),
        selectinload(ProductionMaterialConsumption.items),
    )

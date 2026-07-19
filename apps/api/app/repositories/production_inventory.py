from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.production_inventory_application import (
    ProductionInventoryApplication,
)
from app.models.production_inventory_application_item import (
    ProductionInventoryApplicationItem,
)


def get_active_application_for_batch(
    db: Session,
    production_batch_id: int,
    *,
    for_update: bool = False,
) -> ProductionInventoryApplication | None:
    statement = (
        select(ProductionInventoryApplication)
        .options(
            joinedload(
                ProductionInventoryApplication.location,
                innerjoin=True,
            ),
            selectinload(ProductionInventoryApplication.items).joinedload(
                ProductionInventoryApplicationItem.inventory_movement,
            ),
        )
        .where(
            ProductionInventoryApplication.production_batch_id
            == production_batch_id,
            ProductionInventoryApplication.status == "active",
        )
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def get_latest_application_for_batch(
    db: Session,
    production_batch_id: int,
) -> ProductionInventoryApplication | None:
    statement = (
        select(ProductionInventoryApplication)
        .options(
            joinedload(
                ProductionInventoryApplication.location,
                innerjoin=True,
            ),
            selectinload(ProductionInventoryApplication.items).joinedload(
                ProductionInventoryApplicationItem.inventory_movement,
            ),
        )
        .where(
            ProductionInventoryApplication.production_batch_id
            == production_batch_id,
        )
        .order_by(ProductionInventoryApplication.id.desc())
        .limit(1)
    )
    return db.scalar(statement)


def get_application_for_update(
    db: Session,
    application_id: int,
) -> ProductionInventoryApplication | None:
    statement = (
        select(ProductionInventoryApplication)
        .options(
            joinedload(
                ProductionInventoryApplication.location,
                innerjoin=True,
            ),
            selectinload(ProductionInventoryApplication.items).joinedload(
                ProductionInventoryApplicationItem.inventory_movement,
            ),
        )
        .where(ProductionInventoryApplication.id == application_id)
        .with_for_update()
    )
    return db.scalar(statement)


def has_active_application_for_movement(
    db: Session,
    inventory_movement_id: int,
) -> bool:
    statement = (
        select(ProductionInventoryApplicationItem.id)
        .join(ProductionInventoryApplication)
        .where(
            ProductionInventoryApplicationItem.inventory_movement_id
            == inventory_movement_id,
            ProductionInventoryApplication.status == "active",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def create_application(
    db: Session,
    values: dict[str, object],
) -> ProductionInventoryApplication:
    application = ProductionInventoryApplication(**values)
    db.add(application)
    return application


def create_application_item(
    db: Session,
    values: dict[str, object],
) -> ProductionInventoryApplicationItem:
    item = ProductionInventoryApplicationItem(**values)
    db.add(item)
    return item


def mark_application_voided(
    db: Session,
    application: ProductionInventoryApplication,
    reason: str,
    voided_at: datetime,
) -> ProductionInventoryApplication:
    application.status = "voided"
    application.void_reason = reason
    application.voided_at = voided_at
    db.add(application)
    return application

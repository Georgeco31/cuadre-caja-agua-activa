from datetime import date, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.production_batch import ProductionBatch
from app.models.production_item import ProductionItem


def get_production_batch(
    db: Session,
    batch_id: int,
) -> ProductionBatch | None:
    statement = (
        select(ProductionBatch)
        .options(selectinload(ProductionBatch.items))
        .where(ProductionBatch.id == batch_id)
    )
    return db.scalar(statement)


def get_production_batch_for_update(
    db: Session,
    batch_id: int,
) -> ProductionBatch | None:
    statement = (
        select(ProductionBatch)
        .options(selectinload(ProductionBatch.items))
        .where(ProductionBatch.id == batch_id)
        .with_for_update()
    )
    return db.scalar(statement)


def list_production_batches(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[ProductionBatch]:
    statement = select(ProductionBatch).options(
        selectinload(ProductionBatch.items),
    )

    if date_from is not None:
        statement = statement.where(ProductionBatch.production_date >= date_from)
    if date_to is not None:
        statement = statement.where(ProductionBatch.production_date <= date_to)
    if status is not None:
        statement = statement.where(ProductionBatch.status == status)
    if product_id is not None:
        statement = statement.where(
            ProductionBatch.items.any(ProductionItem.product_id == product_id),
        )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                ProductionBatch.production_number.ilike(search_pattern),
                ProductionBatch.items.any(
                    or_(
                        ProductionItem.product_name_snapshot.ilike(search_pattern),
                        ProductionItem.product_sku_snapshot.ilike(search_pattern),
                        ProductionItem.product_presentation_snapshot.ilike(
                            search_pattern,
                        ),
                    ),
                ),
            ),
        )

    statement = statement.order_by(
        ProductionBatch.production_date.desc(),
        ProductionBatch.id.desc(),
    )
    return list(db.scalars(statement))


def create_production_batch(
    db: Session,
    values: dict[str, object],
) -> ProductionBatch:
    batch = ProductionBatch(**values)
    db.add(batch)
    return batch


def create_production_item(
    db: Session,
    values: dict[str, object],
) -> ProductionItem:
    item = ProductionItem(**values)
    db.add(item)
    return item


def mark_production_batch_voided(
    db: Session,
    batch: ProductionBatch,
    reason: str,
    voided_at: datetime,
) -> ProductionBatch:
    batch.status = "voided"
    batch.void_reason = reason
    batch.voided_at = voided_at
    db.add(batch)
    return batch

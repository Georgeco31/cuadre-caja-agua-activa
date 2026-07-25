from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories import products
from app.schemas.product import (
    ProductCreate,
    ProductProductionClassificationUpdate,
    ProductUpdate,
)


def create_product(db: Session, payload: ProductCreate) -> Product:
    if payload.sku is not None:
        _ensure_sku_is_available(db, payload.sku)

    product = products.create_product(db, payload.model_dump())
    _commit_product(db, product)
    return product


def list_products(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    category: str | None = None,
    unit: str | None = None,
    product_kind: str | None = None,
) -> list[Product]:
    return products.list_products(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        category=category,
        unit=unit,
        product_kind=product_kind,
    )


def get_product(db: Session, product_id: int) -> Product:
    product = products.get_product(db, product_id)
    if product is None:
        raise ValueError("El producto no existe.")
    return product


def update_product(
    db: Session,
    product_id: int,
    payload: ProductUpdate,
) -> Product:
    product = get_product(db, product_id)
    values = payload.model_dump(exclude_unset=True)

    if "sku" in values and values["sku"] is not None:
        _ensure_sku_is_available(
            db,
            str(values["sku"]),
            exclude_product_id=product.id,
        )

    products.update_product(db, product, values)
    _commit_product(db, product)
    return product


def deactivate_product(db: Session, product_id: int) -> Product:
    product = get_product(db, product_id)
    products.set_product_active(db, product, False)
    _commit_product(db, product)
    return product


def activate_product(db: Session, product_id: int) -> Product:
    product = get_product(db, product_id)
    products.set_product_active(db, product, True)
    _commit_product(db, product)
    return product


def update_production_classification(
    db: Session,
    product_id: int,
    payload: ProductProductionClassificationUpdate,
) -> Product:
    product = get_product(db, product_id)
    products.update_product(db, product, payload.model_dump(exclude_unset=True))
    _commit_product(db, product)
    return product


def _ensure_sku_is_available(
    db: Session,
    sku: str,
    exclude_product_id: int | None = None,
) -> None:
    existing_product = products.get_product_by_sku(
        db,
        sku,
        exclude_product_id=exclude_product_id,
    )
    if existing_product is not None:
        raise ValueError("El SKU ya esta registrado.")


def _commit_product(db: Session, product: Product) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("El SKU ya esta registrado.") from error
    db.refresh(product)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

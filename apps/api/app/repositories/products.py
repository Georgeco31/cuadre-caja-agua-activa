from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_product_by_sku(
    db: Session,
    sku: str,
    exclude_product_id: int | None = None,
) -> Product | None:
    statement = select(Product).where(Product.sku == sku)
    if exclude_product_id is not None:
        statement = statement.where(Product.id != exclude_product_id)
    return db.scalar(statement)


def list_products(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    category: str | None = None,
    unit: str | None = None,
    product_kind: str | None = None,
) -> list[Product]:
    statement = select(Product)

    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern),
                Product.category.ilike(search_pattern),
                Product.presentation.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(Product.is_active == is_active)
    if category is not None:
        statement = statement.where(Product.category == category)
    if unit is not None:
        statement = statement.where(Product.unit == unit)
    if product_kind is not None:
        statement = statement.where(Product.product_kind == product_kind)

    statement = statement.order_by(func.lower(Product.name), Product.id)
    return list(db.scalars(statement))


def create_product(db: Session, values: dict[str, object]) -> Product:
    product = Product(**values)
    db.add(product)
    return product


def update_product(
    db: Session,
    product: Product,
    values: dict[str, object],
) -> Product:
    for field_name, value in values.items():
        setattr(product, field_name, value)
    db.add(product)
    return product


def set_product_active(
    db: Session,
    product: Product,
    is_active: bool,
) -> Product:
    product.is_active = is_active
    db.add(product)
    return product

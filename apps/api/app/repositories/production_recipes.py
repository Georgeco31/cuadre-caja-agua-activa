from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.product import Product
from app.models.production_recipe import ProductionRecipe
from app.models.production_recipe_item import ProductionRecipeItem


def get_recipe(db: Session, recipe_id: int) -> ProductionRecipe | None:
    statement = (
        select(ProductionRecipe)
        .options(*_recipe_options())
        .where(ProductionRecipe.id == recipe_id)
    )
    return db.scalar(statement)


def get_recipe_for_update(
    db: Session,
    recipe_id: int,
) -> ProductionRecipe | None:
    statement = (
        select(ProductionRecipe)
        .options(*_recipe_options())
        .where(ProductionRecipe.id == recipe_id)
        .with_for_update()
    )
    return db.scalar(statement)


def list_recipes(
    db: Session,
    search: str | None = None,
    status: str | None = None,
    output_product_id: int | None = None,
    product_kind: str | None = None,
    is_valid_today: bool | None = None,
    today: date | None = None,
) -> list[ProductionRecipe]:
    statement = (
        select(ProductionRecipe)
        .join(ProductionRecipe.output_product)
        .options(*_recipe_options())
    )
    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                ProductionRecipe.recipe_number.ilike(search_pattern),
                ProductionRecipe.name.ilike(search_pattern),
                ProductionRecipe.notes.ilike(search_pattern),
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern),
            ),
        )
    if status is not None:
        statement = statement.where(ProductionRecipe.status == status)
    if output_product_id is not None:
        statement = statement.where(
            ProductionRecipe.output_product_id == output_product_id,
        )
    if product_kind is not None:
        statement = statement.where(Product.product_kind == product_kind)
    if is_valid_today is not None:
        current_date = today or date.today()
        valid_condition = (
            or_(
                ProductionRecipe.valid_from.is_(None),
                ProductionRecipe.valid_from <= current_date,
            )
            & or_(
                ProductionRecipe.valid_to.is_(None),
                ProductionRecipe.valid_to >= current_date,
            )
        )
        statement = statement.where(
            valid_condition if is_valid_today else ~valid_condition,
        )
    statement = statement.order_by(
        ProductionRecipe.created_at.desc(),
        ProductionRecipe.id.desc(),
    )
    return list(db.scalars(statement))


def create_recipe(
    db: Session,
    values: dict[str, object],
) -> ProductionRecipe:
    recipe = ProductionRecipe(**values)
    db.add(recipe)
    return recipe


def update_recipe(
    db: Session,
    recipe: ProductionRecipe,
    values: dict[str, object],
) -> ProductionRecipe:
    for field_name, value in values.items():
        setattr(recipe, field_name, value)
    db.add(recipe)
    return recipe


def mark_recipe_voided(
    db: Session,
    recipe: ProductionRecipe,
    reason: str,
    voided_at: datetime,
) -> ProductionRecipe:
    recipe.status = "voided"
    recipe.void_reason = reason
    recipe.voided_at = voided_at
    db.add(recipe)
    return recipe


def get_item(
    db: Session,
    item_id: int,
) -> ProductionRecipeItem | None:
    statement = (
        select(ProductionRecipeItem)
        .options(
            joinedload(ProductionRecipeItem.input_product),
            joinedload(ProductionRecipeItem.recipe).joinedload(
                ProductionRecipe.output_product,
            ),
        )
        .where(ProductionRecipeItem.id == item_id)
    )
    return db.scalar(statement)


def get_item_for_update(
    db: Session,
    item_id: int,
) -> ProductionRecipeItem | None:
    statement = (
        select(ProductionRecipeItem)
        .options(
            joinedload(ProductionRecipeItem.input_product),
            joinedload(ProductionRecipeItem.recipe).joinedload(
                ProductionRecipe.output_product,
            ),
        )
        .where(ProductionRecipeItem.id == item_id)
        .with_for_update()
    )
    return db.scalar(statement)


def create_item(
    db: Session,
    values: dict[str, object],
) -> ProductionRecipeItem:
    item = ProductionRecipeItem(**values)
    db.add(item)
    return item


def update_item(
    db: Session,
    item: ProductionRecipeItem,
    values: dict[str, object],
) -> ProductionRecipeItem:
    for field_name, value in values.items():
        setattr(item, field_name, value)
    db.add(item)
    return item


def get_active_items_total(db: Session, recipe_id: int) -> Decimal:
    statement = select(
        func.coalesce(func.sum(ProductionRecipeItem.total_cost), 0),
    ).where(
        ProductionRecipeItem.recipe_id == recipe_id,
        ProductionRecipeItem.is_active.is_(True),
    )
    return Decimal(db.scalar(statement) or 0)


def _recipe_options():
    return (
        joinedload(ProductionRecipe.output_product),
        selectinload(ProductionRecipe.items),
    )

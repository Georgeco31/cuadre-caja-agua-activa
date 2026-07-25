from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.production_recipe import ProductionRecipe
from app.models.production_recipe_item import ProductionRecipeItem
from app.repositories import products
from app.repositories import production_recipes as recipe_repository
from app.schemas.production_recipe import (
    ProductionRecipeCostEstimate,
    ProductionRecipeCostItem,
    ProductionRecipeCreate,
    ProductionRecipeItemCreate,
    ProductionRecipeItemUpdate,
    ProductionRecipeUpdate,
)

QUANTITY_QUANTUM = Decimal("0.001")
COST_QUANTUM = Decimal("0.0001")


def create_recipe(
    db: Session,
    payload: ProductionRecipeCreate,
    created_by: int,
) -> ProductionRecipe:
    output_product = _get_active_product_or_fail(db, payload.output_product_id)
    recipe = recipe_repository.create_recipe(
        db,
        {
            **payload.model_dump(),
            "output_product_id": output_product.id,
            "recipe_number": f"PENDING-{uuid4().hex}",
            "status": "inactive",
            "estimated_material_cost": Decimal("0.0000"),
            "estimated_cost_per_unit": Decimal("0.0000"),
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        recipe.recipe_number = f"REC-{date.today():%Y%m%d}-{recipe.id:04d}"
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar la formula de produccion.") from error
    return _get_recipe_or_fail(db, recipe.id)


def list_recipes(
    db: Session,
    search: str | None = None,
    status: str | None = None,
    output_product_id: int | None = None,
    product_kind: str | None = None,
    is_valid_today: bool | None = None,
) -> list[ProductionRecipe]:
    return recipe_repository.list_recipes(
        db=db,
        search=_normalize_filter(search),
        status=status,
        output_product_id=output_product_id,
        product_kind=product_kind,
        is_valid_today=is_valid_today,
    )


def get_recipe(db: Session, recipe_id: int) -> ProductionRecipe:
    return _get_recipe_or_fail(db, recipe_id)


def update_recipe(
    db: Session,
    recipe_id: int,
    payload: ProductionRecipeUpdate,
) -> ProductionRecipe:
    recipe = _get_recipe_for_update_or_fail(db, recipe_id)
    _ensure_recipe_is_editable(recipe)
    values = payload.model_dump(exclude_unset=True)
    if "output_product_id" in values:
        product = _get_active_product_or_fail(
            db,
            int(values["output_product_id"]),
        )
        values["output_product_id"] = product.id
    valid_from = values.get("valid_from", recipe.valid_from)
    valid_to = values.get("valid_to", recipe.valid_to)
    _validate_dates(valid_from, valid_to)
    recipe_repository.update_recipe(db, recipe, values)
    db.flush()
    _recalculate_recipe_costs(db, recipe)
    db.commit()
    return _get_recipe_or_fail(db, recipe.id)


def activate_recipe(db: Session, recipe_id: int) -> ProductionRecipe:
    recipe = _get_recipe_for_update_or_fail(db, recipe_id)
    if recipe.status == "voided":
        raise ValueError("La formula esta anulada y no puede activarse.")
    _get_active_product_or_fail(db, recipe.output_product_id)
    active_items = [item for item in recipe.items if item.is_active]
    if not active_items:
        raise ValueError(
            "La formula debe tener al menos un insumo activo para activarse.",
        )
    for item in active_items:
        _get_active_product_or_fail(db, item.input_product_id)
    recipe_repository.update_recipe(db, recipe, {"status": "active"})
    db.commit()
    return _get_recipe_or_fail(db, recipe.id)


def deactivate_recipe(db: Session, recipe_id: int) -> ProductionRecipe:
    recipe = _get_recipe_for_update_or_fail(db, recipe_id)
    if recipe.status == "voided":
        raise ValueError("La formula anulada no puede desactivarse.")
    recipe_repository.update_recipe(db, recipe, {"status": "inactive"})
    db.commit()
    return _get_recipe_or_fail(db, recipe.id)


def void_recipe(
    db: Session,
    recipe_id: int,
    reason: str,
) -> ProductionRecipe:
    recipe = _get_recipe_for_update_or_fail(db, recipe_id)
    if recipe.status == "voided":
        raise ValueError("La formula ya esta anulada.")
    recipe_repository.mark_recipe_voided(
        db,
        recipe,
        reason,
        datetime.now(timezone.utc),
    )
    db.commit()
    return _get_recipe_or_fail(db, recipe.id)


def create_recipe_item(
    db: Session,
    recipe_id: int,
    payload: ProductionRecipeItemCreate,
) -> ProductionRecipeItem:
    recipe = _get_recipe_for_update_or_fail(db, recipe_id)
    _ensure_recipe_is_editable(recipe)
    product = _get_active_product_or_fail(db, payload.input_product_id)
    unit_cost = (
        payload.unit_cost
        if payload.unit_cost is not None
        else Decimal(product.cost_estimate)
    )
    values = {
        **payload.model_dump(exclude={"unit_cost"}),
        **_product_snapshot(product),
        "recipe_id": recipe.id,
        "unit_cost": _money(unit_cost),
        "total_cost": _item_total(payload.quantity_required, unit_cost),
        "is_active": True,
    }
    item = recipe_repository.create_item(db, values)
    db.flush()
    _recalculate_recipe_costs(db, recipe)
    db.commit()
    return _get_item_or_fail(db, item.id)


def update_recipe_item(
    db: Session,
    item_id: int,
    payload: ProductionRecipeItemUpdate,
) -> ProductionRecipeItem:
    item = _get_item_for_update_or_fail(db, item_id)
    _ensure_recipe_is_editable(item.recipe)
    values = payload.model_dump(exclude_unset=True)
    if "input_product_id" in values:
        product = _get_active_product_or_fail(
            db,
            int(values["input_product_id"]),
        )
        values.update(_product_snapshot(product))
    quantity = Decimal(values.get("quantity_required", item.quantity_required))
    unit_cost = Decimal(values.get("unit_cost", item.unit_cost))
    values["unit_cost"] = _money(unit_cost)
    values["total_cost"] = _item_total(quantity, unit_cost)
    recipe_repository.update_item(db, item, values)
    db.flush()
    _recalculate_recipe_costs(db, item.recipe)
    db.commit()
    return _get_item_or_fail(db, item.id)


def set_recipe_item_active(
    db: Session,
    item_id: int,
    is_active: bool,
) -> ProductionRecipeItem:
    item = _get_item_for_update_or_fail(db, item_id)
    _ensure_recipe_is_editable(item.recipe)
    if is_active:
        _get_active_product_or_fail(db, item.input_product_id)
    recipe_repository.update_item(db, item, {"is_active": is_active})
    db.flush()
    _recalculate_recipe_costs(db, item.recipe)
    db.commit()
    return _get_item_or_fail(db, item.id)


def get_cost_estimate(
    db: Session,
    recipe_id: int,
    output_quantity: Decimal | None = None,
) -> ProductionRecipeCostEstimate:
    recipe = _get_recipe_or_fail(db, recipe_id)
    requested_quantity = output_quantity or Decimal(recipe.output_quantity)
    factor = requested_quantity / Decimal(recipe.output_quantity)
    cost_items: list[ProductionRecipeCostItem] = []
    estimated_total = Decimal("0")
    for item in recipe.items:
        if not item.is_active:
            continue
        scaled_quantity = (
            Decimal(item.quantity_required) * factor
        ).quantize(QUANTITY_QUANTUM, rounding=ROUND_HALF_UP)
        scaled_total = _item_total(scaled_quantity, Decimal(item.unit_cost))
        estimated_total += scaled_total
        cost_items.append(
            ProductionRecipeCostItem(
                input_product_id=item.input_product_id,
                input_product_name_snapshot=item.input_product_name_snapshot,
                quantity_required_base=item.quantity_required,
                quantity_required_scaled=scaled_quantity,
                unit_cost=item.unit_cost,
                total_cost_scaled=scaled_total,
            ),
        )
    estimated_total = _money(estimated_total)
    return ProductionRecipeCostEstimate(
        recipe_id=recipe.id,
        recipe_number=recipe.recipe_number,
        output_product_id=recipe.output_product_id,
        output_product_name=recipe.output_product.name,
        base_output_quantity=recipe.output_quantity,
        requested_output_quantity=requested_quantity,
        estimated_material_cost=estimated_total,
        estimated_cost_per_unit=_money(
            estimated_total / requested_quantity,
        ),
        items=cost_items,
    )


def _recalculate_recipe_costs(
    db: Session,
    recipe: ProductionRecipe,
) -> None:
    material_cost = _money(
        recipe_repository.get_active_items_total(db, recipe.id),
    )
    cost_per_unit = _money(material_cost / Decimal(recipe.output_quantity))
    recipe_repository.update_recipe(
        db,
        recipe,
        {
            "estimated_material_cost": material_cost,
            "estimated_cost_per_unit": cost_per_unit,
        },
    )


def _get_recipe_or_fail(db: Session, recipe_id: int) -> ProductionRecipe:
    recipe = recipe_repository.get_recipe(db, recipe_id)
    if recipe is None:
        raise ValueError("La formula de produccion no existe.")
    return recipe


def _get_recipe_for_update_or_fail(
    db: Session,
    recipe_id: int,
) -> ProductionRecipe:
    recipe = recipe_repository.get_recipe_for_update(db, recipe_id)
    if recipe is None:
        raise ValueError("La formula de produccion no existe.")
    return recipe


def _get_item_or_fail(db: Session, item_id: int) -> ProductionRecipeItem:
    item = recipe_repository.get_item(db, item_id)
    if item is None:
        raise ValueError("El insumo de la formula no existe.")
    return item


def _get_item_for_update_or_fail(
    db: Session,
    item_id: int,
) -> ProductionRecipeItem:
    item = recipe_repository.get_item_for_update(db, item_id)
    if item is None:
        raise ValueError("El insumo de la formula no existe.")
    return item


def _get_active_product_or_fail(db: Session, product_id: int) -> Product:
    product = products.get_product(db, product_id)
    if product is None:
        raise ValueError("El producto no existe.")
    if not product.is_active:
        raise ValueError(f"El producto {product.name} esta inactivo.")
    return product


def _product_snapshot(product: Product) -> dict[str, object]:
    return {
        "input_product_id": product.id,
        "input_product_sku_snapshot": product.sku,
        "input_product_name_snapshot": product.name,
        "input_product_kind_snapshot": product.product_kind,
        "input_product_presentation_snapshot": product.presentation,
    }


def _ensure_recipe_is_editable(recipe: ProductionRecipe) -> None:
    if recipe.status == "voided":
        raise ValueError("La formula anulada no puede modificarse.")


def _validate_dates(
    valid_from: date | None,
    valid_to: date | None,
) -> None:
    if valid_from is not None and valid_to is not None and valid_from > valid_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _item_total(quantity: Decimal, unit_cost: Decimal) -> Decimal:
    return _money(Decimal(quantity) * Decimal(unit_cost))


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(COST_QUANTUM, rounding=ROUND_HALF_UP)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

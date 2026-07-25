from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.production_batch import ProductionBatch
from app.models.production_item import ProductionItem
from app.models.production_material_consumption import (
    ProductionMaterialConsumption,
)
from app.models.production_recipe import ProductionRecipe
from app.models.production_recipe_item import ProductionRecipeItem
from app.repositories import inventory as inventory_repository
from app.repositories import production as production_repository
from app.repositories import production_material_consumptions as consumption_repository
from app.repositories import production_recipes as recipe_repository
from app.schemas.inventory import InventoryMovementCreate
from app.schemas.production_material_consumption import (
    ProductionBatchMaterialConsumptionRead,
    ProductionMaterialConsumptionCreate,
    ProductionMaterialConsumptionPreview,
    ProductionMaterialConsumptionPreviewItem,
    ProductionMaterialConsumptionPreviewRequest,
)
from app.services import inventory as inventory_service

QUANTITY_QUANTUM = Decimal("0.001")
COST_QUANTUM = Decimal("0.0001")
MOVEMENT_COST_QUANTUM = Decimal("0.01")
HUNDRED = Decimal("100")


@dataclass(frozen=True)
class MaterialLine:
    production_item: ProductionItem
    recipe: ProductionRecipe
    recipe_item: ProductionRecipeItem
    quantity_consumed: Decimal
    available_stock: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    has_sufficient_stock: bool


def preview_material_consumption(
    db: Session,
    batch_id: int,
    payload: ProductionMaterialConsumptionPreviewRequest,
) -> ProductionMaterialConsumptionPreview:
    batch = _get_valid_batch(db, batch_id, for_update=False)
    location = _get_valid_location(
        db,
        payload.source_location_id,
        for_update=False,
    )
    lines = _build_material_lines(
        db,
        batch,
        location.id,
        payload.items,
        lock_stock=False,
    )
    return _build_preview(batch.id, location.id, lines)


def create_material_consumption(
    db: Session,
    batch_id: int,
    payload: ProductionMaterialConsumptionCreate,
    created_by: int,
) -> ProductionMaterialConsumption:
    batch = _get_valid_batch(db, batch_id, for_update=True)
    if consumption_repository.get_active_consumption_for_batch(db, batch.id):
        raise ValueError("La produccion ya tiene un consumo de insumos activo.")
    location = _get_valid_location(
        db,
        payload.source_location_id,
        for_update=True,
    )
    lines = _build_material_lines(
        db,
        batch,
        location.id,
        payload.items,
        lock_stock=True,
    )
    insufficient_names = sorted(
        {
            line.recipe_item.input_product_name_snapshot
            for line in lines
            if not line.has_sufficient_stock
        },
    )
    if insufficient_names:
        raise ValueError(
            "No hay stock suficiente para consumir: "
            + ", ".join(insufficient_names)
            + ".",
        )

    total_material_cost = _cost(sum(line.total_cost for line in lines))
    consumption = consumption_repository.create_consumption(
        db,
        {
            "consumption_number": f"PENDING-{batch.id}-{datetime.now().timestamp()}",
            "production_batch_id": batch.id,
            "source_location_id": location.id,
            "movement_date": payload.movement_date,
            "status": "active",
            "total_material_cost": total_material_cost,
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        consumption.consumption_number = (
            f"PMC-{payload.movement_date:%Y%m%d}-{consumption.id:04d}"
        )
        for line in lines:
            movement = inventory_service.create_movement_in_transaction(
                db,
                InventoryMovementCreate(
                    movement_date=payload.movement_date,
                    movement_type="exit",
                    product_id=line.recipe_item.input_product_id,
                    location_id=location.id,
                    quantity=line.quantity_consumed,
                    unit_cost=line.unit_cost.quantize(
                        MOVEMENT_COST_QUANTUM,
                        rounding=ROUND_HALF_UP,
                    ),
                    reason=_build_movement_reason(
                        consumption.consumption_number,
                        batch.production_number,
                        payload.notes,
                    ),
                ),
                created_by,
            )
            db.flush()
            consumption_repository.create_consumption_item(
                db,
                {
                    "consumption_id": consumption.id,
                    "production_item_id": line.production_item.id,
                    "recipe_id": line.recipe.id,
                    "recipe_item_id": line.recipe_item.id,
                    "input_product_id": line.recipe_item.input_product_id,
                    "input_product_sku_snapshot": (
                        line.recipe_item.input_product_sku_snapshot
                    ),
                    "input_product_name_snapshot": (
                        line.recipe_item.input_product_name_snapshot
                    ),
                    "input_product_kind_snapshot": (
                        line.recipe_item.input_product_kind_snapshot
                    ),
                    "input_product_presentation_snapshot": (
                        line.recipe_item.input_product_presentation_snapshot
                    ),
                    "recipe_number_snapshot": line.recipe.recipe_number,
                    "recipe_name_snapshot": line.recipe.name,
                    "quantity_required_base": line.recipe_item.quantity_required,
                    "quantity_consumed": line.quantity_consumed,
                    "unit_cost": line.unit_cost,
                    "total_cost": line.total_cost,
                    "inventory_movement_id": movement.id,
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
            "La produccion ya tiene un consumo de insumos activo.",
        ) from error
    except Exception:
        db.rollback()
        raise

    return get_material_consumption(db, consumption.id)


def get_batch_material_consumption(
    db: Session,
    batch_id: int,
) -> ProductionBatchMaterialConsumptionRead:
    batch = production_repository.get_production_batch(db, batch_id)
    if batch is None:
        raise ValueError("La produccion no existe.")
    consumption = consumption_repository.get_active_consumption_for_batch(
        db,
        batch.id,
    )
    return ProductionBatchMaterialConsumptionRead(
        status="consumed" if consumption is not None else "not_consumed",
        active_consumption=consumption,
    )


def list_material_consumptions(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    production_batch_id: int | None = None,
    source_location_id: int | None = None,
    input_product_id: int | None = None,
    search: str | None = None,
) -> list[ProductionMaterialConsumption]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return consumption_repository.list_consumptions(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        production_batch_id=production_batch_id,
        source_location_id=source_location_id,
        input_product_id=input_product_id,
        search=_normalize_filter(search),
    )


def get_material_consumption(
    db: Session,
    consumption_id: int,
) -> ProductionMaterialConsumption:
    consumption = consumption_repository.get_consumption(db, consumption_id)
    if consumption is None:
        raise ValueError("El consumo de insumos no existe.")
    return consumption


def void_material_consumption(
    db: Session,
    consumption_id: int,
    reason: str,
) -> ProductionMaterialConsumption:
    consumption = consumption_repository.get_consumption(
        db,
        consumption_id,
        for_update=True,
    )
    if consumption is None:
        raise ValueError("El consumo de insumos no existe.")
    if consumption.status == "voided":
        raise ValueError("El consumo de insumos ya esta anulado.")

    voided_at = datetime.now(timezone.utc)
    try:
        for item in consumption.items:
            inventory_service.void_movement_in_transaction(
                db,
                item.inventory_movement_id,
                f"Consumo de insumos anulado: {reason}",
                voided_at=voided_at,
                allow_production_material_consumption=True,
            )
            db.flush()
        consumption_repository.mark_consumption_voided(
            db,
            consumption,
            reason,
            voided_at,
        )
        db.commit()
    except ValueError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular el consumo de insumos.") from error
    except Exception:
        db.rollback()
        raise
    return get_material_consumption(db, consumption.id)


def _get_valid_batch(
    db: Session,
    batch_id: int,
    *,
    for_update: bool,
) -> ProductionBatch:
    batch = (
        production_repository.get_production_batch_for_update(db, batch_id)
        if for_update
        else production_repository.get_production_batch(db, batch_id)
    )
    if batch is None:
        raise ValueError("La produccion no existe.")
    if batch.status != "active":
        raise ValueError("No se pueden consumir insumos de una produccion anulada.")
    return batch


def _get_valid_location(
    db: Session,
    location_id: int,
    *,
    for_update: bool,
):
    location = inventory_repository.get_location(
        db,
        location_id,
        for_update=for_update,
    )
    if location is None:
        raise ValueError("La ubicacion de inventario no existe.")
    if not location.is_active:
        raise ValueError("No se pueden consumir insumos de una ubicacion inactiva.")
    return location


def _build_material_lines(
    db: Session,
    batch: ProductionBatch,
    location_id: int,
    selections,
    *,
    lock_stock: bool,
) -> list[MaterialLine]:
    batch_items = {item.id: item for item in batch.items}
    selected_ids = [selection.production_item_id for selection in selections]
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError(
            "Cada producto producido debe tener una sola formula seleccionada.",
        )
    if any(production_item_id not in batch_items for production_item_id in selected_ids):
        raise ValueError(
            "El producto producido no pertenece a la produccion.",
        )
    if set(selected_ids) != set(batch_items):
        raise ValueError(
            "Debe seleccionar una formula para cada producto de la produccion.",
        )

    prepared: list[
        tuple[ProductionItem, ProductionRecipe, ProductionRecipeItem, Decimal]
    ] = []
    required_by_product: dict[int, Decimal] = defaultdict(
        lambda: Decimal("0.000"),
    )
    for selection in selections:
        production_item = batch_items.get(selection.production_item_id)
        if production_item is None:
            raise RuntimeError("La seleccion de produccion validada no existe.")
        recipe = recipe_repository.get_recipe(db, selection.recipe_id)
        if recipe is None:
            raise ValueError("La formula de produccion no existe.")
        if recipe.status != "active":
            raise ValueError("La formula de produccion debe estar activa.")
        if recipe.output_product_id != production_item.product_id:
            raise ValueError(
                "La formula seleccionada no corresponde al producto producido.",
            )
        active_items = [item for item in recipe.items if item.is_active]
        if not active_items:
            raise ValueError("La formula no tiene insumos activos.")
        for recipe_item in active_items:
            quantity = _calculate_quantity(
                recipe_item,
                production_item.quantity_produced,
                recipe.output_quantity,
            )
            if quantity <= 0:
                raise ValueError(
                    "La cantidad de insumo calculada debe ser mayor a cero.",
                )
            prepared.append((production_item, recipe, recipe_item, quantity))
            required_by_product[recipe_item.input_product_id] += quantity

    stock_by_product: dict[int, Decimal] = {}
    for product_id in sorted(required_by_product):
        product = inventory_repository.get_product(
            db,
            product_id,
            for_update=lock_stock,
        )
        if product is None:
            raise ValueError("El insumo de la formula no existe.")
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")
        stock = inventory_repository.get_stock(
            db,
            product_id,
            location_id,
            for_update=lock_stock,
        )
        stock_by_product[product_id] = (
            Decimal(stock.quantity_on_hand)
            if stock is not None
            else Decimal("0.000")
        )

    lines: list[MaterialLine] = []
    for production_item, recipe, recipe_item, quantity in prepared:
        available_stock = stock_by_product[recipe_item.input_product_id]
        unit_cost = _cost(Decimal(recipe_item.unit_cost))
        lines.append(
            MaterialLine(
                production_item=production_item,
                recipe=recipe,
                recipe_item=recipe_item,
                quantity_consumed=quantity,
                available_stock=available_stock,
                unit_cost=unit_cost,
                total_cost=_cost(quantity * unit_cost),
                has_sufficient_stock=(
                    required_by_product[recipe_item.input_product_id]
                    <= available_stock
                ),
            ),
        )
    return lines


def _calculate_quantity(
    recipe_item: ProductionRecipeItem,
    quantity_produced: Decimal,
    recipe_output_quantity: Decimal,
) -> Decimal:
    base_quantity = (
        Decimal(recipe_item.quantity_required)
        * (
            Decimal(quantity_produced)
            / Decimal(recipe_output_quantity)
        )
    )
    waste_quantity = (
        base_quantity
        * (Decimal(recipe_item.waste_percentage) / HUNDRED)
    )
    return (base_quantity + waste_quantity).quantize(
        QUANTITY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def _build_preview(
    batch_id: int,
    source_location_id: int,
    lines: list[MaterialLine],
) -> ProductionMaterialConsumptionPreview:
    return ProductionMaterialConsumptionPreview(
        production_batch_id=batch_id,
        source_location_id=source_location_id,
        total_material_cost=_cost(sum(line.total_cost for line in lines)),
        items=[
            ProductionMaterialConsumptionPreviewItem(
                production_item_id=line.production_item.id,
                output_product_name=line.production_item.product_name_snapshot,
                recipe_id=line.recipe.id,
                recipe_name=line.recipe.name,
                input_product_id=line.recipe_item.input_product_id,
                input_product_name=(
                    line.recipe_item.input_product_name_snapshot
                ),
                quantity_consumed=line.quantity_consumed,
                available_stock=line.available_stock,
                unit_cost=line.unit_cost,
                total_cost=line.total_cost,
                has_sufficient_stock=line.has_sufficient_stock,
            )
            for line in lines
        ],
    )


def _build_movement_reason(
    consumption_number: str,
    production_number: str,
    notes: str | None,
) -> str:
    reason = (
        f"Consumo {consumption_number} de produccion {production_number}"
    )
    return f"{reason} - {notes}" if notes is not None else reason


def _cost(value: Decimal) -> Decimal:
    return Decimal(value).quantize(COST_QUANTUM, rounding=ROUND_HALF_UP)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None

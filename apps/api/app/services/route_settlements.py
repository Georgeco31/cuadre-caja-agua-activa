from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories import route_closures as route_closures_repository
from app.repositories import route_loads as route_loads_repository
from app.repositories import route_returns as route_returns_repository
from app.schemas.route_settlement import (
    RouteSettlementItemRead,
    RouteSettlementRead,
)
from app.services import route_activity as route_activity_service

MONEY_QUANTUM = Decimal("0.01")
QUANTITY_QUANTUM = Decimal("0.001")
ZERO_MONEY = Decimal("0.00")
ZERO_QUANTITY = Decimal("0.000")


def get_route_settlement(
    db: Session,
    load_id: int,
) -> RouteSettlementRead:
    route_load = route_loads_repository.get_route_load(db, load_id)
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")

    route_return = route_returns_repository.get_active_return_for_load(db, load_id)
    route_closure = route_closures_repository.get_active_closure_for_load(
        db,
        load_id,
    )
    activity = route_activity_service.get_commercial_activity(db, load_id)

    registered_products = {
        product.product_id: product for product in activity.products_sold
    }
    returned_by_load_item = (
        {
            item.route_load_item_id: item.quantity_returned
            for item in route_return.items
        }
        if route_return is not None
        else {}
    )

    items: list[RouteSettlementItemRead] = []
    total_loaded = ZERO_QUANTITY
    total_returned = ZERO_QUANTITY if route_return is not None else None
    total_physical_sold = ZERO_QUANTITY if route_return is not None else None
    total_registered_sold = ZERO_QUANTITY

    for load_item in route_load.items:
        loaded = load_item.quantity_loaded.quantize(QUANTITY_QUANTUM)
        returned = (
            returned_by_load_item.get(load_item.id, ZERO_QUANTITY).quantize(
                QUANTITY_QUANTUM,
            )
            if route_return is not None
            else None
        )
        physical_sold = (
            (loaded - returned).quantize(QUANTITY_QUANTUM)
            if returned is not None
            else None
        )
        registered_product = registered_products.pop(load_item.product_id, None)
        registered_sold = (
            registered_product.total_quantity.quantize(QUANTITY_QUANTUM)
            if registered_product is not None
            else ZERO_QUANTITY
        )
        difference = (
            (physical_sold - registered_sold).quantize(QUANTITY_QUANTUM)
            if physical_sold is not None
            else None
        )
        items.append(
            RouteSettlementItemRead(
                product_id=load_item.product_id,
                product_name_snapshot=load_item.product_name_snapshot,
                product_presentation_snapshot=(
                    load_item.product_presentation_snapshot
                ),
                loaded_quantity=loaded,
                returned_quantity=returned,
                physical_sold_quantity=physical_sold,
                registered_sold_quantity=registered_sold,
                physical_vs_registered_difference=difference,
            ),
        )
        total_loaded += loaded
        total_registered_sold += registered_sold
        if total_returned is not None and returned is not None:
            total_returned += returned
        if total_physical_sold is not None and physical_sold is not None:
            total_physical_sold += physical_sold

    for product_id, registered_product in sorted(registered_products.items()):
        registered_sold = registered_product.total_quantity.quantize(
            QUANTITY_QUANTUM,
        )
        physical_sold = ZERO_QUANTITY if route_return is not None else None
        difference = (
            (physical_sold - registered_sold).quantize(QUANTITY_QUANTUM)
            if physical_sold is not None
            else None
        )
        items.append(
            RouteSettlementItemRead(
                product_id=product_id,
                product_name_snapshot=registered_product.product_name_snapshot,
                product_presentation_snapshot=None,
                loaded_quantity=ZERO_QUANTITY,
                returned_quantity=(
                    ZERO_QUANTITY if route_return is not None else None
                ),
                physical_sold_quantity=physical_sold,
                registered_sold_quantity=registered_sold,
                physical_vs_registered_difference=difference,
            ),
        )
        total_registered_sold += registered_sold

    total_loaded = total_loaded.quantize(QUANTITY_QUANTUM)
    total_registered_sold = total_registered_sold.quantize(QUANTITY_QUANTUM)
    if total_returned is not None:
        total_returned = total_returned.quantize(QUANTITY_QUANTUM)
    if total_physical_sold is not None:
        total_physical_sold = total_physical_sold.quantize(QUANTITY_QUANTUM)
    physical_difference = (
        (total_physical_sold - total_registered_sold).quantize(
            QUANTITY_QUANTUM,
        )
        if total_physical_sold is not None
        else None
    )

    if route_closure is not None:
        cash_sales_amount = route_closure.cash_sales_total
        credit_sales_amount = route_closure.credit_sales_total
        payments_amount = route_closure.payments_total
        expected_cash = route_closure.expected_cash_total
        delivered_cash = route_closure.delivered_cash_total
        cash_difference = route_closure.difference_amount
    else:
        cash_sales_amount = activity.cash_sales_total
        credit_sales_amount = activity.credit_sales_total
        payments_amount = activity.payments_total
        expected_cash = activity.expected_cash_total
        delivered_cash = None
        cash_difference = None

    cash_sales_amount = cash_sales_amount.quantize(MONEY_QUANTUM)
    credit_sales_amount = credit_sales_amount.quantize(MONEY_QUANTUM)
    payments_amount = payments_amount.quantize(MONEY_QUANTUM)
    expected_cash = expected_cash.quantize(MONEY_QUANTUM)
    if delivered_cash is not None:
        delivered_cash = delivered_cash.quantize(MONEY_QUANTUM)
    if cash_difference is not None:
        cash_difference = cash_difference.quantize(MONEY_QUANTUM)

    has_product_difference = any(
        item.physical_vs_registered_difference is not None
        and item.physical_vs_registered_difference != ZERO_QUANTITY
        for item in items
    )
    has_cash_difference = (
        cash_difference is not None and cash_difference != ZERO_MONEY
    )
    is_pending = route_return is None or delivered_cash is None
    if is_pending:
        settlement_status = "pending"
    elif has_product_difference or has_cash_difference:
        settlement_status = "with_difference"
    else:
        settlement_status = "balanced"

    messages: list[str] = []
    if route_return is None:
        messages.append("No hay retorno registrado todavia.")
    if delivered_cash is None:
        messages.append("No hay dinero entregado registrado todavia.")
    if has_product_difference:
        messages.append("La ruta tiene diferencia de producto.")
    if has_cash_difference:
        messages.append("La ruta tiene diferencia de dinero.")
    if settlement_status == "balanced":
        messages.append("La ruta esta cuadrada.")

    settlement_observation = (
        route_closure.notes if route_closure is not None else None
    )
    return RouteSettlementRead(
        route_load_id=route_load.id,
        load_number=route_load.load_number,
        load_date=route_load.load_date,
        route_load_status=route_load.status,
        route_id=route_load.route_id,
        route_name=route_load.route_name,
        vehicle_id=route_load.vehicle_id,
        vehicle_name=route_load.vehicle_name,
        responsible_name=(
            route_load.delivery_route.reference_driver
            or route_load.vehicle.reference_driver
        ),
        route_return_id=route_return.id if route_return is not None else None,
        return_number=(
            route_return.return_number if route_return is not None else None
        ),
        return_date=route_return.return_date if route_return is not None else None,
        route_closure_id=(
            route_closure.id if route_closure is not None else None
        ),
        closure_number=(
            route_closure.closure_number if route_closure is not None else None
        ),
        closure_date=(
            route_closure.closure_date if route_closure is not None else None
        ),
        total_loaded_quantity=total_loaded,
        total_returned_quantity=total_returned,
        physical_sold_quantity=total_physical_sold,
        registered_sold_quantity=total_registered_sold,
        physical_vs_registered_difference=physical_difference,
        cash_sales_amount=cash_sales_amount,
        credit_sales_amount=credit_sales_amount,
        registered_sales_amount=(cash_sales_amount + credit_sales_amount).quantize(
            MONEY_QUANTUM,
        ),
        registered_payments_amount=payments_amount,
        expected_cash_amount=expected_cash,
        delivered_cash_amount=delivered_cash,
        cash_difference=cash_difference,
        status=settlement_status,
        return_observation=route_return.notes if route_return is not None else None,
        settlement_observation=settlement_observation,
        difference_reason=(
            settlement_observation
            if has_product_difference or has_cash_difference
            else None
        ),
        messages=messages,
        items=items,
    )

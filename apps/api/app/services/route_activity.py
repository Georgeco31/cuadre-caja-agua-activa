from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.repositories import credit_payments as credit_payments_repository
from app.repositories import route_loads as route_loads_repository
from app.repositories import sales as sales_repository
from app.schemas.route_activity import (
    RouteActivityProductRead,
    RouteCommercialActivityRead,
)

MONEY_QUANTUM = Decimal("0.01")
QUANTITY_QUANTUM = Decimal("0.001")


def get_commercial_activity(
    db: Session,
    load_id: int,
) -> RouteCommercialActivityRead:
    route_load = route_loads_repository.get_route_load(db, load_id)
    if route_load is None:
        raise ValueError("La carga de ruta no existe.")

    sales = sales_repository.list_sales(
        db,
        status="active",
        route_load_id=load_id,
    )
    cash_sales = [sale for sale in sales if sale.sale_type == "cash"]
    credit_sales = [sale for sale in sales if sale.sale_type == "credit"]
    payments = credit_payments_repository.list_credit_payments(
        db,
        status="active",
        route_load_id=load_id,
    )

    cash_sales_total = _sum_sales(cash_sales)
    credit_sales_total = _sum_sales(credit_sales)
    payments_total = sum(
        (payment.amount for payment in payments),
        start=Decimal("0.00"),
    ).quantize(MONEY_QUANTUM)

    return RouteCommercialActivityRead(
        load_id=route_load.id,
        load_number=route_load.load_number,
        load_date=route_load.load_date,
        route_id=route_load.route_id,
        route_name=route_load.route_name,
        vehicle_id=route_load.vehicle_id,
        vehicle_name=route_load.vehicle_name,
        status=route_load.status,
        cash_sales=cash_sales,
        credit_sales=credit_sales,
        payments=payments,
        cash_sales_total=cash_sales_total,
        credit_sales_total=credit_sales_total,
        payments_total=payments_total,
        expected_cash_total=(cash_sales_total + payments_total).quantize(
            MONEY_QUANTUM,
        ),
        products_sold=_group_products(sales),
    )


def _sum_sales(sales: list[Sale]) -> Decimal:
    return sum(
        (sale.total_amount for sale in sales),
        start=Decimal("0.00"),
    ).quantize(MONEY_QUANTUM)


def _group_products(sales: list[Sale]) -> list[RouteActivityProductRead]:
    grouped: dict[int, dict[str, object]] = {}
    for sale in sales:
        for item in sale.items:
            current = grouped.setdefault(
                item.product_id,
                {
                    "product_id": item.product_id,
                    "product_name_snapshot": item.product_name_snapshot,
                    "total_quantity": Decimal("0.000"),
                    "total_amount": Decimal("0.00"),
                },
            )
            current["total_quantity"] = Decimal(
                current["total_quantity"],
            ) + item.quantity
            current["total_amount"] = Decimal(
                current["total_amount"],
            ) + item.subtotal

    return [
        RouteActivityProductRead(
            product_id=int(values["product_id"]),
            product_name_snapshot=str(values["product_name_snapshot"]),
            total_quantity=Decimal(values["total_quantity"]).quantize(
                QUANTITY_QUANTUM,
            ),
            total_amount=Decimal(values["total_amount"]).quantize(MONEY_QUANTUM),
        )
        for _, values in sorted(grouped.items())
    ]

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.models.cash_count_item import CashCountItem
from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.models.delivery_route import DeliveryRoute
from app.models.expense import Expense
from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.product import Product
from app.models.production_batch import ProductionBatch
from app.models.production_item import ProductionItem
from app.models.route_cash_receipt import RouteCashReceipt
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.route_load_item import RouteLoadItem
from app.models.route_return import RouteReturn
from app.models.route_return_item import RouteReturnItem
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.user import User
from app.models.vehicle import Vehicle

REPORT_PATH = "/api/v1/reports/daily-operational-summary"
REPORT_DATE = date(2026, 7, 23)


def test_daily_operational_summary_requires_authentication(api_client) -> None:
    client, _ = api_client

    response = client.get(REPORT_PATH)

    assert response.status_code == 401


def test_daily_operational_summary_without_data_returns_zeroes_and_alerts(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        f"{REPORT_PATH}?date=2026-07-23",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == "2026-07-23"
    assert body["cash_summary"] == {
        "cash_session_exists": False,
        "cash_session_id": None,
        "cash_session_status": None,
        "total_coins": "0.00",
        "total_bills": "0.00",
        "total_counted": "0.00",
        "total_expenses": "0.00",
        "total_final": "0.00",
        "pre_count_expenses_total": "0.00",
        "post_count_expenses_total": "0.00",
        "expenses_count": 0,
        "route_cash_receipts_total": "0.00",
        "route_cash_receipts_count": 0,
    }
    assert body["production_summary"]["products"] == []
    assert body["production_summary"]["total_quantity_produced"] == "0.000"
    assert body["route_loads_summary"]["loads"] == []
    assert body["route_returns_summary"]["returns"] == []
    assert body["route_closures_summary"]["closures"] == []
    assert body["route_cash_receipts_summary"]["receipts"] == []
    assert body["sales_summary"]["products_sold"] == []
    assert body["totals"] == {
        "total_business_cash_inflow_reference": "0.00",
        "total_route_delivered_cash": "0.00",
        "total_route_cash_registered": "0.00",
        "total_cash_counted": "0.00",
        "total_cash_final": "0.00",
    }
    assert {alert["code"] for alert in body["alerts"]} == {
        "cash_session_missing",
        "production_missing",
        "sales_missing",
    }


def test_daily_operational_summary_without_date_uses_today(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(REPORT_PATH, headers=api_auth_headers)

    assert response.status_code == 200
    assert response.json()["date"] == date.today().isoformat()


def test_daily_operational_summary_calculates_sections_and_excludes_voided(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_complete_daily_operation(
        testing_session_local,
        coin_id=api_denominations["coin_100"].id,
        bill_id=api_denominations["bill_1000"].id,
    )

    response = client.get(
        f"{REPORT_PATH}?date={REPORT_DATE.isoformat()}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()

    assert body["cash_summary"] == {
        "cash_session_exists": True,
        "cash_session_id": body["cash_summary"]["cash_session_id"],
        "cash_session_status": "open",
        "total_coins": "2.00",
        "total_bills": "30.00",
        "total_counted": "32.00",
        "total_expenses": "2.00",
        "total_final": "30.00",
        "pre_count_expenses_total": "3.00",
        "post_count_expenses_total": "2.00",
        "expenses_count": 2,
        "route_cash_receipts_total": "101.00",
        "route_cash_receipts_count": 1,
    }

    production = body["production_summary"]
    assert production["production_batches_count"] == 2
    assert production["active_production_batches_count"] == 1
    assert production["voided_production_batches_count"] == 1
    assert production["total_quantity_produced"] == "15.000"
    assert production["total_quantity_waste"] == "1.500"
    assert production["total_quantity_net"] == "13.500"
    assert [
        (item["product_name_snapshot"], item["quantity_net"])
        for item in production["products"]
    ] == [("Botella", "4.500"), ("Galón", "9.000")]

    loads = body["route_loads_summary"]
    assert loads["route_loads_count"] == 4
    assert loads["active_route_loads_count"] == 3
    assert loads["voided_route_loads_count"] == 1
    assert loads["total_items_loaded"] == 4
    assert loads["total_quantity_loaded"] == "21.000"

    returns = body["route_returns_summary"]
    assert returns["route_returns_count"] == 2
    assert returns["active_route_returns_count"] == 1
    assert returns["voided_route_returns_count"] == 1
    assert returns["total_quantity_returned"] == "5.000"

    closures = body["route_closures_summary"]
    assert closures["route_closures_count"] == 3
    assert closures["active_route_closures_count"] == 2
    assert closures["voided_route_closures_count"] == 1
    assert closures["expected_cash_total"] == "180.00"
    assert closures["delivered_cash_total"] == "175.00"
    assert closures["difference_total"] == "-5.00"
    assert closures["closures_with_shortage_count"] == 1
    assert closures["closures_with_surplus_count"] == 0
    assert closures["closures_balanced_count"] == 1

    receipts = body["route_cash_receipts_summary"]
    assert receipts["receipts_count"] == 2
    assert receipts["active_receipts_count"] == 1
    assert receipts["voided_receipts_count"] == 1
    assert receipts["delivered_cash_total"] == "100.00"
    assert receipts["received_amount_total"] == "101.00"
    assert receipts["difference_total"] == "1.00"

    sales = body["sales_summary"]
    assert sales["cash_sales_total"] == "60.00"
    assert sales["credit_sales_total"] == "40.00"
    assert sales["total_sales_amount"] == "100.00"
    assert sales["cash_sales_count"] == 1
    assert sales["credit_sales_count"] == 1
    assert sales["voided_sales_count"] == 1
    assert [
        (item["product_name_snapshot"], item["quantity"], item["amount"])
        for item in sales["products_sold"]
    ] == [
        ("Botella", "2.000", "20.00"),
        ("Galón", "4.000", "80.00"),
    ]

    receivables = body["receivables_summary"]
    assert receivables == {
        "payments_total": "15.00",
        "payments_count": 1,
        "voided_payments_count": 1,
        "credit_sales_created_total": "40.00",
        "outstanding_balance_created_today": "25.00",
        "customers_with_credit_sales_count": 1,
    }
    assert body["totals"] == {
        "total_business_cash_inflow_reference": "176.00",
        "total_route_delivered_cash": "175.00",
        "total_route_cash_registered": "101.00",
        "total_cash_counted": "32.00",
        "total_cash_final": "30.00",
    }
    assert {alert["code"] for alert in body["alerts"]} == {
        "cash_session_open",
        "route_closure_shortage",
        "route_closure_cash_unregistered",
        "route_cash_receipt_difference",
        "route_load_without_return",
        "route_load_without_closure",
    }


def test_daily_operational_summary_is_read_only(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_complete_daily_operation(
        testing_session_local,
        coin_id=api_denominations["coin_100"].id,
        bill_id=api_denominations["bill_1000"].id,
    )
    before = _database_snapshot(testing_session_local)

    response = client.get(
        f"{REPORT_PATH}?date={REPORT_DATE.isoformat()}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert _database_snapshot(testing_session_local) == before


def _add_complete_daily_operation(
    testing_session_local,
    *,
    coin_id: int,
    bill_id: int,
) -> None:
    now = datetime.now(UTC)
    with testing_session_local() as session:
        user_id = session.scalar(select(User.id).limit(1))
        assert user_id is not None

        product_gallon = Product(
            sku="GAL-20",
            name="Galón",
            category="gallon",
            unit="gallon",
            default_price=Decimal("20.00"),
            cost_estimate=Decimal("5.00"),
        )
        product_bottle = Product(
            sku="BOT-1",
            name="Botella",
            category="bottle",
            unit="bottle",
            default_price=Decimal("10.00"),
            cost_estimate=Decimal("2.00"),
        )
        customer = Customer(
            name="Cliente crédito",
            customer_type="store",
            credit_allowed=True,
            credit_limit=Decimal("500.00"),
        )
        route = DeliveryRoute(
            code="ROUTE-DAILY",
            name="Ruta centro",
            expected_daily_cash=Decimal("0.00"),
        )
        vehicle = Vehicle(
            code="VEH-DAILY",
            name="Camión 1",
            vehicle_type="truck",
            fuel_type="diesel",
        )
        session.add_all(
            [product_gallon, product_bottle, customer, route, vehicle],
        )
        session.flush()

        warehouse = InventoryLocation(
            code="WAREHOUSE-DAILY",
            name="Bodega",
            location_type="warehouse",
        )
        truck = InventoryLocation(
            code="TRUCK-DAILY",
            name="Camión 1",
            location_type="vehicle",
            vehicle_id=vehicle.id,
        )
        cash_session = CashSession(
            session_date=REPORT_DATE,
            status="open",
            created_by=user_id,
        )
        session.add_all([warehouse, truck, cash_session])
        session.flush()
        session.add_all(
            [
                CashCountItem(
                    cash_session_id=cash_session.id,
                    denomination_id=coin_id,
                    quantity=2,
                    subtotal=Decimal("2.00"),
                ),
                CashCountItem(
                    cash_session_id=cash_session.id,
                    denomination_id=bill_id,
                    quantity=3,
                    subtotal=Decimal("30.00"),
                ),
                Expense(
                    cash_session_id=cash_session.id,
                    description="Gasto previo",
                    amount=Decimal("3.00"),
                    expense_timing="before_count",
                    expense_date=REPORT_DATE,
                ),
                Expense(
                    cash_session_id=cash_session.id,
                    description="Gasto posterior",
                    amount=Decimal("2.00"),
                    expense_timing="after_count",
                    expense_date=REPORT_DATE,
                ),
            ],
        )

        active_batch = ProductionBatch(
            production_number="PROD-DAILY-ACTIVE",
            production_date=REPORT_DATE,
            status="active",
            created_by=user_id,
        )
        voided_batch = ProductionBatch(
            production_number="PROD-DAILY-VOIDED",
            production_date=REPORT_DATE,
            status="voided",
            void_reason="Prueba controlada",
            voided_at=now,
            created_by=user_id,
        )
        session.add_all([active_batch, voided_batch])
        session.flush()
        session.add_all(
            [
                _production_item(
                    active_batch.id,
                    product_gallon,
                    produced="10.000",
                    waste="1.000",
                ),
                _production_item(
                    active_batch.id,
                    product_bottle,
                    produced="5.000",
                    waste="0.500",
                ),
                _production_item(
                    voided_batch.id,
                    product_gallon,
                    produced="99.000",
                    waste="0.000",
                ),
            ],
        )

        loads = [
            _route_load("A", route.id, vehicle.id, warehouse.id, truck.id, user_id),
            _route_load("B", route.id, vehicle.id, warehouse.id, truck.id, user_id),
            _route_load("C", route.id, vehicle.id, warehouse.id, truck.id, user_id),
            _route_load(
                "VOIDED",
                route.id,
                vehicle.id,
                warehouse.id,
                truck.id,
                user_id,
                status="voided",
                voided_at=now,
            ),
        ]
        session.add_all(loads)
        session.flush()

        load_item_specs = [
            (loads[0], product_gallon, "12.000"),
            (loads[1], product_gallon, "3.000"),
            (loads[1], product_bottle, "4.000"),
            (loads[2], product_bottle, "2.000"),
            (loads[3], product_gallon, "50.000"),
        ]
        load_items: list[RouteLoadItem] = []
        for index, (load, product, quantity) in enumerate(
            load_item_specs,
            start=1,
        ):
            source_movement = _movement(
                index * 2,
                product,
                warehouse.id,
                user_id,
                "exit",
                quantity,
            )
            destination_movement = _movement(
                index * 2 + 1,
                product,
                truck.id,
                user_id,
                "entry",
                quantity,
            )
            session.add_all([source_movement, destination_movement])
            session.flush()
            load_item = RouteLoadItem(
                route_load_id=load.id,
                product_id=product.id,
                product_sku_snapshot=product.sku,
                product_name_snapshot=product.name,
                quantity_loaded=Decimal(quantity),
                source_exit_movement_id=source_movement.id,
                destination_entry_movement_id=destination_movement.id,
            )
            session.add(load_item)
            session.flush()
            load_items.append(load_item)

        active_return = _route_return(
            "ACTIVE",
            loads[0],
            route.id,
            vehicle.id,
            truck.id,
            warehouse.id,
            user_id,
        )
        voided_return = _route_return(
            "VOIDED",
            loads[3],
            route.id,
            vehicle.id,
            truck.id,
            warehouse.id,
            user_id,
            status="voided",
            voided_at=now,
        )
        session.add_all([active_return, voided_return])
        session.flush()
        for index, (route_return, load_item, quantity) in enumerate(
            [
                (active_return, load_items[0], "5.000"),
                (voided_return, load_items[4], "20.000"),
            ],
            start=20,
        ):
            product = (
                product_gallon
                if load_item.product_id == product_gallon.id
                else product_bottle
            )
            source_movement = _movement(
                index * 2,
                product,
                truck.id,
                user_id,
                "exit",
                quantity,
            )
            destination_movement = _movement(
                index * 2 + 1,
                product,
                warehouse.id,
                user_id,
                "entry",
                quantity,
            )
            session.add_all([source_movement, destination_movement])
            session.flush()
            session.add(
                RouteReturnItem(
                    route_return_id=route_return.id,
                    route_load_item_id=load_item.id,
                    product_id=product.id,
                    product_sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    quantity_returned=Decimal(quantity),
                    source_exit_movement_id=source_movement.id,
                    destination_entry_movement_id=destination_movement.id,
                ),
            )

        closure_a = _closure(
            "A",
            loads[0],
            route,
            vehicle,
            user_id,
            expected="100.00",
            delivered="100.00",
        )
        closure_b = _closure(
            "B",
            loads[1],
            route,
            vehicle,
            user_id,
            expected="80.00",
            delivered="75.00",
        )
        voided_closure = _closure(
            "VOIDED",
            loads[0],
            route,
            vehicle,
            user_id,
            expected="40.00",
            delivered="45.00",
            status="voided",
            voided_at=now,
        )
        session.add_all([closure_a, closure_b, voided_closure])
        session.flush()
        session.add_all(
            [
                _receipt(
                    "ACTIVE",
                    closure_a,
                    cash_session.id,
                    user_id,
                    delivered="100.00",
                    received="101.00",
                ),
                _receipt(
                    "VOIDED",
                    closure_b,
                    cash_session.id,
                    user_id,
                    delivered="75.00",
                    received="75.00",
                    status="voided",
                    voided_at=now,
                ),
            ],
        )

        cash_sale = _sale(
            "CASH",
            user_id,
            sale_type="cash",
            total="60.00",
            paid="60.00",
            balance="0.00",
        )
        credit_sale = _sale(
            "CREDIT",
            user_id,
            sale_type="credit",
            total="40.00",
            paid="15.00",
            balance="25.00",
            customer=customer,
        )
        voided_sale = _sale(
            "VOIDED",
            user_id,
            sale_type="cash",
            total="999.00",
            paid="999.00",
            balance="0.00",
            status="voided",
            voided_at=now,
        )
        session.add_all([cash_sale, credit_sale, voided_sale])
        session.flush()
        session.add_all(
            [
                _sale_item(cash_sale.id, product_gallon, "3.000", "60.00"),
                _sale_item(credit_sale.id, product_gallon, "1.000", "20.00"),
                _sale_item(credit_sale.id, product_bottle, "2.000", "20.00"),
                _sale_item(voided_sale.id, product_gallon, "1.000", "999.00"),
                CreditPayment(
                    sale_id=credit_sale.id,
                    customer_id=customer.id,
                    payment_date=REPORT_DATE,
                    amount=Decimal("15.00"),
                    payment_method="cash",
                    status="active",
                    created_by=user_id,
                ),
                CreditPayment(
                    sale_id=credit_sale.id,
                    customer_id=customer.id,
                    payment_date=REPORT_DATE,
                    amount=Decimal("7.00"),
                    payment_method="cash",
                    status="voided",
                    void_reason="Prueba controlada",
                    voided_at=now,
                    created_by=user_id,
                ),
            ],
        )
        session.commit()


def _production_item(
    batch_id: int,
    product: Product,
    *,
    produced: str,
    waste: str,
) -> ProductionItem:
    return ProductionItem(
        production_batch_id=batch_id,
        product_id=product.id,
        product_sku_snapshot=product.sku,
        product_name_snapshot=product.name,
        quantity_produced=Decimal(produced),
        quantity_waste=Decimal(waste),
    )


def _route_load(
    suffix: str,
    route_id: int,
    vehicle_id: int,
    source_id: int,
    destination_id: int,
    user_id: int,
    *,
    status: str = "active",
    voided_at: datetime | None = None,
) -> RouteLoad:
    return RouteLoad(
        load_number=f"LOAD-DAILY-{suffix}",
        load_date=REPORT_DATE,
        route_id=route_id,
        vehicle_id=vehicle_id,
        source_location_id=source_id,
        destination_location_id=destination_id,
        status=status,
        void_reason="Prueba controlada" if status == "voided" else None,
        voided_at=voided_at,
        created_by=user_id,
    )


def _movement(
    suffix: int,
    product: Product,
    location_id: int,
    user_id: int,
    movement_type: str,
    quantity: str,
) -> InventoryMovement:
    return InventoryMovement(
        movement_date=REPORT_DATE,
        movement_type=movement_type,
        product_id=product.id,
        location_id=location_id,
        product_sku_snapshot=product.sku,
        product_name_snapshot=product.name,
        quantity=Decimal(quantity),
        reason=f"Movimiento controlado {suffix}",
        status="active",
        created_by=user_id,
    )


def _route_return(
    suffix: str,
    load: RouteLoad,
    route_id: int,
    vehicle_id: int,
    source_id: int,
    destination_id: int,
    user_id: int,
    *,
    status: str = "active",
    voided_at: datetime | None = None,
) -> RouteReturn:
    return RouteReturn(
        return_number=f"RETURN-DAILY-{suffix}",
        return_date=REPORT_DATE,
        route_load_id=load.id,
        route_id=route_id,
        vehicle_id=vehicle_id,
        source_location_id=source_id,
        destination_location_id=destination_id,
        status=status,
        void_reason="Prueba controlada" if status == "voided" else None,
        voided_at=voided_at,
        created_by=user_id,
    )


def _closure(
    suffix: str,
    load: RouteLoad,
    route: DeliveryRoute,
    vehicle: Vehicle,
    user_id: int,
    *,
    expected: str,
    delivered: str,
    status: str = "active",
    voided_at: datetime | None = None,
) -> RouteClosure:
    expected_amount = Decimal(expected)
    delivered_amount = Decimal(delivered)
    return RouteClosure(
        closure_number=f"CLOSE-DAILY-{suffix}",
        closure_date=REPORT_DATE,
        route_load_id=load.id,
        route_id=route.id,
        vehicle_id=vehicle.id,
        load_number_snapshot=load.load_number,
        route_name_snapshot=route.name,
        vehicle_name_snapshot=vehicle.name,
        cash_sales_total=expected_amount,
        credit_sales_total=Decimal("0.00"),
        payments_total=Decimal("0.00"),
        expected_cash_total=expected_amount,
        delivered_cash_total=delivered_amount,
        difference_amount=delivered_amount - expected_amount,
        status=status,
        void_reason="Prueba controlada" if status == "voided" else None,
        voided_at=voided_at,
        created_by=user_id,
    )


def _receipt(
    suffix: str,
    closure: RouteClosure,
    cash_session_id: int,
    user_id: int,
    *,
    delivered: str,
    received: str,
    status: str = "active",
    voided_at: datetime | None = None,
) -> RouteCashReceipt:
    delivered_amount = Decimal(delivered)
    received_amount = Decimal(received)
    return RouteCashReceipt(
        receipt_number=f"RCR-DAILY-{suffix}",
        receipt_date=REPORT_DATE,
        route_closure_id=closure.id,
        cash_session_id=cash_session_id,
        route_load_id=closure.route_load_id,
        route_id=closure.route_id,
        vehicle_id=closure.vehicle_id,
        closure_number_snapshot=closure.closure_number,
        route_name_snapshot=closure.route_name_snapshot,
        vehicle_name_snapshot=closure.vehicle_name_snapshot,
        delivered_cash_total=delivered_amount,
        received_amount=received_amount,
        difference_amount=received_amount - delivered_amount,
        status=status,
        void_reason="Prueba controlada" if status == "voided" else None,
        voided_at=voided_at,
        created_by=user_id,
    )


def _sale(
    suffix: str,
    user_id: int,
    *,
    sale_type: str,
    total: str,
    paid: str,
    balance: str,
    customer: Customer | None = None,
    status: str = "active",
    voided_at: datetime | None = None,
) -> Sale:
    return Sale(
        sale_number=f"SALE-DAILY-{suffix}",
        sale_date=REPORT_DATE,
        customer_id=customer.id if customer is not None else None,
        customer_name_snapshot=customer.name if customer is not None else "Consumidor final",
        sale_type=sale_type,
        payment_method="cash",
        status=status,
        total_amount=Decimal(total),
        paid_amount=Decimal(paid),
        balance_amount=Decimal(balance),
        credit_status="pending" if sale_type == "credit" else "none",
        void_reason="Prueba controlada" if status == "voided" else None,
        voided_at=voided_at,
        created_by=user_id,
    )


def _sale_item(
    sale_id: int,
    product: Product,
    quantity: str,
    subtotal: str,
) -> SaleItem:
    quantity_amount = Decimal(quantity)
    subtotal_amount = Decimal(subtotal)
    return SaleItem(
        sale_id=sale_id,
        product_id=product.id,
        product_sku_snapshot=product.sku,
        product_name_snapshot=product.name,
        quantity=quantity_amount,
        unit_price=(subtotal_amount / quantity_amount).quantize(Decimal("0.01")),
        subtotal=subtotal_amount,
    )


def _database_snapshot(testing_session_local) -> dict[str, object]:
    models = [
        CashSession,
        CashCountItem,
        Expense,
        ProductionBatch,
        ProductionItem,
        RouteLoad,
        RouteLoadItem,
        RouteReturn,
        RouteReturnItem,
        RouteClosure,
        RouteCashReceipt,
        Sale,
        SaleItem,
        CreditPayment,
        InventoryMovement,
        InventoryStock,
    ]
    with testing_session_local() as session:
        cash_session = session.scalar(
            select(CashSession).where(CashSession.session_date == REPORT_DATE),
        )
        assert cash_session is not None
        return {
            "counts": {
                model.__tablename__: session.scalar(
                    select(func.count()).select_from(model),
                )
                for model in models
            },
            "cash_status": cash_session.status,
            "counted": tuple(
                session.execute(
                    select(
                        CashCountItem.id,
                        CashCountItem.quantity,
                        CashCountItem.subtotal,
                    ).order_by(CashCountItem.id),
                ),
            ),
            "sales": tuple(
                session.execute(
                    select(
                        Sale.id,
                        Sale.status,
                        Sale.total_amount,
                        Sale.balance_amount,
                    ).order_by(Sale.id),
                ),
            ),
            "payments": tuple(
                session.execute(
                    select(
                        CreditPayment.id,
                        CreditPayment.status,
                        CreditPayment.amount,
                    ).order_by(CreditPayment.id),
                ),
            ),
        }

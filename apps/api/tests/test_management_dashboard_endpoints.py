from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.cash_count_item import CashCountItem
from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.models.delivery_route import DeliveryRoute
from app.models.denomination import Denomination
from app.models.expense import Expense
from app.models.inventory_location import InventoryLocation
from app.models.inventory_stock import InventoryStock
from app.models.operating_expense import OperatingExpense
from app.models.operating_expense_category import OperatingExpenseCategory
from app.models.payroll_run import PayrollRun
from app.models.product import Product
from app.models.production_batch import ProductionBatch
from app.models.production_inventory_application import (
    ProductionInventoryApplication,
)
from app.models.production_item import ProductionItem
from app.models.production_material_consumption import (
    ProductionMaterialConsumption,
)
from app.models.purchase import Purchase
from app.models.route_cash_receipt import RouteCashReceipt
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.route_return import RouteReturn
from app.models.sale import Sale
from app.models.supplier import Supplier
from app.models.user import User
from app.models.vehicle import Vehicle

REPORT_URL = (
    "/api/v1/reports/management-dashboard"
    "?date_from=2026-07-01&date_to=2026-07-31"
)


def test_management_dashboard_requires_authentication(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/reports/management-dashboard")

    assert response.status_code == 401


def test_management_dashboard_uses_current_month_by_default(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    today = date.today()

    response = client.get(
        "/api/v1/reports/management-dashboard",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    period = response.json()["period"]
    assert period["date_from"] == today.replace(day=1).isoformat()
    assert period["date_to"][:7] == today.strftime("%Y-%m")


def test_management_dashboard_accepts_a_single_date_bound(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/reports/management-dashboard?date_from=2026-07-10",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["period"] == {
        "date_from": "2026-07-10",
        "date_to": "2026-07-10",
    }


def test_management_dashboard_rejects_inverted_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        (
            "/api/v1/reports/management-dashboard"
            "?date_from=2026-07-31&date_to=2026-07-01"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "La fecha hasta no puede ser menor que la fecha desde."
    )


def test_management_dashboard_returns_zeroes_and_empty_charts_without_data(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["cash"]["cash_sessions_count"] == 0
    assert body["sales"]["sales_total"] == "0.00"
    assert body["receivables"]["pending_balance_total"] == "0.00"
    assert body["operating_expenses"]["operating_expenses_total"] == "0.00"
    assert body["purchases"]["purchases_total"] == "0.00"
    assert body["production"]["production_batches_count"] == 0
    assert body["inventory"]["total_stock_quantity"] == "0.000"
    assert body["routes"]["route_closures_count"] == 0
    assert body["payroll"]["net_pay_total"] == "0.00"
    assert body["charts"] == {
        "daily_sales": [],
        "daily_cash": [],
        "daily_expenses": [],
        "production_by_product": [],
        "purchases_by_supplier": [],
    }
    assert body["alerts"] == []


def test_management_dashboard_calculates_cash_sales_and_receivables(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, _ = populated_management_dashboard

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["cash"] == {
        "cash_sessions_count": 1,
        "cash_total_counted": "100.00",
        "cash_total_expenses_after_count": "15.00",
        "cash_final_total": "85.00",
        "open_cash_sessions_count": 1,
        "closed_cash_sessions_count": 0,
    }
    assert body["sales"] == {
        "cash_sales_total": "100.00",
        "credit_sales_total": "60.00",
        "sales_total": "160.00",
        "active_sales_count": 2,
        "voided_sales_count": 1,
        "average_sale_amount": "80.00",
    }
    assert body["receivables"] == {
        "credit_sales_total": "60.00",
        "payments_total": "20.00",
        "pending_balance_total": "40.00",
        "customers_with_balance_count": 1,
        "overdue_balance_total": "40.00",
        "overdue_customers_count": 1,
    }


def test_management_dashboard_excludes_voided_expenses_and_purchases(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, _ = populated_management_dashboard

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["operating_expenses"] == {
        "operating_expenses_total": "35.00",
        "paid_expenses_total": "10.00",
        "unpaid_expenses_total": "25.00",
        "voided_expenses_count": 1,
        "top_categories": [
            {
                "category_id": body["operating_expenses"]["top_categories"][0][
                    "category_id"
                ],
                "category_name": "Combustible",
                "total_amount": "35.00",
            }
        ],
    }
    assert body["purchases"]["purchases_total"] == "130.00"
    assert body["purchases"]["active_purchases_count"] == 2
    assert body["purchases"]["voided_purchases_count"] == 1
    assert body["purchases"]["paid_purchases_total"] == "50.00"
    assert body["purchases"]["unpaid_purchases_total"] == "80.00"
    assert body["purchases"]["top_suppliers"][0]["supplier_name"] == (
        "Proveedor principal"
    )
    assert body["purchases"]["top_suppliers"][0]["total_amount"] == "130.00"


def test_management_dashboard_calculates_production_and_inventory_read_only(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, testing_session_local = populated_management_dashboard
    before = _stock_snapshot(testing_session_local)

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["production"] == {
        "production_batches_count": 1,
        "production_items_total_quantity": "12.000",
        "production_waste_total_quantity": "1.000",
        "production_applied_to_inventory_count": 1,
        "material_consumptions_count": 1,
        "material_consumptions_total_cost": "33.44",
    }
    assert body["inventory"]["active_locations_count"] == 2
    assert body["inventory"]["active_products_with_stock_count"] == 2
    assert body["inventory"]["total_stock_quantity"] == "14.000"
    assert len(body["inventory"]["low_stock_items"]) == 1
    assert body["inventory"]["low_stock_items"][0]["product_name"] == "Bidón 20L"
    assert body["inventory"]["low_stock_items"][0][
        "total_stock_quantity"
    ] == "4.000"
    assert body["inventory"]["low_stock_items"][0][
        "alert_threshold"
    ] == "5.000"
    assert _stock_snapshot(testing_session_local) == before


def test_management_dashboard_calculates_routes_and_payroll(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, _ = populated_management_dashboard

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["routes"] == {
        "route_loads_count": 1,
        "route_returns_count": 1,
        "route_closures_count": 1,
        "route_expected_cash_total": "80.00",
        "route_delivered_cash_total": "75.00",
        "route_difference_total": "-5.00",
        "route_cash_receipts_total": "75.00",
    }
    assert body["payroll"] == {
        "payroll_runs_count": 1,
        "gross_pay_total": "1000.00",
        "deductions_total": "100.00",
        "net_pay_total": "900.00",
        "voided_payroll_runs_count": 1,
    }


def test_management_dashboard_returns_chart_series(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, _ = populated_management_dashboard

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    charts = response.json()["charts"]
    assert charts["daily_sales"] == [
        {
            "date": "2026-07-10",
            "cash_sales_total": "100.00",
            "credit_sales_total": "60.00",
            "payments_total": "20.00",
        }
    ]
    assert charts["daily_cash"] == [
        {
            "date": "2026-07-10",
            "cash_total_counted": "100.00",
            "cash_final_total": "85.00",
        }
    ]
    assert charts["daily_expenses"] == [
        {
            "date": "2026-07-10",
            "operating_expenses_total": "35.00",
            "cash_expenses_total": "15.00",
        }
    ]
    assert charts["production_by_product"][0]["product_name"] == "Bidón 20L"
    assert charts["production_by_product"][0]["quantity_produced"] == "12.000"
    assert charts["purchases_by_supplier"][0]["total_amount"] == "130.00"


def test_management_dashboard_returns_management_alerts(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, _ = populated_management_dashboard

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    alerts = response.json()["alerts"]
    assert {alert["title"] for alert in alerts} == {
        "Cuadres abiertos",
        "Diferencias negativas en ruta",
        "Stock bajo",
        "Cartera vencida",
        "Gastos operativos pendientes",
        "Compras pendientes",
        "Nómina calculada",
    }
    assert all(alert["count"] > 0 for alert in alerts)
    assert alerts[-1]["type"] == "info"


def test_management_dashboard_does_not_create_or_modify_business_records(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, testing_session_local = populated_management_dashboard
    before = _business_record_counts(testing_session_local)

    response = client.get(REPORT_URL, headers=api_auth_headers)

    assert response.status_code == 200
    assert _business_record_counts(testing_session_local) == before


def test_management_dashboard_returns_zeroes_for_range_without_records(
    populated_management_dashboard,
    api_auth_headers,
) -> None:
    client, _ = populated_management_dashboard

    response = client.get(
        (
            "/api/v1/reports/management-dashboard"
            "?date_from=2025-01-01&date_to=2025-01-31"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sales"]["sales_total"] == "0.00"
    assert body["production"]["production_batches_count"] == 0
    assert body["charts"]["daily_sales"] == []
    assert body["charts"]["daily_cash"] == []


def _stock_snapshot(testing_session_local) -> list[tuple[int, int, str]]:
    with testing_session_local() as session:
        rows = session.execute(
            select(
                InventoryStock.product_id,
                InventoryStock.location_id,
                InventoryStock.quantity_on_hand,
            ).order_by(InventoryStock.id)
        ).all()
        return [
            (product_id, location_id, str(quantity))
            for product_id, location_id, quantity in rows
        ]


def _business_record_counts(testing_session_local) -> dict[str, int]:
    models = [
        CashSession,
        Sale,
        CreditPayment,
        Expense,
        OperatingExpense,
        Purchase,
        InventoryStock,
        ProductionBatch,
        ProductionInventoryApplication,
        ProductionMaterialConsumption,
        RouteLoad,
        RouteReturn,
        RouteClosure,
        RouteCashReceipt,
        PayrollRun,
    ]
    with testing_session_local() as session:
        return {
            model.__tablename__: int(
                session.scalar(select(func.count()).select_from(model)) or 0
            )
            for model in models
        }


def _seed_management_data(testing_session_local) -> None:
    report_date = date(2026, 7, 10)
    voided_at = datetime(2026, 7, 10, 18, 0, tzinfo=timezone.utc)
    with testing_session_local() as session:
        user = session.scalar(select(User).where(User.username == "admin"))
        assert user is not None

        customer = Customer(
            name="Cliente crédito",
            credit_allowed=True,
            credit_limit=Decimal("500.00"),
        )
        supplier = Supplier(name="Proveedor principal")
        category = OperatingExpenseCategory(name="Combustible")
        product = Product(
            sku="B20",
            name="Bidón 20L",
            category="water",
            unit="unit",
            default_price=Decimal("2.00"),
            cost_estimate=Decimal("1.00"),
            product_kind="finished_good",
        )
        second_product = Product(
            sku="BOT",
            name="Botella 1L",
            category="water",
            unit="unit",
            default_price=Decimal("1.00"),
            cost_estimate=Decimal("0.50"),
            product_kind="finished_good",
        )
        vehicle = Vehicle(
            name="Camión 1",
            vehicle_type="truck",
            fuel_type="diesel",
        )
        route = DeliveryRoute(
            name="Ruta centro",
            expected_daily_cash=Decimal("80.00"),
        )
        warehouse = InventoryLocation(
            code="BOD",
            name="Bodega",
            location_type="warehouse",
        )
        truck_location = InventoryLocation(
            code="CAM",
            name="Camión",
            location_type="vehicle",
            vehicle=vehicle,
        )
        inactive_location = InventoryLocation(
            code="OLD",
            name="Bodega inactiva",
            location_type="warehouse",
            is_active=False,
        )
        denomination = Denomination(
            type="bill",
            value=Decimal("10.00"),
            label="$10",
        )
        session.add_all(
            [
                customer,
                supplier,
                category,
                product,
                second_product,
                vehicle,
                route,
                warehouse,
                truck_location,
                inactive_location,
                denomination,
            ]
        )
        session.flush()

        cash_session = CashSession(
            session_date=report_date,
            status="open",
            created_by=user.id,
        )
        route_load = RouteLoad(
            load_number="CAR-001",
            load_date=report_date,
            route_id=route.id,
            vehicle_id=vehicle.id,
            source_location_id=warehouse.id,
            destination_location_id=truck_location.id,
            status="active",
            created_by=user.id,
        )
        voided_route_load = RouteLoad(
            load_number="CAR-VOID",
            load_date=report_date,
            route_id=route.id,
            vehicle_id=vehicle.id,
            source_location_id=warehouse.id,
            destination_location_id=truck_location.id,
            status="voided",
            void_reason="Prueba",
            voided_at=voided_at,
            created_by=user.id,
        )
        production_batch = ProductionBatch(
            production_number="PROD-001",
            production_date=report_date,
            status="active",
            created_by=user.id,
        )
        voided_batch = ProductionBatch(
            production_number="PROD-VOID",
            production_date=report_date,
            status="voided",
            void_reason="Prueba",
            voided_at=voided_at,
            created_by=user.id,
        )
        session.add_all(
            [
                cash_session,
                route_load,
                voided_route_load,
                production_batch,
                voided_batch,
                InventoryStock(
                    product_id=product.id,
                    location_id=warehouse.id,
                    quantity_on_hand=Decimal("4.000"),
                ),
                InventoryStock(
                    product_id=second_product.id,
                    location_id=warehouse.id,
                    quantity_on_hand=Decimal("10.000"),
                ),
            ]
        )
        session.flush()

        active_cash_sale = Sale(
            sale_number="VTA-CASH",
            sale_date=report_date,
            customer_name_snapshot="Consumidor final",
            sale_type="cash",
            payment_method="cash",
            status="active",
            total_amount=Decimal("100.00"),
            paid_amount=Decimal("100.00"),
            balance_amount=Decimal("0.00"),
            credit_status="none",
            created_by=user.id,
        )
        active_credit_sale = Sale(
            sale_number="VTA-CREDIT",
            sale_date=report_date,
            customer_id=customer.id,
            customer_name_snapshot=customer.name,
            sale_type="credit",
            payment_method="cash",
            status="active",
            total_amount=Decimal("60.00"),
            paid_amount=Decimal("20.00"),
            balance_amount=Decimal("40.00"),
            credit_status="pending",
            due_date=date(2026, 7, 15),
            created_by=user.id,
        )
        voided_sale = Sale(
            sale_number="VTA-VOID",
            sale_date=report_date,
            customer_name_snapshot="Anulada",
            sale_type="cash",
            payment_method="cash",
            status="voided",
            total_amount=Decimal("999.00"),
            paid_amount=Decimal("999.00"),
            balance_amount=Decimal("0.00"),
            credit_status="none",
            void_reason="Prueba",
            voided_at=voided_at,
            created_by=user.id,
        )
        session.add_all([active_cash_sale, active_credit_sale, voided_sale])
        session.flush()

        route_closure = RouteClosure(
            closure_number="CIE-001",
            closure_date=report_date,
            route_load_id=route_load.id,
            route_id=route.id,
            vehicle_id=vehicle.id,
            load_number_snapshot=route_load.load_number,
            route_name_snapshot=route.name,
            vehicle_name_snapshot=vehicle.name,
            cash_sales_total=Decimal("70.00"),
            credit_sales_total=Decimal("20.00"),
            payments_total=Decimal("10.00"),
            expected_cash_total=Decimal("80.00"),
            delivered_cash_total=Decimal("75.00"),
            difference_amount=Decimal("-5.00"),
            status="active",
            created_by=user.id,
        )
        voided_route_closure = RouteClosure(
            closure_number="CIE-VOID",
            closure_date=report_date,
            route_load_id=voided_route_load.id,
            route_id=route.id,
            vehicle_id=vehicle.id,
            load_number_snapshot=voided_route_load.load_number,
            route_name_snapshot=route.name,
            vehicle_name_snapshot=vehicle.name,
            cash_sales_total=Decimal("999.00"),
            credit_sales_total=Decimal("0.00"),
            payments_total=Decimal("0.00"),
            expected_cash_total=Decimal("999.00"),
            delivered_cash_total=Decimal("999.00"),
            difference_amount=Decimal("0.00"),
            status="voided",
            void_reason="Prueba",
            voided_at=voided_at,
            created_by=user.id,
        )
        session.add_all([route_closure, voided_route_closure])
        session.flush()

        session.add_all(
            [
                CashCountItem(
                    cash_session_id=cash_session.id,
                    denomination_id=denomination.id,
                    quantity=10,
                    subtotal=Decimal("100.00"),
                ),
                Expense(
                    cash_session_id=cash_session.id,
                    description="Gasto posterior",
                    amount=Decimal("15.00"),
                    expense_timing="after_count",
                    expense_date=report_date,
                ),
                CreditPayment(
                    sale_id=active_credit_sale.id,
                    customer_id=customer.id,
                    payment_date=report_date,
                    amount=Decimal("20.00"),
                    payment_method="cash",
                    status="active",
                    created_by=user.id,
                ),
                CreditPayment(
                    sale_id=active_credit_sale.id,
                    customer_id=customer.id,
                    payment_date=report_date,
                    amount=Decimal("999.00"),
                    payment_method="cash",
                    status="voided",
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
                OperatingExpense(
                    expense_number="GOP-PAID",
                    expense_date=report_date,
                    category_id=category.id,
                    description="Gasto pagado",
                    amount=Decimal("10.00"),
                    payment_status="paid",
                    payment_method="cash",
                    status="active",
                    created_by=user.id,
                ),
                OperatingExpense(
                    expense_number="GOP-UNPAID",
                    expense_date=report_date,
                    category_id=category.id,
                    description="Gasto pendiente",
                    amount=Decimal("25.00"),
                    payment_status="unpaid",
                    payment_method="unknown",
                    status="active",
                    created_by=user.id,
                ),
                OperatingExpense(
                    expense_number="GOP-VOID",
                    expense_date=report_date,
                    category_id=category.id,
                    description="Gasto anulado",
                    amount=Decimal("999.00"),
                    payment_status="unpaid",
                    payment_method="unknown",
                    status="voided",
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
                Purchase(
                    purchase_number="COM-PAID",
                    supplier_id=supplier.id,
                    purchase_date=report_date,
                    status="active",
                    payment_status="paid",
                    subtotal_amount=Decimal("50.00"),
                    discount_amount=Decimal("0.00"),
                    tax_amount=Decimal("0.00"),
                    total_amount=Decimal("50.00"),
                    created_by=user.id,
                ),
                Purchase(
                    purchase_number="COM-UNPAID",
                    supplier_id=supplier.id,
                    purchase_date=report_date,
                    status="active",
                    payment_status="unpaid",
                    subtotal_amount=Decimal("80.00"),
                    discount_amount=Decimal("0.00"),
                    tax_amount=Decimal("0.00"),
                    total_amount=Decimal("80.00"),
                    created_by=user.id,
                ),
                Purchase(
                    purchase_number="COM-VOID",
                    supplier_id=supplier.id,
                    purchase_date=report_date,
                    status="voided",
                    payment_status="unpaid",
                    subtotal_amount=Decimal("999.00"),
                    discount_amount=Decimal("0.00"),
                    tax_amount=Decimal("0.00"),
                    total_amount=Decimal("999.00"),
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
                ProductionItem(
                    production_batch_id=production_batch.id,
                    product_id=product.id,
                    product_sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    quantity_produced=Decimal("12.000"),
                    quantity_waste=Decimal("1.000"),
                ),
                ProductionItem(
                    production_batch_id=voided_batch.id,
                    product_id=product.id,
                    product_sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    quantity_produced=Decimal("999.000"),
                    quantity_waste=Decimal("0.000"),
                ),
                ProductionInventoryApplication(
                    production_batch_id=production_batch.id,
                    location_id=warehouse.id,
                    status="active",
                    applied_at=voided_at,
                    created_by=user.id,
                ),
                ProductionMaterialConsumption(
                    consumption_number="CON-001",
                    production_batch_id=production_batch.id,
                    source_location_id=warehouse.id,
                    movement_date=report_date,
                    status="active",
                    total_material_cost=Decimal("33.4400"),
                    created_by=user.id,
                ),
                ProductionMaterialConsumption(
                    consumption_number="CON-VOID",
                    production_batch_id=production_batch.id,
                    source_location_id=warehouse.id,
                    movement_date=report_date,
                    status="voided",
                    total_material_cost=Decimal("999.0000"),
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
                RouteReturn(
                    return_number="RET-001",
                    return_date=report_date,
                    route_load_id=route_load.id,
                    route_id=route.id,
                    vehicle_id=vehicle.id,
                    source_location_id=truck_location.id,
                    destination_location_id=warehouse.id,
                    status="active",
                    created_by=user.id,
                ),
                RouteReturn(
                    return_number="RET-VOID",
                    return_date=report_date,
                    route_load_id=voided_route_load.id,
                    route_id=route.id,
                    vehicle_id=vehicle.id,
                    source_location_id=truck_location.id,
                    destination_location_id=warehouse.id,
                    status="voided",
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
                RouteCashReceipt(
                    receipt_number="RCR-001",
                    receipt_date=report_date,
                    route_closure_id=route_closure.id,
                    cash_session_id=cash_session.id,
                    route_load_id=route_load.id,
                    route_id=route.id,
                    vehicle_id=vehicle.id,
                    closure_number_snapshot=route_closure.closure_number,
                    route_name_snapshot=route.name,
                    vehicle_name_snapshot=vehicle.name,
                    delivered_cash_total=Decimal("75.00"),
                    received_amount=Decimal("75.00"),
                    difference_amount=Decimal("0.00"),
                    status="active",
                    created_by=user.id,
                ),
                RouteCashReceipt(
                    receipt_number="RCR-VOID",
                    receipt_date=report_date,
                    route_closure_id=voided_route_closure.id,
                    cash_session_id=cash_session.id,
                    route_load_id=voided_route_load.id,
                    route_id=route.id,
                    vehicle_id=vehicle.id,
                    closure_number_snapshot=voided_route_closure.closure_number,
                    route_name_snapshot=route.name,
                    vehicle_name_snapshot=vehicle.name,
                    delivered_cash_total=Decimal("999.00"),
                    received_amount=Decimal("999.00"),
                    difference_amount=Decimal("0.00"),
                    status="voided",
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
                PayrollRun(
                    payroll_number="ROL-001",
                    period_start=date(2026, 7, 1),
                    period_end=date(2026, 7, 15),
                    payroll_date=report_date,
                    status="active",
                    employees_count=1,
                    gross_total=Decimal("1000.00"),
                    bonuses_total=Decimal("0.00"),
                    advances_deducted_total=Decimal("0.00"),
                    loan_deductions_total=Decimal("0.00"),
                    other_deductions_total=Decimal("100.00"),
                    total_deductions=Decimal("100.00"),
                    net_pay_total=Decimal("900.00"),
                    created_by=user.id,
                ),
                PayrollRun(
                    payroll_number="ROL-VOID",
                    period_start=date(2026, 7, 1),
                    period_end=date(2026, 7, 15),
                    payroll_date=report_date,
                    status="voided",
                    employees_count=1,
                    gross_total=Decimal("999.00"),
                    bonuses_total=Decimal("0.00"),
                    advances_deducted_total=Decimal("0.00"),
                    loan_deductions_total=Decimal("0.00"),
                    other_deductions_total=Decimal("0.00"),
                    total_deductions=Decimal("0.00"),
                    net_pay_total=Decimal("999.00"),
                    void_reason="Prueba",
                    voided_at=voided_at,
                    created_by=user.id,
                ),
            ]
        )
        session.commit()
@pytest.fixture
def populated_management_dashboard(api_client, api_auth_headers):
    _, testing_session_local = api_client
    _seed_management_data(testing_session_local)
    return api_client

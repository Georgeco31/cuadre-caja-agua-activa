import importlib.util
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.delivery_route import DeliveryRoute
from app.models.inventory_location import InventoryLocation
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.sale import Sale
from app.models.sale_date_correction import SaleDateCorrection
from app.models.user import User
from app.models.vehicle import Vehicle


def test_admin_corrects_cash_sale_with_audit_reports_and_immutable_values(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])
    original_snapshot = _sale_business_snapshot(sale)

    response = _correct_sale(
        client,
        api_auth_headers,
        sale["id"],
        new_sale_date="2026-06-30",
        reason="La fecha fue digitada un día adelante",
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["sale"]["sale_date"] == "2026-06-30"
    assert body["previous_sale_date"] == "2026-07-28"
    assert body["new_sale_date"] == "2026-06-30"
    assert body["reason"] == "La fecha fue digitada un día adelante"
    assert body["correction_type"] == "date_change"
    assert _sale_business_snapshot(body["sale"]) == original_snapshot

    old_report = client.get(
        "/api/v1/reports/daily-operational-summary?date=2026-07-28",
        headers=api_auth_headers,
    )
    new_report = client.get(
        "/api/v1/reports/daily-operational-summary?date=2026-06-30",
        headers=api_auth_headers,
    )
    assert old_report.status_code == 200
    assert new_report.status_code == 200
    assert old_report.json()["sales_summary"]["cash_sales_count"] == 0
    assert new_report.json()["sales_summary"]["cash_sales_count"] == 1
    assert new_report.json()["sales_summary"]["cash_sales_total"] == "10.00"
    old_month = client.get(
        "/api/v1/reports/monthly-operational-summary?year=2026&month=7",
        headers=api_auth_headers,
    )
    new_month = client.get(
        "/api/v1/reports/monthly-operational-summary?year=2026&month=6",
        headers=api_auth_headers,
    )
    assert old_month.status_code == 200
    assert new_month.status_code == 200
    assert old_month.json()["sales_summary"]["cash_sales_count"] == 0
    assert new_month.json()["sales_summary"]["cash_sales_count"] == 1
    assert new_month.json()["sales_summary"]["cash_sales_total"] == "10.00"

    with testing_session_local() as session:
        stored_sale = session.get(Sale, sale["id"])
        corrections = session.query(SaleDateCorrection).all()
        assert stored_sale is not None
        assert stored_sale.sale_date.isoformat() == "2026-06-30"
        assert session.query(Sale).count() == 1
        assert len(corrections) == 1
        audit = corrections[0]
        admin = session.query(User).filter(User.username == "admin").one()
        assert audit.sale_id == sale["id"]
        assert audit.previous_sale_date.isoformat() == "2026-07-28"
        assert audit.new_sale_date.isoformat() == "2026-06-30"
        assert audit.reason == "La fecha fue digitada un día adelante"
        assert audit.created_by == admin.id
        assert audit.created_at is not None

    voided = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Prueba de regresión de anulación"},
    )
    assert voided.status_code == 200, voided.text
    assert voided.json()["status"] == "voided"


def test_admin_corrects_credit_sale_without_changing_payment(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    customer = _create_customer(client, api_auth_headers)
    sale = _create_credit_sale(
        client,
        api_auth_headers,
        customer["id"],
        product["id"],
    )
    payment_response = client.post(
        f"/api/v1/sales/{sale['id']}/payments",
        headers=api_auth_headers,
        json={
            "payment_date": "2026-07-29",
            "amount": "3.00",
            "payment_method": "cash",
        },
    )
    assert payment_response.status_code == 201, payment_response.text
    payment = payment_response.json()
    sale_before = client.get(
        f"/api/v1/sales/{sale['id']}",
        headers=api_auth_headers,
    ).json()

    response = _correct_sale(
        client,
        api_auth_headers,
        sale["id"],
        new_sale_date="2026-07-26",
        reason="Venta real registrada con fecha incorrecta",
    )

    assert response.status_code == 200, response.text
    corrected_sale = response.json()["sale"]
    assert corrected_sale["sale_type"] == "credit"
    assert corrected_sale["sale_date"] == "2026-07-26"
    assert corrected_sale["total_amount"] == sale_before["total_amount"]
    assert corrected_sale["paid_amount"] == sale_before["paid_amount"]
    assert corrected_sale["balance_amount"] == sale_before["balance_amount"]
    assert corrected_sale["credit_status"] == sale_before["credit_status"]
    assert corrected_sale["customer_id"] == sale_before["customer_id"]
    assert corrected_sale["items"] == sale_before["items"]

    with testing_session_local() as session:
        stored_payment = session.get(CreditPayment, payment["id"])
        assert stored_payment is not None
        assert stored_payment.payment_date.isoformat() == "2026-07-29"
        assert stored_payment.amount == Decimal("3.00")
        assert stored_payment.status == "active"


def test_operator_receives_specific_403_for_sale_date_correction(
    api_client,
    api_auth_headers,
    api_operator_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])

    response = _correct_sale(
        client,
        api_operator_auth_headers,
        sale["id"],
        new_sale_date="2026-07-27",
        reason="Intento no autorizado",
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "No tienes permiso para corregir ventas. "
        "Solicita autorización a George."
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"new_sale_date": "2026-07-27", "reason": ""},
        {"new_sale_date": "2026-07-27", "reason": "   "},
        {"new_sale_date": "2026-02-30", "reason": "Fecha imposible"},
        {"new_sale_date": "27-07-2026", "reason": "Formato incorrecto"},
    ],
)
def test_sale_date_correction_rejects_invalid_payload(
    api_client,
    api_auth_headers,
    payload,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])

    response = client.patch(
        f"/api/v1/sales/{sale['id']}/date",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_sale_date_correction_returns_404_for_missing_sale(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = _correct_sale(
        client,
        api_auth_headers,
        999,
        new_sale_date="2026-07-27",
        reason="Venta no existente",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La venta no existe."


def test_sale_date_correction_rejects_voided_sale(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])
    voided = client.post(
        f"/api/v1/sales/{sale['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Venta anulada para la prueba"},
    )
    assert voided.status_code == 200

    response = _correct_sale(
        client,
        api_auth_headers,
        sale["id"],
        new_sale_date="2026-07-27",
        reason="No debe aceptarse",
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "La venta anulada no puede corregirse."


def test_sale_date_correction_rejects_same_date(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])

    response = _correct_sale(
        client,
        api_auth_headers,
        sale["id"],
        new_sale_date=sale["sale_date"],
        reason="No existe cambio",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "La nueva fecha debe ser diferente de la fecha actual."
    )


@pytest.mark.parametrize("closed_date", ["2026-07-28", "2026-07-27"])
def test_sale_date_correction_rejects_closed_cash_dates(
    api_client,
    api_auth_headers,
    closed_date: str,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])
    with testing_session_local() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(
            CashSession(
                session_date=datetime.fromisoformat(closed_date).date(),
                status="closed",
                created_by=admin.id,
                closed_at=datetime.now(UTC),
            ),
        )
        session.commit()

    response = _correct_sale(
        client,
        api_auth_headers,
        sale["id"],
        new_sale_date="2026-07-27",
        reason="No debe mover un cierre de caja",
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "La fecha no puede corregirse porque la venta está ligada "
        "a un cierre de caja."
    )


def test_sale_date_correction_rejects_active_route_closure(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    sale = _create_cash_sale(client, api_auth_headers, product["id"])
    with testing_session_local() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        route = DeliveryRoute(code="CORR-ROUTE", name="Ruta cerrada")
        vehicle = Vehicle(code="CORR-VEHICLE", name="Vehículo cerrado")
        session.add_all([route, vehicle])
        session.flush()
        source = InventoryLocation(
            code="CORR-SOURCE",
            name="Bodega corrección",
            location_type="warehouse",
        )
        destination = InventoryLocation(
            code="CORR-DESTINATION",
            name="Vehículo corrección",
            location_type="vehicle",
            vehicle_id=vehicle.id,
        )
        session.add_all([source, destination])
        session.flush()
        route_load = RouteLoad(
            load_number="LOAD-CORRECTION-CLOSED",
            load_date=datetime(2026, 7, 28).date(),
            route_id=route.id,
            vehicle_id=vehicle.id,
            source_location_id=source.id,
            destination_location_id=destination.id,
            status="active",
            created_by=admin.id,
        )
        session.add(route_load)
        session.flush()
        stored_sale = session.get(Sale, sale["id"])
        assert stored_sale is not None
        stored_sale.route_load_id = route_load.id
        session.add(
            RouteClosure(
                closure_number="CLOSE-CORRECTION-0001",
                closure_date=datetime(2026, 7, 28).date(),
                route_load_id=route_load.id,
                route_id=route.id,
                vehicle_id=vehicle.id,
                load_number_snapshot=route_load.load_number,
                route_name_snapshot=route.name,
                vehicle_name_snapshot=vehicle.name,
                cash_sales_total=Decimal("10.00"),
                credit_sales_total=Decimal("0.00"),
                payments_total=Decimal("0.00"),
                expected_cash_total=Decimal("10.00"),
                delivered_cash_total=Decimal("10.00"),
                difference_amount=Decimal("0.00"),
                status="active",
                created_by=admin.id,
            ),
        )
        session.commit()

    response = _correct_sale(
        client,
        api_auth_headers,
        sale["id"],
        new_sale_date="2026-07-27",
        reason="No debe mover un cierre de ruta",
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "La fecha no puede corregirse porque la venta está ligada a un cierre."
    )


def test_sale_date_correction_requires_authentication(api_client) -> None:
    client, _ = api_client

    response = client.patch(
        "/api/v1/sales/1/date",
        json={
            "new_sale_date": "2026-07-27",
            "reason": "Sin sesión",
        },
    )

    assert response.status_code == 401


def test_sale_date_correction_migration_follows_current_head() -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0027_sales_date_corrections.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0027_sale_date_corrections",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "0027_sale_date_corrections"
    assert migration.down_revision == "0026_user_roles"
    assert len(migration.revision) <= 32


def _create_product(client, headers) -> dict:
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": "CORR-DATE-PRODUCT",
            "name": "Producto corrección fecha",
            "category": "water",
            "unit": "container",
            "presentation": "20 L",
            "default_price": "10.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_customer(client, headers) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": "Cliente corrección fecha",
            "credit_allowed": True,
            "credit_limit": "100.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_cash_sale(client, headers, product_id: int) -> dict:
    response = client.post(
        "/api/v1/sales/cash",
        headers=headers,
        json={
            "sale_date": "2026-07-28",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": "1",
                    "unit_price": "10.00",
                },
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_credit_sale(
    client,
    headers,
    customer_id: int,
    product_id: int,
) -> dict:
    response = client.post(
        "/api/v1/sales/credit",
        headers=headers,
        json={
            "sale_date": "2026-07-28",
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": "1",
                    "unit_price": "10.00",
                },
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _correct_sale(
    client,
    headers,
    sale_id: int,
    *,
    new_sale_date: str,
    reason: str,
):
    return client.patch(
        f"/api/v1/sales/{sale_id}/date",
        headers=headers,
        json={
            "new_sale_date": new_sale_date,
            "reason": reason,
        },
    )


def _sale_business_snapshot(sale: dict) -> dict:
    return {
        "id": sale["id"],
        "sale_number": sale["sale_number"],
        "customer_id": sale["customer_id"],
        "customer_name_snapshot": sale["customer_name_snapshot"],
        "sale_type": sale["sale_type"],
        "payment_method": sale["payment_method"],
        "status": sale["status"],
        "total_amount": sale["total_amount"],
        "paid_amount": sale["paid_amount"],
        "balance_amount": sale["balance_amount"],
        "credit_status": sale["credit_status"],
        "due_date": sale["due_date"],
        "void_reason": sale["void_reason"],
        "voided_at": sale["voided_at"],
        "items": sale["items"],
    }

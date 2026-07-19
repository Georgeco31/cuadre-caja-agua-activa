import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.production_inventory_application import (
    ProductionInventoryApplication,
)
from app.models.production_inventory_application_item import (
    ProductionInventoryApplicationItem,
)
from app.models.production_item import ProductionItem


def test_production_does_not_change_inventory_before_application(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])

    status_response = client.get(
        f"/api/v1/production/batches/{production['id']}/inventory-application",
        headers=api_auth_headers,
    )

    assert status_response.status_code == 200
    assert status_response.json() == {
        "state": "not_applied",
        "application_id": None,
        "production_batch_id": production["id"],
        "location_id": None,
        "location_name": None,
        "status": None,
        "applied_at": None,
        "void_reason": None,
        "voided_at": None,
        "created_by": None,
        "created_at": None,
        "updated_at": None,
        "items": [],
    }
    with testing_session_local() as session:
        assert session.query(InventoryMovement).count() == 0
        assert session.query(InventoryStock).count() == 0
        assert session.query(ProductionInventoryApplication).count() == 0


def test_apply_production_creates_net_entry_and_traceability(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers, cost_estimate="0.40")
    location = _create_location(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product["id"],
        quantity_produced="500",
        quantity_waste="5",
    )

    response = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
        notes="Ingreso de planta",
    )

    assert response.status_code == 201, response.json()
    application = response.json()
    assert application["state"] == "applied"
    assert application["status"] == "active"
    assert application["location_id"] == location["id"]
    assert application["location_name"] == location["name"]
    assert len(application["items"]) == 1
    assert Decimal(application["items"][0]["quantity_applied"]) == Decimal(
        "495.000",
    )
    status_response = client.get(
        f"/api/v1/production/batches/{production['id']}/inventory-application",
        headers=api_auth_headers,
    )
    assert status_response.status_code == 200
    assert status_response.json()["application_id"] == application["application_id"]
    assert status_response.json()["state"] == "applied"

    movement_id = application["items"][0]["inventory_movement_id"]
    with testing_session_local() as session:
        movement = session.get(InventoryMovement, movement_id)
        stock = session.query(InventoryStock).one()
        stored_application = session.get(
            ProductionInventoryApplication,
            application["application_id"],
        )
        stored_item = session.query(ProductionInventoryApplicationItem).one()
        assert movement is not None
        assert movement.movement_type == "entry"
        assert movement.status == "active"
        assert movement.movement_date.isoformat() == "2026-07-18"
        assert movement.quantity == Decimal("495.000")
        assert movement.unit_cost == Decimal("0.40")
        assert movement.total_cost == Decimal("198.00")
        assert movement.reason == (
            f"Produccion {production['production_number']} - Ingreso de planta"
        )
        assert stock.quantity_on_hand == Decimal("495.000")
        assert stored_application is not None
        assert stored_application.status == "active"
        assert stored_item.inventory_movement_id == movement.id


def test_apply_skips_zero_net_items(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    first = _create_product(client, api_auth_headers, sku="PROD-A")
    second = _create_product(client, api_auth_headers, sku="PROD-B")
    location = _create_location(client, api_auth_headers)
    production = _create_production_with_items(
        client,
        api_auth_headers,
        [
            _item(first["id"], "10", "10"),
            _item(second["id"], "8", "1.5"),
        ],
    )

    response = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    assert response.status_code == 201
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["product_id"] == second["id"]
    assert Decimal(response.json()["items"][0]["quantity_applied"]) == Decimal(
        "6.500",
    )
    with testing_session_local() as session:
        assert session.query(InventoryMovement).count() == 1
        assert session.query(InventoryStock).count() == 1


def test_apply_rejects_production_without_net_quantity(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product["id"],
        quantity_produced="10",
        quantity_waste="10",
    )

    response = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "La produccion no tiene cantidad neta para inventario."
    )
    with testing_session_local() as session:
        assert session.query(ProductionInventoryApplication).count() == 0
        assert session.query(InventoryMovement).count() == 0


def test_production_rejects_waste_greater_than_produced(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = client.post(
        "/api/v1/production/batches",
        headers=api_auth_headers,
        json={
            "production_date": "2026-07-18",
            "items": [_item(product["id"], "5", "5.001")],
        },
    )

    assert response.status_code == 422
    assert "merma no puede ser mayor" in str(response.json())


def test_apply_rejects_voided_batch(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    _void_production(client, api_auth_headers, production["id"])

    response = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    assert response.status_code == 400
    with testing_session_local() as session:
        assert session.query(ProductionInventoryApplication).count() == 0


def test_apply_requires_existing_active_location(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    deactivate = client.patch(
        f"/api/v1/inventory/locations/{location['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    missing = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        999,
    )
    inactive = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert "ubicacion inactiva" in inactive.json()["detail"]


def test_apply_is_atomic_if_a_product_became_inactive(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    first = _create_product(client, api_auth_headers, sku="PROD-A")
    second = _create_product(client, api_auth_headers, sku="PROD-B")
    location = _create_location(client, api_auth_headers)
    production = _create_production_with_items(
        client,
        api_auth_headers,
        [_item(first["id"], "10"), _item(second["id"], "20")],
    )
    deactivate = client.patch(
        f"/api/v1/products/{second['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    response = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    assert response.status_code == 400
    with testing_session_local() as session:
        assert session.query(ProductionInventoryApplication).count() == 0
        assert session.query(ProductionInventoryApplicationItem).count() == 0
        assert session.query(InventoryMovement).count() == 0
        assert session.query(InventoryStock).count() == 0


def test_batch_accepts_only_one_active_application(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    first = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    second = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )

    assert first.status_code == 201
    assert second.status_code == 409
    with testing_session_local() as session:
        assert session.query(ProductionInventoryApplication).count() == 1
        assert session.query(InventoryMovement).count() == 1


def test_active_application_blocks_production_void(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    applied = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )
    assert applied.status_code == 201

    response = client.post(
        f"/api/v1/production/batches/{production['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Registro incorrecto"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Primero anule la aplicacion a inventario antes de anular la produccion."
    )


def test_void_application_reverses_stock_and_preserves_history(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product["id"],
        quantity_produced="12",
        quantity_waste="2",
    )
    applied = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    ).json()

    response = _void_application(
        client,
        api_auth_headers,
        applied["application_id"],
    )

    assert response.status_code == 200, response.json()
    voided = response.json()
    assert voided["state"] == "voided"
    assert voided["status"] == "voided"
    assert voided["void_reason"] == "Aplicacion incorrecta"
    assert voided["voided_at"] is not None
    with testing_session_local() as session:
        application = session.get(
            ProductionInventoryApplication,
            applied["application_id"],
        )
        movement = session.get(
            InventoryMovement,
            applied["items"][0]["inventory_movement_id"],
        )
        stock = session.query(InventoryStock).one()
        assert application is not None
        assert application.status == "voided"
        assert movement is not None
        assert movement.status == "voided"
        assert movement.void_reason == (
            "Aplicacion de produccion anulada: Aplicacion incorrecta"
        )
        assert stock.quantity_on_hand == Decimal("0.000")
        assert session.query(ProductionInventoryApplicationItem).count() == 1
        assert session.query(ProductionItem).count() == 1


def test_void_application_cannot_be_repeated(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    applied = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    ).json()
    first_void = _void_application(
        client,
        api_auth_headers,
        applied["application_id"],
    )
    assert first_void.status_code == 200

    second_void = _void_application(
        client,
        api_auth_headers,
        applied["application_id"],
    )

    assert second_void.status_code == 409


def test_void_application_rolls_back_when_stock_is_insufficient(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product["id"],
        quantity_produced="10",
    )
    applied = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    ).json()
    exit_response = _create_manual_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        "exit",
        "4",
    )
    assert exit_response.status_code == 201

    response = _void_application(
        client,
        api_auth_headers,
        applied["application_id"],
    )

    assert response.status_code == 400
    assert "stock actual es insuficiente" in response.json()["detail"]
    with testing_session_local() as session:
        application = session.get(
            ProductionInventoryApplication,
            applied["application_id"],
        )
        movement = session.get(
            InventoryMovement,
            applied["items"][0]["inventory_movement_id"],
        )
        stock = session.query(InventoryStock).one()
        assert application is not None
        assert application.status == "active"
        assert movement is not None
        assert movement.status == "active"
        assert stock.quantity_on_hand == Decimal("6.000")


def test_generated_movement_cannot_be_voided_directly(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    applied = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    ).json()

    response = client.post(
        "/api/v1/inventory/movements/"
        f"{applied['items'][0]['inventory_movement_id']}/void",
        headers=api_auth_headers,
        json={"reason": "Intento manual"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Anule la aplicacion a inventario desde produccion."
    )


def test_voided_application_allows_reapply_and_production_void_afterward(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    location = _create_location(client, api_auth_headers)
    production = _create_production(client, api_auth_headers, product["id"])
    first = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    ).json()
    assert _void_application(
        client,
        api_auth_headers,
        first["application_id"],
    ).status_code == 200

    second_response = _apply_inventory(
        client,
        api_auth_headers,
        production["id"],
        location["id"],
    )
    assert second_response.status_code == 201
    second = second_response.json()
    assert second["application_id"] != first["application_id"]
    assert _void_application(
        client,
        api_auth_headers,
        second["application_id"],
    ).status_code == 200

    void_production = _void_production(
        client,
        api_auth_headers,
        production["id"],
    )

    assert void_production["status"] == "voided"
    with testing_session_local() as session:
        applications = session.query(ProductionInventoryApplication).all()
        assert len(applications) == 2
        assert {application.status for application in applications} == {"voided"}
        assert session.query(ProductionInventoryApplicationItem).count() == 2
        assert session.query(InventoryMovement).count() == 2


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/production/batches/1/apply-inventory",
            {
                "location_id": 1,
                "movement_date": "2026-07-18",
            },
        ),
        (
            "GET",
            "/api/v1/production/batches/1/inventory-application",
            None,
        ),
        (
            "POST",
            "/api/v1/production/inventory-applications/1/void",
            {"reason": "Error"},
        ),
    ],
)
def test_production_inventory_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_application_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/production/inventory-applications/1/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_production_inventory_migration_creates_required_tables(
    monkeypatch,
) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0013_production_inventory.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0013_production_inventory",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    created_tables: list[str] = []
    created_checks: list[tuple[str, str]] = []
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *args, **kwargs: created_tables.append(table_name),
    )
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        migration.op,
        "create_check_constraint",
        lambda name, table, *args, **kwargs: created_checks.append((name, table)),
    )

    migration.upgrade()

    assert migration.revision == "0013_prod_inventory"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0012_production"
    assert created_tables == [
        "production_inventory_applications",
        "production_inventory_application_items",
    ]
    assert created_checks == [
        (
            "ck_production_items_waste_not_greater_than_produced",
            "production_items",
        ),
    ]


def _create_product(
    client,
    headers,
    *,
    sku: str = "BIDON-20L",
    cost_estimate: str = "0.40",
) -> dict:
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": sku,
            "name": f"Producto {sku}",
            "category": "water",
            "unit": "container",
            "presentation": "20 L",
            "default_price": "1.00",
            "cost_estimate": cost_estimate,
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_location(client, headers) -> dict:
    response = client.post(
        "/api/v1/inventory/locations",
        headers=headers,
        json={
            "code": "BODEGA-PROD",
            "name": "Bodega de produccion",
            "location_type": "warehouse",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _item(
    product_id: int,
    quantity_produced: str,
    quantity_waste: str = "0",
) -> dict[str, object]:
    return {
        "product_id": product_id,
        "quantity_produced": quantity_produced,
        "quantity_waste": quantity_waste,
    }


def _create_production(
    client,
    headers,
    product_id: int,
    *,
    quantity_produced: str = "10",
    quantity_waste: str = "0",
) -> dict:
    return _create_production_with_items(
        client,
        headers,
        [_item(product_id, quantity_produced, quantity_waste)],
    )


def _create_production_with_items(client, headers, items: list[dict]) -> dict:
    response = client.post(
        "/api/v1/production/batches",
        headers=headers,
        json={
            "production_date": "2026-07-18",
            "notes": "Produccion de prueba",
            "items": items,
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _apply_inventory(
    client,
    headers,
    batch_id: int,
    location_id: int,
    *,
    notes: str | None = None,
):
    return client.post(
        f"/api/v1/production/batches/{batch_id}/apply-inventory",
        headers=headers,
        json={
            "location_id": location_id,
            "movement_date": "2026-07-18",
            "notes": notes,
        },
    )


def _void_application(client, headers, application_id: int):
    return client.post(
        f"/api/v1/production/inventory-applications/{application_id}/void",
        headers=headers,
        json={"reason": "Aplicacion incorrecta"},
    )


def _void_production(client, headers, batch_id: int) -> dict:
    response = client.post(
        f"/api/v1/production/batches/{batch_id}/void",
        headers=headers,
        json={"reason": "Produccion incorrecta"},
    )
    assert response.status_code == 200, response.json()
    return response.json()


def _create_manual_movement(
    client,
    headers,
    product_id: int,
    location_id: int,
    movement_type: str,
    quantity: str,
):
    return client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "movement_date": "2026-07-18",
            "movement_type": movement_type,
            "product_id": product_id,
            "location_id": location_id,
            "quantity": quantity,
            "reason": "Movimiento de prueba",
        },
    )

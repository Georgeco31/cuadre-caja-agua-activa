import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.production_batch import ProductionBatch
from app.models.production_item import ProductionItem


def test_create_production_with_one_item_and_snapshots(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = _production_response(
        client,
        api_auth_headers,
        items=[
            _item_payload(
                product["id"],
                quantity_produced="500",
                quantity_waste="5",
                notes=" Envases danados ",
            ),
        ],
        notes=" Produccion controlada ",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["production_number"] == "PROD-20260718-0001"
    assert body["production_date"] == "2026-07-18"
    assert body["status"] == "active"
    assert body["notes"] == "Produccion controlada"
    assert body["void_reason"] is None
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["product_sku_snapshot"] == product["sku"]
    assert item["product_name_snapshot"] == product["name"]
    assert item["product_presentation_snapshot"] == product["presentation"]
    assert Decimal(item["quantity_produced"]) == Decimal("500.000")
    assert Decimal(item["quantity_waste"]) == Decimal("5.000")
    assert item["notes"] == "Envases danados"


def test_create_production_with_multiple_items(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first = _create_product(client, api_auth_headers, sku="BIDON-20L")
    second = _create_product(
        client,
        api_auth_headers,
        sku="BOT-500ML",
        name="Botella 500 ml",
        presentation="500 ml",
    )

    production = _create_production(
        client,
        api_auth_headers,
        items=[
            _item_payload(first["id"], quantity_produced="20.5"),
            _item_payload(
                second["id"],
                quantity_produced="300",
                quantity_waste="2",
            ),
        ],
    )

    assert [item["product_id"] for item in production["items"]] == [
        first["id"],
        second["id"],
    ]


def test_production_numbers_are_unique(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    first = _create_production(client, api_auth_headers, product_id=product["id"])
    second = _create_production(client, api_auth_headers, product_id=product["id"])

    assert first["production_number"] != second["production_number"]
    assert second["production_number"] == "PROD-20260718-0002"


@pytest.mark.parametrize(
    "payload",
    [
        {"production_date": "2026-07-18", "items": []},
        {"items": [{"product_id": 1, "quantity_produced": "1"}]},
        {
            "production_date": "fecha-invalida",
            "items": [{"product_id": 1, "quantity_produced": "1"}],
        },
    ],
)
def test_production_rejects_missing_items_or_invalid_date(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/production/batches",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("quantity_produced", "0"),
        ("quantity_produced", "-1"),
        ("quantity_produced", "1.0001"),
        ("quantity_waste", "-0.001"),
        ("quantity_waste", "1.0001"),
    ],
)
def test_production_rejects_invalid_quantities(
    api_client,
    api_auth_headers,
    field: str,
    value: str,
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    item = _item_payload(product["id"])
    item[field] = value

    response = _production_response(
        client,
        api_auth_headers,
        items=[item],
    )

    assert response.status_code == 422


def test_production_rejects_missing_product(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = _production_response(
        client,
        api_auth_headers,
        items=[_item_payload(999)],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El producto 999 no existe."


def test_production_rejects_inactive_product(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = _production_response(
        client,
        api_auth_headers,
        items=[_item_payload(product["id"])],
    )

    assert response.status_code == 400
    assert "esta inactivo" in response.json()["detail"]


def test_product_snapshots_are_preserved(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product_id=product["id"],
    )

    update_response = client.patch(
        f"/api/v1/products/{product['id']}",
        headers=api_auth_headers,
        json={"name": "Bidon actualizado", "presentation": "19 L"},
    )
    assert update_response.status_code == 200
    detail = client.get(
        f"/api/v1/production/batches/{production['id']}",
        headers=api_auth_headers,
    ).json()

    assert detail["items"][0]["product_name_snapshot"] == product["name"]
    assert detail["items"][0]["product_presentation_snapshot"] == "20 L"


def test_list_get_and_filter_production(api_client, api_auth_headers) -> None:
    client, _ = api_client
    first_product = _create_product(client, api_auth_headers, sku="PROD-A")
    second_product = _create_product(
        client,
        api_auth_headers,
        sku="PROD-B",
        name="Botella familiar",
    )
    first = _create_production(
        client,
        api_auth_headers,
        product_id=first_product["id"],
        production_date="2026-07-01",
    )
    second = _create_production(
        client,
        api_auth_headers,
        product_id=second_product["id"],
        production_date="2026-07-20",
    )
    _void_production(client, api_auth_headers, second["id"])

    all_items = client.get(
        "/api/v1/production/batches",
        headers=api_auth_headers,
    )
    by_date = client.get(
        "/api/v1/production/batches?date_from=2026-07-10&date_to=2026-07-31",
        headers=api_auth_headers,
    )
    by_status = client.get(
        "/api/v1/production/batches?status=active",
        headers=api_auth_headers,
    )
    by_product = client.get(
        f"/api/v1/production/batches?product_id={second_product['id']}",
        headers=api_auth_headers,
    )
    by_search = client.get(
        "/api/v1/production/batches?search=familiar",
        headers=api_auth_headers,
    )
    by_number = client.get(
        f"/api/v1/production/batches?search={first['production_number']}",
        headers=api_auth_headers,
    )
    detail = client.get(
        f"/api/v1/production/batches/{first['id']}",
        headers=api_auth_headers,
    )

    assert all_items.status_code == 200
    assert [item["id"] for item in all_items.json()] == [second["id"], first["id"]]
    assert [item["id"] for item in by_date.json()] == [second["id"]]
    assert [item["id"] for item in by_status.json()] == [first["id"]]
    assert [item["id"] for item in by_product.json()] == [second["id"]]
    assert [item["id"] for item in by_search.json()] == [second["id"]]
    assert [item["id"] for item in by_number.json()] == [first["id"]]
    assert detail.status_code == 200
    assert detail.json()["id"] == first["id"]


def test_production_list_rejects_invalid_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/production/batches?date_from=2026-07-31&date_to=2026-07-01",
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_get_missing_production_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/production/batches/999",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_void_production_preserves_batch_and_items(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product_id=product["id"],
    )

    voided = _void_production(client, api_auth_headers, production["id"])

    assert voided["status"] == "voided"
    assert voided["void_reason"] == "Prueba de anulacion"
    assert voided["voided_at"] is not None
    assert len(voided["items"]) == 1
    with testing_session_local() as session:
        stored_batch = session.get(ProductionBatch, production["id"])
        stored_items = session.query(ProductionItem).filter_by(
            production_batch_id=production["id"],
        ).all()
    assert stored_batch is not None
    assert len(stored_items) == 1


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_production_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product_id=product["id"],
    )

    response = client.post(
        f"/api/v1/production/batches/{production['id']}/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_production_cannot_be_repeated(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)
    production = _create_production(
        client,
        api_auth_headers,
        product_id=product["id"],
    )
    _void_production(client, api_auth_headers, production["id"])

    response = client.post(
        f"/api/v1/production/batches/{production['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Segundo intento"},
    )

    assert response.status_code == 409


def test_create_and_void_production_do_not_change_inventory(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers)
    with testing_session_local() as session:
        location = InventoryLocation(
            code="BODEGA",
            name="Bodega principal",
            location_type="warehouse",
            is_active=True,
        )
        session.add(location)
        session.flush()
        stock = InventoryStock(
            product_id=product["id"],
            location_id=location.id,
            quantity_on_hand=Decimal("75.000"),
        )
        session.add(stock)
        session.commit()
        stock_id = stock.id
        movement_count_before = session.query(InventoryMovement).count()

    production = _create_production(
        client,
        api_auth_headers,
        product_id=product["id"],
    )
    _void_production(client, api_auth_headers, production["id"])

    with testing_session_local() as session:
        stored_stock = session.get(InventoryStock, stock_id)
        assert stored_stock is not None
        assert stored_stock.quantity_on_hand == Decimal("75.000")
        assert session.query(InventoryMovement).count() == movement_count_before


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/production/batches",
            {
                "production_date": "2026-07-18",
                "items": [{"product_id": 1, "quantity_produced": "1"}],
            },
        ),
        ("GET", "/api/v1/production/batches", None),
        ("GET", "/api/v1/production/batches/1", None),
        (
            "POST",
            "/api/v1/production/batches/1/void",
            {"reason": "Error"},
        ),
    ],
)
def test_production_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_production_migration_creates_required_tables(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0012_create_production.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0012_production",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    created_tables: list[str] = []
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *args, **kwargs: created_tables.append(table_name),
    )
    monkeypatch.setattr(migration.op, "create_index", lambda *args, **kwargs: None)

    migration.upgrade()

    assert migration.revision == "0012_production"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0011_inventory"
    assert created_tables == ["production_batches", "production_items"]


def _create_product(
    client,
    headers,
    *,
    sku: str = "BIDON-20L",
    name: str = "Bidon 20L",
    presentation: str = "20 L",
) -> dict:
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": sku,
            "name": name,
            "category": "water",
            "unit": "container",
            "presentation": presentation,
            "default_price": "1.00",
            "cost_estimate": "0.40",
        },
    )
    assert response.status_code == 201
    return response.json()


def _item_payload(
    product_id: int,
    *,
    quantity_produced: str = "10",
    quantity_waste: str = "0",
    notes: str | None = None,
) -> dict[str, object]:
    return {
        "product_id": product_id,
        "quantity_produced": quantity_produced,
        "quantity_waste": quantity_waste,
        "notes": notes,
    }


def _production_response(
    client,
    headers,
    *,
    items: list[dict[str, object]],
    production_date: str = "2026-07-18",
    notes: str | None = "Produccion de prueba",
):
    return client.post(
        "/api/v1/production/batches",
        headers=headers,
        json={
            "production_date": production_date,
            "notes": notes,
            "items": items,
        },
    )


def _create_production(
    client,
    headers,
    *,
    product_id: int | None = None,
    items: list[dict[str, object]] | None = None,
    production_date: str = "2026-07-18",
) -> dict:
    if items is None:
        assert product_id is not None
        items = [_item_payload(product_id)]
    response = _production_response(
        client,
        headers,
        items=items,
        production_date=production_date,
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _void_production(client, headers, batch_id: int) -> dict:
    response = client.post(
        f"/api/v1/production/batches/{batch_id}/void",
        headers=headers,
        json={"reason": "Prueba de anulacion"},
    )
    assert response.status_code == 200, response.json()
    return response.json()

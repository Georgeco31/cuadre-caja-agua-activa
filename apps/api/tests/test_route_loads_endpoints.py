import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.route_load import RouteLoad
from app.models.route_load_item import RouteLoadItem


def test_create_route_load_moves_stock_and_creates_traceability(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_load(client, api_auth_headers, source_quantity="500")

    response = _create_load_response(
        client,
        api_auth_headers,
        setup,
        quantity="120",
        notes=" Carga inicial ",
    )

    assert response.status_code == 201, response.json()
    route_load = response.json()
    assert route_load["load_number"] == "LOAD-20260718-0001"
    assert route_load["status"] == "active"
    assert route_load["route_name"] == setup["route"]["name"]
    assert route_load["vehicle_name"] == setup["vehicle"]["name"]
    assert route_load["source_location_name"] == setup["source"]["name"]
    assert route_load["destination_location_name"] == setup["destination"]["name"]
    assert route_load["notes"] == "Carga inicial"
    assert len(route_load["items"]) == 1
    item = route_load["items"][0]
    assert Decimal(item["quantity_loaded"]) == Decimal("120.000")
    assert item["product_name_snapshot"] == setup["products"][0]["name"]
    assert item["source_exit_movement_status"] == "active"
    assert item["destination_entry_movement_status"] == "active"

    with testing_session_local() as session:
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["source"]["id"],
        ) == Decimal("380.000")
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["destination"]["id"],
        ) == Decimal("120.000")
        exit_movement = session.get(
            InventoryMovement,
            item["source_exit_movement_id"],
        )
        entry_movement = session.get(
            InventoryMovement,
            item["destination_entry_movement_id"],
        )
        assert exit_movement is not None
        assert entry_movement is not None
        assert exit_movement.movement_type == "exit"
        assert entry_movement.movement_type == "entry"
        assert exit_movement.location_id == setup["source"]["id"]
        assert entry_movement.location_id == setup["destination"]["id"]
        assert exit_movement.reason == f"Carga de ruta {route_load['load_number']}"
        assert entry_movement.reason == exit_movement.reason
        assert exit_movement.unit_cost == Decimal("0.40")
        assert exit_movement.total_cost == Decimal("48.00")
        assert session.query(RouteLoadItem).count() == 1


def test_create_route_load_with_multiple_products(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_load(
        client,
        api_auth_headers,
        product_count=2,
        source_quantity="100",
    )

    response = _create_load_response(
        client,
        api_auth_headers,
        setup,
        items=[
            _item(setup["products"][0]["id"], "20.5"),
            _item(setup["products"][1]["id"], "30"),
        ],
    )

    assert response.status_code == 201
    assert len(response.json()["items"]) == 2
    with testing_session_local() as session:
        assert session.query(RouteLoadItem).count() == 2
        assert session.query(InventoryMovement).filter(
            InventoryMovement.reason.like("Carga de ruta%"),
        ).count() == 4


@pytest.mark.parametrize(
    "payload",
    [
        {
            "route_id": 1,
            "vehicle_id": 1,
            "source_location_id": 1,
            "destination_location_id": 2,
            "items": [{"product_id": 1, "quantity_loaded": "1"}],
        },
        {
            "load_date": "2026-07-18",
            "route_id": 1,
            "vehicle_id": 1,
            "source_location_id": 1,
            "destination_location_id": 2,
            "items": [],
        },
        {
            "load_date": "2026-07-18",
            "route_id": 1,
            "vehicle_id": 1,
            "source_location_id": 1,
            "destination_location_id": 2,
            "items": [{"product_id": 1, "quantity_loaded": "0"}],
        },
        {
            "load_date": "2026-07-18",
            "route_id": 1,
            "vehicle_id": 1,
            "source_location_id": 1,
            "destination_location_id": 1,
            "items": [{"product_id": 1, "quantity_loaded": "1"}],
        },
        {
            "load_date": "2026-07-18",
            "route_id": 1,
            "vehicle_id": 1,
            "source_location_id": 1,
            "destination_location_id": 2,
            "items": [
                {"product_id": 1, "quantity_loaded": "1"},
                {"product_id": 1, "quantity_loaded": "2"},
            ],
        },
    ],
)
def test_route_load_rejects_invalid_payload(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/route-loads",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_route_load_requires_existing_active_route(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    deactivate = client.patch(
        f"/api/v1/delivery-routes/{setup['route']['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    missing = _create_load_response(
        client,
        api_auth_headers,
        setup,
        route_id=999,
    )
    inactive = _create_load_response(client, api_auth_headers, setup)

    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert "ruta inactiva" in inactive.json()["detail"]


def test_route_load_requires_existing_active_vehicle(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    deactivate = client.patch(
        f"/api/v1/vehicles/{setup['vehicle']['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    missing = _create_load_response(
        client,
        api_auth_headers,
        setup,
        vehicle_id=999,
    )
    inactive = _create_load_response(client, api_auth_headers, setup)

    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert "vehiculo inactivo" in inactive.json()["detail"]


def test_route_load_requires_existing_active_locations(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)

    missing_source = _create_load_response(
        client,
        api_auth_headers,
        setup,
        source_location_id=999,
    )
    missing_destination = _create_load_response(
        client,
        api_auth_headers,
        setup,
        destination_location_id=999,
    )
    assert missing_source.status_code == 404
    assert missing_destination.status_code == 404

    deactivate_source = client.patch(
        f"/api/v1/inventory/locations/{setup['source']['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate_source.status_code == 200
    inactive_source = _create_load_response(client, api_auth_headers, setup)
    assert inactive_source.status_code == 400
    assert "origen esta inactiva" in inactive_source.json()["detail"]


def test_route_load_rejects_inactive_destination(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    deactivate = client.patch(
        f"/api/v1/inventory/locations/{setup['destination']['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    response = _create_load_response(client, api_auth_headers, setup)

    assert response.status_code == 400
    assert "destino esta inactiva" in response.json()["detail"]


def test_route_load_requires_vehicle_destination(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    warehouse = _create_location(
        client,
        api_auth_headers,
        code="BODEGA-2",
        name="Bodega secundaria",
    )

    response = _create_load_response(
        client,
        api_auth_headers,
        setup,
        destination_location_id=warehouse["id"],
    )

    assert response.status_code == 400
    assert "tipo vehiculo" in response.json()["detail"]


def test_route_load_validates_destination_vehicle(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    other_vehicle = _create_vehicle(
        client,
        api_auth_headers,
        code="CAM-02",
        name="Camion 2",
    )

    response = _create_load_response(
        client,
        api_auth_headers,
        setup,
        vehicle_id=other_vehicle["id"],
    )

    assert response.status_code == 400
    assert "no corresponde" in response.json()["detail"]


def test_route_load_requires_existing_active_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    deactivate = client.patch(
        f"/api/v1/products/{setup['products'][0]['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    missing = _create_load_response(
        client,
        api_auth_headers,
        setup,
        items=[_item(999, "1")],
    )
    inactive = _create_load_response(client, api_auth_headers, setup)

    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert "esta inactivo" in inactive.json()["detail"]


def test_route_load_is_atomic_when_an_item_has_insufficient_stock(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_load(
        client,
        api_auth_headers,
        product_count=2,
        source_quantity="10",
    )

    response = _create_load_response(
        client,
        api_auth_headers,
        setup,
        items=[
            _item(setup["products"][0]["id"], "5"),
            _item(setup["products"][1]["id"], "11"),
        ],
    )

    assert response.status_code == 400
    assert "stock suficiente" in response.json()["detail"]
    with testing_session_local() as session:
        assert session.query(RouteLoad).count() == 0
        assert session.query(RouteLoadItem).count() == 0
        assert session.query(InventoryMovement).filter(
            InventoryMovement.reason.like("Carga de ruta%"),
        ).count() == 0
        for product in setup["products"]:
            assert _stock_quantity(
                session,
                product["id"],
                setup["source"]["id"],
            ) == Decimal("10.000")
        assert session.query(InventoryStock).filter_by(
            location_id=setup["destination"]["id"],
        ).count() == 0


def test_list_detail_and_filter_route_loads(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_setup = _setup_load(client, api_auth_headers, suffix="A")
    first = _create_load_response(
        client,
        api_auth_headers,
        first_setup,
        load_date="2026-07-01",
    ).json()
    _void_load(client, api_auth_headers, first["id"])
    second_setup = _setup_load(client, api_auth_headers, suffix="B")
    second = _create_load_response(
        client,
        api_auth_headers,
        second_setup,
        load_date="2026-07-20",
    ).json()

    all_loads = client.get("/api/v1/route-loads", headers=api_auth_headers)
    by_date = client.get(
        "/api/v1/route-loads?date_from=2026-07-10&date_to=2026-07-31",
        headers=api_auth_headers,
    )
    by_status = client.get(
        "/api/v1/route-loads?status=voided",
        headers=api_auth_headers,
    )
    by_route = client.get(
        f"/api/v1/route-loads?route_id={second_setup['route']['id']}",
        headers=api_auth_headers,
    )
    by_vehicle = client.get(
        f"/api/v1/route-loads?vehicle_id={second_setup['vehicle']['id']}",
        headers=api_auth_headers,
    )
    by_product = client.get(
        f"/api/v1/route-loads?product_id={second_setup['products'][0]['id']}",
        headers=api_auth_headers,
    )
    by_search = client.get(
        f"/api/v1/route-loads?search={second_setup['route']['name']}",
        headers=api_auth_headers,
    )
    detail = client.get(
        f"/api/v1/route-loads/{second['id']}",
        headers=api_auth_headers,
    )

    assert [item["id"] for item in all_loads.json()] == [second["id"], first["id"]]
    assert [item["id"] for item in by_date.json()] == [second["id"]]
    assert [item["id"] for item in by_status.json()] == [first["id"]]
    assert [item["id"] for item in by_route.json()] == [second["id"]]
    assert [item["id"] for item in by_vehicle.json()] == [second["id"]]
    assert [item["id"] for item in by_product.json()] == [second["id"]]
    assert [item["id"] for item in by_search.json()] == [second["id"]]
    assert detail.status_code == 200
    assert detail.json()["id"] == second["id"]


def test_route_load_list_rejects_invalid_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/route-loads?date_from=2026-07-31&date_to=2026-07-01",
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_void_route_load_reverses_stock_and_preserves_records(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_load(client, api_auth_headers, source_quantity="50")
    route_load = _create_load_response(
        client,
        api_auth_headers,
        setup,
        quantity="20",
    ).json()

    response = _void_load_response(
        client,
        api_auth_headers,
        route_load["id"],
    )

    assert response.status_code == 200, response.json()
    voided = response.json()
    assert voided["status"] == "voided"
    assert voided["void_reason"] == "Carga incorrecta"
    assert voided["voided_at"] is not None
    assert voided["items"][0]["source_exit_movement_status"] == "voided"
    assert voided["items"][0]["destination_entry_movement_status"] == "voided"
    with testing_session_local() as session:
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["source"]["id"],
        ) == Decimal("50.000")
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["destination"]["id"],
        ) == Decimal("0.000")
        assert session.query(RouteLoad).count() == 1
        assert session.query(RouteLoadItem).count() == 1
        assert session.query(InventoryMovement).count() == 3


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_route_load_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/route-loads/1/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_route_load_cannot_be_repeated(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    route_load = _create_load_response(client, api_auth_headers, setup).json()
    _void_load(client, api_auth_headers, route_load["id"])

    response = _void_load_response(
        client,
        api_auth_headers,
        route_load["id"],
    )

    assert response.status_code == 409


def test_void_route_load_rolls_back_when_destination_stock_is_insufficient(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_load(client, api_auth_headers, source_quantity="10")
    route_load = _create_load_response(client, api_auth_headers, setup).json()
    manual_exit = _create_movement(
        client,
        api_auth_headers,
        setup["products"][0]["id"],
        setup["destination"]["id"],
        movement_type="exit",
        quantity="4",
        reason="Consumo posterior",
    )
    assert manual_exit.status_code == 201

    response = _void_load_response(
        client,
        api_auth_headers,
        route_load["id"],
    )

    assert response.status_code == 400
    assert "stock actual es insuficiente" in response.json()["detail"]
    with testing_session_local() as session:
        stored_load = session.get(RouteLoad, route_load["id"])
        assert stored_load is not None
        assert stored_load.status == "active"
        for movement_id in (
            route_load["items"][0]["source_exit_movement_id"],
            route_load["items"][0]["destination_entry_movement_id"],
        ):
            movement = session.get(InventoryMovement, movement_id)
            assert movement is not None
            assert movement.status == "active"
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["source"]["id"],
        ) == Decimal("0.000")
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["destination"]["id"],
        ) == Decimal("6.000")


def test_route_load_movements_cannot_be_voided_directly(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_load(client, api_auth_headers)
    route_load = _create_load_response(client, api_auth_headers, setup).json()

    response = client.post(
        "/api/v1/inventory/movements/"
        f"{route_load['items'][0]['source_exit_movement_id']}/void",
        headers=api_auth_headers,
        json={"reason": "Intento manual"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Anule la carga desde el modulo de cargas de camion."
    )


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/route-loads",
            {
                "load_date": "2026-07-18",
                "route_id": 1,
                "vehicle_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "items": [{"product_id": 1, "quantity_loaded": "1"}],
            },
        ),
        ("GET", "/api/v1/route-loads", None),
        ("GET", "/api/v1/route-loads/1", None),
        ("POST", "/api/v1/route-loads/1/void", {"reason": "Error"}),
    ],
)
def test_route_load_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_route_load_migration_creates_required_tables(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0014_create_route_loads.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0014_route_loads",
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

    assert migration.revision == "0014_route_loads"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0013_prod_inventory"
    assert created_tables == ["route_loads", "route_load_items"]


def _setup_load(
    client,
    headers,
    *,
    suffix: str = "01",
    product_count: int = 1,
    source_quantity: str = "10",
) -> dict:
    route = _create_route(client, headers, code=f"RUTA-{suffix}")
    vehicle = _create_vehicle(client, headers, code=f"CAM-{suffix}")
    source = _create_location(
        client,
        headers,
        code=f"BOD-{suffix}",
        name=f"Bodega {suffix}",
    )
    destination = _create_location(
        client,
        headers,
        code=f"VEH-{suffix}",
        name=f"Inventario camion {suffix}",
        location_type="vehicle",
        vehicle_id=vehicle["id"],
    )
    products = [
        _create_product(client, headers, sku=f"PROD-{suffix}-{index}")
        for index in range(1, product_count + 1)
    ]
    for product in products:
        response = _create_movement(
            client,
            headers,
            product["id"],
            source["id"],
            movement_type="entry",
            quantity=source_quantity,
            reason="Stock inicial controlado",
        )
        assert response.status_code == 201, response.json()
    return {
        "route": route,
        "vehicle": vehicle,
        "source": source,
        "destination": destination,
        "products": products,
    }


def _create_route(client, headers, *, code: str) -> dict:
    response = client.post(
        "/api/v1/delivery-routes",
        headers=headers,
        json={"code": code, "name": f"Ruta {code}", "expected_daily_cash": "0"},
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_vehicle(client, headers, *, code: str, name: str | None = None) -> dict:
    response = client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "code": code,
            "name": name or f"Vehiculo {code}",
            "vehicle_type": "truck",
            "fuel_type": "diesel",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_location(
    client,
    headers,
    *,
    code: str,
    name: str,
    location_type: str = "warehouse",
    vehicle_id: int | None = None,
) -> dict:
    response = client.post(
        "/api/v1/inventory/locations",
        headers=headers,
        json={
            "code": code,
            "name": name,
            "location_type": location_type,
            "vehicle_id": vehicle_id,
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_product(client, headers, *, sku: str) -> dict:
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
            "cost_estimate": "0.40",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_movement(
    client,
    headers,
    product_id: int,
    location_id: int,
    *,
    movement_type: str,
    quantity: str,
    reason: str,
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
            "reason": reason,
        },
    )


def _item(product_id: int, quantity: str) -> dict[str, object]:
    return {"product_id": product_id, "quantity_loaded": quantity}


def _create_load_response(
    client,
    headers,
    setup: dict,
    *,
    load_date: str = "2026-07-18",
    route_id: int | None = None,
    vehicle_id: int | None = None,
    source_location_id: int | None = None,
    destination_location_id: int | None = None,
    quantity: str = "10",
    notes: str | None = None,
    items: list[dict[str, object]] | None = None,
):
    return client.post(
        "/api/v1/route-loads",
        headers=headers,
        json={
            "load_date": load_date,
            "route_id": route_id or setup["route"]["id"],
            "vehicle_id": vehicle_id or setup["vehicle"]["id"],
            "source_location_id": source_location_id or setup["source"]["id"],
            "destination_location_id": (
                destination_location_id or setup["destination"]["id"]
            ),
            "notes": notes,
            "items": items or [_item(setup["products"][0]["id"], quantity)],
        },
    )


def _void_load_response(client, headers, load_id: int):
    return client.post(
        f"/api/v1/route-loads/{load_id}/void",
        headers=headers,
        json={"reason": "Carga incorrecta"},
    )


def _void_load(client, headers, load_id: int) -> dict:
    response = _void_load_response(client, headers, load_id)
    assert response.status_code == 200, response.json()
    return response.json()


def _stock_quantity(session, product_id: int, location_id: int) -> Decimal:
    stock = session.query(InventoryStock).filter_by(
        product_id=product_id,
        location_id=location_id,
    ).one()
    return stock.quantity_on_hand

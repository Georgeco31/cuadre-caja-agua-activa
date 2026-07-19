import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.route_return import RouteReturn
from app.models.route_return_item import RouteReturnItem


def test_create_route_return_moves_stock_and_creates_traceability(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_return(client, api_auth_headers, load_quantity="120")

    response = _create_return_response(
        client,
        api_auth_headers,
        setup,
        quantity="20",
        notes=" Retorno controlado ",
    )

    assert response.status_code == 201, response.json()
    route_return = response.json()
    assert route_return["return_number"] == "RETURN-20260718-0001"
    assert route_return["status"] == "active"
    assert route_return["route_load_id"] == setup["load"]["id"]
    assert route_return["route_load_number"] == setup["load"]["load_number"]
    assert route_return["route_load_status"] == "active"
    assert route_return["route_id"] == setup["route"]["id"]
    assert route_return["vehicle_id"] == setup["vehicle"]["id"]
    assert route_return["source_location_id"] == setup["vehicle_location"]["id"]
    assert route_return["destination_location_id"] == setup["warehouse"]["id"]
    assert route_return["notes"] == "Retorno controlado"
    assert len(route_return["items"]) == 1
    item = route_return["items"][0]
    assert item["route_load_item_id"] == setup["load"]["items"][0]["id"]
    assert Decimal(item["quantity_loaded"]) == Decimal("120.000")
    assert Decimal(item["quantity_returned"]) == Decimal("20.000")
    assert item["source_exit_movement_status"] == "active"
    assert item["destination_entry_movement_status"] == "active"

    with testing_session_local() as session:
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["vehicle_location"]["id"],
        ) == Decimal("100.000")
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["warehouse"]["id"],
        ) == Decimal("400.000")
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
        assert exit_movement.location_id == setup["vehicle_location"]["id"]
        assert entry_movement.location_id == setup["warehouse"]["id"]
        assert exit_movement.reason == f"Retorno de ruta {route_return['return_number']}"
        assert entry_movement.reason == exit_movement.reason
        assert session.query(RouteReturnItem).count() == 1


def test_create_route_return_with_multiple_products(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_return(
        client,
        api_auth_headers,
        product_count=2,
        load_quantity="40",
    )

    response = _create_return_response(
        client,
        api_auth_headers,
        setup,
        items=[
            _return_item(setup["load"]["items"][0]["id"], "10.5"),
            _return_item(setup["load"]["items"][1]["id"], "15"),
        ],
    )

    assert response.status_code == 201, response.json()
    assert len(response.json()["items"]) == 2
    with testing_session_local() as session:
        assert session.query(RouteReturnItem).count() == 2
        assert session.query(InventoryMovement).filter(
            InventoryMovement.reason.like("Retorno de ruta%"),
        ).count() == 4


@pytest.mark.parametrize(
    "payload",
    [
        {
            "route_load_id": 1,
            "destination_location_id": 1,
            "items": [{"route_load_item_id": 1, "quantity_returned": "1"}],
        },
        {
            "return_date": "",
            "route_load_id": 1,
            "destination_location_id": 1,
            "items": [{"route_load_item_id": 1, "quantity_returned": "1"}],
        },
        {
            "return_date": "2026-07-18",
            "route_load_id": 1,
            "destination_location_id": 1,
            "items": [],
        },
        {
            "return_date": "2026-07-18",
            "route_load_id": 1,
            "destination_location_id": 1,
            "items": [{"route_load_item_id": 1, "quantity_returned": "0"}],
        },
        {
            "return_date": "2026-07-18",
            "route_load_id": 1,
            "destination_location_id": 1,
            "items": [
                {"route_load_item_id": 1, "quantity_returned": "1"},
                {"route_load_item_id": 1, "quantity_returned": "2"},
            ],
        },
    ],
)
def test_route_return_rejects_invalid_payload(
    api_client,
    api_auth_headers,
    payload: dict[str, object],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/route-returns",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_route_return_requires_existing_active_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    voided_load = _void_load(client, api_auth_headers, setup["load"]["id"])
    assert voided_load["status"] == "voided"

    missing = _create_return_response(
        client,
        api_auth_headers,
        setup,
        route_load_id=999,
    )
    voided = _create_return_response(client, api_auth_headers, setup)

    assert missing.status_code == 404
    assert voided.status_code == 400
    assert "carga anulada" in voided.json()["detail"]


def test_route_return_allows_only_one_active_return_per_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    first = _create_return_response(client, api_auth_headers, setup, quantity="2")
    assert first.status_code == 201

    duplicate = _create_return_response(client, api_auth_headers, setup, quantity="1")

    assert duplicate.status_code == 409
    assert "retorno activo" in duplicate.json()["detail"]


def test_route_return_allows_new_active_return_after_previous_is_voided(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    first = _create_return_response(client, api_auth_headers, setup, quantity="2").json()
    _void_return(client, api_auth_headers, first["id"])

    second = _create_return_response(client, api_auth_headers, setup, quantity="1")

    assert second.status_code == 201, second.json()
    assert second.json()["id"] != first["id"]


def test_route_return_requires_existing_active_locations(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)

    missing = _create_return_response(
        client,
        api_auth_headers,
        setup,
        destination_location_id=999,
    )
    assert missing.status_code == 404

    deactivate_destination = client.patch(
        f"/api/v1/inventory/locations/{setup['warehouse']['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate_destination.status_code == 200
    inactive_destination = _create_return_response(client, api_auth_headers, setup)
    assert inactive_destination.status_code == 400
    assert "destino esta inactiva" in inactive_destination.json()["detail"]


def test_route_return_rejects_inactive_source_location(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    deactivate = client.patch(
        f"/api/v1/inventory/locations/{setup['vehicle_location']['id']}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    response = _create_return_response(client, api_auth_headers, setup)

    assert response.status_code == 400
    assert "origen del vehiculo esta inactiva" in response.json()["detail"]


def test_route_return_rejects_same_or_vehicle_destination(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)

    same = _create_return_response(
        client,
        api_auth_headers,
        setup,
        destination_location_id=setup["vehicle_location"]["id"],
    )
    other_vehicle_location = _create_location(
        client,
        api_auth_headers,
        code="VEH-RET-02",
        name="Inventario camion retorno 02",
        location_type="vehicle",
    )
    vehicle_destination = _create_return_response(
        client,
        api_auth_headers,
        setup,
        destination_location_id=other_vehicle_location["id"],
    )

    assert same.status_code == 400
    assert "deben ser distintas" in same.json()["detail"]
    assert vehicle_destination.status_code == 400
    assert "no puede ser de tipo vehiculo" in vehicle_destination.json()["detail"]


def test_route_return_item_must_belong_to_selected_load(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_setup = _setup_return(client, api_auth_headers, suffix="A")
    second_setup = _setup_return(client, api_auth_headers, suffix="B")

    missing_item = _create_return_response(
        client,
        api_auth_headers,
        first_setup,
        items=[_return_item(999, "1")],
    )
    other_load_item = _create_return_response(
        client,
        api_auth_headers,
        first_setup,
        items=[_return_item(second_setup["load"]["items"][0]["id"], "1")],
    )

    assert missing_item.status_code == 400
    assert other_load_item.status_code == 400
    assert "no pertenece" in missing_item.json()["detail"]
    assert "no pertenece" in other_load_item.json()["detail"]


def test_route_return_rejects_quantity_greater_than_loaded(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers, load_quantity="10")

    response = _create_return_response(
        client,
        api_auth_headers,
        setup,
        quantity="10.001",
    )

    assert response.status_code == 400
    assert "superar la cantidad cargada" in response.json()["detail"]


def test_route_return_rejects_quantity_greater_than_vehicle_stock(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers, load_quantity="10")
    consumed = _create_movement(
        client,
        api_auth_headers,
        setup["products"][0]["id"],
        setup["vehicle_location"]["id"],
        movement_type="exit",
        quantity="4",
        reason="Consumo posterior a la carga",
    )
    assert consumed.status_code == 201

    response = _create_return_response(
        client,
        api_auth_headers,
        setup,
        quantity="7",
    )

    assert response.status_code == 400
    assert "stock suficiente" in response.json()["detail"]


def test_route_return_is_atomic_when_second_item_has_insufficient_stock(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_return(
        client,
        api_auth_headers,
        product_count=2,
        load_quantity="10",
    )
    consumed = _create_movement(
        client,
        api_auth_headers,
        setup["products"][1]["id"],
        setup["vehicle_location"]["id"],
        movement_type="exit",
        quantity="9",
        reason="Consumo controlado",
    )
    assert consumed.status_code == 201

    response = _create_return_response(
        client,
        api_auth_headers,
        setup,
        items=[
            _return_item(setup["load"]["items"][0]["id"], "5"),
            _return_item(setup["load"]["items"][1]["id"], "2"),
        ],
    )

    assert response.status_code == 400
    with testing_session_local() as session:
        assert session.query(RouteReturn).count() == 0
        assert session.query(RouteReturnItem).count() == 0
        assert session.query(InventoryMovement).filter(
            InventoryMovement.reason.like("Retorno de ruta%"),
        ).count() == 0
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["vehicle_location"]["id"],
        ) == Decimal("10.000")
        assert _stock_quantity(
            session,
            setup["products"][1]["id"],
            setup["vehicle_location"]["id"],
        ) == Decimal("1.000")


def test_list_detail_and_filter_route_returns(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_setup = _setup_return(client, api_auth_headers, suffix="A")
    first = _create_return_response(
        client,
        api_auth_headers,
        first_setup,
        return_date="2026-07-01",
    ).json()
    _void_return(client, api_auth_headers, first["id"])
    second_setup = _setup_return(client, api_auth_headers, suffix="B")
    second = _create_return_response(
        client,
        api_auth_headers,
        second_setup,
        return_date="2026-07-20",
    ).json()

    all_returns = client.get("/api/v1/route-returns", headers=api_auth_headers)
    by_date = client.get(
        "/api/v1/route-returns?date_from=2026-07-10&date_to=2026-07-31",
        headers=api_auth_headers,
    )
    by_status = client.get(
        "/api/v1/route-returns?status=voided",
        headers=api_auth_headers,
    )
    by_route = client.get(
        f"/api/v1/route-returns?route_id={second_setup['route']['id']}",
        headers=api_auth_headers,
    )
    by_vehicle = client.get(
        f"/api/v1/route-returns?vehicle_id={second_setup['vehicle']['id']}",
        headers=api_auth_headers,
    )
    by_load = client.get(
        f"/api/v1/route-returns?route_load_id={second_setup['load']['id']}",
        headers=api_auth_headers,
    )
    by_product = client.get(
        f"/api/v1/route-returns?product_id={second_setup['products'][0]['id']}",
        headers=api_auth_headers,
    )
    by_search = client.get(
        f"/api/v1/route-returns?search={second_setup['load']['load_number']}",
        headers=api_auth_headers,
    )
    detail = client.get(
        f"/api/v1/route-returns/{second['id']}",
        headers=api_auth_headers,
    )

    assert [item["id"] for item in all_returns.json()] == [second["id"], first["id"]]
    assert [item["id"] for item in by_date.json()] == [second["id"]]
    assert [item["id"] for item in by_status.json()] == [first["id"]]
    assert [item["id"] for item in by_route.json()] == [second["id"]]
    assert [item["id"] for item in by_vehicle.json()] == [second["id"]]
    assert [item["id"] for item in by_load.json()] == [second["id"]]
    assert [item["id"] for item in by_product.json()] == [second["id"]]
    assert [item["id"] for item in by_search.json()] == [second["id"]]
    assert detail.status_code == 200
    assert detail.json()["id"] == second["id"]


def test_route_return_list_rejects_invalid_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/route-returns?date_from=2026-07-31&date_to=2026-07-01",
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_void_route_return_reverses_stock_and_preserves_records(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_return(client, api_auth_headers, load_quantity="20")
    route_return = _create_return_response(
        client,
        api_auth_headers,
        setup,
        quantity="8",
    ).json()

    response = _void_return_response(
        client,
        api_auth_headers,
        route_return["id"],
    )

    assert response.status_code == 200, response.json()
    voided = response.json()
    assert voided["status"] == "voided"
    assert voided["void_reason"] == "Retorno incorrecto"
    assert voided["voided_at"] is not None
    assert voided["items"][0]["source_exit_movement_status"] == "voided"
    assert voided["items"][0]["destination_entry_movement_status"] == "voided"
    with testing_session_local() as session:
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["vehicle_location"]["id"],
        ) == Decimal("20.000")
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["warehouse"]["id"],
        ) == Decimal("480.000")
        assert session.query(RouteReturn).count() == 1
        assert session.query(RouteReturnItem).count() == 1
        for movement_id in (
            route_return["items"][0]["source_exit_movement_id"],
            route_return["items"][0]["destination_entry_movement_id"],
        ):
            assert session.get(InventoryMovement, movement_id) is not None


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_route_return_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/route-returns/1/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_route_return_cannot_be_repeated(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    route_return = _create_return_response(client, api_auth_headers, setup).json()
    _void_return(client, api_auth_headers, route_return["id"])

    response = _void_return_response(client, api_auth_headers, route_return["id"])

    assert response.status_code == 409


def test_void_route_return_rolls_back_when_destination_stock_is_insufficient(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    setup = _setup_return(
        client,
        api_auth_headers,
        source_quantity="20",
        load_quantity="20",
    )
    route_return = _create_return_response(
        client,
        api_auth_headers,
        setup,
        quantity="10",
    ).json()
    consumed = _create_movement(
        client,
        api_auth_headers,
        setup["products"][0]["id"],
        setup["warehouse"]["id"],
        movement_type="exit",
        quantity="4",
        reason="Consumo posterior al retorno",
    )
    assert consumed.status_code == 201

    response = _void_return_response(
        client,
        api_auth_headers,
        route_return["id"],
    )

    assert response.status_code == 400
    assert "stock actual es insuficiente" in response.json()["detail"]
    with testing_session_local() as session:
        stored_return = session.get(RouteReturn, route_return["id"])
        assert stored_return is not None
        assert stored_return.status == "active"
        for movement_id in (
            route_return["items"][0]["source_exit_movement_id"],
            route_return["items"][0]["destination_entry_movement_id"],
        ):
            movement = session.get(InventoryMovement, movement_id)
            assert movement is not None
            assert movement.status == "active"
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["vehicle_location"]["id"],
        ) == Decimal("10.000")
        assert _stock_quantity(
            session,
            setup["products"][0]["id"],
            setup["warehouse"]["id"],
        ) == Decimal("6.000")


def test_route_return_movements_cannot_be_voided_directly(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    route_return = _create_return_response(client, api_auth_headers, setup).json()

    response = client.post(
        "/api/v1/inventory/movements/"
        f"{route_return['items'][0]['source_exit_movement_id']}/void",
        headers=api_auth_headers,
        json={"reason": "Intento manual"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Anule el retorno desde el modulo de retornos de ruta."
    )


def test_route_load_cannot_be_voided_with_active_return(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    setup = _setup_return(client, api_auth_headers)
    route_return = _create_return_response(client, api_auth_headers, setup).json()

    blocked = _void_load_response(client, api_auth_headers, setup["load"]["id"])
    assert blocked.status_code == 400
    assert blocked.json()["detail"] == (
        "Primero anule el retorno de ruta antes de anular la carga."
    )

    _void_return(client, api_auth_headers, route_return["id"])
    allowed = _void_load_response(client, api_auth_headers, setup["load"]["id"])
    assert allowed.status_code == 200, allowed.json()
    assert allowed.json()["status"] == "voided"


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/route-returns",
            {
                "return_date": "2026-07-18",
                "route_load_id": 1,
                "destination_location_id": 1,
                "items": [{"route_load_item_id": 1, "quantity_returned": "1"}],
            },
        ),
        ("GET", "/api/v1/route-returns", None),
        ("GET", "/api/v1/route-returns/1", None),
        ("POST", "/api/v1/route-returns/1/void", {"reason": "Error"}),
    ],
)
def test_route_return_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_route_return_migration_creates_required_tables(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0015_create_route_returns.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0015_route_returns",
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

    assert migration.revision == "0015_route_returns"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0014_route_loads"
    assert created_tables == ["route_returns", "route_return_items"]


def _setup_return(
    client,
    headers,
    *,
    suffix: str = "01",
    product_count: int = 1,
    source_quantity: str = "500",
    load_quantity: str = "20",
) -> dict:
    route = _create_route(client, headers, code=f"RUTA-RET-{suffix}")
    vehicle = _create_vehicle(client, headers, code=f"CAM-RET-{suffix}")
    warehouse = _create_location(
        client,
        headers,
        code=f"BOD-RET-{suffix}",
        name=f"Bodega retorno {suffix}",
    )
    vehicle_location = _create_location(
        client,
        headers,
        code=f"VEH-RET-{suffix}",
        name=f"Inventario camion retorno {suffix}",
        location_type="vehicle",
        vehicle_id=vehicle["id"],
    )
    products = [
        _create_product(client, headers, sku=f"PROD-RET-{suffix}-{index}")
        for index in range(1, product_count + 1)
    ]
    for product in products:
        response = _create_movement(
            client,
            headers,
            product["id"],
            warehouse["id"],
            movement_type="entry",
            quantity=source_quantity,
            reason="Stock inicial controlado",
        )
        assert response.status_code == 201, response.json()
    load_response = client.post(
        "/api/v1/route-loads",
        headers=headers,
        json={
            "load_date": "2026-07-18",
            "route_id": route["id"],
            "vehicle_id": vehicle["id"],
            "source_location_id": warehouse["id"],
            "destination_location_id": vehicle_location["id"],
            "items": [
                {
                    "product_id": product["id"],
                    "quantity_loaded": load_quantity,
                }
                for product in products
            ],
        },
    )
    assert load_response.status_code == 201, load_response.json()
    return {
        "route": route,
        "vehicle": vehicle,
        "warehouse": warehouse,
        "vehicle_location": vehicle_location,
        "products": products,
        "load": load_response.json(),
    }


def _create_route(client, headers, *, code: str) -> dict:
    response = client.post(
        "/api/v1/delivery-routes",
        headers=headers,
        json={"code": code, "name": f"Ruta {code}", "expected_daily_cash": "0"},
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_vehicle(client, headers, *, code: str) -> dict:
    response = client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "code": code,
            "name": f"Vehiculo {code}",
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


def _return_item(route_load_item_id: int, quantity: str) -> dict[str, object]:
    return {
        "route_load_item_id": route_load_item_id,
        "quantity_returned": quantity,
    }


def _create_return_response(
    client,
    headers,
    setup: dict,
    *,
    return_date: str = "2026-07-18",
    route_load_id: int | None = None,
    destination_location_id: int | None = None,
    quantity: str = "5",
    notes: str | None = None,
    items: list[dict[str, object]] | None = None,
):
    return client.post(
        "/api/v1/route-returns",
        headers=headers,
        json={
            "return_date": return_date,
            "route_load_id": route_load_id or setup["load"]["id"],
            "destination_location_id": (
                destination_location_id or setup["warehouse"]["id"]
            ),
            "notes": notes,
            "items": items
            or [_return_item(setup["load"]["items"][0]["id"], quantity)],
        },
    )


def _void_return_response(client, headers, return_id: int):
    return client.post(
        f"/api/v1/route-returns/{return_id}/void",
        headers=headers,
        json={"reason": "Retorno incorrecto"},
    )


def _void_return(client, headers, return_id: int) -> dict:
    response = _void_return_response(client, headers, return_id)
    assert response.status_code == 200, response.json()
    return response.json()


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

import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.customer import Customer
from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.product import Product
from app.models.sale import Sale


def test_create_inventory_location(api_client, api_auth_headers) -> None:
    client, _ = api_client
    vehicle = _create_vehicle(client, api_auth_headers)

    response = client.post(
        "/api/v1/inventory/locations",
        headers=api_auth_headers,
        json={
            "code": " CAMION-01 ",
            "name": " Inventario camion 1 ",
            "location_type": "vehicle",
            "vehicle_id": vehicle["id"],
            "description": " Stock movil ",
            "notes": " Ubicacion manual ",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "CAMION-01"
    assert body["name"] == "Inventario camion 1"
    assert body["location_type"] == "vehicle"
    assert body["vehicle_id"] == vehicle["id"]
    assert body["description"] == "Stock movil"
    assert body["notes"] == "Ubicacion manual"
    assert body["is_active"] is True


def test_create_location_requires_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/inventory/locations",
        headers=api_auth_headers,
        json={"location_type": "warehouse"},
    )

    assert response.status_code == 422


def test_create_location_rejects_blank_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/inventory/locations",
        headers=api_auth_headers,
        json={"name": "   ", "location_type": "warehouse"},
    )

    assert response.status_code == 422


def test_create_location_rejects_duplicate_code(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_location(client, api_auth_headers, code="BODEGA-01")

    response = client.post(
        "/api/v1/inventory/locations",
        headers=api_auth_headers,
        json={
            "code": "BODEGA-01",
            "name": "Bodega duplicada",
            "location_type": "warehouse",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "El codigo de ubicacion ya esta registrado."
    )


def test_location_allows_null_or_empty_code(api_client, api_auth_headers) -> None:
    client, _ = api_client

    empty_code = _create_location(
        client,
        api_auth_headers,
        code="   ",
        name="Bodega sin codigo 1",
    )
    null_code = _create_location(
        client,
        api_auth_headers,
        code=None,
        name="Bodega sin codigo 2",
    )

    assert empty_code["code"] is None
    assert null_code["code"] is None


def test_list_and_search_locations(api_client, api_auth_headers) -> None:
    client, _ = api_client
    expected = _create_location(
        client,
        api_auth_headers,
        code="CENTRO",
        name="Bodega central",
    )
    _create_location(
        client,
        api_auth_headers,
        code="NORTE",
        name="Bodega norte",
    )

    all_items = client.get(
        "/api/v1/inventory/locations",
        headers=api_auth_headers,
    )
    search_items = client.get(
        "/api/v1/inventory/locations?search=central",
        headers=api_auth_headers,
    )

    assert all_items.status_code == 200
    assert len(all_items.json()) == 2
    assert [item["id"] for item in search_items.json()] == [expected["id"]]


def test_filter_locations_by_status_and_type(api_client, api_auth_headers) -> None:
    client, _ = api_client
    active = _create_location(client, api_auth_headers, name="Bodega activa")
    inactive = _create_location(
        client,
        api_auth_headers,
        code="AREA-01",
        name="Area inactiva",
        location_type="production_area",
    )
    client.patch(
        f"/api/v1/inventory/locations/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    active_items = client.get(
        "/api/v1/inventory/locations?is_active=true",
        headers=api_auth_headers,
    ).json()
    production_items = client.get(
        "/api/v1/inventory/locations?location_type=production_area",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in active_items] == [active["id"]]
    assert [item["id"] for item in production_items] == [inactive["id"]]


def test_get_and_update_location(api_client, api_auth_headers) -> None:
    client, _ = api_client
    location = _create_location(client, api_auth_headers)

    updated_response = client.patch(
        f"/api/v1/inventory/locations/{location['id']}",
        headers=api_auth_headers,
        json={
            "code": "BODEGA-EDITADA",
            "name": "Bodega editada",
            "description": "Nueva descripcion",
            "location_type": "other",
        },
    )
    detail_response = client.get(
        f"/api/v1/inventory/locations/{location['id']}",
        headers=api_auth_headers,
    )

    assert updated_response.status_code == 200
    assert detail_response.json()["name"] == "Bodega editada"
    assert detail_response.json()["code"] == "BODEGA-EDITADA"
    assert detail_response.json()["location_type"] == "other"


def test_location_rejects_missing_vehicle(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/inventory/locations",
        headers=api_auth_headers,
        json={
            "name": "Camion inexistente",
            "location_type": "vehicle",
            "vehicle_id": 999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "El vehiculo no existe."


def test_deactivate_and_reactivate_location_without_deleting(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    location = _create_location(client, api_auth_headers)

    deactivated = client.patch(
        f"/api/v1/inventory/locations/{location['id']}/deactivate",
        headers=api_auth_headers,
    )
    activated = client.patch(
        f"/api/v1/inventory/locations/{location['id']}/activate",
        headers=api_auth_headers,
    )

    assert deactivated.json()["is_active"] is False
    assert activated.json()["is_active"] is True
    with testing_session_local() as session:
        assert session.get(InventoryLocation, location["id"]) is not None


def test_create_entry_increases_stock_and_saves_snapshots(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="100",
        unit_cost="0.40",
    )
    stock = _get_single_stock(client, api_auth_headers)

    assert movement["movement_type"] == "entry"
    assert movement["product_sku_snapshot"] == product["sku"]
    assert movement["product_name_snapshot"] == product["name"]
    assert movement["product_presentation_snapshot"] == product["presentation"]
    assert movement["location_name"] == location["name"]
    assert Decimal(movement["quantity"]) == Decimal("100.000")
    assert movement["unit_cost"] == "0.40"
    assert movement["total_cost"] == "40.00"
    assert Decimal(stock["quantity_on_hand"]) == Decimal("100.000")


def test_movement_without_unit_cost_has_no_total_cost(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        unit_cost=None,
    )

    assert movement["unit_cost"] is None
    assert movement["total_cost"] is None


def test_exit_decreases_stock(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="20",
    )

    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type="exit",
        quantity="7.5",
    )

    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal("12.500")


def test_positive_adjustment_increases_stock(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type="adjustment_in",
        quantity="2.125",
    )

    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal("2.125")


def test_negative_adjustment_decreases_stock(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="10",
    )

    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type="adjustment_out",
        quantity="3",
    )

    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal("7.000")


@pytest.mark.parametrize("quantity", ["0", "-1"])
def test_movement_rejects_nonpositive_quantity(
    api_client,
    api_auth_headers,
    quantity: str,
) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity=quantity,
    )

    assert response.status_code == 422


def test_movement_rejects_more_than_three_quantity_decimals(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="1.0001",
    )

    assert response.status_code == 422


def test_movement_rejects_negative_unit_cost(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        unit_cost="-0.01",
    )

    assert response.status_code == 422


@pytest.mark.parametrize("movement_type", ["exit", "adjustment_out"])
def test_movement_cannot_leave_negative_stock(
    api_client,
    api_auth_headers,
    movement_type: str,
) -> None:
    client, testing_session_local = api_client
    product, location = _setup_inventory(client, api_auth_headers)

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type=movement_type,
        quantity="1",
    )

    assert response.status_code == 400
    assert "stock suficiente" in response.json()["detail"]
    with testing_session_local() as session:
        assert session.query(InventoryStock).count() == 0


def test_movement_rejects_missing_product(api_client, api_auth_headers) -> None:
    client, _ = api_client
    location = _create_location(client, api_auth_headers)

    response = _movement_response(
        client,
        api_auth_headers,
        999,
        location["id"],
    )

    assert response.status_code == 404


def test_movement_rejects_missing_location(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers)

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        999,
    )

    assert response.status_code == 404


def test_movement_rejects_inactive_product(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )

    assert response.status_code == 400
    assert "producto inactivo" in response.json()["detail"]


def test_movement_rejects_inactive_location(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    client.patch(
        f"/api/v1/inventory/locations/{location['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = _movement_response(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )

    assert response.status_code == 400
    assert "ubicacion inactiva" in response.json()["detail"]


def test_stock_filters_and_reuses_unique_row(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    first_product = _create_product(client, api_auth_headers, sku="PROD-1")
    second_product = _create_product(client, api_auth_headers, sku="PROD-2")
    first_location = _create_location(
        client,
        api_auth_headers,
        code="LOC-1",
    )
    second_location = _create_location(
        client,
        api_auth_headers,
        code="LOC-2",
        name="Segunda bodega",
    )
    _create_movement(
        client,
        api_auth_headers,
        first_product["id"],
        first_location["id"],
        quantity="2",
    )
    _create_movement(
        client,
        api_auth_headers,
        first_product["id"],
        first_location["id"],
        movement_type="exit",
        quantity="2",
    )
    _create_movement(
        client,
        api_auth_headers,
        second_product["id"],
        second_location["id"],
        quantity="5",
    )

    by_product = client.get(
        f"/api/v1/inventory/stocks?product_id={first_product['id']}",
        headers=api_auth_headers,
    ).json()
    by_location = client.get(
        f"/api/v1/inventory/stocks?location_id={second_location['id']}",
        headers=api_auth_headers,
    ).json()
    positive = client.get(
        "/api/v1/inventory/stocks?only_positive=true",
        headers=api_auth_headers,
    ).json()

    assert len(by_product) == 1
    assert Decimal(by_product[0]["quantity_on_hand"]) == Decimal("0.000")
    assert [item["product_id"] for item in by_location] == [second_product["id"]]
    assert [item["product_id"] for item in positive] == [second_product["id"]]
    with testing_session_local() as session:
        assert session.query(InventoryStock).count() == 2


def test_list_and_get_movements(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )

    listed = client.get(
        "/api/v1/inventory/movements",
        headers=api_auth_headers,
    )
    detail = client.get(
        f"/api/v1/inventory/movements/{movement['id']}",
        headers=api_auth_headers,
    )

    assert [item["id"] for item in listed.json()] == [movement["id"]]
    assert detail.status_code == 200
    assert detail.json()["id"] == movement["id"]


def test_get_missing_movement_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/inventory/movements/999",
        headers=api_auth_headers,
    )

    assert response.status_code == 404


def test_filter_movements_by_date(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_date="2026-07-01",
    )
    expected = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_date="2026-07-20",
    )

    items = client.get(
        "/api/v1/inventory/movements?date_from=2026-07-10&date_to=2026-07-31",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in items] == [expected["id"]]


def test_filter_movements_by_product_and_location(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_product = _create_product(client, api_auth_headers, sku="FILTER-1")
    second_product = _create_product(client, api_auth_headers, sku="FILTER-2")
    first_location = _create_location(client, api_auth_headers, code="FILTER-A")
    second_location = _create_location(
        client,
        api_auth_headers,
        code="FILTER-B",
        name="Ubicacion B",
    )
    _create_movement(
        client,
        api_auth_headers,
        first_product["id"],
        first_location["id"],
    )
    expected = _create_movement(
        client,
        api_auth_headers,
        second_product["id"],
        second_location["id"],
    )

    by_product = client.get(
        f"/api/v1/inventory/movements?product_id={second_product['id']}",
        headers=api_auth_headers,
    ).json()
    by_location = client.get(
        f"/api/v1/inventory/movements?location_id={second_location['id']}",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in by_product] == [expected["id"]]
    assert [item["id"] for item in by_location] == [expected["id"]]


def test_filter_movements_by_type_and_status(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    entry = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="5",
    )
    adjustment = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type="adjustment_in",
    )
    _void_movement(client, api_auth_headers, adjustment["id"])

    entries = client.get(
        "/api/v1/inventory/movements?movement_type=entry",
        headers=api_auth_headers,
    ).json()
    voided = client.get(
        "/api/v1/inventory/movements?status=voided",
        headers=api_auth_headers,
    ).json()

    assert [item["id"] for item in entries] == [entry["id"]]
    assert [item["id"] for item in voided] == [adjustment["id"]]


def test_movements_reject_invalid_date_range(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/inventory/movements?date_from=2026-07-31&date_to=2026-07-01",
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_void_entry_decreases_stock(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="10",
    )

    voided = _void_movement(client, api_auth_headers, movement["id"])

    assert voided["status"] == "voided"
    assert voided["void_reason"] == "Error de registro"
    assert voided["voided_at"] is not None
    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal("0.000")


def test_void_exit_increases_stock(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="10",
    )
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type="exit",
        quantity="4",
    )

    _void_movement(client, api_auth_headers, movement["id"])

    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal("10.000")


@pytest.mark.parametrize(
    ("movement_type", "stock_before_void", "stock_after_void"),
    [
        ("adjustment_in", "12.000", "10.000"),
        ("adjustment_out", "8.000", "10.000"),
    ],
)
def test_void_adjustment_reverses_stock(
    api_client,
    api_auth_headers,
    movement_type: str,
    stock_before_void: str,
    stock_after_void: str,
) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="10",
    )
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type=movement_type,
        quantity="2",
    )
    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal(stock_before_void)

    _void_movement(client, api_auth_headers, movement["id"])

    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal(stock_after_void)


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_movement_requires_reason(
    api_client,
    api_auth_headers,
    payload: dict[str, str],
) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )

    response = client.post(
        f"/api/v1/inventory/movements/{movement['id']}/void",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_void_movement_cannot_be_repeated(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )
    _void_movement(client, api_auth_headers, movement["id"])

    response = client.post(
        f"/api/v1/inventory/movements/{movement['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Segundo intento"},
    )

    assert response.status_code == 409


def test_void_movement_does_not_delete_record(api_client, api_auth_headers) -> None:
    client, testing_session_local = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    movement = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )
    _void_movement(client, api_auth_headers, movement["id"])

    with testing_session_local() as session:
        stored_movement = session.get(InventoryMovement, movement["id"])

    assert stored_movement is not None
    assert stored_movement.status == "voided"


def test_void_entry_rejects_negative_reversal(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    entry = _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        quantity="10",
    )
    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
        movement_type="exit",
        quantity="7",
    )

    response = client.post(
        f"/api/v1/inventory/movements/{entry['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Entrada incorrecta"},
    )

    assert response.status_code == 400
    assert "stock actual es insuficiente" in response.json()["detail"]
    assert Decimal(_get_single_stock(client, api_auth_headers)["quantity_on_hand"]) == Decimal("3.000")


def test_inventory_movement_does_not_modify_other_modules(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product, location = _setup_inventory(client, api_auth_headers)
    with testing_session_local() as session:
        stored_product = session.get(Product, product["id"])
        assert stored_product is not None
        price_before = stored_product.default_price
        counts_before = (
            session.query(Sale).count(),
            session.query(CreditPayment).count(),
            session.query(CashSession).count(),
            session.query(Customer).count(),
        )

    _create_movement(
        client,
        api_auth_headers,
        product["id"],
        location["id"],
    )

    with testing_session_local() as session:
        stored_product = session.get(Product, product["id"])
        assert stored_product is not None
        assert stored_product.default_price == price_before
        assert (
            session.query(Sale).count(),
            session.query(CreditPayment).count(),
            session.query(CashSession).count(),
            session.query(Customer).count(),
        ) == counts_before


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("POST", "/api/v1/inventory/locations", {"name": "Bodega"}),
        ("GET", "/api/v1/inventory/locations", None),
        ("GET", "/api/v1/inventory/locations/1", None),
        ("PATCH", "/api/v1/inventory/locations/1", {"name": "Bodega"}),
        ("PATCH", "/api/v1/inventory/locations/1/deactivate", None),
        ("PATCH", "/api/v1/inventory/locations/1/activate", None),
        ("GET", "/api/v1/inventory/stocks", None),
        (
            "POST",
            "/api/v1/inventory/movements",
            {
                "movement_date": "2026-07-18",
                "movement_type": "entry",
                "product_id": 1,
                "location_id": 1,
                "quantity": "1",
            },
        ),
        ("GET", "/api/v1/inventory/movements", None),
        ("GET", "/api/v1/inventory/movements/1", None),
        (
            "POST",
            "/api/v1/inventory/movements/1/void",
            {"reason": "Error"},
        ),
    ],
)
def test_inventory_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=payload)

    assert response.status_code == 401


def test_inventory_migration_creates_required_tables(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0011_create_inventory.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0011_inventory",
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
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda *args, **kwargs: None,
    )

    migration.upgrade()

    assert migration.revision == "0011_inventory"
    assert len(migration.revision) <= 32
    assert migration.down_revision == "0010_payments"
    assert created_tables == [
        "inventory_locations",
        "inventory_stocks",
        "inventory_movements",
    ]


def _setup_inventory(client, headers) -> tuple[dict, dict]:
    return (
        _create_product(client, headers),
        _create_location(client, headers),
    )


def _create_product(
    client,
    headers,
    *,
    sku: str = "BIDON-20L",
    name: str = "Bidon 20L",
) -> dict:
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": sku,
            "name": name,
            "category": "water",
            "unit": "container",
            "presentation": "20L",
            "default_price": "1.00",
            "cost_estimate": "0.40",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_vehicle(client, headers) -> dict:
    response = client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "code": "CAM-01",
            "name": "Camion 1",
            "vehicle_type": "truck",
            "fuel_type": "diesel",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_location(
    client,
    headers,
    *,
    code: str | None = "BODEGA-PRINCIPAL",
    name: str = "Bodega principal",
    location_type: str = "warehouse",
) -> dict:
    response = client.post(
        "/api/v1/inventory/locations",
        headers=headers,
        json={
            "code": code,
            "name": name,
            "location_type": location_type,
        },
    )
    assert response.status_code == 201
    return response.json()


def _movement_response(
    client,
    headers,
    product_id: int,
    location_id: int,
    *,
    movement_date: str = "2026-07-18",
    movement_type: str = "entry",
    quantity: str = "1",
    unit_cost: str | None = "0.40",
):
    return client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "movement_date": movement_date,
            "movement_type": movement_type,
            "product_id": product_id,
            "location_id": location_id,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "reason": "Movimiento de prueba",
        },
    )


def _create_movement(
    client,
    headers,
    product_id: int,
    location_id: int,
    **kwargs,
) -> dict:
    response = _movement_response(
        client,
        headers,
        product_id,
        location_id,
        **kwargs,
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _get_single_stock(client, headers) -> dict:
    response = client.get("/api/v1/inventory/stocks", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    return items[0]


def _void_movement(client, headers, movement_id: int) -> dict:
    response = client.post(
        f"/api/v1/inventory/movements/{movement_id}/void",
        headers=headers,
        json={"reason": "Error de registro"},
    )
    assert response.status_code == 200, response.json()
    return response.json()

import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from app.models.cash_session import CashSession
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.product import Product
from app.models.production_batch import ProductionBatch
from app.models.production_material_consumption import (
    ProductionMaterialConsumption,
)
from app.models.production_material_consumption_item import (
    ProductionMaterialConsumptionItem,
)
from app.models.production_recipe import ProductionRecipe
from app.models.production_recipe_item import ProductionRecipeItem
from app.models.purchase import Purchase
from app.models.sale import Sale


def test_preview_is_read_only_and_calculates_waste_from_gross_production(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    scenario = _create_scenario(
        client,
        api_auth_headers,
        quantity_produced="100",
        quantity_waste="20",
        quantity_required="1.250",
        waste_percentage="10",
        stock="200",
        unit_cost="0.1234",
    )

    response = _preview(client, api_auth_headers, scenario)

    assert response.status_code == 200, response.json()
    preview = response.json()
    assert preview["production_batch_id"] == scenario["batch"]["id"]
    assert preview["source_location_id"] == scenario["location"]["id"]
    assert Decimal(preview["items"][0]["quantity_consumed"]) == Decimal("137.500")
    assert Decimal(preview["items"][0]["available_stock"]) == Decimal("200.000")
    assert Decimal(preview["items"][0]["unit_cost"]) == Decimal("0.1234")
    assert Decimal(preview["items"][0]["total_cost"]) == Decimal("16.9675")
    assert Decimal(preview["total_material_cost"]) == Decimal("16.9675")
    assert preview["items"][0]["has_sufficient_stock"] is True
    with testing_session_local() as session:
        assert session.query(ProductionMaterialConsumption).count() == 0
        assert session.query(ProductionMaterialConsumptionItem).count() == 0
        assert session.query(InventoryMovement).count() == 1
        stock = session.query(InventoryStock).one()
        assert stock.quantity_on_hand == Decimal("200.000")


def test_preview_marks_aggregate_repeated_input_as_insufficient(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    input_product = _create_product(
        client,
        api_auth_headers,
        sku="TAPA",
        name="Tapa",
        product_kind="supply",
    )
    first_output = _create_product(
        client,
        api_auth_headers,
        sku="OUT-1",
        name="Bidon A",
    )
    second_output = _create_product(
        client,
        api_auth_headers,
        sku="OUT-2",
        name="Bidon B",
    )
    first_recipe = _create_active_recipe(
        client,
        api_auth_headers,
        first_output["id"],
        input_product["id"],
        quantity_required="1",
    )
    second_recipe = _create_active_recipe(
        client,
        api_auth_headers,
        second_output["id"],
        input_product["id"],
        quantity_required="1",
    )
    location = _create_location(client, api_auth_headers)
    _add_stock(
        client,
        api_auth_headers,
        input_product["id"],
        location["id"],
        "15",
    )
    batch = _create_batch(
        client,
        api_auth_headers,
        [(first_output["id"], "10", "0"), (second_output["id"], "10", "0")],
    )
    scenario = {
        "batch": batch,
        "location": location,
        "selections": [
            {
                "production_item_id": batch["items"][0]["id"],
                "recipe_id": first_recipe["id"],
            },
            {
                "production_item_id": batch["items"][1]["id"],
                "recipe_id": second_recipe["id"],
            },
        ],
    }

    response = _preview(client, api_auth_headers, scenario)

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
    assert all(
        item["has_sufficient_stock"] is False
        for item in response.json()["items"]
    )


def test_apply_creates_exit_movements_snapshots_and_decreases_stock(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    scenario = _create_scenario(
        client,
        api_auth_headers,
        quantity_produced="50",
        quantity_required="1",
        stock="100",
        unit_cost="0.0500",
    )
    second_input = _create_product(
        client,
        api_auth_headers,
        sku="ETIQUETA",
        name="Etiqueta",
        product_kind="packaging",
    )
    second_item = client.post(
        f"/api/v1/production/recipes/{scenario['recipe']['id']}/items",
        headers=api_auth_headers,
        json={
            "input_product_id": second_input["id"],
            "quantity_required": "2",
            "unit_cost": "0.0300",
            "waste_percentage": "0",
        },
    )
    assert second_item.status_code == 201, second_item.json()
    _add_stock(
        client,
        api_auth_headers,
        second_input["id"],
        scenario["location"]["id"],
        "150",
    )

    response = _apply(client, api_auth_headers, scenario)

    assert response.status_code == 201, response.json()
    consumption = response.json()
    assert consumption["consumption_number"].startswith("PMC-20260718-")
    assert consumption["production_number"] == scenario["batch"]["production_number"]
    assert consumption["source_location_name"] == scenario["location"]["name"]
    assert consumption["status"] == "active"
    assert len(consumption["items"]) == 2
    assert Decimal(consumption["total_material_cost"]) == Decimal("5.5000")
    assert {
        (item["input_product_name_snapshot"], item["quantity_consumed"])
        for item in consumption["items"]
    } == {("Tapa", "50.000"), ("Etiqueta", "100.000")}
    assert all(item["recipe_number_snapshot"] for item in consumption["items"])
    assert all(item["recipe_name_snapshot"] for item in consumption["items"])

    with testing_session_local() as session:
        movements = (
            session.query(InventoryMovement)
            .filter(InventoryMovement.movement_type == "exit")
            .all()
        )
        stocks = {
            stock.product_id: stock.quantity_on_hand
            for stock in session.query(InventoryStock).all()
        }
        stored_items = session.query(ProductionMaterialConsumptionItem).all()
        assert len(movements) == 2
        assert all(movement.status == "active" for movement in movements)
        assert stocks[scenario["input_product"]["id"]] == Decimal("50.000")
        assert stocks[second_input["id"]] == Decimal("50.000")
        assert len(stored_items) == 2
        assert {item.inventory_movement_id for item in stored_items} == {
            movement.id for movement in movements
        }


def test_apply_multiple_production_items_is_atomic(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    first = _create_scenario(client, api_auth_headers, stock="100", sku_suffix="A")
    second_output = _create_product(
        client,
        api_auth_headers,
        sku="OUTPUT-B",
        name="Producto final B",
    )
    second_input = _create_product(
        client,
        api_auth_headers,
        sku="INPUT-B",
        name="Insumo B",
        product_kind="raw_material",
    )
    second_recipe = _create_active_recipe(
        client,
        api_auth_headers,
        second_output["id"],
        second_input["id"],
    )
    _add_stock(
        client,
        api_auth_headers,
        second_input["id"],
        first["location"]["id"],
        "100",
    )
    batch = _create_batch(
        client,
        api_auth_headers,
        [
            (first["output_product"]["id"], "10", "0"),
            (second_output["id"], "20", "5"),
        ],
    )
    scenario = {
        "batch": batch,
        "location": first["location"],
        "selections": [
            {
                "production_item_id": batch["items"][0]["id"],
                "recipe_id": first["recipe"]["id"],
            },
            {
                "production_item_id": batch["items"][1]["id"],
                "recipe_id": second_recipe["id"],
            },
        ],
    }

    response = _apply(client, api_auth_headers, scenario)

    assert response.status_code == 201, response.json()
    assert {item["quantity_consumed"] for item in response.json()["items"]} == {
        "10.000",
        "20.000",
    }
    with testing_session_local() as session:
        assert session.query(ProductionMaterialConsumption).count() == 1
        assert session.query(ProductionMaterialConsumptionItem).count() == 2


def test_apply_rejects_insufficient_stock_without_partial_changes(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    scenario = _create_scenario(
        client,
        api_auth_headers,
        quantity_produced="20",
        stock="10",
    )

    response = _apply(client, api_auth_headers, scenario)

    assert response.status_code == 400
    assert "stock suficiente" in response.json()["detail"]
    with testing_session_local() as session:
        assert session.query(ProductionMaterialConsumption).count() == 0
        assert (
            session.query(InventoryMovement)
            .filter(InventoryMovement.movement_type == "exit")
            .count()
            == 0
        )
        assert session.query(InventoryStock).one().quantity_on_hand == Decimal(
            "10.000",
        )


@pytest.mark.parametrize(
    ("mutation", "expected_detail"),
    [
        ("missing_batch", "La produccion no existe."),
        ("missing_location", "La ubicacion de inventario no existe."),
        ("foreign_item", "El producto producido no pertenece"),
        ("missing_recipe", "La formula de produccion no existe."),
        ("wrong_recipe", "no corresponde al producto"),
        ("incomplete_selection", "Debe seleccionar una formula para cada producto"),
        ("duplicate_selection", "una sola formula seleccionada"),
    ],
)
def test_preview_validates_references_and_selection(
    api_client,
    api_auth_headers,
    mutation,
    expected_detail,
) -> None:
    client, _ = api_client
    scenario = _create_scenario(client, api_auth_headers)
    batch_id = scenario["batch"]["id"]
    payload = _payload(scenario)
    if mutation == "missing_batch":
        batch_id = 99999
    elif mutation == "missing_location":
        payload["source_location_id"] = 99999
    elif mutation == "foreign_item":
        other = _create_batch(
            client,
            api_auth_headers,
            [(scenario["output_product"]["id"], "1", "0")],
        )
        payload["items"][0]["production_item_id"] = other["items"][0]["id"]
    elif mutation == "missing_recipe":
        payload["items"][0]["recipe_id"] = 99999
    elif mutation == "wrong_recipe":
        other_output = _create_product(
            client,
            api_auth_headers,
            sku="OTHER-OUTPUT",
            name="Otro terminado",
        )
        wrong = _create_active_recipe(
            client,
            api_auth_headers,
            other_output["id"],
            scenario["input_product"]["id"],
        )
        payload["items"][0]["recipe_id"] = wrong["id"]
    elif mutation == "incomplete_selection":
        second_output = _create_product(
            client,
            api_auth_headers,
            sku="SECOND-OUTPUT",
            name="Segundo terminado",
        )
        second_batch = _create_batch(
            client,
            api_auth_headers,
            [
                (scenario["output_product"]["id"], "1", "0"),
                (second_output["id"], "1", "0"),
            ],
        )
        batch_id = second_batch["id"]
        payload["items"][0]["production_item_id"] = second_batch["items"][0]["id"]
    elif mutation == "duplicate_selection":
        payload["items"].append(dict(payload["items"][0]))

    response = client.post(
        f"/api/v1/production/batches/{batch_id}/material-consumption/preview",
        headers=api_auth_headers,
        json=payload,
    )

    expected_status = 404 if "no existe" in expected_detail else 400
    assert response.status_code == expected_status, response.json()
    assert expected_detail in response.json()["detail"]


def test_preview_rejects_voided_batch_inactive_location_and_recipe(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    batch_scenario = _create_scenario(
        client,
        api_auth_headers,
        sku_suffix="VOID-BATCH",
    )
    assert client.post(
        f"/api/v1/production/batches/{batch_scenario['batch']['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    ).status_code == 200
    voided_batch = _preview(client, api_auth_headers, batch_scenario)

    location_scenario = _create_scenario(
        client,
        api_auth_headers,
        sku_suffix="INACTIVE-LOCATION",
    )
    assert client.patch(
        f"/api/v1/inventory/locations/{location_scenario['location']['id']}/deactivate",
        headers=api_auth_headers,
    ).status_code == 200
    inactive_location = _preview(client, api_auth_headers, location_scenario)

    recipe_scenario = _create_scenario(
        client,
        api_auth_headers,
        sku_suffix="INACTIVE-RECIPE",
    )
    assert client.patch(
        f"/api/v1/production/recipes/{recipe_scenario['recipe']['id']}/deactivate",
        headers=api_auth_headers,
    ).status_code == 200
    inactive_recipe = _preview(client, api_auth_headers, recipe_scenario)

    assert voided_batch.status_code == 400
    assert inactive_location.status_code == 400
    assert inactive_recipe.status_code == 400


def test_preview_rejects_recipe_without_active_items(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    scenario = _create_scenario(client, api_auth_headers, sku_suffix="NO-ITEMS")
    recipe_item_id = scenario["recipe"]["items"][0]["id"]
    deactivate = client.patch(
        f"/api/v1/production/recipe-items/{recipe_item_id}/deactivate",
        headers=api_auth_headers,
    )
    assert deactivate.status_code == 200

    response = _preview(client, api_auth_headers, scenario)

    assert response.status_code == 400
    assert response.json()["detail"] == "La formula no tiene insumos activos."


def test_active_consumption_is_unique_and_blocks_production_void(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    scenario = _create_scenario(client, api_auth_headers, stock="100")
    first = _apply(client, api_auth_headers, scenario)
    second = _apply(client, api_auth_headers, scenario)
    void_batch = client.post(
        f"/api/v1/production/batches/{scenario['batch']['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Error"},
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert void_batch.status_code == 409
    assert void_batch.json()["detail"] == (
        "Primero anule el consumo de insumos antes de anular la produccion."
    )


def test_batch_status_list_detail_and_filters(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    scenario = _create_scenario(client, api_auth_headers, stock="100")
    before = client.get(
        f"/api/v1/production/batches/{scenario['batch']['id']}/material-consumption",
        headers=api_auth_headers,
    )
    created = _apply(client, api_auth_headers, scenario).json()
    after = client.get(
        f"/api/v1/production/batches/{scenario['batch']['id']}/material-consumption",
        headers=api_auth_headers,
    )
    detail = client.get(
        f"/api/v1/production/material-consumptions/{created['id']}",
        headers=api_auth_headers,
    )
    listed = client.get(
        "/api/v1/production/material-consumptions",
        headers=api_auth_headers,
        params={
            "date_from": "2026-07-18",
            "date_to": "2026-07-18",
            "status": "active",
            "production_batch_id": scenario["batch"]["id"],
            "source_location_id": scenario["location"]["id"],
            "input_product_id": scenario["input_product"]["id"],
            "search": created["consumption_number"],
        },
    )

    assert before.status_code == 200
    assert before.json() == {
        "status": "not_consumed",
        "active_consumption": None,
    }
    assert after.status_code == 200
    assert after.json()["status"] == "consumed"
    assert after.json()["active_consumption"]["id"] == created["id"]
    assert detail.status_code == 200
    assert detail.json()["id"] == created["id"]
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [created["id"]]


def test_void_reverses_stock_voids_movements_and_preserves_history(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    scenario = _create_scenario(
        client,
        api_auth_headers,
        quantity_produced="25",
        stock="100",
    )
    created = _apply(client, api_auth_headers, scenario).json()

    response = client.post(
        f"/api/v1/production/material-consumptions/{created['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Registro por error"},
    )

    assert response.status_code == 200, response.json()
    assert response.json()["status"] == "voided"
    assert response.json()["void_reason"] == "Registro por error"
    assert response.json()["voided_at"] is not None
    with testing_session_local() as session:
        stored = session.get(ProductionMaterialConsumption, created["id"])
        movement = session.get(
            InventoryMovement,
            created["items"][0]["inventory_movement_id"],
        )
        stock = session.query(InventoryStock).one()
        assert stored is not None and stored.status == "voided"
        assert movement is not None and movement.status == "voided"
        assert movement.void_reason == (
            "Consumo de insumos anulado: Registro por error"
        )
        assert stock.quantity_on_hand == Decimal("100.000")
        assert session.query(ProductionMaterialConsumptionItem).count() == 1

    second_void = client.post(
        f"/api/v1/production/material-consumptions/{created['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Otra vez"},
    )
    assert second_void.status_code == 409


def test_voided_consumption_allows_new_consumption_and_batch_void_afterward(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    scenario = _create_scenario(client, api_auth_headers, stock="100")
    first = _apply(client, api_auth_headers, scenario).json()
    assert _void(client, api_auth_headers, first["id"]).status_code == 200
    second = _apply(client, api_auth_headers, scenario)
    assert second.status_code == 201
    assert second.json()["id"] != first["id"]
    assert _void(
        client,
        api_auth_headers,
        second.json()["id"],
    ).status_code == 200
    void_batch = client.post(
        f"/api/v1/production/batches/{scenario['batch']['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Registro incorrecto"},
    )
    assert void_batch.status_code == 200
    assert void_batch.json()["status"] == "voided"


def test_consumption_movement_cannot_be_voided_directly(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    scenario = _create_scenario(client, api_auth_headers, stock="100")
    created = _apply(client, api_auth_headers, scenario).json()

    response = client.post(
        "/api/v1/inventory/movements/"
        f"{created['items'][0]['inventory_movement_id']}/void",
        headers=api_auth_headers,
        json={"reason": "Intento manual"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Anule el consumo desde el modulo de consumo de insumos."
    )


def test_apply_does_not_modify_cash_purchases_sales_batch_recipe_or_products(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    scenario = _create_scenario(
        client,
        api_auth_headers,
        stock="100",
        sku_suffix="ISOLATION",
    )
    with testing_session_local() as session:
        batch = session.get(ProductionBatch, scenario["batch"]["id"])
        recipe = session.get(ProductionRecipe, scenario["recipe"]["id"])
        recipe_item = session.get(
            ProductionRecipeItem,
            scenario["recipe"]["items"][0]["id"],
        )
        output_product = session.get(
            Product,
            scenario["output_product"]["id"],
        )
        input_product = session.get(
            Product,
            scenario["input_product"]["id"],
        )
        assert all(
            value is not None
            for value in (
                batch,
                recipe,
                recipe_item,
                output_product,
                input_product,
            )
        )
        snapshots = {
            "batch": (
                batch.production_number,
                batch.production_date,
                batch.status,
                batch.notes,
                batch.updated_at,
            ),
            "recipe": (
                recipe.recipe_number,
                recipe.name,
                recipe.output_quantity,
                recipe.status,
                recipe.estimated_material_cost,
                recipe.updated_at,
            ),
            "recipe_item": (
                recipe_item.quantity_required,
                recipe_item.unit_cost,
                recipe_item.waste_percentage,
                recipe_item.is_active,
                recipe_item.updated_at,
            ),
            "output_product": (
                output_product.name,
                output_product.cost_estimate,
                output_product.updated_at,
            ),
            "input_product": (
                input_product.name,
                input_product.cost_estimate,
                input_product.updated_at,
            ),
        }

    response = _apply(client, api_auth_headers, scenario)
    assert response.status_code == 201, response.json()

    with testing_session_local() as session:
        batch = session.get(ProductionBatch, scenario["batch"]["id"])
        recipe = session.get(ProductionRecipe, scenario["recipe"]["id"])
        recipe_item = session.get(
            ProductionRecipeItem,
            scenario["recipe"]["items"][0]["id"],
        )
        output_product = session.get(
            Product,
            scenario["output_product"]["id"],
        )
        input_product = session.get(
            Product,
            scenario["input_product"]["id"],
        )
        assert session.query(CashSession).count() == 0
        assert session.query(Purchase).count() == 0
        assert session.query(Sale).count() == 0
        assert snapshots["batch"] == (
            batch.production_number,
            batch.production_date,
            batch.status,
            batch.notes,
            batch.updated_at,
        )
        assert snapshots["recipe"] == (
            recipe.recipe_number,
            recipe.name,
            recipe.output_quantity,
            recipe.status,
            recipe.estimated_material_cost,
            recipe.updated_at,
        )
        assert snapshots["recipe_item"] == (
            recipe_item.quantity_required,
            recipe_item.unit_cost,
            recipe_item.waste_percentage,
            recipe_item.is_active,
            recipe_item.updated_at,
        )
        assert snapshots["output_product"] == (
            output_product.name,
            output_product.cost_estimate,
            output_product.updated_at,
        )
        assert snapshots["input_product"] == (
            input_product.name,
            input_product.cost_estimate,
            input_product.updated_at,
        )


@pytest.mark.parametrize("payload", [{}, {"reason": "   "}])
def test_void_requires_reason(api_client, api_auth_headers, payload) -> None:
    client, _ = api_client
    response = client.post(
        "/api/v1/production/material-consumptions/1/void",
        headers=api_auth_headers,
        json=payload,
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/api/v1/production/batches/1/material-consumption/preview",
            {
                "source_location_id": 1,
                "movement_date": "2026-07-18",
                "items": [{"production_item_id": 1, "recipe_id": 1}],
            },
        ),
        (
            "POST",
            "/api/v1/production/batches/1/material-consumption",
            {
                "source_location_id": 1,
                "movement_date": "2026-07-18",
                "items": [{"production_item_id": 1, "recipe_id": 1}],
            },
        ),
        (
            "GET",
            "/api/v1/production/batches/1/material-consumption",
            None,
        ),
        ("GET", "/api/v1/production/material-consumptions", None),
        ("GET", "/api/v1/production/material-consumptions/1", None),
        (
            "POST",
            "/api/v1/production/material-consumptions/1/void",
            {"reason": "Error"},
        ),
    ],
)
def test_material_consumption_endpoints_require_authentication(
    api_client,
    method,
    path,
    payload,
) -> None:
    client, _ = api_client
    response = client.request(method, path, json=payload)
    assert response.status_code == 401


def test_material_consumption_migration_creates_required_tables(
    monkeypatch,
) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0025_create_production_material_consumptions.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0025_materials",
        migration_path,
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []
    created_indexes: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *args, **kwargs: created_tables.append(
            (table_name, args),
        ),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda *args, **kwargs: created_indexes.append((args, kwargs)),
    )

    migration.upgrade()

    assert migration.revision == "0025_materials"
    assert migration.down_revision == "0024_recipes"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == [
        "production_material_consumptions",
        "production_material_consumption_items",
    ]
    for _, table_elements in created_tables:
        assert any(
            isinstance(element, migration.sa.PrimaryKeyConstraint)
            for element in table_elements
        )
        assert any(
            isinstance(element, migration.sa.ForeignKeyConstraint)
            for element in table_elements
        )
        assert any(
            isinstance(element, migration.sa.CheckConstraint)
            for element in table_elements
        )
    active_index = next(
        (args, kwargs)
        for args, kwargs in created_indexes
        if args[0] == "uq_production_material_consumptions_active_batch"
    )
    assert active_index[1]["unique"] is True
    assert "postgresql_where" in active_index[1]


def _create_scenario(
    client,
    headers,
    *,
    quantity_produced="10",
    quantity_waste="0",
    quantity_required="1",
    waste_percentage="0",
    stock="50",
    unit_cost="0.0500",
    sku_suffix="",
):
    suffix = f"-{sku_suffix}" if sku_suffix else ""
    output = _create_product(
        client,
        headers,
        sku=f"OUTPUT{suffix}",
        name=f"Producto final{suffix}",
    )
    input_product = _create_product(
        client,
        headers,
        sku=f"INPUT{suffix}",
        name="Tapa" if not suffix else f"Insumo{suffix}",
        product_kind="supply",
    )
    recipe = _create_active_recipe(
        client,
        headers,
        output["id"],
        input_product["id"],
        quantity_required=quantity_required,
        waste_percentage=waste_percentage,
        unit_cost=unit_cost,
    )
    location = _create_location(client, headers, suffix=sku_suffix)
    _add_stock(client, headers, input_product["id"], location["id"], stock)
    batch = _create_batch(
        client,
        headers,
        [(output["id"], quantity_produced, quantity_waste)],
    )
    return {
        "output_product": output,
        "input_product": input_product,
        "recipe": recipe,
        "location": location,
        "batch": batch,
        "selections": [
            {
                "production_item_id": batch["items"][0]["id"],
                "recipe_id": recipe["id"],
            },
        ],
    }


def _create_product(client, headers, *, sku, name, product_kind="finished_good"):
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": sku,
            "name": name,
            "category": "other",
            "unit": "unit",
            "default_price": "1.00",
            "cost_estimate": "0.05",
            "product_kind": product_kind,
            "is_returnable_container": False,
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_active_recipe(
    client,
    headers,
    output_product_id,
    input_product_id,
    *,
    quantity_required="1",
    waste_percentage="0",
    unit_cost="0.0500",
):
    recipe_response = client.post(
        "/api/v1/production/recipes",
        headers=headers,
        json={
            "name": f"Formula {output_product_id}",
            "output_product_id": output_product_id,
            "output_quantity": "1",
        },
    )
    assert recipe_response.status_code == 201, recipe_response.json()
    recipe = recipe_response.json()
    item_response = client.post(
        f"/api/v1/production/recipes/{recipe['id']}/items",
        headers=headers,
        json={
            "input_product_id": input_product_id,
            "quantity_required": quantity_required,
            "unit_cost": unit_cost,
            "waste_percentage": waste_percentage,
        },
    )
    assert item_response.status_code == 201, item_response.json()
    activate = client.patch(
        f"/api/v1/production/recipes/{recipe['id']}/activate",
        headers=headers,
    )
    assert activate.status_code == 200, activate.json()
    return activate.json()


def _create_location(client, headers, *, suffix=""):
    location_suffix = f"-{suffix}" if suffix else ""
    response = client.post(
        "/api/v1/inventory/locations",
        headers=headers,
        json={
            "code": f"BODEGA{location_suffix}",
            "name": f"Bodega principal{location_suffix}",
            "location_type": "warehouse",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _add_stock(client, headers, product_id, location_id, quantity):
    response = client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "movement_date": "2026-07-18",
            "movement_type": "entry",
            "product_id": product_id,
            "location_id": location_id,
            "quantity": quantity,
            "unit_cost": "0.05",
            "reason": "Stock inicial de prueba",
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _create_batch(client, headers, items):
    response = client.post(
        "/api/v1/production/batches",
        headers=headers,
        json={
            "production_date": "2026-07-18",
            "items": [
                {
                    "product_id": product_id,
                    "quantity_produced": produced,
                    "quantity_waste": waste,
                }
                for product_id, produced, waste in items
            ],
        },
    )
    assert response.status_code == 201, response.json()
    return response.json()


def _payload(scenario, *, notes=None):
    payload = {
        "source_location_id": scenario["location"]["id"],
        "movement_date": "2026-07-18",
        "items": scenario["selections"],
    }
    if notes is not None:
        payload["notes"] = notes
    return payload


def _preview(client, headers, scenario):
    return client.post(
        "/api/v1/production/batches/"
        f"{scenario['batch']['id']}/material-consumption/preview",
        headers=headers,
        json=_payload(scenario),
    )


def _apply(client, headers, scenario):
    return client.post(
        "/api/v1/production/batches/"
        f"{scenario['batch']['id']}/material-consumption",
        headers=headers,
        json=_payload(scenario, notes="Consumo de prueba"),
    )


def _void(client, headers, consumption_id):
    return client.post(
        f"/api/v1/production/material-consumptions/{consumption_id}/void",
        headers=headers,
        json={"reason": "Consumo incorrecto"},
    )

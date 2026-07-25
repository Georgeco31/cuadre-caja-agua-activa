import importlib.util
import re
from datetime import date, timedelta
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.models.cash_session import CashSession
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.production_batch import ProductionBatch
from app.models.production_recipe import ProductionRecipe
from app.models.production_recipe_item import ProductionRecipeItem
from app.models.purchase import Purchase
from app.models.sale import Sale


def test_classify_products_and_reject_invalid_kind(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    raw_material = _create_product(client, api_auth_headers, name="Agua tratada")
    finished_good = _create_product(client, api_auth_headers, name="Bidon 20L")

    raw_response = client.patch(
        f"/api/v1/products/{raw_material['id']}/production-classification",
        headers=api_auth_headers,
        json={
            "product_kind": "raw_material",
            "production_notes": " Materia prima principal ",
        },
    )
    finished_response = client.patch(
        f"/api/v1/products/{finished_good['id']}/production-classification",
        headers=api_auth_headers,
        json={"product_kind": "finished_good", "production_notes": None},
    )
    invalid_response = client.patch(
        f"/api/v1/products/{finished_good['id']}/production-classification",
        headers=api_auth_headers,
        json={"product_kind": "invalid"},
    )

    assert raw_response.status_code == 200
    assert raw_response.json()["product_kind"] == "raw_material"
    assert raw_response.json()["production_notes"] == "Materia prima principal"
    assert finished_response.status_code == 200
    assert finished_response.json()["product_kind"] == "finished_good"
    assert invalid_response.status_code == 422


def test_create_recipe_without_items_and_isolated_from_operational_modules(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    output_product = _create_product(
        client,
        api_auth_headers,
        name="Bidon terminado",
        product_kind="finished_good",
    )
    with testing_session_local() as session:
        before = _operational_counts(session)

    response = _recipe_response(
        client,
        api_auth_headers,
        output_product["id"],
        name=" Formula Bidon 20L ",
        output_quantity="2",
        valid_from="2026-07-18",
        notes=" Formula base ",
    )

    assert response.status_code == 201
    body = response.json()
    assert re.fullmatch(r"REC-\d{8}-\d{4,}", body["recipe_number"])
    assert body["name"] == "Formula Bidon 20L"
    assert body["output_product_id"] == output_product["id"]
    assert body["output_product_name"] == "Bidon terminado"
    assert body["output_quantity"] == "2.000"
    assert body["status"] == "inactive"
    assert body["estimated_material_cost"] == "0.0000"
    assert body["estimated_cost_per_unit"] == "0.0000"
    assert body["notes"] == "Formula base"
    assert body["items"] == []

    with testing_session_local() as session:
        assert _operational_counts(session) == before
        assert session.scalar(select(func.count(ProductionRecipe.id))) == 1
        assert session.scalar(select(func.count(ProductionRecipeItem.id))) == 0


def test_recipe_rejects_missing_inactive_product_and_invalid_quantity(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    inactive = _create_product(client, api_auth_headers, name="Inactivo")
    client.patch(
        f"/api/v1/products/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    missing = _recipe_response(client, api_auth_headers, 999)
    inactive_response = _recipe_response(
        client,
        api_auth_headers,
        inactive["id"],
    )
    zero = _recipe_response(
        client,
        api_auth_headers,
        inactive["id"],
        output_quantity="0",
    )
    negative = _recipe_response(
        client,
        api_auth_headers,
        inactive["id"],
        output_quantity="-1",
    )

    assert missing.status_code == 404
    assert inactive_response.status_code == 400
    assert "esta inactivo" in inactive_response.json()["detail"]
    assert zero.status_code == 422
    assert negative.status_code == 422


@pytest.mark.parametrize(
    "item_overrides",
    [
        {"quantity_required": "0"},
        {"quantity_required": "-1"},
        {"unit_cost": "-0.0001"},
        {"waste_percentage": "-0.001"},
    ],
)
def test_recipe_item_rejects_invalid_amounts(
    api_client,
    api_auth_headers,
    item_overrides,
) -> None:
    client, _ = api_client
    recipe, input_product = _recipe_with_products(client, api_auth_headers)

    response = _item_response(
        client,
        api_auth_headers,
        recipe["id"],
        input_product["id"],
        **item_overrides,
    )

    assert response.status_code == 422


def test_recipe_item_rejects_missing_and_inactive_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    recipe, input_product = _recipe_with_products(client, api_auth_headers)
    client.patch(
        f"/api/v1/products/{input_product['id']}/deactivate",
        headers=api_auth_headers,
    )

    missing = _item_response(
        client,
        api_auth_headers,
        recipe["id"],
        999,
    )
    inactive = _item_response(
        client,
        api_auth_headers,
        recipe["id"],
        input_product["id"],
    )

    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert "esta inactivo" in inactive.json()["detail"]


def test_add_item_uses_default_cost_saves_snapshots_and_recalculates(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    recipe, input_product = _recipe_with_products(
        client,
        api_auth_headers,
        input_overrides={
            "sku": "TAPA-01",
            "name": "Tapa plastica",
            "presentation": "Unidad",
            "product_kind": "supply",
            "cost_estimate": "0.03",
        },
        recipe_overrides={"output_quantity": "2"},
    )

    response = client.post(
        f"/api/v1/production/recipes/{recipe['id']}/items",
        headers=api_auth_headers,
        json={
            "input_product_id": input_product["id"],
            "quantity_required": "4",
            "waste_percentage": "1.5",
            "notes": " Tapa del bidon ",
        },
    )
    detail = client.get(
        f"/api/v1/production/recipes/{recipe['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 201
    item = response.json()
    assert item["input_product_sku_snapshot"] == "TAPA-01"
    assert item["input_product_name_snapshot"] == "Tapa plastica"
    assert item["input_product_kind_snapshot"] == "supply"
    assert item["input_product_presentation_snapshot"] == "Unidad"
    assert item["quantity_required"] == "4.000"
    assert item["unit_cost"] == "0.0300"
    assert item["total_cost"] == "0.1200"
    assert item["waste_percentage"] == "1.500"
    assert item["notes"] == "Tapa del bidon"
    assert item["is_active"] is True
    assert detail.status_code == 200
    assert detail.json()["estimated_material_cost"] == "0.1200"
    assert detail.json()["estimated_cost_per_unit"] == "0.0600"

    client.patch(
        f"/api/v1/products/{input_product['id']}",
        headers=api_auth_headers,
        json={
            "name": "Tapa renombrada",
            "presentation": "Funda",
            "product_kind": "packaging",
        },
    )
    unchanged = client.get(
        f"/api/v1/production/recipes/{recipe['id']}",
        headers=api_auth_headers,
    ).json()["items"][0]
    assert unchanged["input_product_name_snapshot"] == "Tapa plastica"
    assert unchanged["input_product_presentation_snapshot"] == "Unidad"
    assert unchanged["input_product_kind_snapshot"] == "supply"


def test_update_and_toggle_item_recalculate_recipe_costs(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    recipe, input_product = _recipe_with_products(client, api_auth_headers)
    item = _create_item(
        client,
        api_auth_headers,
        recipe["id"],
        input_product["id"],
        quantity_required="2",
        unit_cost="0.25",
    )

    updated = client.patch(
        f"/api/v1/production/recipe-items/{item['id']}",
        headers=api_auth_headers,
        json={
            "quantity_required": "3",
            "unit_cost": "0.20",
            "waste_percentage": "2",
        },
    )
    after_update = _get_recipe(client, api_auth_headers, recipe["id"])
    deactivated = client.patch(
        f"/api/v1/production/recipe-items/{item['id']}/deactivate",
        headers=api_auth_headers,
    )
    after_deactivate = _get_recipe(client, api_auth_headers, recipe["id"])
    activated = client.patch(
        f"/api/v1/production/recipe-items/{item['id']}/activate",
        headers=api_auth_headers,
    )
    after_activate = _get_recipe(client, api_auth_headers, recipe["id"])

    assert updated.status_code == 200
    assert updated.json()["total_cost"] == "0.6000"
    assert after_update["estimated_material_cost"] == "0.6000"
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
    assert after_deactivate["estimated_material_cost"] == "0.0000"
    assert after_deactivate["estimated_cost_per_unit"] == "0.0000"
    assert activated.status_code == 200
    assert activated.json()["is_active"] is True
    assert after_activate["estimated_material_cost"] == "0.6000"


def test_recipe_activation_deactivation_and_void_lifecycle(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    recipe, input_product = _recipe_with_products(client, api_auth_headers)
    no_items = client.patch(
        f"/api/v1/production/recipes/{recipe['id']}/activate",
        headers=api_auth_headers,
    )
    item = _create_item(
        client,
        api_auth_headers,
        recipe["id"],
        input_product["id"],
    )
    activate = client.patch(
        f"/api/v1/production/recipes/{recipe['id']}/activate",
        headers=api_auth_headers,
    )
    deactivate = client.patch(
        f"/api/v1/production/recipes/{recipe['id']}/deactivate",
        headers=api_auth_headers,
    )
    blank_void = client.post(
        f"/api/v1/production/recipes/{recipe['id']}/void",
        headers=api_auth_headers,
        json={"reason": "   "},
    )
    voided = client.post(
        f"/api/v1/production/recipes/{recipe['id']}/void",
        headers=api_auth_headers,
        json={"reason": " Formula registrada por error "},
    )
    repeated = client.post(
        f"/api/v1/production/recipes/{recipe['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Otra vez"},
    )
    edit_item = client.patch(
        f"/api/v1/production/recipe-items/{item['id']}",
        headers=api_auth_headers,
        json={"unit_cost": "1"},
    )

    assert no_items.status_code == 400
    assert activate.status_code == 200
    assert activate.json()["status"] == "active"
    assert deactivate.status_code == 200
    assert deactivate.json()["status"] == "inactive"
    assert blank_void.status_code == 422
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    assert voided.json()["void_reason"] == "Formula registrada por error"
    assert voided.json()["voided_at"] is not None
    assert repeated.status_code == 409
    assert edit_item.status_code == 409


def test_cost_estimate_base_and_scaled_quantities(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    recipe, first_input = _recipe_with_products(
        client,
        api_auth_headers,
        recipe_overrides={"output_quantity": "1"},
    )
    second_input = _create_product(
        client,
        api_auth_headers,
        name="Etiqueta",
        product_kind="packaging",
    )
    _create_item(
        client,
        api_auth_headers,
        recipe["id"],
        first_input["id"],
        quantity_required="1",
        unit_cost="0.03",
    )
    _create_item(
        client,
        api_auth_headers,
        recipe["id"],
        second_input["id"],
        quantity_required="1",
        unit_cost="0.52",
    )

    base = client.get(
        f"/api/v1/production/recipes/{recipe['id']}/cost-estimate",
        headers=api_auth_headers,
    )
    scaled = client.get(
        f"/api/v1/production/recipes/{recipe['id']}/cost-estimate",
        headers=api_auth_headers,
        params={"output_quantity": "100"},
    )

    assert base.status_code == 200
    assert base.json()["requested_output_quantity"] == "1.000"
    assert base.json()["estimated_material_cost"] == "0.5500"
    assert base.json()["estimated_cost_per_unit"] == "0.5500"
    assert [item["quantity_required_scaled"] for item in base.json()["items"]] == [
        "1.000",
        "1.000",
    ]
    assert scaled.status_code == 200
    assert scaled.json()["requested_output_quantity"] == "100"
    assert scaled.json()["estimated_material_cost"] == "55.0000"
    assert scaled.json()["estimated_cost_per_unit"] == "0.5500"
    assert [
        item["quantity_required_scaled"] for item in scaled.json()["items"]
    ] == ["100.000", "100.000"]
    assert [item["total_cost_scaled"] for item in scaled.json()["items"]] == [
        "3.0000",
        "52.0000",
    ]


def test_update_recipe_header_and_list_filters(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    today = date.today()
    finished = _create_product(
        client,
        api_auth_headers,
        name="Producto final",
        product_kind="finished_good",
    )
    other = _create_product(
        client,
        api_auth_headers,
        name="Servicio final",
        product_kind="service",
    )
    first = _create_recipe(
        client,
        api_auth_headers,
        finished["id"],
        name="Formula vigente alfa",
        valid_from=(today - timedelta(days=1)).isoformat(),
        valid_to=(today + timedelta(days=1)).isoformat(),
    )
    second = _create_recipe(
        client,
        api_auth_headers,
        other["id"],
        name="Formula vencida beta",
        valid_to=(today - timedelta(days=1)).isoformat(),
    )
    updated = client.patch(
        f"/api/v1/production/recipes/{first['id']}",
        headers=api_auth_headers,
        json={
            "name": "Formula vigente actualizada",
            "output_quantity": "5",
            "notes": "Nueva base",
        },
    )
    by_search = client.get(
        "/api/v1/production/recipes",
        headers=api_auth_headers,
        params={"search": "actualizada"},
    )
    by_product = client.get(
        "/api/v1/production/recipes",
        headers=api_auth_headers,
        params={"output_product_id": other["id"]},
    )
    by_kind = client.get(
        "/api/v1/production/recipes",
        headers=api_auth_headers,
        params={"product_kind": "finished_good"},
    )
    valid_today = client.get(
        "/api/v1/production/recipes",
        headers=api_auth_headers,
        params={"is_valid_today": "true"},
    )
    invalid_today = client.get(
        "/api/v1/production/recipes",
        headers=api_auth_headers,
        params={"is_valid_today": "false"},
    )
    by_status = client.get(
        "/api/v1/production/recipes",
        headers=api_auth_headers,
        params={"status": "inactive"},
    )

    assert updated.status_code == 200
    assert updated.json()["name"] == "Formula vigente actualizada"
    assert updated.json()["output_quantity"] == "5.000"
    assert [item["id"] for item in by_search.json()] == [first["id"]]
    assert [item["id"] for item in by_product.json()] == [second["id"]]
    assert [item["id"] for item in by_kind.json()] == [first["id"]]
    assert [item["id"] for item in valid_today.json()] == [first["id"]]
    assert [item["id"] for item in invalid_today.json()] == [second["id"]]
    assert {item["id"] for item in by_status.json()} == {
        first["id"],
        second["id"],
    }


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("PATCH", "/api/v1/products/1/production-classification", {
            "product_kind": "supply",
        }),
        ("POST", "/api/v1/production/recipes", {
            "name": "Formula",
            "output_product_id": 1,
            "output_quantity": "1",
        }),
        ("GET", "/api/v1/production/recipes", None),
        ("GET", "/api/v1/production/recipes/1", None),
        ("PATCH", "/api/v1/production/recipes/1", {"name": "Formula"}),
        ("PATCH", "/api/v1/production/recipes/1/activate", None),
        ("PATCH", "/api/v1/production/recipes/1/deactivate", None),
        ("POST", "/api/v1/production/recipes/1/void", {"reason": "Error"}),
        ("POST", "/api/v1/production/recipes/1/items", {
            "input_product_id": 1,
            "quantity_required": "1",
        }),
        ("PATCH", "/api/v1/production/recipe-items/1", {"unit_cost": "1"}),
        ("PATCH", "/api/v1/production/recipe-items/1/deactivate", None),
        ("PATCH", "/api/v1/production/recipe-items/1/activate", None),
        ("GET", "/api/v1/production/recipes/1/cost-estimate", None),
    ],
)
def test_recipe_endpoints_require_authentication(
    api_client,
    method,
    path,
    json_body,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_recipe_migration_has_expected_revision_and_tables() -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0024_create_production_recipes.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0024_recipes",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "0024_recipes"
    assert migration.down_revision == "0023_payroll"
    assert len(migration.revision) <= 32


def _recipe_with_products(
    client,
    headers,
    input_overrides=None,
    recipe_overrides=None,
):
    output_product = _create_product(
        client,
        headers,
        name="Producto terminado",
        product_kind="finished_good",
    )
    input_product = _create_product(
        client,
        headers,
        **{
            "name": "Insumo",
            "product_kind": "supply",
            **(input_overrides or {}),
        },
    )
    recipe = _create_recipe(
        client,
        headers,
        output_product["id"],
        **(recipe_overrides or {}),
    )
    return recipe, input_product


def _create_product(client, headers, **overrides):
    payload = {
        "name": "Producto Agua Activa",
        "category": "other",
        "unit": "unit",
        "default_price": "1.00",
        "cost_estimate": "0.00",
        "product_kind": "finished_good",
        "is_returnable_container": False,
        **overrides,
    }
    response = client.post("/api/v1/products", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()


def _recipe_response(client, headers, output_product_id, **overrides):
    payload = {
        "name": "Formula base",
        "output_product_id": output_product_id,
        "output_quantity": "1",
        **overrides,
    }
    return client.post(
        "/api/v1/production/recipes",
        headers=headers,
        json=payload,
    )


def _create_recipe(client, headers, output_product_id, **overrides):
    response = _recipe_response(
        client,
        headers,
        output_product_id,
        **overrides,
    )
    assert response.status_code == 201
    return response.json()


def _item_response(
    client,
    headers,
    recipe_id,
    input_product_id,
    **overrides,
):
    payload = {
        "input_product_id": input_product_id,
        "quantity_required": "1",
        "unit_cost": "0.05",
        "waste_percentage": "0",
        **overrides,
    }
    return client.post(
        f"/api/v1/production/recipes/{recipe_id}/items",
        headers=headers,
        json=payload,
    )


def _create_item(client, headers, recipe_id, input_product_id, **overrides):
    response = _item_response(
        client,
        headers,
        recipe_id,
        input_product_id,
        **overrides,
    )
    assert response.status_code == 201
    return response.json()


def _get_recipe(client, headers, recipe_id):
    response = client.get(
        f"/api/v1/production/recipes/{recipe_id}",
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()


def _operational_counts(session) -> tuple[int, ...]:
    models = (
        InventoryMovement,
        InventoryStock,
        ProductionBatch,
        CashSession,
        Purchase,
        Sale,
    )
    return tuple(
        session.scalar(select(func.count(model.id))) or 0
        for model in models
    )

import importlib.util
from pathlib import Path

import pytest

from app.models.product import Product


def test_create_product(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={
            "sku": "BIDON-20L",
            "name": "Bidon 20L",
            "description": "Bidon de agua de 20 litros",
            "category": "water",
            "unit": "container",
            "presentation": "20L",
            "default_price": "1.00",
            "cost_estimate": "0.40",
            "is_returnable_container": True,
            "notes": "Producto principal",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["sku"] == "BIDON-20L"
    assert body["name"] == "Bidon 20L"
    assert body["category"] == "water"
    assert body["unit"] == "container"
    assert body["default_price"] == "1.00"
    assert body["cost_estimate"] == "0.40"
    assert body["is_returnable_container"] is True
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_create_product_requires_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={"default_price": "1.00"},
    )

    assert response.status_code == 422


def test_create_product_rejects_blank_name(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={"name": "   ", "default_price": "1.00"},
    )

    assert response.status_code == 422


def test_create_product_requires_default_price(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={"name": "Producto"},
    )

    assert response.status_code == 422


def test_create_product_rejects_negative_default_price(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={"name": "Producto", "default_price": "-0.01"},
    )

    assert response.status_code == 422


def test_create_product_rejects_negative_cost_estimate(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={
            "name": "Producto",
            "default_price": "1.00",
            "cost_estimate": "-0.01",
        },
    )

    assert response.status_code == 422


def test_create_product_rejects_duplicate_sku(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    _create_product(client, api_auth_headers, name="Primer producto", sku="AGUA-1")

    response = client.post(
        "/api/v1/products",
        headers=api_auth_headers,
        json={
            "name": "Segundo producto",
            "sku": " AGUA-1 ",
            "default_price": "2.00",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "El SKU ya esta registrado."


def test_create_products_allows_empty_or_null_sku(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    empty_sku = _create_product(
        client,
        api_auth_headers,
        name="Producto sin codigo 1",
        sku="   ",
    )
    null_sku = _create_product(
        client,
        api_auth_headers,
        name="Producto sin codigo 2",
        sku=None,
    )

    assert empty_sku["sku"] is None
    assert null_sku["sku"] is None


def test_list_products(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_product(client, api_auth_headers, name="Agua 20L")
    _create_product(client, api_auth_headers, name="Botella 500ml")

    response = client.get("/api/v1/products", headers=api_auth_headers)

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == [
        "Agua 20L",
        "Botella 500ml",
    ]


@pytest.mark.parametrize("search", ["bidon", "BIDON-20L", "water", "20L"])
def test_list_products_filters_by_search(
    api_client,
    api_auth_headers,
    search: str,
) -> None:
    client, _ = api_client
    _create_product(
        client,
        api_auth_headers,
        sku="BIDON-20L",
        name="Bidon principal",
        category="water",
        presentation="20L",
    )
    _create_product(
        client,
        api_auth_headers,
        sku="DISP-01",
        name="Dispensador",
        category="dispenser",
        presentation="Mesa",
    )

    response = client.get(
        "/api/v1/products",
        headers=api_auth_headers,
        params={"search": search},
    )

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == [
        "Bidon principal"
    ]


def test_list_products_filters_by_active_status(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    active = _create_product(client, api_auth_headers, name="Producto activo")
    inactive = _create_product(client, api_auth_headers, name="Producto inactivo")
    client.patch(
        f"/api/v1/products/{inactive['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.get(
        "/api/v1/products",
        headers=api_auth_headers,
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [active["id"]]


def test_list_products_filters_by_category(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_product(
        client,
        api_auth_headers,
        name="Agua",
        category="water",
    )
    _create_product(
        client,
        api_auth_headers,
        name="Dispensador",
        category="dispenser",
    )

    response = client.get(
        "/api/v1/products",
        headers=api_auth_headers,
        params={"category": "water"},
    )

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["Agua"]


def test_list_products_filters_by_unit(api_client, api_auth_headers) -> None:
    client, _ = api_client
    _create_product(
        client,
        api_auth_headers,
        name="Bidon",
        unit="container",
    )
    _create_product(
        client,
        api_auth_headers,
        name="Pack botellas",
        unit="pack",
    )

    response = client.get(
        "/api/v1/products",
        headers=api_auth_headers,
        params={"unit": "container"},
    )

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["Bidon"]


def test_get_product_detail(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, name="Producto detalle")

    response = client.get(
        f"/api/v1/products/{product['id']}",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == product


def test_get_product_detail_returns_404(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get("/api/v1/products/999", headers=api_auth_headers)

    assert response.status_code == 404


def test_update_product(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(
        client,
        api_auth_headers,
        name="Producto original",
        default_price="1.00",
        cost_estimate="0.25",
    )

    response = client.patch(
        f"/api/v1/products/{product['id']}",
        headers=api_auth_headers,
        json={
            "name": "Producto actualizado",
            "presentation": "Pack x 12",
            "default_price": "12.50",
            "cost_estimate": "7.25",
            "notes": "Datos revisados",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Producto actualizado"
    assert body["presentation"] == "Pack x 12"
    assert body["default_price"] == "12.50"
    assert body["cost_estimate"] == "7.25"
    assert body["notes"] == "Datos revisados"


def test_deactivate_product(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, name="Producto")

    response = client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_reactivate_product(api_client, api_auth_headers) -> None:
    client, _ = api_client
    product = _create_product(client, api_auth_headers, name="Producto")
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    response = client.patch(
        f"/api/v1/products/{product['id']}/activate",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_deactivate_product_does_not_delete_record(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    product = _create_product(client, api_auth_headers, name="Producto persistente")

    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )

    with testing_session_local() as session:
        stored_product = session.get(Product, product["id"])
        assert stored_product is not None
        assert stored_product.is_active is False


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/products", {"name": "Producto", "default_price": "1.00"}),
        ("GET", "/api/v1/products", None),
        ("GET", "/api/v1/products/1", None),
        ("PATCH", "/api/v1/products/1", {"name": "Producto"}),
        ("PATCH", "/api/v1/products/1/deactivate", None),
        ("PATCH", "/api/v1/products/1/activate", None),
    ],
)
def test_product_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body: dict[str, str] | None,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_product_migration_creates_products_table(monkeypatch) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0004_create_products.py"
    )
    spec = importlib.util.spec_from_file_location("migration_0004_products", migration_path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: list[tuple[str, tuple[object, ...]]] = []

    def record_create_table(table_name: str, *elements: object) -> None:
        created_tables.append((table_name, elements))

    monkeypatch.setattr(migration.op, "create_table", record_create_table)

    migration.upgrade()

    assert migration.revision == "0004_products"
    assert migration.down_revision == "0003_customers"
    assert len(migration.revision) <= 32
    assert [table_name for table_name, _ in created_tables] == ["products"]
    column_names = {
        element.name
        for element in created_tables[0][1]
        if element.__class__.__name__ == "Column"
    }
    assert column_names == {
        "id",
        "sku",
        "name",
        "description",
        "category",
        "unit",
        "presentation",
        "default_price",
        "cost_estimate",
        "is_returnable_container",
        "is_active",
        "notes",
        "created_at",
        "updated_at",
    }


def _create_product(client, headers: dict[str, str], **overrides):
    payload = {
        "name": "Producto Agua Activa",
        "category": "other",
        "unit": "unit",
        "default_price": "1.00",
        "cost_estimate": "0.00",
        "is_returnable_container": False,
        **overrides,
    }
    response = client.post("/api/v1/products", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()

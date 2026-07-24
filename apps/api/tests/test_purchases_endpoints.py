import re

import pytest
from sqlalchemy import func, select

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.expense import Expense
from app.models.inventory_movement import InventoryMovement
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.sale import Sale


def test_create_purchase_with_multiple_items_and_backend_totals(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)
    product = _create_product(
        client,
        api_auth_headers,
        sku="BIDON-20L",
        name="Bidon 20L",
        presentation="20 L",
    )

    response = client.post(
        "/api/v1/purchases",
        headers=api_auth_headers,
        json={
            "supplier_id": supplier["id"],
            "purchase_date": "2026-07-18",
            "document_number": " FAC-001 ",
            "document_type": "factura",
            "payment_status": "unpaid",
            "notes": " Compra controlada ",
            "subtotal_amount": "9999.99",
            "total_amount": "9999.99",
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": "3",
                    "unit_cost": "2.50",
                    "discount_amount": "0.50",
                    "tax_amount": "0.84",
                    "notes": "Bodega",
                },
                {
                    "description": "Servicio de transporte",
                    "quantity": "2",
                    "unit_cost": "5.00",
                    "discount_amount": "1.00",
                    "tax_amount": "0",
                },
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert re.fullmatch(r"PUR-20260718-\d{4,}", body["purchase_number"])
    assert body["supplier"]["id"] == supplier["id"]
    assert body["document_number"] == "FAC-001"
    assert body["status"] == "active"
    assert body["payment_status"] == "unpaid"
    assert body["subtotal_amount"] == "16.00"
    assert body["discount_amount"] == "1.50"
    assert body["tax_amount"] == "0.84"
    assert body["total_amount"] == "16.84"
    assert len(body["items"]) == 2
    first = body["items"][0]
    assert first["subtotal_amount"] == "7.00"
    assert first["total_amount"] == "7.84"
    assert first["product_sku_snapshot"] == "BIDON-20L"
    assert first["product_name_snapshot"] == "Bidon 20L"
    assert first["product_presentation_snapshot"] == "20 L"
    assert body["items"][1]["description"] == "Servicio de transporte"


@pytest.mark.parametrize(
    "overrides",
    [
        {"items": []},
        {"items": None},
        {"purchase_date": None},
        {"purchase_date": ""},
    ],
)
def test_purchase_requires_date_and_items(
    api_client,
    api_auth_headers,
    overrides,
) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)

    response = _purchase_response(
        client,
        api_auth_headers,
        supplier["id"],
        **overrides,
    )

    assert response.status_code == 422


def test_purchase_rejects_missing_or_inactive_supplier(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    missing_response = _purchase_response(
        client,
        api_auth_headers,
        999,
    )
    supplier = _create_supplier(client, api_auth_headers)
    client.patch(
        f"/api/v1/suppliers/{supplier['id']}/deactivate",
        headers=api_auth_headers,
    )
    inactive_response = _purchase_response(
        client,
        api_auth_headers,
        supplier["id"],
    )

    assert missing_response.status_code == 404
    assert inactive_response.status_code == 400
    assert inactive_response.json()["detail"] == "El proveedor esta inactivo."


@pytest.mark.parametrize(
    ("item_overrides", "expected_status"),
    [
        ({"description": None, "product_id": None}, 422),
        ({"quantity": "0"}, 422),
        ({"quantity": "-1"}, 422),
        ({"unit_cost": "-0.01"}, 422),
        ({"discount_amount": "-0.01"}, 422),
        ({"tax_amount": "-0.01"}, 422),
        ({"unit_cost": "1.00", "discount_amount": "1.01"}, 422),
    ],
)
def test_purchase_rejects_invalid_item_amounts(
    api_client,
    api_auth_headers,
    item_overrides,
    expected_status,
) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)

    response = _purchase_response(
        client,
        api_auth_headers,
        supplier["id"],
        items=[_item_payload(**item_overrides)],
    )

    assert response.status_code == expected_status


def test_purchase_rejects_missing_or_inactive_product(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)
    missing_response = _purchase_response(
        client,
        api_auth_headers,
        supplier["id"],
        items=[_item_payload(product_id=999, description=None)],
    )
    product = _create_product(client, api_auth_headers, name="Producto inactivo")
    client.patch(
        f"/api/v1/products/{product['id']}/deactivate",
        headers=api_auth_headers,
    )
    inactive_response = _purchase_response(
        client,
        api_auth_headers,
        supplier["id"],
        items=[_item_payload(product_id=product["id"], description=None)],
    )

    assert missing_response.status_code == 404
    assert inactive_response.status_code == 400
    assert "esta inactivo" in inactive_response.json()["detail"]


def test_product_snapshots_do_not_change_after_product_edit(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)
    product = _create_product(
        client,
        api_auth_headers,
        sku="SNAP-1",
        name="Producto original",
        presentation="Caja x 6",
    )
    purchase = _create_purchase(
        client,
        api_auth_headers,
        supplier["id"],
        items=[_item_payload(product_id=product["id"], description=None)],
    )

    update_response = client.patch(
        f"/api/v1/products/{product['id']}",
        headers=api_auth_headers,
        json={"name": "Producto cambiado", "presentation": "Caja x 12"},
    )
    detail = client.get(
        f"/api/v1/purchases/{purchase['id']}",
        headers=api_auth_headers,
    ).json()

    assert update_response.status_code == 200
    assert detail["items"][0]["product_name_snapshot"] == "Producto original"
    assert detail["items"][0]["product_presentation_snapshot"] == "Caja x 6"


def test_purchase_number_is_unique(api_client, api_auth_headers) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)

    first = _create_purchase(client, api_auth_headers, supplier["id"])
    second = _create_purchase(client, api_auth_headers, supplier["id"])

    assert first["purchase_number"] != second["purchase_number"]


def test_list_and_filter_purchases(api_client, api_auth_headers) -> None:
    client, _ = api_client
    first_supplier = _create_supplier(
        client,
        api_auth_headers,
        name="Proveedor Alfa",
    )
    second_supplier = _create_supplier(
        client,
        api_auth_headers,
        name="Proveedor Beta",
    )
    product = _create_product(client, api_auth_headers, name="Filtro producto")
    first = _create_purchase(
        client,
        api_auth_headers,
        first_supplier["id"],
        purchase_date="2026-07-01",
        document_number="DOC-ALFA",
        payment_status="paid",
        items=[_item_payload(product_id=product["id"], description=None)],
    )
    second = _create_purchase(
        client,
        api_auth_headers,
        second_supplier["id"],
        purchase_date="2026-07-20",
        payment_status="unpaid",
    )
    _void_purchase(client, api_auth_headers, second["id"])

    all_response = client.get("/api/v1/purchases", headers=api_auth_headers)
    date_response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"date_from": "2026-07-01", "date_to": "2026-07-10"},
    )
    status_response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"status": "voided"},
    )
    payment_response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"payment_status": "paid"},
    )
    supplier_response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"supplier_id": first_supplier["id"]},
    )
    product_response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"product_id": product["id"]},
    )
    search_response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"search": "DOC-ALFA"},
    )

    assert [item["id"] for item in all_response.json()] == [
        second["id"],
        first["id"],
    ]
    for response in (
        date_response,
        payment_response,
        supplier_response,
        product_response,
        search_response,
    ):
        assert [item["id"] for item in response.json()] == [first["id"]]
    assert [item["id"] for item in status_response.json()] == [second["id"]]


def test_purchase_date_filter_rejects_reversed_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/purchases",
        headers=api_auth_headers,
        params={"date_from": "2026-07-20", "date_to": "2026-07-01"},
    )

    assert response.status_code == 400


def test_get_purchase_detail_and_404(api_client, api_auth_headers) -> None:
    client, _ = api_client
    supplier = _create_supplier(client, api_auth_headers)
    purchase = _create_purchase(client, api_auth_headers, supplier["id"])

    detail_response = client.get(
        f"/api/v1/purchases/{purchase['id']}",
        headers=api_auth_headers,
    )
    missing_response = client.get(
        "/api/v1/purchases/999",
        headers=api_auth_headers,
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == purchase
    assert missing_response.status_code == 404


def test_void_purchase_requires_reason_preserves_items_and_cannot_repeat(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    supplier = _create_supplier(client, api_auth_headers)
    purchase = _create_purchase(client, api_auth_headers, supplier["id"])

    missing_reason = client.post(
        f"/api/v1/purchases/{purchase['id']}/void",
        headers=api_auth_headers,
        json={"reason": "   "},
    )
    voided_response = client.post(
        f"/api/v1/purchases/{purchase['id']}/void",
        headers=api_auth_headers,
        json={"reason": " Compra registrada por error "},
    )
    repeated_response = client.post(
        f"/api/v1/purchases/{purchase['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Otro motivo"},
    )

    assert missing_reason.status_code == 422
    assert voided_response.status_code == 200
    assert voided_response.json()["status"] == "voided"
    assert voided_response.json()["void_reason"] == "Compra registrada por error"
    assert voided_response.json()["voided_at"] is not None
    assert len(voided_response.json()["items"]) == 1
    assert repeated_response.status_code == 409
    with testing_session_local() as session:
        assert session.get(Purchase, purchase["id"]) is not None
        assert (
            session.scalar(
                select(func.count())
                .select_from(PurchaseItem)
                .where(PurchaseItem.purchase_id == purchase["id"]),
            )
            == 1
        )


def test_create_and_void_purchase_have_no_operational_side_effects(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    supplier = _create_supplier(client, api_auth_headers)
    with testing_session_local() as session:
        before = _operational_counts(session)

    purchase = _create_purchase(client, api_auth_headers, supplier["id"])
    _void_purchase(client, api_auth_headers, purchase["id"])

    with testing_session_local() as session:
        after = _operational_counts(session)
    assert after == before


def test_new_database_has_no_fake_purchase_data(api_client) -> None:
    _, testing_session_local = api_client

    with testing_session_local() as session:
        assert session.scalar(select(func.count()).select_from(Purchase)) == 0
        assert session.scalar(select(func.count()).select_from(PurchaseItem)) == 0


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        (
            "POST",
            "/api/v1/purchases",
            {
                "supplier_id": 1,
                "purchase_date": "2026-07-18",
                "items": [
                    {
                        "description": "Item",
                        "quantity": "1",
                        "unit_cost": "1",
                    }
                ],
            },
        ),
        ("GET", "/api/v1/purchases", None),
        ("GET", "/api/v1/purchases/1", None),
        (
            "POST",
            "/api/v1/purchases/1/void",
            {"reason": "Error"},
        ),
    ],
)
def test_purchase_endpoints_require_authentication(
    api_client,
    method: str,
    path: str,
    json_body,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def _create_supplier(client, headers: dict[str, str], **overrides):
    response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": "Proveedor compras", **overrides},
    )
    assert response.status_code == 201
    return response.json()


def _create_product(client, headers: dict[str, str], **overrides):
    response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": "Producto compras",
            "category": "other",
            "unit": "unit",
            "default_price": "1.00",
            **overrides,
        },
    )
    assert response.status_code == 201
    return response.json()


def _item_payload(**overrides):
    return {
        "product_id": None,
        "description": "Item manual",
        "quantity": "1",
        "unit_cost": "2.50",
        "discount_amount": "0",
        "tax_amount": "0",
        **overrides,
    }


def _purchase_response(client, headers, supplier_id: int, **overrides):
    payload = {
        "supplier_id": supplier_id,
        "purchase_date": "2026-07-18",
        "document_number": "DOC-001",
        "document_type": "factura",
        "payment_status": "unpaid",
        "notes": "Compra de prueba",
        "items": [_item_payload()],
        **overrides,
    }
    return client.post("/api/v1/purchases", headers=headers, json=payload)


def _create_purchase(client, headers, supplier_id: int, **overrides):
    response = _purchase_response(client, headers, supplier_id, **overrides)
    assert response.status_code == 201, response.text
    return response.json()


def _void_purchase(client, headers, purchase_id: int):
    response = client.post(
        f"/api/v1/purchases/{purchase_id}/void",
        headers=headers,
        json={"reason": "Prueba de anulacion"},
    )
    assert response.status_code == 200
    return response.json()


def _operational_counts(session) -> dict[str, int]:
    return {
        model.__tablename__: session.scalar(
            select(func.count()).select_from(model),
        )
        for model in (
            InventoryMovement,
            CashSession,
            Expense,
            Sale,
            CreditPayment,
        )
    }

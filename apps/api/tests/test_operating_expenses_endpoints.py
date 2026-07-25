import importlib.util
import re
from pathlib import Path

import pytest
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, func, select

from app.models.cash_session import CashSession
from app.models.expense import Expense
from app.models.inventory_movement import InventoryMovement
from app.models.operating_expense import OperatingExpense
from app.models.operating_expense_category import OperatingExpenseCategory
from app.models.purchase import Purchase
from app.models.recurring_operating_expense import RecurringOperatingExpense
from app.models.sale import Sale


def test_create_list_update_and_toggle_category(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    created = _create_category(
        client,
        api_auth_headers,
        name=" Mantenimiento ",
        description=" Bombas y equipos ",
    )
    duplicate = client.post(
        "/api/v1/operating-expenses/categories",
        headers=api_auth_headers,
        json={"name": "mantenimiento"},
    )
    detail = client.get(
        f"/api/v1/operating-expenses/categories/{created['id']}",
        headers=api_auth_headers,
    )
    updated = client.patch(
        f"/api/v1/operating-expenses/categories/{created['id']}",
        headers=api_auth_headers,
        json={"name": "Mantenimiento general", "description": None},
    )
    deactivated = client.patch(
        f"/api/v1/operating-expenses/categories/{created['id']}/deactivate",
        headers=api_auth_headers,
    )
    inactive_list = client.get(
        "/api/v1/operating-expenses/categories",
        headers=api_auth_headers,
        params={"is_active": "false", "search": "general"},
    )
    activated = client.patch(
        f"/api/v1/operating-expenses/categories/{created['id']}/activate",
        headers=api_auth_headers,
    )

    assert created["name"] == "Mantenimiento"
    assert created["description"] == "Bombas y equipos"
    assert duplicate.status_code == 409
    assert detail.status_code == 200
    assert updated.json()["name"] == "Mantenimiento general"
    assert updated.json()["description"] is None
    assert deactivated.json()["is_active"] is False
    assert [item["id"] for item in inactive_list.json()] == [created["id"]]
    assert activated.json()["is_active"] is True


@pytest.mark.parametrize("payload", [{}, {"name": "   "}, {"name": None}])
def test_category_requires_name(
    api_client,
    api_auth_headers,
    payload,
) -> None:
    client, _ = api_client

    response = client.post(
        "/api/v1/operating-expenses/categories",
        headers=api_auth_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_create_expense_with_optional_supplier(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    category = _create_category(client, api_auth_headers)
    supplier = _create_supplier(client, api_auth_headers)

    expense = _create_expense(
        client,
        api_auth_headers,
        category["id"],
        supplier_id=supplier["id"],
        expense_date="2026-07-18",
        description=" Reparacion de bomba ",
        amount="75.00",
        payment_status="paid",
        payment_method="cash",
        document_number=" REC-001 ",
        paid_date="2026-07-18",
        notes=" Fuera de caja ",
    )

    assert re.fullmatch(r"OPEX-20260718-\d{4,}", expense["expense_number"])
    assert expense["description"] == "Reparacion de bomba"
    assert expense["amount"] == "75.00"
    assert expense["category"]["id"] == category["id"]
    assert expense["supplier"]["id"] == supplier["id"]
    assert expense["document_number"] == "REC-001"
    assert expense["status"] == "active"
    assert expense["recurring_template_id"] is None


def test_expense_rejects_missing_or_inactive_category(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    missing_field = client.post(
        "/api/v1/operating-expenses",
        headers=api_auth_headers,
        json={
            "expense_date": "2026-07-18",
            "description": "Sin categoria",
            "amount": "5.00",
        },
    )
    missing = _expense_response(client, api_auth_headers, 999)
    category = _create_category(client, api_auth_headers)
    client.patch(
        f"/api/v1/operating-expenses/categories/{category['id']}/deactivate",
        headers=api_auth_headers,
    )
    inactive = _expense_response(client, api_auth_headers, category["id"])

    assert missing_field.status_code == 422
    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert inactive.json()["detail"] == "La categoria de gasto esta inactiva."


def test_expense_rejects_missing_or_inactive_supplier(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    category = _create_category(client, api_auth_headers)
    missing = _expense_response(
        client,
        api_auth_headers,
        category["id"],
        supplier_id=999,
    )
    supplier = _create_supplier(client, api_auth_headers)
    client.patch(
        f"/api/v1/suppliers/{supplier['id']}/deactivate",
        headers=api_auth_headers,
    )
    inactive = _expense_response(
        client,
        api_auth_headers,
        category["id"],
        supplier_id=supplier["id"],
    )

    assert missing.status_code == 404
    assert inactive.status_code == 400
    assert inactive.json()["detail"] == "El proveedor esta inactivo."


@pytest.mark.parametrize("amount", ["0", "-0.01", "1.001"])
def test_expense_rejects_invalid_amount(
    api_client,
    api_auth_headers,
    amount,
) -> None:
    client, _ = api_client
    category = _create_category(client, api_auth_headers)

    response = _expense_response(
        client,
        api_auth_headers,
        category["id"],
        amount=amount,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("payment_status", "pending"),
        ("payment_method", "bank"),
    ],
)
def test_expense_rejects_invalid_states(
    api_client,
    api_auth_headers,
    field,
    value,
) -> None:
    client, _ = api_client
    category = _create_category(client, api_auth_headers)

    response = _expense_response(
        client,
        api_auth_headers,
        category["id"],
        **{field: value},
    )

    assert response.status_code == 422


def test_list_filter_detail_and_update_active_expense(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    first_category = _create_category(
        client,
        api_auth_headers,
        name="Servicios",
    )
    second_category = _create_category(
        client,
        api_auth_headers,
        name="Combustible",
    )
    supplier = _create_supplier(client, api_auth_headers)
    first = _create_expense(
        client,
        api_auth_headers,
        first_category["id"],
        supplier_id=supplier["id"],
        expense_date="2026-07-01",
        description="Internet oficina",
        payment_status="paid",
        payment_method="transfer",
    )
    second = _create_expense(
        client,
        api_auth_headers,
        second_category["id"],
        expense_date="2026-07-20",
        description="Diesel",
        payment_status="unpaid",
    )

    filter_sets = (
        ({"date_from": "2026-07-01", "date_to": "2026-07-10"}, first["id"]),
        ({"category_id": first_category["id"]}, first["id"]),
        ({"supplier_id": supplier["id"]}, first["id"]),
        ({"payment_status": "unpaid"}, second["id"]),
        ({"payment_method": "transfer"}, first["id"]),
        ({"search": "internet"}, first["id"]),
    )
    for params, expected_id in filter_sets:
        response = client.get(
            "/api/v1/operating-expenses",
            headers=api_auth_headers,
            params=params,
        )
        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [expected_id]

    detail = client.get(
        f"/api/v1/operating-expenses/{first['id']}",
        headers=api_auth_headers,
    )
    updated = client.patch(
        f"/api/v1/operating-expenses/{first['id']}",
        headers=api_auth_headers,
        json={
            "description": "Internet y telefonia",
            "amount": "42.50",
            "supplier_id": None,
            "payment_status": "partial",
        },
    )

    assert detail.json() == first
    assert updated.status_code == 200
    assert updated.json()["description"] == "Internet y telefonia"
    assert updated.json()["amount"] == "42.50"
    assert updated.json()["supplier"] is None
    assert updated.json()["payment_status"] == "partial"


def test_void_expense_requires_reason_and_blocks_repeat_and_edit(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    category = _create_category(client, api_auth_headers)
    expense = _create_expense(client, api_auth_headers, category["id"])

    missing_reason = client.post(
        f"/api/v1/operating-expenses/{expense['id']}/void",
        headers=api_auth_headers,
        json={"reason": "   "},
    )
    voided = client.post(
        f"/api/v1/operating-expenses/{expense['id']}/void",
        headers=api_auth_headers,
        json={"reason": " Registrado por error "},
    )
    repeated = client.post(
        f"/api/v1/operating-expenses/{expense['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Otro motivo"},
    )
    edit = client.patch(
        f"/api/v1/operating-expenses/{expense['id']}",
        headers=api_auth_headers,
        json={"amount": "10.00"},
    )

    assert missing_reason.status_code == 422
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    assert voided.json()["void_reason"] == "Registrado por error"
    assert voided.json()["voided_at"] is not None
    assert repeated.status_code == 409
    assert edit.status_code == 409
    with testing_session_local() as session:
        assert session.get(OperatingExpense, expense["id"]) is not None


def test_create_list_update_toggle_and_generate_from_recurring_template(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    category = _create_category(client, api_auth_headers, name="Internet")
    supplier = _create_supplier(client, api_auth_headers)

    template = _create_template(
        client,
        api_auth_headers,
        category["id"],
        supplier_id=supplier["id"],
    )
    detail = client.get(
        f"/api/v1/operating-expenses/recurring/{template['id']}",
        headers=api_auth_headers,
    )
    listed = client.get(
        "/api/v1/operating-expenses/recurring",
        headers=api_auth_headers,
        params={
            "frequency": "monthly",
            "category_id": category["id"],
            "supplier_id": supplier["id"],
            "search": "internet",
        },
    )
    updated = client.patch(
        f"/api/v1/operating-expenses/recurring/{template['id']}",
        headers=api_auth_headers,
        json={"amount": "37.00", "notes": "Tarifa actualizada"},
    )
    generated = client.post(
        (
            f"/api/v1/operating-expenses/recurring/{template['id']}"
            "/create-expense"
        ),
        headers=api_auth_headers,
        json={
            "expense_date": "2026-08-01",
            "due_date": "2026-08-01",
            "payment_status": "unpaid",
            "notes": "Generado manualmente",
        },
    )

    assert detail.json() == template
    assert [item["id"] for item in listed.json()] == [template["id"]]
    assert updated.json()["amount"] == "37.00"
    assert generated.status_code == 201
    body = generated.json()
    assert body["recurring_template_id"] == template["id"]
    assert body["category_id"] == category["id"]
    assert body["supplier_id"] == supplier["id"]
    assert body["description"] == template["description"]
    assert body["amount"] == "37.00"
    assert body["payment_method"] == template["payment_method"]
    assert body["notes"] == "Generado manualmente"

    deactivated = client.patch(
        f"/api/v1/operating-expenses/recurring/{template['id']}/deactivate",
        headers=api_auth_headers,
    )
    blocked = client.post(
        (
            f"/api/v1/operating-expenses/recurring/{template['id']}"
            "/create-expense"
        ),
        headers=api_auth_headers,
        json={"expense_date": "2026-09-01"},
    )
    activated = client.patch(
        f"/api/v1/operating-expenses/recurring/{template['id']}/activate",
        headers=api_auth_headers,
    )
    assert deactivated.json()["is_active"] is False
    assert blocked.status_code == 400
    assert activated.json()["is_active"] is True


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": "0"},
        {"amount": "-1"},
        {"frequency": "biweekly"},
        {"description": "   "},
        {"end_date": "2026-06-30"},
    ],
)
def test_recurring_template_rejects_invalid_values(
    api_client,
    api_auth_headers,
    overrides,
) -> None:
    client, _ = api_client
    category = _create_category(client, api_auth_headers)

    response = _template_response(
        client,
        api_auth_headers,
        category["id"],
        **overrides,
    )

    assert response.status_code == 422


def test_summary_excludes_voided_and_groups_active_expenses(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client
    services = _create_category(
        client,
        api_auth_headers,
        name="Servicios",
    )
    maintenance = _create_category(
        client,
        api_auth_headers,
        name="Mantenimiento",
    )
    supplier = _create_supplier(client, api_auth_headers)
    paid = _create_expense(
        client,
        api_auth_headers,
        services["id"],
        supplier_id=supplier["id"],
        amount="75.00",
        payment_status="paid",
    )
    _create_expense(
        client,
        api_auth_headers,
        services["id"],
        amount="35.00",
        payment_status="unpaid",
    )
    _create_expense(
        client,
        api_auth_headers,
        maintenance["id"],
        supplier_id=supplier["id"],
        amount="20.00",
        payment_status="partial",
    )
    client.post(
        f"/api/v1/operating-expenses/{paid['id']}/void",
        headers=api_auth_headers,
        json={"reason": "Duplicado"},
    )

    response = client.get(
        "/api/v1/operating-expenses/summary",
        headers=api_auth_headers,
        params={"date_from": "2026-07-01", "date_to": "2026-07-31"},
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_expenses_amount"] == "55.00"
    assert summary["paid_amount"] == "0.00"
    assert summary["unpaid_amount"] == "35.00"
    assert summary["partial_amount"] == "20.00"
    assert summary["expenses_count"] == 2
    assert summary["voided_count"] == 1
    assert {
        row["category_name"]: row["total_amount"]
        for row in summary["by_category"]
    } == {"Mantenimiento": "20.00", "Servicios": "35.00"}
    assert {
        row["supplier_name"]: row["total_amount"]
        for row in summary["by_supplier"]
    } == {"Proveedor operativo": "20.00", "Sin proveedor": "35.00"}
    assert {
        row["payment_status"]: row["total_amount"]
        for row in summary["by_payment_status"]
    } == {"partial": "20.00", "unpaid": "35.00"}


def test_operating_expenses_have_no_side_effects(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    category = _create_category(client, api_auth_headers)
    with testing_session_local() as session:
        before = _operational_counts(session)

    expense = _create_expense(client, api_auth_headers, category["id"])
    template = _create_template(
        client,
        api_auth_headers,
        category["id"],
    )
    generated = client.post(
        (
            f"/api/v1/operating-expenses/recurring/{template['id']}"
            "/create-expense"
        ),
        headers=api_auth_headers,
        json={"expense_date": "2026-08-01"},
    )

    assert generated.status_code == 201
    with testing_session_local() as session:
        after = _operational_counts(session)
        assert (
            session.scalar(select(func.count()).select_from(OperatingExpense))
            == 2
        )
        assert session.get(OperatingExpense, expense["id"]) is not None
    assert after == before


def test_new_database_has_no_fake_operating_expense_data(api_client) -> None:
    _, testing_session_local = api_client

    with testing_session_local() as session:
        assert (
            session.scalar(
                select(func.count()).select_from(OperatingExpenseCategory),
            )
            == 0
        )
        assert (
            session.scalar(select(func.count()).select_from(OperatingExpense))
            == 0
        )
        assert (
            session.scalar(
                select(func.count()).select_from(RecurringOperatingExpense),
            )
            == 0
        )


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/api/v1/operating-expenses/categories", {"name": "Otros"}),
        ("GET", "/api/v1/operating-expenses/categories", None),
        ("GET", "/api/v1/operating-expenses/categories/1", None),
        ("PATCH", "/api/v1/operating-expenses/categories/1", {"name": "Otro"}),
        ("PATCH", "/api/v1/operating-expenses/categories/1/deactivate", None),
        ("PATCH", "/api/v1/operating-expenses/categories/1/activate", None),
        ("POST", "/api/v1/operating-expenses", {}),
        ("GET", "/api/v1/operating-expenses", None),
        ("GET", "/api/v1/operating-expenses/1", None),
        ("PATCH", "/api/v1/operating-expenses/1", {"amount": "1.00"}),
        ("POST", "/api/v1/operating-expenses/1/void", {"reason": "Error"}),
        ("POST", "/api/v1/operating-expenses/recurring", {}),
        ("GET", "/api/v1/operating-expenses/recurring", None),
        ("GET", "/api/v1/operating-expenses/recurring/1", None),
        ("PATCH", "/api/v1/operating-expenses/recurring/1", {"amount": "1"}),
        (
            "PATCH",
            "/api/v1/operating-expenses/recurring/1/deactivate",
            None,
        ),
        ("PATCH", "/api/v1/operating-expenses/recurring/1/activate", None),
        (
            "POST",
            "/api/v1/operating-expenses/recurring/1/create-expense",
            {"expense_date": "2026-08-01"},
        ),
        ("GET", "/api/v1/operating-expenses/summary", None),
    ],
)
def test_operating_expense_endpoints_require_authentication(
    api_client,
    method,
    path,
    json_body,
) -> None:
    client, _ = api_client

    response = client.request(method, path, json=json_body)

    assert response.status_code == 401


def test_operating_expense_migration_creates_tables_checks_fks_and_indexes(
    monkeypatch,
) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "0021_create_operating_expenses.py"
    )
    spec = importlib.util.spec_from_file_location(
        "migration_0021_operating_expenses",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    created_tables: dict[str, tuple[object, ...]] = {}
    created_indexes: list[tuple[object, ...]] = []

    monkeypatch.setattr(
        migration.op,
        "create_table",
        lambda table_name, *elements: created_tables.update(
            {table_name: elements},
        ),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda *args, **kwargs: created_indexes.append(args),
    )

    migration.upgrade()

    assert migration.revision == "0021_op_expenses"
    assert migration.down_revision == "0020_price_lists"
    assert len(migration.revision) <= 32
    assert set(created_tables) == {
        "operating_expense_categories",
        "operating_expenses",
        "recurring_operating_expenses",
    }
    check_text = " ".join(
        str(element.sqltext)
        for elements in created_tables.values()
        for element in elements
        if isinstance(element, CheckConstraint)
    )
    for required_text in (
        "amount > 0",
        "payment_status IN",
        "payment_method IN",
        "frequency IN",
    ):
        assert required_text in check_text
    foreign_key_targets = {
        foreign_key.target_fullname
        for elements in created_tables.values()
        for element in elements
        if isinstance(element, ForeignKeyConstraint)
        for foreign_key in element.elements
    }
    assert {
        "operating_expense_categories.id",
        "suppliers.id",
        "users.id",
        "recurring_operating_expenses.id",
    } <= foreign_key_targets
    assert len(created_indexes) >= 20


def _create_category(client, headers, **overrides):
    payload = {
        "name": "Gastos generales",
        "description": "Control administrativo",
        **overrides,
    }
    response = client.post(
        "/api/v1/operating-expenses/categories",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    return response.json()


def _create_supplier(client, headers):
    response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": "Proveedor operativo"},
    )
    assert response.status_code == 201
    return response.json()


def _expense_response(client, headers, category_id: int, **overrides):
    payload = {
        "expense_date": "2026-07-18",
        "category_id": category_id,
        "description": "Gasto de prueba",
        "amount": "15.00",
        "payment_status": "unpaid",
        "payment_method": "unknown",
        **overrides,
    }
    return client.post(
        "/api/v1/operating-expenses",
        headers=headers,
        json=payload,
    )


def _create_expense(client, headers, category_id: int, **overrides):
    response = _expense_response(
        client,
        headers,
        category_id,
        **overrides,
    )
    assert response.status_code == 201
    return response.json()


def _template_response(client, headers, category_id: int, **overrides):
    payload = {
        "name": "Internet mensual",
        "category_id": category_id,
        "description": "Pago mensual de internet",
        "amount": "35.00",
        "frequency": "monthly",
        "start_date": "2026-07-01",
        "next_due_date": "2026-08-01",
        "payment_method": "transfer",
        "notes": "Pago recurrente",
        **overrides,
    }
    return client.post(
        "/api/v1/operating-expenses/recurring",
        headers=headers,
        json=payload,
    )


def _create_template(client, headers, category_id: int, **overrides):
    response = _template_response(
        client,
        headers,
        category_id,
        **overrides,
    )
    assert response.status_code == 201
    return response.json()


def _operational_counts(session) -> dict[str, int]:
    models = {
        "cash_sessions": CashSession,
        "cash_expenses": Expense,
        "inventory_movements": InventoryMovement,
        "purchases": Purchase,
        "sales": Sale,
    }
    return {
        name: session.scalar(select(func.count()).select_from(model)) or 0
        for name, model in models.items()
    }

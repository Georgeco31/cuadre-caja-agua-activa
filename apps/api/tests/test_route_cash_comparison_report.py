from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.models.cash_count_item import CashCountItem
from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.delivery_route import DeliveryRoute
from app.models.expense import Expense
from app.models.inventory_location import InventoryLocation
from app.models.inventory_movement import InventoryMovement
from app.models.inventory_stock import InventoryStock
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.sale import Sale
from app.models.user import User
from app.models.vehicle import Vehicle

REPORT_PATH = "/api/v1/reports/route-cash-comparison"


def test_route_cash_comparison_requires_authentication(api_client) -> None:
    client, _ = api_client

    response = client.get(REPORT_PATH)

    assert response.status_code == 401


def test_route_cash_comparison_without_data_uses_today_and_zeroes(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(REPORT_PATH, headers=api_auth_headers)

    assert response.status_code == 200
    body = response.json()
    today = date.today().isoformat()
    assert body["date_from"] == today
    assert body["date_to"] == today
    assert body["rows"] == []
    assert body["totals"] == {
        "route_closures_count": 0,
        "route_expected_cash_total": "0.00",
        "route_delivered_cash_total": "0.00",
        "route_difference_total": "0.00",
        "cash_total_counted": "0.00",
        "cash_total_expenses": "0.00",
        "cash_total_final": "0.00",
        "cash_vs_route_delivered_difference": "0.00",
    }


def test_route_cash_comparison_with_routes_without_cash_excludes_voided(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_route_closure(
        testing_session_local,
        suffix="active",
        closure_date=date(2026, 7, 18),
        expected=Decimal("120.00"),
        delivered=Decimal("115.00"),
    )
    _add_route_closure(
        testing_session_local,
        suffix="voided",
        closure_date=date(2026, 7, 18),
        expected=Decimal("80.00"),
        delivered=Decimal("80.00"),
        status="voided",
    )

    response = client.get(
        f"{REPORT_PATH}?date_from=2026-07-18",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date_from"] == "2026-07-18"
    assert body["date_to"] == "2026-07-18"
    assert body["totals"]["route_closures_count"] == 1
    assert body["totals"]["route_expected_cash_total"] == "120.00"
    assert body["totals"]["route_delivered_cash_total"] == "115.00"
    assert body["totals"]["route_difference_total"] == "-5.00"
    assert body["totals"]["cash_vs_route_delivered_difference"] == "-115.00"
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["cash_session_exists"] is False
    assert row["has_cash_session"] is False
    assert row["has_route_closures"] is True
    assert row["cash_session_id"] is None
    assert row["cash_session_status"] is None
    assert row["cash_total_counted"] == "0.00"
    assert row["comparison_status"] == "no_cash_session"
    assert [closure["closure_number"] for closure in row["route_closures"]] == [
        "CLOSE-active"
    ]


def test_route_cash_comparison_with_cash_without_routes_uses_official_summary(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    cash_session_id = _add_cash_session(
        testing_session_local,
        session_date=date(2026, 7, 19),
        coin_denomination_id=api_denominations["coin_100"].id,
        bill_denomination_id=api_denominations["bill_2000"].id,
        coins=Decimal("2.00"),
        bills=Decimal("20.00"),
        post_count_expense=Decimal("5.00"),
        pre_count_expense=Decimal("3.00"),
        status="closed",
    )

    response = client.get(
        (
            f"{REPORT_PATH}?date_from=2026-07-19"
            "&date_to=2026-07-19"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    row = response.json()["rows"][0]
    assert row["route_closures_count"] == 0
    assert row["has_route_closures"] is False
    assert row["cash_session_exists"] is True
    assert row["has_cash_session"] is True
    assert row["cash_session_id"] == cash_session_id
    assert row["cash_session_status"] == "closed"
    assert row["cash_total_coins"] == "2.00"
    assert row["cash_total_bills"] == "20.00"
    assert row["cash_total_counted"] == "22.00"
    assert row["cash_total_expenses"] == "5.00"
    assert row["cash_total_final"] == "17.00"
    assert row["cash_vs_route_delivered_difference"] == "22.00"
    assert row["comparison_status"] == "no_route_closures"


def test_route_cash_comparison_groups_dates_calculates_range_and_statuses(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    coin_id = api_denominations["coin_100"].id
    bill_id = api_denominations["bill_1000"].id
    _add_route_closure(
        testing_session_local,
        suffix="matched-a",
        closure_date=date(2026, 7, 20),
        expected=Decimal("7.00"),
        delivered=Decimal("6.00"),
    )
    _add_route_closure(
        testing_session_local,
        suffix="matched-b",
        closure_date=date(2026, 7, 20),
        expected=Decimal("5.00"),
        delivered=Decimal("4.00"),
    )
    _add_cash_session(
        testing_session_local,
        session_date=date(2026, 7, 20),
        coin_denomination_id=coin_id,
        bill_denomination_id=bill_id,
        coins=Decimal("0.00"),
        bills=Decimal("10.00"),
        post_count_expense=Decimal("1.00"),
    )
    _add_route_closure(
        testing_session_local,
        suffix="cash-higher",
        closure_date=date(2026, 7, 21),
        expected=Decimal("15.00"),
        delivered=Decimal("15.00"),
    )
    _add_cash_session(
        testing_session_local,
        session_date=date(2026, 7, 21),
        coin_denomination_id=coin_id,
        bill_denomination_id=bill_id,
        coins=Decimal("2.00"),
        bills=Decimal("20.00"),
    )
    _add_route_closure(
        testing_session_local,
        suffix="routes-higher",
        closure_date=date(2026, 7, 22),
        expected=Decimal("14.00"),
        delivered=Decimal("15.00"),
    )
    _add_cash_session(
        testing_session_local,
        session_date=date(2026, 7, 22),
        coin_denomination_id=coin_id,
        bill_denomination_id=bill_id,
        coins=Decimal("0.00"),
        bills=Decimal("10.00"),
        post_count_expense=Decimal("2.00"),
    )

    response = client.get(
        (
            f"{REPORT_PATH}?date_from=2026-07-20"
            "&date_to=2026-07-22"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    rows_by_date = {row["date"]: row for row in body["rows"]}
    assert list(rows_by_date) == ["2026-07-20", "2026-07-21", "2026-07-22"]
    matched = rows_by_date["2026-07-20"]
    assert matched["route_closures_count"] == 2
    assert matched["route_expected_cash_total"] == "12.00"
    assert matched["route_delivered_cash_total"] == "10.00"
    assert matched["route_difference_total"] == "-2.00"
    assert matched["comparison_status"] == "matched"
    assert rows_by_date["2026-07-21"]["comparison_status"] == (
        "cash_higher_than_routes"
    )
    assert rows_by_date["2026-07-22"]["comparison_status"] == (
        "routes_higher_than_cash"
    )
    assert body["totals"] == {
        "route_closures_count": 4,
        "route_expected_cash_total": "41.00",
        "route_delivered_cash_total": "40.00",
        "route_difference_total": "-1.00",
        "cash_total_counted": "42.00",
        "cash_total_expenses": "3.00",
        "cash_total_final": "39.00",
        "cash_vs_route_delivered_difference": "2.00",
    }


def test_route_cash_comparison_filters_both_range_limits(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_route_closure(
        testing_session_local,
        suffix="before",
        closure_date=date(2026, 7, 1),
        expected=Decimal("10.00"),
        delivered=Decimal("10.00"),
    )
    _add_cash_session(
        testing_session_local,
        session_date=date(2026, 7, 2),
        coin_denomination_id=api_denominations["coin_100"].id,
        bill_denomination_id=api_denominations["bill_1000"].id,
        coins=Decimal("1.00"),
        bills=Decimal("10.00"),
    )
    _add_route_closure(
        testing_session_local,
        suffix="after",
        closure_date=date(2026, 7, 3),
        expected=Decimal("20.00"),
        delivered=Decimal("20.00"),
    )

    response = client.get(
        (
            f"{REPORT_PATH}?date_from=2026-07-02"
            "&date_to=2026-07-02"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert [row["date"] for row in body["rows"]] == ["2026-07-02"]
    assert body["totals"]["route_closures_count"] == 0
    assert body["totals"]["cash_total_counted"] == "11.00"


def test_route_cash_comparison_rejects_invalid_date_range(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    response = client.get(
        (
            f"{REPORT_PATH}?date_from=2026-07-31"
            "&date_to=2026-07-01"
        ),
        headers=api_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "La fecha desde no puede ser mayor que la fecha hasta."
    )


def test_route_cash_comparison_is_read_only(
    api_client,
    api_denominations,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _add_route_closure(
        testing_session_local,
        suffix="readonly",
        closure_date=date(2026, 7, 23),
        expected=Decimal("30.00"),
        delivered=Decimal("29.00"),
    )
    _add_cash_session(
        testing_session_local,
        session_date=date(2026, 7, 23),
        coin_denomination_id=api_denominations["coin_100"].id,
        bill_denomination_id=api_denominations["bill_1000"].id,
        coins=Decimal("1.00"),
        bills=Decimal("30.00"),
        post_count_expense=Decimal("2.00"),
    )
    before = _database_snapshot(testing_session_local)

    response = client.get(
        f"{REPORT_PATH}?date_from=2026-07-23",
        headers=api_auth_headers,
    )

    assert response.status_code == 200
    assert _database_snapshot(testing_session_local) == before


def _add_route_closure(
    testing_session_local,
    *,
    suffix: str,
    closure_date: date,
    expected: Decimal,
    delivered: Decimal,
    status: str = "active",
) -> int:
    with testing_session_local() as session:
        user_id = session.scalar(select(User.id).limit(1))
        assert user_id is not None
        route = DeliveryRoute(
            code=f"ROUTE-{suffix}",
            name=f"Ruta {suffix}",
            expected_daily_cash=Decimal("0.00"),
        )
        vehicle = Vehicle(
            code=f"VEHICLE-{suffix}",
            name=f"Camion {suffix}",
            vehicle_type="truck",
            fuel_type="diesel",
        )
        session.add_all([route, vehicle])
        session.flush()
        source = InventoryLocation(
            code=f"SOURCE-{suffix}",
            name=f"Bodega {suffix}",
            location_type="warehouse",
        )
        destination = InventoryLocation(
            code=f"DESTINATION-{suffix}",
            name=f"Vehiculo {suffix}",
            location_type="vehicle",
            vehicle_id=vehicle.id,
        )
        session.add_all([source, destination])
        session.flush()
        route_load = RouteLoad(
            load_number=f"LOAD-{suffix}",
            load_date=closure_date,
            route_id=route.id,
            vehicle_id=vehicle.id,
            source_location_id=source.id,
            destination_location_id=destination.id,
            status="active",
            created_by=user_id,
        )
        session.add(route_load)
        session.flush()
        is_voided = status == "voided"
        closure = RouteClosure(
            closure_number=f"CLOSE-{suffix}",
            closure_date=closure_date,
            route_load_id=route_load.id,
            route_id=route.id,
            vehicle_id=vehicle.id,
            load_number_snapshot=route_load.load_number,
            route_name_snapshot=route.name,
            vehicle_name_snapshot=vehicle.name,
            cash_sales_total=expected,
            credit_sales_total=Decimal("0.00"),
            payments_total=Decimal("0.00"),
            expected_cash_total=expected,
            delivered_cash_total=delivered,
            difference_amount=delivered - expected,
            status=status,
            void_reason="Cierre anulado de prueba" if is_voided else None,
            voided_at=datetime.now(UTC) if is_voided else None,
            created_by=user_id,
        )
        session.add(closure)
        session.commit()
        return closure.id


def _add_cash_session(
    testing_session_local,
    *,
    session_date: date,
    coin_denomination_id: int,
    bill_denomination_id: int,
    coins: Decimal,
    bills: Decimal,
    post_count_expense: Decimal = Decimal("0.00"),
    pre_count_expense: Decimal = Decimal("0.00"),
    status: str = "open",
) -> int:
    with testing_session_local() as session:
        user_id = session.scalar(select(User.id).limit(1))
        assert user_id is not None
        cash_session = CashSession(
            session_date=session_date,
            status=status,
            created_by=user_id,
        )
        session.add(cash_session)
        session.flush()
        session.add_all(
            [
                CashCountItem(
                    cash_session_id=cash_session.id,
                    denomination_id=coin_denomination_id,
                    quantity=1 if coins else 0,
                    subtotal=coins,
                ),
                CashCountItem(
                    cash_session_id=cash_session.id,
                    denomination_id=bill_denomination_id,
                    quantity=1 if bills else 0,
                    subtotal=bills,
                ),
            ]
        )
        if post_count_expense:
            session.add(
                Expense(
                    cash_session_id=cash_session.id,
                    description="Gasto posterior",
                    amount=post_count_expense,
                    expense_timing="after_count",
                    expense_date=session_date,
                )
            )
        if pre_count_expense:
            session.add(
                Expense(
                    cash_session_id=cash_session.id,
                    description="Gasto previo",
                    amount=pre_count_expense,
                    expense_timing="before_count",
                    expense_date=session_date,
                )
            )
        session.commit()
        return cash_session.id


def _database_snapshot(testing_session_local) -> dict[str, object]:
    with testing_session_local() as session:
        closure = session.scalar(select(RouteClosure).limit(1))
        cash_session = session.scalar(select(CashSession).limit(1))
        assert closure is not None
        assert cash_session is not None
        return {
            "counts": {
                model.__tablename__: session.scalar(
                    select(func.count()).select_from(model)
                )
                for model in (
                    RouteClosure,
                    CashSession,
                    Expense,
                    Sale,
                    CreditPayment,
                    InventoryMovement,
                    InventoryStock,
                )
            },
            "closure": (
                closure.status,
                closure.expected_cash_total,
                closure.delivered_cash_total,
                closure.difference_amount,
            ),
            "cash_session": (
                cash_session.status,
                cash_session.session_date,
            ),
        }

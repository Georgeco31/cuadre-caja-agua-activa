from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import json

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.cash_session import CashSession
from app.models.credit_payment import CreditPayment
from app.models.route_closure import RouteClosure
from app.models.sale import Sale
from app.models.simple_route import (
    SimpleRouteCashReceipt,
    SimpleRouteCollection,
    SimpleRouteExpense,
    SimpleRouteSale,
    SimpleRouteSheet,
    SimpleRouteTrip,
    SimpleRouteTripItem,
)
from app.repositories import simple_routes as repository
from app.schemas.simple_route import (
    SimpleRouteAnalyticsRanking,
    SimpleRouteAnalyticsRead,
    SimpleRouteAnalyticsTrend,
    SimpleRouteAugustDryRunCandidate,
    SimpleRouteAugustDryRunRead,
    SimpleRouteCancel,
    SimpleRouteCashReceiptCreate,
    SimpleRouteCashReceiptRead,
    SimpleRouteCollectionCreate,
    SimpleRouteExpenseCreate,
    SimpleRouteListItem,
    SimpleRouteProductSettlement,
    SimpleRouteSaleCreate,
    SimpleRouteSettle,
    SimpleRouteSettlementRead,
    SimpleRouteSheetCreate,
    SimpleRouteSheetUpdate,
    SimpleRouteTripCreate,
    SimpleRouteTripItemCreate,
    SimpleRouteTripUpdate,
)

MONEY = Decimal("0.01")
QUANTITY = Decimal("0.001")
ZERO_MONEY = Decimal("0.00")
ZERO_QUANTITY = Decimal("0.000")
AUGUST_ROUTE_REVIEW_DATE = date(2026, 8, 1)


def create_sheet(
    db: Session,
    payload: SimpleRouteSheetCreate,
    created_by: int,
) -> SimpleRouteSheet:
    _validate_optional_references(
        db,
        employee_id=payload.employee_id,
        vehicle_id=payload.vehicle_id,
    )
    sheet = repository.create_sheet(
        db,
        {
            **payload.model_dump(),
            "status": "draft",
            "cash_received_in_cash_session": False,
            "created_by": created_by,
        },
    )
    db.flush()
    _audit(db, sheet.id, "sheet_created", created_by)
    return _commit_and_reload(db, sheet.id, "No se pudo crear la hoja de ruta.")


def update_sheet(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteSheetUpdate,
    actor_id: int,
) -> SimpleRouteSheet:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    values = payload.model_dump(exclude_unset=True)
    _validate_optional_references(
        db,
        employee_id=values.get("employee_id"),
        vehicle_id=values.get("vehicle_id"),
    )
    for field, value in values.items():
        setattr(sheet, field, value)
    _audit(db, sheet.id, "sheet_updated", actor_id)
    return _commit_and_reload(db, sheet.id, "No se pudo actualizar la hoja.")


def list_sheets(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    employee_id: int | None = None,
    vehicle_id: int | None = None,
    search: str | None = None,
) -> list[SimpleRouteListItem]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    sheets = repository.list_sheets(
        db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        employee_id=employee_id,
        vehicle_id=vehicle_id,
        search=_normalize_filter(search),
    )
    return [_list_item(sheet, calculate_settlement(sheet)) for sheet in sheets]


def get_sheet(db: Session, sheet_id: int) -> SimpleRouteSheet:
    sheet = repository.get_sheet(db, sheet_id)
    if sheet is None:
        raise ValueError("La hoja de ruta simple no existe.")
    return sheet


def add_trip(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteTripCreate,
    actor_id: int,
) -> SimpleRouteTrip:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    next_number = max((trip.trip_number for trip in sheet.trips), default=0) + 1
    trip_number = payload.trip_number or next_number
    if any(trip.trip_number == trip_number for trip in sheet.trips):
        raise ValueError("Ya existe un viaje con ese número en la hoja.")
    trip = repository.create_trip(
        db,
        {
            "route_sheet_id": sheet.id,
            "trip_number": trip_number,
            "notes": payload.notes,
        },
    )
    _mark_in_progress(sheet)
    db.flush()
    _audit(db, sheet.id, "trip_added", actor_id, metadata={"trip_id": trip.id})
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo agregar el viaje.") from error
    return _get_trip_or_raise(db, sheet.id, trip.id)


def update_trip(
    db: Session,
    sheet_id: int,
    trip_id: int,
    payload: SimpleRouteTripUpdate,
    actor_id: int,
) -> SimpleRouteTrip:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    trip = _get_trip_or_raise(db, sheet.id, trip_id)
    trip.notes = payload.notes
    _audit(db, sheet.id, "trip_updated", actor_id, metadata={"trip_id": trip.id})
    db.commit()
    return _get_trip_or_raise(db, sheet.id, trip.id)


def add_trip_item(
    db: Session,
    sheet_id: int,
    trip_id: int,
    payload: SimpleRouteTripItemCreate,
    actor_id: int,
) -> SimpleRouteTripItem:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    trip = _get_trip_or_raise(db, sheet.id, trip_id)
    product, label = _resolve_product_label(db, payload.product_id, payload.item_label)
    quantity = _quantity(payload.quantity)
    if payload.movement_type == "return":
        key = _item_key(payload.product_id, label, payload.item_category)
        totals = _physical_totals(sheet)
        out_total, return_total = totals.get(
            key,
            (ZERO_QUANTITY, ZERO_QUANTITY),
        )
        if return_total + quantity > out_total:
            raise ValueError(
                "El retorno acumulado no puede ser mayor que la salida acumulada."
            )
    item = repository.create_trip_item(
        db,
        {
            "trip_id": trip.id,
            "movement_type": payload.movement_type,
            "product_id": product.id if product is not None else None,
            "item_label": label,
            "item_category": payload.item_category,
            "quantity": quantity,
            "notes": payload.notes,
        },
    )
    _mark_in_progress(sheet)
    db.flush()
    _audit(
        db,
        sheet.id,
        "trip_item_added",
        actor_id,
        metadata={"trip_id": trip.id, "item_id": item.id},
    )
    db.commit()
    db.refresh(item)
    return item


def add_sale(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteSaleCreate,
    actor_id: int,
) -> SimpleRouteSale:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    customer_name = _resolve_customer_name(db, payload.customer_id, payload.customer_name)
    item_values: list[dict[str, object]] = []
    total = ZERO_MONEY
    for payload_item in payload.items:
        product, label = _resolve_product_label(
            db,
            payload_item.product_id,
            payload_item.product_name,
        )
        quantity = _quantity(payload_item.quantity)
        unit_price = _money(payload_item.unit_price)
        subtotal = _money(quantity * unit_price)
        total += subtotal
        item_values.append(
            {
                "product_id": product.id if product is not None else None,
                "product_name_snapshot": label,
                "item_category": payload_item.item_category,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )
    total = _money(total)
    paid, pending = _sale_amounts(payload.sale_type, total, payload.paid_amount)
    sale = repository.create_sale(
        db,
        {
            "route_sheet_id": sheet.id,
            "customer_id": payload.customer_id,
            "customer_name_snapshot": customer_name,
            "sale_type": payload.sale_type,
            "sale_date": payload.sale_date or sheet.route_date,
            "total_amount": total,
            "paid_amount": paid,
            "pending_amount": pending,
            "status": "active",
            "notes": payload.notes,
        },
    )
    db.flush()
    for values in item_values:
        repository.create_sale_item(
            db,
            {"simple_route_sale_id": sale.id, **values},
        )
    _mark_in_progress(sheet)
    _audit(db, sheet.id, "sale_added", actor_id, metadata={"sale_id": sale.id})
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar la venta de ruta.") from error
    created = repository.get_sale(db, sale.id)
    if created is None:
        raise RuntimeError("La venta de ruta no pudo recuperarse.")
    return created


def add_collection(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteCollectionCreate,
    actor_id: int,
) -> SimpleRouteCollection:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    linked_sale = None
    if payload.simple_route_sale_id is not None:
        linked_sale = repository.get_sale(db, payload.simple_route_sale_id)
        if linked_sale is None or linked_sale.status != "active":
            raise ValueError("El fiado de ruta enlazado no existe o no está activo.")
        if linked_sale.remaining_amount <= ZERO_MONEY:
            raise ValueError("El fiado de ruta enlazado ya no tiene saldo.")
        if _money(payload.amount) > linked_sale.remaining_amount:
            raise ValueError("El abono no puede superar el saldo del fiado de ruta.")
    customer_name = _resolve_customer_name(
        db,
        payload.customer_id,
        payload.customer_name,
    )
    if customer_name is None and linked_sale is not None:
        customer_name = linked_sale.customer_name_snapshot
    collection = repository.create_collection(
        db,
        {
            "route_sheet_id": sheet.id,
            "simple_route_sale_id": payload.simple_route_sale_id,
            "customer_id": payload.customer_id,
            "customer_name_snapshot": customer_name,
            "amount": _money(payload.amount),
            "collection_date": payload.collection_date or sheet.route_date,
            "notes": payload.notes,
        },
    )
    _mark_in_progress(sheet)
    db.flush()
    _audit(
        db,
        sheet.id,
        "collection_added",
        actor_id,
        metadata={"collection_id": collection.id},
    )
    db.commit()
    db.refresh(collection)
    return collection


def add_expense(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteExpenseCreate,
    actor_id: int,
) -> SimpleRouteExpense:
    sheet = _get_sheet_for_update(db, sheet_id)
    _ensure_editable(sheet)
    expense = repository.create_expense(
        db,
        {
            "route_sheet_id": sheet.id,
            "description": payload.description,
            "amount": _money(payload.amount),
            "category": payload.category,
            "expense_date": payload.expense_date or sheet.route_date,
            "notes": payload.notes,
        },
    )
    _mark_in_progress(sheet)
    db.flush()
    _audit(
        db,
        sheet.id,
        "expense_added",
        actor_id,
        metadata={"expense_id": expense.id},
    )
    db.commit()
    db.refresh(expense)
    return expense


def get_settlement(db: Session, sheet_id: int) -> SimpleRouteSettlementRead:
    return calculate_settlement(get_sheet(db, sheet_id))


def calculate_settlement(sheet: SimpleRouteSheet) -> SimpleRouteSettlementRead:
    physical: dict[tuple[object, ...], dict[str, object]] = {}
    for trip in sheet.trips:
        for item in trip.items:
            key = _item_key(item.product_id, item.item_label, item.item_category)
            row = physical.setdefault(
                key,
                {
                    "product_id": item.product_id,
                    "item_label": item.item_label,
                    "item_category": item.item_category,
                    "out": ZERO_QUANTITY,
                    "returned": ZERO_QUANTITY,
                    "registered": ZERO_QUANTITY,
                },
            )
            field = "out" if item.movement_type == "out" else "returned"
            row[field] = _quantity(Decimal(row[field]) + item.quantity)
    active_sales = [sale for sale in sheet.sales if sale.status == "active"]
    for sale in active_sales:
        for item in sale.items:
            key = _item_key(
                item.product_id,
                item.product_name_snapshot,
                item.item_category,
            )
            row = physical.setdefault(
                key,
                {
                    "product_id": item.product_id,
                    "item_label": item.product_name_snapshot,
                    "item_category": item.item_category,
                    "out": ZERO_QUANTITY,
                    "returned": ZERO_QUANTITY,
                    "registered": ZERO_QUANTITY,
                },
            )
            row["registered"] = _quantity(
                Decimal(row["registered"]) + item.quantity
            )
    products: list[SimpleRouteProductSettlement] = []
    has_product_difference = False
    for row in physical.values():
        total_out = _quantity(Decimal(row["out"]))
        returned = _quantity(Decimal(row["returned"]))
        registered = _quantity(Decimal(row["registered"]))
        physical_sold = _quantity(total_out - returned)
        difference = _quantity(physical_sold - registered)
        has_product_difference = has_product_difference or difference != ZERO_QUANTITY
        products.append(
            SimpleRouteProductSettlement(
                product_id=row["product_id"],
                item_label=str(row["item_label"]),
                item_category=row["item_category"],
                total_out=total_out,
                total_returned=returned,
                physical_sold=physical_sold,
                registered_sold=registered,
                physical_difference=difference,
            )
        )
    products.sort(key=lambda item: (item.item_label.casefold(), item.item_category))
    route_sales_total = _sum_money(sale.total_amount for sale in active_sales)
    cash_sales_collected = _sum_money(
        sale.paid_amount for sale in active_sales if sale.sale_type == "cash"
    )
    partial_sales_collected = _sum_money(
        sale.paid_amount for sale in active_sales if sale.sale_type == "partial"
    )
    route_credit_total = _sum_money(sale.pending_amount for sale in active_sales)
    collections_total = _sum_money(item.amount for item in sheet.collections)
    expenses_total = _sum_money(item.amount for item in sheet.expenses)
    expected_cash = _money(
        cash_sales_collected
        + partial_sales_collected
        + collections_total
        - expenses_total
    )
    cash_delivered = (
        _money(sheet.cash_delivered) if sheet.cash_delivered is not None else None
    )
    cash_difference = (
        _money(cash_delivered - expected_cash)
        if cash_delivered is not None
        else None
    )
    if sheet.status == "cancelled":
        status = "cancelled"
    elif sheet.status != "settled" or cash_difference is None:
        status = "pending"
    elif has_product_difference or cash_difference != ZERO_MONEY:
        status = "with_difference"
    else:
        status = "balanced"
    return SimpleRouteSettlementRead(
        route_sheet_id=sheet.id,
        status=status,
        products=products,
        route_sales_total=route_sales_total,
        cash_sales_collected=cash_sales_collected,
        partial_sales_collected=partial_sales_collected,
        route_credit_total=route_credit_total,
        collections_total=collections_total,
        expenses_total=expenses_total,
        expected_cash=expected_cash,
        cash_delivered=cash_delivered,
        cash_difference=cash_difference,
        cash_receipt_status=(
            "received" if sheet.cash_received_in_cash_session else "pending"
        ),
        cash_session_id=sheet.cash_session_id,
    )


def settle_sheet(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteSettle,
    actor_id: int,
) -> SimpleRouteSheet:
    sheet = _get_sheet_for_update(db, sheet_id)
    if sheet.status == "cancelled":
        raise ValueError("La hoja cancelada no puede liquidarse.")
    if sheet.status == "settled":
        raise ValueError("La hoja de ruta ya está liquidada.")
    sheet.cash_delivered = _money(payload.cash_delivered)
    sheet.status = "settled"
    sheet.settled_by = actor_id
    sheet.settled_at = datetime.now(timezone.utc)
    if payload.notes is not None:
        sheet.notes = payload.notes
    _audit(db, sheet.id, "sheet_settled", actor_id)
    return _commit_and_reload(db, sheet.id, "No se pudo liquidar la hoja.")


def cancel_sheet(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteCancel,
    actor_id: int,
) -> SimpleRouteSheet:
    sheet = _get_sheet_for_update(db, sheet_id)
    if sheet.status == "cancelled":
        raise ValueError("La hoja de ruta ya está cancelada.")
    if sheet.cash_received_in_cash_session:
        raise ValueError(
            "La hoja ya fue recibida en caja y no puede cancelarse sin conciliación."
        )
    sheet.status = "cancelled"
    sheet.cancelled_by = actor_id
    sheet.cancelled_at = datetime.now(timezone.utc)
    sheet.cancellation_reason = payload.reason
    _audit(db, sheet.id, "sheet_cancelled", actor_id, reason=payload.reason)
    return _commit_and_reload(db, sheet.id, "No se pudo cancelar la hoja.")


def receive_cash(
    db: Session,
    sheet_id: int,
    payload: SimpleRouteCashReceiptCreate,
    actor_id: int,
) -> SimpleRouteCashReceipt:
    sheet = _get_sheet_for_update(db, sheet_id)
    if sheet.status != "settled" or sheet.cash_delivered is None:
        raise ValueError("La hoja debe estar liquidada antes de recibirla en caja.")
    if sheet.cash_received_in_cash_session or repository.get_cash_receipt_for_sheet(
        db, sheet.id
    ):
        raise ValueError("El efectivo de esta hoja ya fue recibido en caja.")
    cash_session = repository.get_cash_session(
        db,
        payload.cash_session_id,
        for_update=True,
    )
    if cash_session is None:
        raise ValueError("El cuadre de caja no existe.")
    if cash_session.status != "open":
        raise ValueError("El cuadre de caja está cerrado y no admite recepciones.")
    if cash_session.session_date != sheet.route_date:
        raise ValueError("La fecha del cuadre debe coincidir con la hoja de ruta.")
    receipt = repository.create_cash_receipt(
        db,
        {
            "route_sheet_id": sheet.id,
            "cash_session_id": cash_session.id,
            "amount": _money(sheet.cash_delivered),
            "received_by": actor_id,
            "notes": payload.notes,
        },
    )
    sheet.cash_received_in_cash_session = True
    sheet.cash_session_id = cash_session.id
    db.flush()
    _audit(
        db,
        sheet.id,
        "cash_received",
        actor_id,
        metadata={"cash_session_id": cash_session.id, "receipt_id": receipt.id},
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("El efectivo de esta hoja ya fue recibido en caja.") from error
    created = repository.get_cash_receipt_for_sheet(db, sheet.id)
    if created is None:
        raise RuntimeError("La recepción de efectivo no pudo recuperarse.")
    return created


def list_cash_session_receipts(
    db: Session,
    cash_session_id: int,
) -> list[SimpleRouteCashReceiptRead]:
    cash_session = repository.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre de caja no existe.")
    return [
        SimpleRouteCashReceiptRead(
            id=receipt.id,
            route_sheet_id=receipt.route_sheet_id,
            cash_session_id=receipt.cash_session_id,
            amount=receipt.amount,
            received_by=receipt.received_by,
            received_at=receipt.received_at,
            notes=receipt.notes,
            created_at=receipt.created_at,
            seller_name=receipt.route_sheet.seller_name,
            route_label=receipt.route_sheet.route_label,
        )
        for receipt in repository.list_cash_receipts_for_session(db, cash_session_id)
    ]


def get_analytics(
    db: Session,
    date_from: date,
    date_to: date,
) -> SimpleRouteAnalyticsRead:
    if date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    sheets = repository.list_sheets(db, date_from=date_from, date_to=date_to)
    active_sheets = [sheet for sheet in sheets if sheet.status != "cancelled"]
    settlements = {sheet.id: calculate_settlement(sheet) for sheet in active_sheets}
    route_totals: dict[str, Decimal] = defaultdict(lambda: ZERO_MONEY)
    route_counts: dict[str, int] = defaultdict(int)
    seller_totals: dict[str, Decimal] = defaultdict(lambda: ZERO_MONEY)
    seller_counts: dict[str, int] = defaultdict(int)
    daily: dict[date, Decimal] = defaultdict(lambda: ZERO_MONEY)
    for sheet in active_sheets:
        settlement = settlements[sheet.id]
        route_label = sheet.route_label or "Sin ruta/zona"
        route_totals[route_label] += settlement.route_sales_total
        route_counts[route_label] += 1
        seller_totals[sheet.seller_name] += settlement.route_sales_total
        seller_counts[sheet.seller_name] += 1
        daily[sheet.route_date] += settlement.route_sales_total
    trend = [
        SimpleRouteAnalyticsTrend(route_date=day, total=_money(total))
        for day, total in sorted(daily.items())
    ]
    best_day = max(trend, key=lambda item: item.total, default=None)
    return SimpleRouteAnalyticsRead(
        date_from=date_from,
        date_to=date_to,
        routes_count=len(active_sheets),
        total_route_sales=_sum_money(
            settlement.route_sales_total for settlement in settlements.values()
        ),
        total_cash_sales=_sum_money(
            settlement.cash_sales_collected
            + settlement.partial_sales_collected
            for settlement in settlements.values()
        ),
        total_credit_sales=_sum_money(
            settlement.route_credit_total for settlement in settlements.values()
        ),
        total_collected=_sum_money(
            settlement.cash_sales_collected
            + settlement.partial_sales_collected
            + settlement.collections_total
            for settlement in settlements.values()
        ),
        total_expenses=_sum_money(
            settlement.expenses_total for settlement in settlements.values()
        ),
        total_expected_cash=_sum_money(
            settlement.expected_cash for settlement in settlements.values()
        ),
        total_delivered_cash=_sum_money(
            settlement.cash_delivered or ZERO_MONEY
            for settlement in settlements.values()
        ),
        total_difference=_sum_money(
            settlement.cash_difference or ZERO_MONEY
            for settlement in settlements.values()
        ),
        top_routes=_ranking(route_totals, route_counts),
        top_sellers=_ranking(seller_totals, seller_counts),
        best_sales_day=best_day,
        daily_trend=trend,
        routes_with_differences=[
            sheet_id
            for sheet_id, settlement in settlements.items()
            if settlement.status == "with_difference"
        ],
    )


def august_1_official_route_sales_dry_run(
    db: Session,
) -> SimpleRouteAugustDryRunRead:
    sales = list(
        db.scalars(
            select(Sale)
            .options(selectinload(Sale.payments))
            .where(
                Sale.sale_date == AUGUST_ROUTE_REVIEW_DATE,
                Sale.route_load_id.is_not(None),
            )
            .order_by(Sale.id)
        ).unique()
    )
    cash_session = db.scalar(
        select(CashSession).where(
            CashSession.session_date == AUGUST_ROUTE_REVIEW_DATE
        )
    )
    candidates: list[SimpleRouteAugustDryRunCandidate] = []
    for sale in sales:
        active_payments = [payment for payment in sale.payments if payment.status == "active"]
        closure = db.scalar(
            select(RouteClosure)
            .where(RouteClosure.route_load_id == sale.route_load_id)
            .order_by(RouteClosure.id.desc())
        )
        active_closure = closure is not None and closure.status == "active"
        could_be_voided = (
            sale.status == "active"
            and not active_closure
            and not (sale.sale_type == "credit" and active_payments)
        )
        risks: list[str] = []
        if active_payments:
            risks.append("Tiene abonos oficiales activos")
        if active_closure:
            risks.append("La carga tiene cierre financiero activo")
        if cash_session is not None:
            risks.append("Existe cuadre de caja para la fecha")
        if sale.status == "voided":
            risks.append("La venta ya está anulada")
        candidates.append(
            SimpleRouteAugustDryRunCandidate(
                sale_id=sale.id,
                sale_number=sale.sale_number,
                customer=sale.customer_name_snapshot,
                sale_type=sale.sale_type,
                status=sale.status,
                total_amount=sale.total_amount,
                paid_amount=sale.paid_amount,
                balance_amount=sale.balance_amount,
                payments_total=_sum_money(
                    payment.amount for payment in active_payments
                ),
                route_load_id=int(sale.route_load_id),
                route_closure_id=closure.id if closure is not None else None,
                cash_session_id=cash_session.id if cash_session is not None else None,
                cash_session_status=(
                    cash_session.status if cash_session is not None else None
                ),
                could_be_voided=could_be_voided,
                risk="; ".join(risks) if risks else "Revisión manual obligatoria",
                suggested_reason=(
                    "Venta de ruta del 2026-08-01 migrada al módulo independiente, "
                    "previa autorización de George"
                ),
            )
        )
    return SimpleRouteAugustDryRunRead(
        report_date=AUGUST_ROUTE_REVIEW_DATE,
        candidates_count=len(candidates),
        candidates=candidates,
        modified_records=0,
        warning=(
            "Dry-run de solo lectura. No anula ventas, cobros, cierres ni datos."
        ),
    )


def _validate_optional_references(
    db: Session,
    *,
    employee_id: object = None,
    vehicle_id: object = None,
) -> None:
    if isinstance(employee_id, int) and repository.get_employee(db, employee_id) is None:
        raise ValueError("El empleado seleccionado no existe.")
    if isinstance(vehicle_id, int) and repository.get_vehicle(db, vehicle_id) is None:
        raise ValueError("El vehículo seleccionado no existe.")


def _resolve_product_label(db: Session, product_id: int | None, label: str | None):
    product = repository.get_product(db, product_id) if product_id is not None else None
    if product_id is not None and product is None:
        raise ValueError("El producto seleccionado no existe.")
    resolved_label = product.name if product is not None else label
    if resolved_label is None or not resolved_label.strip():
        raise ValueError("Debe seleccionar un producto o escribir una etiqueta.")
    return product, resolved_label.strip()


def _resolve_customer_name(
    db: Session,
    customer_id: int | None,
    free_name: str | None,
) -> str | None:
    if customer_id is None:
        return free_name
    customer = repository.get_customer(db, customer_id)
    if customer is None:
        raise ValueError("El cliente seleccionado no existe.")
    return customer.name


def _sale_amounts(
    sale_type: str,
    total: Decimal,
    requested_paid: Decimal | None,
) -> tuple[Decimal, Decimal]:
    if sale_type == "cash":
        if requested_paid is not None and _money(requested_paid) != total:
            raise ValueError("En contado, el monto cobrado debe ser igual al total.")
        return total, ZERO_MONEY
    if sale_type == "credit":
        paid = ZERO_MONEY if requested_paid is None else _money(requested_paid)
        if paid != ZERO_MONEY:
            raise ValueError("Use venta parcial cuando exista un cobro inicial.")
        return ZERO_MONEY, total
    if requested_paid is None:
        raise ValueError("La venta parcial requiere el monto cobrado.")
    paid = _money(requested_paid)
    if paid <= ZERO_MONEY or paid >= total:
        raise ValueError("El cobro parcial debe ser mayor que cero y menor al total.")
    return paid, _money(total - paid)


def _get_sheet_for_update(db: Session, sheet_id: int) -> SimpleRouteSheet:
    sheet = repository.get_sheet(db, sheet_id, for_update=True)
    if sheet is None:
        raise ValueError("La hoja de ruta simple no existe.")
    return sheet


def _get_trip_or_raise(db: Session, sheet_id: int, trip_id: int) -> SimpleRouteTrip:
    trip = repository.get_trip(db, sheet_id, trip_id)
    if trip is None:
        raise ValueError("El viaje no existe en esta hoja de ruta.")
    return trip


def _ensure_editable(sheet: SimpleRouteSheet) -> None:
    if sheet.status == "settled":
        raise ValueError("La hoja liquidada no puede editarse libremente.")
    if sheet.status == "cancelled":
        raise ValueError("La hoja cancelada no puede editarse.")


def _mark_in_progress(sheet: SimpleRouteSheet) -> None:
    if sheet.status == "draft":
        sheet.status = "in_progress"


def _commit_and_reload(db: Session, sheet_id: int, message: str) -> SimpleRouteSheet:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(message) from error
    return get_sheet(db, sheet_id)


def _audit(
    db: Session,
    sheet_id: int,
    action: str,
    actor_id: int,
    *,
    reason: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    repository.create_audit_log(
        db,
        {
            "route_sheet_id": sheet_id,
            "action": action,
            "reason": reason,
            "created_by": actor_id,
            "metadata_json": (
                json.dumps(metadata, ensure_ascii=False, sort_keys=True)
                if metadata is not None
                else None
            ),
        },
    )


def _physical_totals(
    sheet: SimpleRouteSheet,
) -> dict[tuple[object, ...], tuple[Decimal, Decimal]]:
    totals: dict[tuple[object, ...], list[Decimal]] = defaultdict(
        lambda: [ZERO_QUANTITY, ZERO_QUANTITY]
    )
    for trip in sheet.trips:
        for item in trip.items:
            key = _item_key(item.product_id, item.item_label, item.item_category)
            index = 0 if item.movement_type == "out" else 1
            totals[key][index] = _quantity(totals[key][index] + item.quantity)
    return {key: (values[0], values[1]) for key, values in totals.items()}


def _item_key(product_id: int | None, label: str, category: str):
    if product_id is not None:
        return ("product", product_id, category)
    return ("label", label.strip().casefold(), category)


def _list_item(
    sheet: SimpleRouteSheet,
    settlement: SimpleRouteSettlementRead,
) -> SimpleRouteListItem:
    return SimpleRouteListItem(
        id=sheet.id,
        route_date=sheet.route_date,
        seller_name=sheet.seller_name,
        vehicle_name=sheet.vehicle_name,
        route_label=sheet.route_label,
        status=sheet.status,
        route_sales_total=settlement.route_sales_total,
        route_credit_total=settlement.route_credit_total,
        expenses_total=settlement.expenses_total,
        expected_cash=settlement.expected_cash,
        cash_delivered=settlement.cash_delivered,
        cash_difference=settlement.cash_difference,
        settlement_status=settlement.status,
        cash_received_in_cash_session=sheet.cash_received_in_cash_session,
    )


def _ranking(
    totals: dict[str, Decimal],
    counts: dict[str, int],
) -> list[SimpleRouteAnalyticsRanking]:
    return [
        SimpleRouteAnalyticsRanking(label=label, total=_money(total), count=counts[label])
        for label, total in sorted(
            totals.items(),
            key=lambda item: (-item[1], item[0].casefold()),
        )[:10]
    ]


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def _quantity(value: Decimal) -> Decimal:
    return Decimal(value).quantize(QUANTITY, rounding=ROUND_HALF_UP)


def _sum_money(values) -> Decimal:
    return _money(sum(values, start=ZERO_MONEY))


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None

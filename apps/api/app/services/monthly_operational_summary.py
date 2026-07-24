from calendar import monthrange
from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.credit_payment import CreditPayment
from app.models.production_batch import ProductionBatch
from app.models.route_cash_receipt import RouteCashReceipt
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.route_return import RouteReturn
from app.models.sale import Sale
from app.repositories import (
    cash_sessions,
    credit_payments,
    production,
    route_cash_receipts,
    route_closures,
    route_loads,
    route_returns,
    sales,
)
from app.schemas.monthly_operational_summary import (
    MonthlyCashSummary,
    MonthlyOperationalAlertByCode,
    MonthlyOperationalAlertsSummary,
    MonthlyOperationalDailyRow,
    MonthlyOperationalPeriod,
    MonthlyOperationalSummary,
    MonthlyOperationalTotals,
    MonthlyProductSold,
    MonthlyProductionProduct,
    MonthlyProductionSummary,
    MonthlyReceivablesSummary,
    MonthlyRouteCashReceiptsSummary,
    MonthlyRouteFinancialSummary,
    MonthlyRouteOperationsSummary,
    MonthlySalesSummary,
)
from app.schemas.summary import CashSessionSummary
from app.services.summary_service import get_cash_session_summary

MONEY_ZERO = Decimal("0.00")
QUANTITY_ZERO = Decimal("0.000")
MONEY_QUANTUM = Decimal("0.01")
QUANTITY_QUANTUM = Decimal("0.001")

ALERT_MESSAGES = {
    "cash_session_missing": "No existe cuadre de caja para este día.",
    "cash_session_open": "El cuadre de caja del día permanece abierto.",
    "route_shortage": "Hay al menos un cierre de ruta con faltante.",
    "route_closure_without_cash_receipt": (
        "Hay al menos un cierre de ruta sin dinero registrado en caja."
    ),
    "route_cash_receipt_difference": (
        "Hay al menos un registro de dinero de ruta en caja con diferencia."
    ),
    "no_production": "No hay producción activa registrada para este día.",
    "no_sales": "No hay ventas activas registradas para este día.",
    "routes_loaded_without_closure": (
        "Hay al menos una carga de ruta sin cierre financiero."
    ),
}


def get_monthly_operational_summary(
    db: Session,
    year: int | None = None,
    month: int | None = None,
) -> MonthlyOperationalSummary:
    today = date.today()
    resolved_year = year if year is not None else today.year
    resolved_month = month if month is not None else today.month
    date_from, date_to, days_in_month = _resolve_period(
        resolved_year,
        resolved_month,
    )

    sessions = cash_sessions.list_cash_sessions(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    cash_by_date = {
        cash_session.session_date: get_cash_session_summary(
            db,
            cash_session.id,
        )
        for cash_session in sessions
    }
    batches = production.list_production_batches(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    monthly_sales = sales.list_sales(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    payments = credit_payments.list_credit_payments(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    loads = route_loads.list_route_loads(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    returns = route_returns.list_route_returns(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    closures = route_closures.list_route_closures(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    receipts = route_cash_receipts.list_route_cash_receipts(
        db,
        date_from=date_from,
        date_to=date_to,
    )

    cash_summary = _build_cash_summary(
        cash_by_date,
        sessions_count=len(sessions),
        open_sessions_count=sum(session.status == "open" for session in sessions),
        closed_sessions_count=sum(
            session.status == "closed" for session in sessions
        ),
        days_in_month=days_in_month,
    )
    production_summary = _build_production_summary(batches)
    sales_summary = _build_sales_summary(monthly_sales)
    receivables_summary = _build_receivables_summary(monthly_sales, payments)
    route_operations_summary = _build_route_operations_summary(loads, returns)
    route_financial_summary = _build_route_financial_summary(closures)
    route_cash_receipts_summary = _build_route_cash_receipts_summary(receipts)

    daily_rows, alerts_summary = _build_daily_rows(
        db=db,
        date_from=date_from,
        days_in_month=days_in_month,
        cash_by_date=cash_by_date,
        batches=batches,
        monthly_sales=monthly_sales,
        payments=payments,
        loads=loads,
        closures=closures,
        receipts=receipts,
    )

    return MonthlyOperationalSummary(
        period=MonthlyOperationalPeriod(
            year=resolved_year,
            month=resolved_month,
            date_from=date_from,
            date_to=date_to,
            days_in_month=days_in_month,
        ),
        cash_summary=cash_summary,
        production_summary=production_summary,
        sales_summary=sales_summary,
        receivables_summary=receivables_summary,
        route_operations_summary=route_operations_summary,
        route_financial_summary=route_financial_summary,
        route_cash_receipts_summary=route_cash_receipts_summary,
        daily_rows=daily_rows,
        alerts_summary=alerts_summary,
        totals=MonthlyOperationalTotals(
            total_business_cash_inflow_reference=_money(
                sales_summary.cash_sales_total
                + receivables_summary.payments_total
                + route_cash_receipts_summary.received_amount_total,
            ),
        ),
    )


def _resolve_period(year: int, month: int) -> tuple[date, date, int]:
    if not 1 <= year <= 9999:
        raise ValueError("El año debe estar entre 1 y 9999.")
    if not 1 <= month <= 12:
        raise ValueError("El mes debe estar entre 1 y 12.")
    days_in_month = monthrange(year, month)[1]
    date_from = date(year, month, 1)
    return date_from, date(year, month, days_in_month), days_in_month


def _build_cash_summary(
    cash_by_date: dict[date, CashSessionSummary],
    *,
    sessions_count: int,
    open_sessions_count: int,
    closed_sessions_count: int,
    days_in_month: int,
) -> MonthlyCashSummary:
    summaries = list(cash_by_date.values())
    total_counted = _sum_money(
        summary.total_counted for summary in summaries
    )
    days_with_cash_session = len(cash_by_date)
    average_daily_counted = (
        _money(total_counted / days_with_cash_session)
        if days_with_cash_session
        else MONEY_ZERO
    )
    return MonthlyCashSummary(
        cash_sessions_count=sessions_count,
        open_cash_sessions_count=open_sessions_count,
        closed_cash_sessions_count=closed_sessions_count,
        total_coins=_sum_money(summary.total_coins for summary in summaries),
        total_bills=_sum_money(summary.total_bills for summary in summaries),
        total_counted=total_counted,
        total_expenses=_sum_money(
            summary.total_expenses for summary in summaries
        ),
        total_final=_sum_money(summary.final_total for summary in summaries),
        average_daily_counted=average_daily_counted,
        days_with_cash_session=days_with_cash_session,
        days_without_cash_session=days_in_month - days_with_cash_session,
    )


def _build_production_summary(
    batches: list[ProductionBatch],
) -> MonthlyProductionSummary:
    active_batches = [batch for batch in batches if batch.status == "active"]
    products: dict[int, dict[str, str | Decimal]] = {}
    for batch in sorted(
        active_batches,
        key=lambda item: (item.production_date, item.id),
    ):
        for item in batch.items:
            product = products.setdefault(
                item.product_id,
                {
                    "name": item.product_name_snapshot,
                    "produced": QUANTITY_ZERO,
                    "waste": QUANTITY_ZERO,
                },
            )
            product["name"] = item.product_name_snapshot
            product["produced"] = _quantity(
                Decimal(product["produced"]) + item.quantity_produced,
            )
            product["waste"] = _quantity(
                Decimal(product["waste"]) + item.quantity_waste,
            )

    product_rows = [
        MonthlyProductionProduct(
            product_id=product_id,
            product_name_snapshot=str(values["name"]),
            quantity_produced=_quantity(Decimal(values["produced"])),
            quantity_waste=_quantity(Decimal(values["waste"])),
            quantity_net=_quantity(
                Decimal(values["produced"]) - Decimal(values["waste"]),
            ),
        )
        for product_id, values in products.items()
    ]
    product_rows.sort(
        key=lambda item: (item.product_name_snapshot.casefold(), item.product_id),
    )
    total_produced = _sum_quantities(
        product.quantity_produced for product in product_rows
    )
    total_waste = _sum_quantities(
        product.quantity_waste for product in product_rows
    )
    return MonthlyProductionSummary(
        production_batches_count=len(batches),
        active_production_batches_count=len(active_batches),
        voided_production_batches_count=sum(
            batch.status == "voided" for batch in batches
        ),
        total_quantity_produced=total_produced,
        total_quantity_waste=total_waste,
        total_quantity_net=_quantity(total_produced - total_waste),
        products=product_rows,
    )


def _build_sales_summary(monthly_sales: list[Sale]) -> MonthlySalesSummary:
    active_sales = [sale for sale in monthly_sales if sale.status == "active"]
    cash_sales = [sale for sale in active_sales if sale.sale_type == "cash"]
    credit_sales = [sale for sale in active_sales if sale.sale_type == "credit"]
    products: dict[int, dict[str, str | Decimal]] = {}
    for sale in sorted(active_sales, key=lambda item: (item.sale_date, item.id)):
        for item in sale.items:
            product = products.setdefault(
                item.product_id,
                {
                    "name": item.product_name_snapshot,
                    "quantity": QUANTITY_ZERO,
                    "amount": MONEY_ZERO,
                },
            )
            product["name"] = item.product_name_snapshot
            product["quantity"] = _quantity(
                Decimal(product["quantity"]) + item.quantity,
            )
            product["amount"] = _money(
                Decimal(product["amount"]) + item.subtotal,
            )

    product_rows = [
        MonthlyProductSold(
            product_id=product_id,
            product_name_snapshot=str(values["name"]),
            quantity=_quantity(Decimal(values["quantity"])),
            amount=_money(Decimal(values["amount"])),
        )
        for product_id, values in products.items()
    ]
    product_rows.sort(
        key=lambda item: (item.product_name_snapshot.casefold(), item.product_id),
    )
    cash_total = _sum_money(sale.total_amount for sale in cash_sales)
    credit_total = _sum_money(sale.total_amount for sale in credit_sales)
    return MonthlySalesSummary(
        cash_sales_total=cash_total,
        credit_sales_total=credit_total,
        total_sales_amount=_money(cash_total + credit_total),
        cash_sales_count=len(cash_sales),
        credit_sales_count=len(credit_sales),
        voided_sales_count=sum(
            sale.status == "voided" for sale in monthly_sales
        ),
        products_sold=product_rows,
    )


def _build_receivables_summary(
    monthly_sales: list[Sale],
    payments: list[CreditPayment],
) -> MonthlyReceivablesSummary:
    active_payments = [
        payment for payment in payments if payment.status == "active"
    ]
    active_credit_sales = [
        sale
        for sale in monthly_sales
        if sale.status == "active" and sale.sale_type == "credit"
    ]
    return MonthlyReceivablesSummary(
        payments_total=_sum_money(
            payment.amount for payment in active_payments
        ),
        payments_count=len(active_payments),
        voided_payments_count=sum(
            payment.status == "voided" for payment in payments
        ),
        credit_sales_created_total=_sum_money(
            sale.total_amount for sale in active_credit_sales
        ),
        pending_credit_total=_sum_money(
            sale.balance_amount for sale in active_credit_sales
        ),
        customers_with_credit_sales_count=len(
            {
                sale.customer_id
                for sale in active_credit_sales
                if sale.customer_id is not None
            },
        ),
    )


def _build_route_operations_summary(
    loads: list[RouteLoad],
    returns: list[RouteReturn],
) -> MonthlyRouteOperationsSummary:
    active_loads = [load for load in loads if load.status == "active"]
    active_returns = [
        route_return
        for route_return in returns
        if route_return.status == "active"
    ]
    return MonthlyRouteOperationsSummary(
        route_loads_count=len(loads),
        active_route_loads_count=len(active_loads),
        voided_route_loads_count=sum(
            load.status == "voided" for load in loads
        ),
        route_returns_count=len(returns),
        active_route_returns_count=len(active_returns),
        voided_route_returns_count=sum(
            route_return.status == "voided" for route_return in returns
        ),
        total_quantity_loaded=_sum_quantities(
            item.quantity_loaded
            for load in active_loads
            for item in load.items
        ),
        total_quantity_returned=_sum_quantities(
            item.quantity_returned
            for route_return in active_returns
            for item in route_return.items
        ),
    )


def _build_route_financial_summary(
    closures: list[RouteClosure],
) -> MonthlyRouteFinancialSummary:
    active_closures = [
        closure for closure in closures if closure.status == "active"
    ]
    return MonthlyRouteFinancialSummary(
        route_closures_count=len(closures),
        active_route_closures_count=len(active_closures),
        voided_route_closures_count=sum(
            closure.status == "voided" for closure in closures
        ),
        expected_cash_total=_sum_money(
            closure.expected_cash_total for closure in active_closures
        ),
        delivered_cash_total=_sum_money(
            closure.delivered_cash_total for closure in active_closures
        ),
        difference_total=_sum_money(
            closure.difference_amount for closure in active_closures
        ),
        closures_with_shortage_count=sum(
            closure.difference_amount < MONEY_ZERO
            for closure in active_closures
        ),
        closures_with_surplus_count=sum(
            closure.difference_amount > MONEY_ZERO
            for closure in active_closures
        ),
        closures_balanced_count=sum(
            closure.difference_amount == MONEY_ZERO
            for closure in active_closures
        ),
    )


def _build_route_cash_receipts_summary(
    receipts: list[RouteCashReceipt],
) -> MonthlyRouteCashReceiptsSummary:
    active_receipts = [
        receipt for receipt in receipts if receipt.status == "active"
    ]
    return MonthlyRouteCashReceiptsSummary(
        receipts_count=len(receipts),
        active_receipts_count=len(active_receipts),
        voided_receipts_count=sum(
            receipt.status == "voided" for receipt in receipts
        ),
        delivered_cash_total=_sum_money(
            receipt.delivered_cash_total for receipt in active_receipts
        ),
        received_amount_total=_sum_money(
            receipt.received_amount for receipt in active_receipts
        ),
        difference_total=_sum_money(
            receipt.difference_amount for receipt in active_receipts
        ),
    )


def _build_daily_rows(
    *,
    db: Session,
    date_from: date,
    days_in_month: int,
    cash_by_date: dict[date, CashSessionSummary],
    batches: list[ProductionBatch],
    monthly_sales: list[Sale],
    payments: list[CreditPayment],
    loads: list[RouteLoad],
    closures: list[RouteClosure],
    receipts: list[RouteCashReceipt],
) -> tuple[
    list[MonthlyOperationalDailyRow],
    MonthlyOperationalAlertsSummary,
]:
    batches_by_date = _group_by_date(batches, "production_date")
    sales_by_date = _group_by_date(monthly_sales, "sale_date")
    payments_by_date = _group_by_date(payments, "payment_date")
    loads_by_date = _group_by_date(loads, "load_date")
    closures_by_date = _group_by_date(closures, "closure_date")
    receipts_by_date = _group_by_date(receipts, "receipt_date")

    active_monthly_closures = [
        closure for closure in closures if closure.status == "active"
    ]
    active_monthly_loads = [load for load in loads if load.status == "active"]
    closure_ids_with_active_receipt = _active_receipt_closure_ids(
        db,
        [closure.id for closure in active_monthly_closures],
    )
    load_ids_with_active_closure = _active_closure_load_ids(
        db,
        [load.id for load in active_monthly_loads],
    )

    rows: list[MonthlyOperationalDailyRow] = []
    alert_counts: Counter[str] = Counter()
    days_with_alerts_count = 0
    for offset in range(days_in_month):
        row_date = date_from + timedelta(days=offset)
        cash = cash_by_date.get(row_date)
        daily_batches = batches_by_date[row_date]
        daily_sales = sales_by_date[row_date]
        daily_payments = payments_by_date[row_date]
        daily_loads = loads_by_date[row_date]
        daily_closures = closures_by_date[row_date]
        daily_receipts = receipts_by_date[row_date]

        active_batches = [
            batch for batch in daily_batches if batch.status == "active"
        ]
        active_sales = [
            sale for sale in daily_sales if sale.status == "active"
        ]
        active_payments = [
            payment
            for payment in daily_payments
            if payment.status == "active"
        ]
        active_loads = [
            load for load in daily_loads if load.status == "active"
        ]
        active_closures = [
            closure
            for closure in daily_closures
            if closure.status == "active"
        ]
        active_receipts = [
            receipt
            for receipt in daily_receipts
            if receipt.status == "active"
        ]

        alert_codes = _daily_alert_codes(
            cash=cash,
            active_batches=active_batches,
            active_sales=active_sales,
            active_loads=active_loads,
            active_closures=active_closures,
            active_receipts=active_receipts,
            closure_ids_with_active_receipt=closure_ids_with_active_receipt,
            load_ids_with_active_closure=load_ids_with_active_closure,
        )
        alert_counts.update(alert_codes)
        if alert_codes:
            days_with_alerts_count += 1

        rows.append(
            MonthlyOperationalDailyRow(
                date=row_date,
                cash_session_exists=cash is not None,
                cash_total_counted=(
                    _money(cash.total_counted)
                    if cash is not None
                    else MONEY_ZERO
                ),
                cash_total_expenses=(
                    _money(cash.total_expenses)
                    if cash is not None
                    else MONEY_ZERO
                ),
                cash_total_final=(
                    _money(cash.final_total)
                    if cash is not None
                    else MONEY_ZERO
                ),
                production_quantity_net=_sum_quantities(
                    item.quantity_produced - item.quantity_waste
                    for batch in active_batches
                    for item in batch.items
                ),
                cash_sales_total=_sum_money(
                    sale.total_amount
                    for sale in active_sales
                    if sale.sale_type == "cash"
                ),
                credit_sales_total=_sum_money(
                    sale.total_amount
                    for sale in active_sales
                    if sale.sale_type == "credit"
                ),
                payments_total=_sum_money(
                    payment.amount for payment in active_payments
                ),
                route_delivered_cash_total=_sum_money(
                    closure.delivered_cash_total
                    for closure in active_closures
                ),
                route_cash_registered_total=_sum_money(
                    receipt.received_amount for receipt in active_receipts
                ),
                alerts_count=len(alert_codes),
                alert_codes=alert_codes,
            ),
        )

    alerts_by_code = [
        MonthlyOperationalAlertByCode(
            code=code,
            count=alert_counts[code],
            message=message,
        )
        for code, message in ALERT_MESSAGES.items()
        if alert_counts[code]
    ]
    return rows, MonthlyOperationalAlertsSummary(
        total_alerts=sum(alert_counts.values()),
        days_with_alerts_count=days_with_alerts_count,
        alerts_by_code=alerts_by_code,
    )


def _daily_alert_codes(
    *,
    cash: CashSessionSummary | None,
    active_batches: list[ProductionBatch],
    active_sales: list[Sale],
    active_loads: list[RouteLoad],
    active_closures: list[RouteClosure],
    active_receipts: list[RouteCashReceipt],
    closure_ids_with_active_receipt: set[int],
    load_ids_with_active_closure: set[int],
) -> list[str]:
    codes: list[str] = []
    if cash is None:
        codes.append("cash_session_missing")
    elif cash.status == "open":
        codes.append("cash_session_open")
    if any(
        closure.difference_amount < MONEY_ZERO
        for closure in active_closures
    ):
        codes.append("route_shortage")
    if any(
        closure.id not in closure_ids_with_active_receipt
        for closure in active_closures
    ):
        codes.append("route_closure_without_cash_receipt")
    if any(
        receipt.difference_amount != MONEY_ZERO
        for receipt in active_receipts
    ):
        codes.append("route_cash_receipt_difference")
    if not active_batches:
        codes.append("no_production")
    if not active_sales:
        codes.append("no_sales")
    if any(
        load.id not in load_ids_with_active_closure
        for load in active_loads
    ):
        codes.append("routes_loaded_without_closure")
    return codes


def _active_receipt_closure_ids(
    db: Session,
    closure_ids: list[int],
) -> set[int]:
    if not closure_ids:
        return set()
    statement = select(RouteCashReceipt.route_closure_id).where(
        RouteCashReceipt.route_closure_id.in_(closure_ids),
        RouteCashReceipt.status == "active",
    )
    return set(db.scalars(statement))


def _active_closure_load_ids(
    db: Session,
    load_ids: list[int],
) -> set[int]:
    if not load_ids:
        return set()
    statement = select(RouteClosure.route_load_id).where(
        RouteClosure.route_load_id.in_(load_ids),
        RouteClosure.status == "active",
    )
    return set(db.scalars(statement))


def _group_by_date(
    values: Iterable[object],
    attribute: str,
) -> defaultdict[date, list]:
    grouped: defaultdict[date, list] = defaultdict(list)
    for value in values:
        grouped[getattr(value, attribute)].append(value)
    return grouped


def _sum_money(values: Iterable[Decimal]) -> Decimal:
    return _money(sum(values, MONEY_ZERO))


def _sum_quantities(values: Iterable[Decimal]) -> Decimal:
    return _quantity(sum(values, QUANTITY_ZERO))


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(MONEY_QUANTUM)


def _quantity(value: Decimal) -> Decimal:
    return Decimal(value).quantize(QUANTITY_QUANTUM)

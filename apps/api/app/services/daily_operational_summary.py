from collections.abc import Iterable
from datetime import date
from decimal import Decimal

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
from app.schemas.daily_operational_summary import (
    DailyCashSummary,
    DailyOperationalAlert,
    DailyOperationalSummary,
    DailyOperationalTotals,
    DailyProductSold,
    DailyProductionProduct,
    DailyProductionSummary,
    DailyReceivablesSummary,
    DailyRouteCashReceipt,
    DailyRouteCashReceiptsSummary,
    DailyRouteClosure,
    DailyRouteClosuresSummary,
    DailyRouteLoad,
    DailyRouteLoadsSummary,
    DailyRouteReturn,
    DailyRouteReturnsSummary,
    DailySalesSummary,
)
from app.services.expense_service import list_expenses
from app.services.route_cash_receipts import get_receipts_for_cash_session
from app.services.summary_service import get_cash_session_summary

MONEY_ZERO = Decimal("0.00")
QUANTITY_ZERO = Decimal("0.000")
MONEY_QUANTUM = Decimal("0.01")
QUANTITY_QUANTUM = Decimal("0.001")


def get_daily_operational_summary(
    db: Session,
    report_date: date | None = None,
) -> DailyOperationalSummary:
    resolved_date = report_date or date.today()

    cash_summary = _build_cash_summary(db, resolved_date)
    production_batches = production.list_production_batches(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )
    loads = route_loads.list_route_loads(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )
    returns = route_returns.list_route_returns(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )
    closures = route_closures.list_route_closures(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )
    receipts = route_cash_receipts.list_route_cash_receipts(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )
    daily_sales = sales.list_sales(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )
    payments = credit_payments.list_credit_payments(
        db,
        date_from=resolved_date,
        date_to=resolved_date,
    )

    production_summary = _build_production_summary(production_batches)
    loads_summary = _build_route_loads_summary(loads)
    returns_summary = _build_route_returns_summary(returns)
    closures_summary = _build_route_closures_summary(closures)
    receipts_summary = _build_route_cash_receipts_summary(receipts)
    sales_summary = _build_sales_summary(daily_sales)
    receivables_summary = _build_receivables_summary(daily_sales, payments)

    return DailyOperationalSummary(
        date=resolved_date,
        cash_summary=cash_summary,
        production_summary=production_summary,
        route_loads_summary=loads_summary,
        route_returns_summary=returns_summary,
        route_closures_summary=closures_summary,
        route_cash_receipts_summary=receipts_summary,
        sales_summary=sales_summary,
        receivables_summary=receivables_summary,
        alerts=_build_alerts(
            db=db,
            cash_summary=cash_summary,
            production_summary=production_summary,
            loads=loads,
            closures=closures,
            receipts=receipts,
            sales_summary=sales_summary,
        ),
        totals=DailyOperationalTotals(
            total_business_cash_inflow_reference=_money(
                sales_summary.cash_sales_total
                + receivables_summary.payments_total
                + receipts_summary.received_amount_total,
            ),
            total_route_delivered_cash=closures_summary.delivered_cash_total,
            total_route_cash_registered=receipts_summary.received_amount_total,
            total_cash_counted=cash_summary.total_counted,
            total_cash_final=cash_summary.total_final,
        ),
    )


def _build_cash_summary(db: Session, report_date: date) -> DailyCashSummary:
    cash_session = cash_sessions.get_cash_session_by_date(db, report_date)
    if cash_session is None:
        return DailyCashSummary(
            cash_session_exists=False,
            cash_session_id=None,
            cash_session_status=None,
            total_coins=MONEY_ZERO,
            total_bills=MONEY_ZERO,
            total_counted=MONEY_ZERO,
            total_expenses=MONEY_ZERO,
            total_final=MONEY_ZERO,
            pre_count_expenses_total=MONEY_ZERO,
            post_count_expenses_total=MONEY_ZERO,
            expenses_count=0,
            route_cash_receipts_total=MONEY_ZERO,
            route_cash_receipts_count=0,
        )

    official_summary = get_cash_session_summary(db, cash_session.id)
    receipt_summary = get_receipts_for_cash_session(db, cash_session.id)
    return DailyCashSummary(
        cash_session_exists=True,
        cash_session_id=cash_session.id,
        cash_session_status=cash_session.status,
        total_coins=_money(official_summary.total_coins),
        total_bills=_money(official_summary.total_bills),
        total_counted=_money(official_summary.total_counted),
        total_expenses=_money(official_summary.total_expenses),
        total_final=_money(official_summary.final_total),
        pre_count_expenses_total=_money(
            official_summary.total_pre_count_expenses,
        ),
        post_count_expenses_total=_money(
            official_summary.total_post_count_expenses,
        ),
        expenses_count=len(list_expenses(db, cash_session.id)),
        route_cash_receipts_total=_money(
            receipt_summary.totals.received_amount_total,
        ),
        route_cash_receipts_count=receipt_summary.totals.receipts_count,
    )


def _build_production_summary(
    batches: list[ProductionBatch],
) -> DailyProductionSummary:
    active_batches = [batch for batch in batches if batch.status == "active"]
    products: dict[int, DailyProductionProduct] = {}
    for batch in active_batches:
        for item in batch.items:
            existing = products.get(item.product_id)
            produced = _quantity(item.quantity_produced)
            waste = _quantity(item.quantity_waste)
            if existing is None:
                products[item.product_id] = DailyProductionProduct(
                    product_id=item.product_id,
                    product_name_snapshot=item.product_name_snapshot,
                    quantity_produced=produced,
                    quantity_waste=waste,
                    quantity_net=_quantity(produced - waste),
                )
                continue
            existing.quantity_produced = _quantity(
                existing.quantity_produced + produced,
            )
            existing.quantity_waste = _quantity(existing.quantity_waste + waste)
            existing.quantity_net = _quantity(
                existing.quantity_produced - existing.quantity_waste,
            )

    product_rows = sorted(
        products.values(),
        key=lambda item: (item.product_name_snapshot.casefold(), item.product_id),
    )
    total_produced = _sum_quantities(
        item.quantity_produced for item in product_rows
    )
    total_waste = _sum_quantities(item.quantity_waste for item in product_rows)
    return DailyProductionSummary(
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


def _build_route_loads_summary(loads: list[RouteLoad]) -> DailyRouteLoadsSummary:
    active_loads = [load for load in loads if load.status == "active"]
    rows = [
        DailyRouteLoad(
            id=load.id,
            load_number=load.load_number,
            route_name=load.route_name,
            vehicle_name=load.vehicle_name,
            status=load.status,
            total_quantity_loaded=_sum_quantities(
                item.quantity_loaded for item in load.items
            ),
        )
        for load in loads
    ]
    return DailyRouteLoadsSummary(
        route_loads_count=len(loads),
        active_route_loads_count=len(active_loads),
        voided_route_loads_count=sum(load.status == "voided" for load in loads),
        total_items_loaded=sum(len(load.items) for load in active_loads),
        total_quantity_loaded=_sum_quantities(
            item.quantity_loaded
            for load in active_loads
            for item in load.items
        ),
        loads=rows,
    )


def _build_route_returns_summary(
    returns: list[RouteReturn],
) -> DailyRouteReturnsSummary:
    active_returns = [
        route_return
        for route_return in returns
        if route_return.status == "active"
    ]
    return DailyRouteReturnsSummary(
        route_returns_count=len(returns),
        active_route_returns_count=len(active_returns),
        voided_route_returns_count=sum(
            route_return.status == "voided" for route_return in returns
        ),
        total_quantity_returned=_sum_quantities(
            item.quantity_returned
            for route_return in active_returns
            for item in route_return.items
        ),
        returns=[
            DailyRouteReturn(
                id=route_return.id,
                return_number=route_return.return_number,
                route_name=route_return.route_name,
                vehicle_name=route_return.vehicle_name,
                status=route_return.status,
                total_quantity_returned=_sum_quantities(
                    item.quantity_returned for item in route_return.items
                ),
            )
            for route_return in returns
        ],
    )


def _build_route_closures_summary(
    closures: list[RouteClosure],
) -> DailyRouteClosuresSummary:
    active_closures = [
        closure for closure in closures if closure.status == "active"
    ]
    return DailyRouteClosuresSummary(
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
        closures=[
            DailyRouteClosure(
                id=closure.id,
                closure_number=closure.closure_number,
                route_name_snapshot=closure.route_name_snapshot,
                vehicle_name_snapshot=closure.vehicle_name_snapshot,
                expected_cash_total=_money(closure.expected_cash_total),
                delivered_cash_total=_money(closure.delivered_cash_total),
                difference_amount=_money(closure.difference_amount),
                status=closure.status,
            )
            for closure in closures
        ],
    )


def _build_route_cash_receipts_summary(
    receipts: list[RouteCashReceipt],
) -> DailyRouteCashReceiptsSummary:
    active_receipts = [
        receipt for receipt in receipts if receipt.status == "active"
    ]
    return DailyRouteCashReceiptsSummary(
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
        receipts=[
            DailyRouteCashReceipt(
                id=receipt.id,
                receipt_number=receipt.receipt_number,
                closure_number_snapshot=receipt.closure_number_snapshot,
                route_name_snapshot=receipt.route_name_snapshot,
                vehicle_name_snapshot=receipt.vehicle_name_snapshot,
                delivered_cash_total=_money(receipt.delivered_cash_total),
                received_amount=_money(receipt.received_amount),
                difference_amount=_money(receipt.difference_amount),
                status=receipt.status,
            )
            for receipt in receipts
        ],
    )


def _build_sales_summary(daily_sales: list[Sale]) -> DailySalesSummary:
    active_sales = [sale for sale in daily_sales if sale.status == "active"]
    cash_sales = [sale for sale in active_sales if sale.sale_type == "cash"]
    credit_sales = [sale for sale in active_sales if sale.sale_type == "credit"]
    products: dict[int, DailyProductSold] = {}
    for sale in active_sales:
        for item in sale.items:
            existing = products.get(item.product_id)
            quantity = _quantity(item.quantity)
            amount = _money(item.subtotal)
            if existing is None:
                products[item.product_id] = DailyProductSold(
                    product_id=item.product_id,
                    product_name_snapshot=item.product_name_snapshot,
                    quantity=quantity,
                    amount=amount,
                )
                continue
            existing.quantity = _quantity(existing.quantity + quantity)
            existing.amount = _money(existing.amount + amount)

    cash_total = _sum_money(sale.total_amount for sale in cash_sales)
    credit_total = _sum_money(sale.total_amount for sale in credit_sales)
    return DailySalesSummary(
        cash_sales_total=cash_total,
        credit_sales_total=credit_total,
        total_sales_amount=_money(cash_total + credit_total),
        cash_sales_count=len(cash_sales),
        credit_sales_count=len(credit_sales),
        voided_sales_count=sum(sale.status == "voided" for sale in daily_sales),
        products_sold=sorted(
            products.values(),
            key=lambda item: (
                item.product_name_snapshot.casefold(),
                item.product_id,
            ),
        ),
    )


def _build_receivables_summary(
    daily_sales: list[Sale],
    payments: list[CreditPayment],
) -> DailyReceivablesSummary:
    active_payments = [
        payment for payment in payments if payment.status == "active"
    ]
    active_credit_sales = [
        sale
        for sale in daily_sales
        if sale.status == "active" and sale.sale_type == "credit"
    ]
    return DailyReceivablesSummary(
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
        outstanding_balance_created_today=_sum_money(
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


def _build_alerts(
    *,
    db: Session,
    cash_summary: DailyCashSummary,
    production_summary: DailyProductionSummary,
    loads: list[RouteLoad],
    closures: list[RouteClosure],
    receipts: list[RouteCashReceipt],
    sales_summary: DailySalesSummary,
) -> list[DailyOperationalAlert]:
    alerts: list[DailyOperationalAlert] = []
    if not cash_summary.cash_session_exists:
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="cash_session_missing",
                message="No existe cuadre de caja para esta fecha.",
            ),
        )
    elif cash_summary.cash_session_status == "open":
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="cash_session_open",
                message="El cuadre de caja de esta fecha está abierto.",
            ),
        )

    active_closures = [
        closure for closure in closures if closure.status == "active"
    ]
    shortage_count = sum(
        closure.difference_amount < MONEY_ZERO
        for closure in active_closures
    )
    if shortage_count:
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="route_closure_shortage",
                message=(
                    f"Hay {shortage_count} cierre(s) de ruta con faltante."
                ),
            ),
        )

    closures_without_receipt = sum(
        not route_cash_receipts.has_active_receipt_for_closure(db, closure.id)
        for closure in active_closures
    )
    if closures_without_receipt:
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="route_closure_cash_unregistered",
                message=(
                    f"Hay {closures_without_receipt} cierre(s) de ruta activo(s) "
                    "sin dinero registrado en caja."
                ),
            ),
        )

    receipts_with_difference = sum(
        receipt.status == "active" and receipt.difference_amount != MONEY_ZERO
        for receipt in receipts
    )
    if receipts_with_difference:
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="route_cash_receipt_difference",
                message=(
                    f"Hay {receipts_with_difference} registro(s) de dinero de "
                    "ruta en caja con diferencia."
                ),
            ),
        )

    active_loads = [load for load in loads if load.status == "active"]
    loads_without_return = sum(
        not route_returns.has_active_return_for_load(db, load.id)
        for load in active_loads
    )
    if loads_without_return:
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="route_load_without_return",
                message=(
                    f"Hay {loads_without_return} carga(s) activa(s) sin retorno."
                ),
            ),
        )

    loads_without_closure = sum(
        not route_closures.has_active_closure_for_load(db, load.id)
        for load in active_loads
    )
    if loads_without_closure:
        alerts.append(
            DailyOperationalAlert(
                type="warning",
                code="route_load_without_closure",
                message=(
                    f"Hay {loads_without_closure} carga(s) activa(s) sin cierre "
                    "financiero."
                ),
            ),
        )

    if production_summary.active_production_batches_count == 0:
        alerts.append(
            DailyOperationalAlert(
                type="info",
                code="production_missing",
                message="No hay producción activa registrada para esta fecha.",
            ),
        )
    if sales_summary.cash_sales_count + sales_summary.credit_sales_count == 0:
        alerts.append(
            DailyOperationalAlert(
                type="info",
                code="sales_missing",
                message="No hay ventas activas registradas para esta fecha.",
            ),
        )
    return alerts


def _sum_money(values: Iterable[Decimal]) -> Decimal:
    return _money(sum(values, MONEY_ZERO))


def _sum_quantities(values: Iterable[Decimal]) -> Decimal:
    return _quantity(sum(values, QUANTITY_ZERO))


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(MONEY_QUANTUM)


def _quantity(value: Decimal) -> Decimal:
    return Decimal(value).quantize(QUANTITY_QUANTUM)

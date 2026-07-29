from calendar import monthrange
from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.credit_payment import CreditPayment
from app.models.inventory_location import InventoryLocation
from app.models.inventory_stock import InventoryStock
from app.models.operating_expense import OperatingExpense
from app.models.payroll_run import PayrollRun
from app.models.product import Product
from app.models.production_batch import ProductionBatch
from app.models.production_inventory_application import (
    ProductionInventoryApplication,
)
from app.models.production_material_consumption import (
    ProductionMaterialConsumption,
)
from app.models.purchase import Purchase
from app.models.route_cash_receipt import RouteCashReceipt
from app.models.route_closure import RouteClosure
from app.models.route_load import RouteLoad
from app.models.route_return import RouteReturn
from app.models.sale import Sale
from app.repositories import cash_sessions
from app.schemas.management_dashboard import (
    ManagementAlert,
    ManagementCashSummary,
    ManagementCharts,
    ManagementDailyCashPoint,
    ManagementDailyExpensesPoint,
    ManagementDailySalesPoint,
    ManagementDashboard,
    ManagementDashboardPeriod,
    ManagementExpenseCategory,
    ManagementInventorySummary,
    ManagementLowStockItem,
    ManagementOperatingExpensesSummary,
    ManagementPayrollSummary,
    ManagementProductionProductPoint,
    ManagementProductionSummary,
    ManagementPurchasesSummary,
    ManagementReceivablesSummary,
    ManagementRoutesSummary,
    ManagementSalesSummary,
    ManagementSupplierTotal,
)
from app.services.summary_service import get_cash_session_summary

MONEY_ZERO = Decimal("0.00")
QUANTITY_ZERO = Decimal("0.000")
MONEY_QUANTUM = Decimal("0.01")
QUANTITY_QUANTUM = Decimal("0.001")
LOW_STOCK_THRESHOLD = Decimal("5.000")
TOP_RESULTS_LIMIT = 5


def get_management_dashboard(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
) -> ManagementDashboard:
    resolved_date_from, resolved_date_to = _resolve_period(date_from, date_to)

    selected_sessions = cash_sessions.list_cash_sessions(
        db,
        date_from=resolved_date_from,
        date_to=resolved_date_to,
    )
    cash_summaries = {
        cash_session.session_date: get_cash_session_summary(
            db,
            cash_session.id,
        )
        for cash_session in selected_sessions
    }
    selected_sales = _list_sales(db, resolved_date_from, resolved_date_to)
    selected_payments = _list_payments(db, resolved_date_from, resolved_date_to)
    selected_expenses = _list_operating_expenses(
        db,
        resolved_date_from,
        resolved_date_to,
    )
    selected_purchases = _list_purchases(
        db,
        resolved_date_from,
        resolved_date_to,
    )
    selected_batches = _list_production_batches(
        db,
        resolved_date_from,
        resolved_date_to,
    )
    selected_consumptions = _list_material_consumptions(
        db,
        resolved_date_from,
        resolved_date_to,
    )
    selected_loads = _list_by_date(
        db,
        RouteLoad,
        RouteLoad.load_date,
        resolved_date_from,
        resolved_date_to,
    )
    selected_returns = _list_by_date(
        db,
        RouteReturn,
        RouteReturn.return_date,
        resolved_date_from,
        resolved_date_to,
    )
    selected_closures = _list_by_date(
        db,
        RouteClosure,
        RouteClosure.closure_date,
        resolved_date_from,
        resolved_date_to,
    )
    selected_receipts = _list_by_date(
        db,
        RouteCashReceipt,
        RouteCashReceipt.receipt_date,
        resolved_date_from,
        resolved_date_to,
    )
    selected_payroll_runs = _list_by_date(
        db,
        PayrollRun,
        PayrollRun.payroll_date,
        resolved_date_from,
        resolved_date_to,
    )

    active_sales = [sale for sale in selected_sales if sale.status == "active"]
    active_credit_sales = [
        sale for sale in active_sales if sale.sale_type == "credit"
    ]
    active_payments = [
        payment for payment in selected_payments if payment.status == "active"
    ]
    active_expenses = [
        expense for expense in selected_expenses if expense.status == "active"
    ]
    active_purchases = [
        purchase for purchase in selected_purchases if purchase.status == "active"
    ]
    active_batches = [
        batch for batch in selected_batches if batch.status == "active"
    ]
    active_consumptions = [
        consumption
        for consumption in selected_consumptions
        if consumption.status == "active"
    ]
    active_closures = [
        closure for closure in selected_closures if closure.status == "active"
    ]
    inventory = _build_inventory_summary(db)
    supplier_totals = _build_supplier_totals(active_purchases)

    cash = _build_cash_summary(selected_sessions, cash_summaries)
    sales = _build_sales_summary(selected_sales, active_sales)
    receivables = _build_receivables_summary(
        active_credit_sales,
        active_payments,
    )
    operating_expenses = _build_operating_expenses_summary(
        selected_expenses,
        active_expenses,
    )
    purchases = _build_purchases_summary(
        selected_purchases,
        active_purchases,
        supplier_totals,
    )
    production = _build_production_summary(
        db,
        active_batches,
        active_consumptions,
    )
    routes = _build_routes_summary(
        selected_loads,
        selected_returns,
        active_closures,
        selected_receipts,
    )
    payroll = _build_payroll_summary(selected_payroll_runs)
    charts = _build_charts(
        active_sales=active_sales,
        active_payments=active_payments,
        cash_summaries=cash_summaries,
        active_expenses=active_expenses,
        selected_sessions=selected_sessions,
        active_batches=active_batches,
        supplier_totals=supplier_totals,
    )

    return ManagementDashboard(
        period=ManagementDashboardPeriod(
            date_from=resolved_date_from,
            date_to=resolved_date_to,
        ),
        cash=cash,
        sales=sales,
        receivables=receivables,
        operating_expenses=operating_expenses,
        purchases=purchases,
        production=production,
        inventory=inventory,
        routes=routes,
        payroll=payroll,
        charts=charts,
        alerts=_build_alerts(
            cash=cash,
            receivables=receivables,
            inventory=inventory,
            active_closures=active_closures,
            active_expenses=active_expenses,
            active_purchases=active_purchases,
            payroll=payroll,
        ),
    )


def _resolve_period(
    date_from: date | None,
    date_to: date | None,
) -> tuple[date, date]:
    if date_from is None and date_to is None:
        today = date.today()
        last_day = monthrange(today.year, today.month)[1]
        return date(today.year, today.month, 1), date(
            today.year,
            today.month,
            last_day,
        )
    if date_from is None:
        date_from = date_to
    if date_to is None:
        date_to = date_from
    if date_from is None or date_to is None:
        raise ValueError("No se pudo resolver el rango de fechas.")
    if date_to < date_from:
        raise ValueError("La fecha hasta no puede ser menor que la fecha desde.")
    return date_from, date_to


def _list_sales(db: Session, date_from: date, date_to: date) -> list[Sale]:
    statement = (
        select(Sale)
        .where(Sale.sale_date >= date_from, Sale.sale_date <= date_to)
        .order_by(Sale.sale_date, Sale.id)
    )
    return list(db.scalars(statement))


def _list_payments(
    db: Session,
    date_from: date,
    date_to: date,
) -> list[CreditPayment]:
    statement = (
        select(CreditPayment)
        .where(
            CreditPayment.payment_date >= date_from,
            CreditPayment.payment_date <= date_to,
        )
        .order_by(CreditPayment.payment_date, CreditPayment.id)
    )
    return list(db.scalars(statement))


def _list_operating_expenses(
    db: Session,
    date_from: date,
    date_to: date,
) -> list[OperatingExpense]:
    statement = (
        select(OperatingExpense)
        .options(selectinload(OperatingExpense.category))
        .where(
            OperatingExpense.expense_date >= date_from,
            OperatingExpense.expense_date <= date_to,
        )
        .order_by(OperatingExpense.expense_date, OperatingExpense.id)
    )
    return list(db.scalars(statement))


def _list_purchases(
    db: Session,
    date_from: date,
    date_to: date,
) -> list[Purchase]:
    statement = (
        select(Purchase)
        .options(selectinload(Purchase.supplier))
        .where(
            Purchase.purchase_date >= date_from,
            Purchase.purchase_date <= date_to,
        )
        .order_by(Purchase.purchase_date, Purchase.id)
    )
    return list(db.scalars(statement))


def _list_production_batches(
    db: Session,
    date_from: date,
    date_to: date,
) -> list[ProductionBatch]:
    statement = (
        select(ProductionBatch)
        .options(selectinload(ProductionBatch.items))
        .where(
            ProductionBatch.production_date >= date_from,
            ProductionBatch.production_date <= date_to,
        )
        .order_by(ProductionBatch.production_date, ProductionBatch.id)
    )
    return list(db.scalars(statement))


def _list_material_consumptions(
    db: Session,
    date_from: date,
    date_to: date,
) -> list[ProductionMaterialConsumption]:
    statement = (
        select(ProductionMaterialConsumption)
        .where(
            ProductionMaterialConsumption.movement_date >= date_from,
            ProductionMaterialConsumption.movement_date <= date_to,
        )
        .order_by(
            ProductionMaterialConsumption.movement_date,
            ProductionMaterialConsumption.id,
        )
    )
    return list(db.scalars(statement))


def _list_by_date(
    db: Session,
    model: type,
    date_field,
    date_from: date,
    date_to: date,
) -> list:
    statement = (
        select(model)
        .where(date_field >= date_from, date_field <= date_to)
        .order_by(date_field, model.id)
    )
    return list(db.scalars(statement))


def _build_cash_summary(
    selected_sessions: list,
    cash_summaries: dict,
) -> ManagementCashSummary:
    summaries = list(cash_summaries.values())
    return ManagementCashSummary(
        cash_sessions_count=len(selected_sessions),
        cash_total_counted=_sum_money(
            summary.total_counted for summary in summaries
        ),
        cash_total_expenses_after_count=_sum_money(
            summary.total_post_count_expenses for summary in summaries
        ),
        cash_final_total=_sum_money(summary.final_total for summary in summaries),
        open_cash_sessions_count=sum(
            cash_session.status == "open" for cash_session in selected_sessions
        ),
        closed_cash_sessions_count=sum(
            cash_session.status == "closed" for cash_session in selected_sessions
        ),
    )


def _build_sales_summary(
    selected_sales: list[Sale],
    active_sales: list[Sale],
) -> ManagementSalesSummary:
    cash_sales_total = _sum_money(
        sale.total_amount
        for sale in active_sales
        if sale.sale_type == "cash"
    )
    credit_sales_total = _sum_money(
        sale.total_amount
        for sale in active_sales
        if sale.sale_type == "credit"
    )
    sales_total = _money(cash_sales_total + credit_sales_total)
    return ManagementSalesSummary(
        cash_sales_total=cash_sales_total,
        credit_sales_total=credit_sales_total,
        sales_total=sales_total,
        active_sales_count=len(active_sales),
        voided_sales_count=sum(sale.status == "voided" for sale in selected_sales),
        average_sale_amount=(
            _money(sales_total / len(active_sales))
            if active_sales
            else MONEY_ZERO
        ),
    )


def _build_receivables_summary(
    active_credit_sales: list[Sale],
    active_payments: list[CreditPayment],
) -> ManagementReceivablesSummary:
    pending_sales = [
        sale for sale in active_credit_sales if sale.balance_amount > MONEY_ZERO
    ]
    overdue_sales = [
        sale
        for sale in pending_sales
        if sale.due_date is not None and sale.due_date < date.today()
    ]
    return ManagementReceivablesSummary(
        credit_sales_total=_sum_money(
            sale.total_amount for sale in active_credit_sales
        ),
        payments_total=_sum_money(payment.amount for payment in active_payments),
        pending_balance_total=_sum_money(
            sale.balance_amount for sale in pending_sales
        ),
        customers_with_balance_count=len(
            {
                sale.customer_id
                for sale in pending_sales
                if sale.customer_id is not None
            }
        ),
        overdue_balance_total=_sum_money(
            sale.balance_amount for sale in overdue_sales
        ),
        overdue_customers_count=len(
            {
                sale.customer_id
                for sale in overdue_sales
                if sale.customer_id is not None
            }
        ),
    )


def _build_operating_expenses_summary(
    selected_expenses: list[OperatingExpense],
    active_expenses: list[OperatingExpense],
) -> ManagementOperatingExpensesSummary:
    category_totals: defaultdict[int, Decimal] = defaultdict(
        lambda: MONEY_ZERO
    )
    category_names: dict[int, str] = {}
    for expense in active_expenses:
        category_totals[expense.category_id] += expense.amount
        category_names[expense.category_id] = expense.category.name
    categories = [
        ManagementExpenseCategory(
            category_id=category_id,
            category_name=category_names[category_id],
            total_amount=_money(total),
        )
        for category_id, total in category_totals.items()
    ]
    categories.sort(
        key=lambda item: (
            -item.total_amount,
            item.category_name.casefold(),
            item.category_id,
        )
    )
    return ManagementOperatingExpensesSummary(
        operating_expenses_total=_sum_money(
            expense.amount for expense in active_expenses
        ),
        paid_expenses_total=_sum_money(
            expense.amount
            for expense in active_expenses
            if expense.payment_status == "paid"
        ),
        unpaid_expenses_total=_sum_money(
            expense.amount
            for expense in active_expenses
            if expense.payment_status != "paid"
        ),
        voided_expenses_count=sum(
            expense.status == "voided" for expense in selected_expenses
        ),
        top_categories=categories[:TOP_RESULTS_LIMIT],
    )


def _build_supplier_totals(
    active_purchases: list[Purchase],
) -> list[ManagementSupplierTotal]:
    totals: defaultdict[int, Decimal] = defaultdict(lambda: MONEY_ZERO)
    names: dict[int, str] = {}
    for purchase in active_purchases:
        totals[purchase.supplier_id] += purchase.total_amount
        names[purchase.supplier_id] = purchase.supplier.name
    rows = [
        ManagementSupplierTotal(
            supplier_id=supplier_id,
            supplier_name=names[supplier_id],
            total_amount=_money(total),
        )
        for supplier_id, total in totals.items()
    ]
    rows.sort(
        key=lambda item: (
            -item.total_amount,
            item.supplier_name.casefold(),
            item.supplier_id,
        )
    )
    return rows


def _build_purchases_summary(
    selected_purchases: list[Purchase],
    active_purchases: list[Purchase],
    supplier_totals: list[ManagementSupplierTotal],
) -> ManagementPurchasesSummary:
    return ManagementPurchasesSummary(
        purchases_total=_sum_money(
            purchase.total_amount for purchase in active_purchases
        ),
        active_purchases_count=len(active_purchases),
        voided_purchases_count=sum(
            purchase.status == "voided" for purchase in selected_purchases
        ),
        unpaid_purchases_total=_sum_money(
            purchase.total_amount
            for purchase in active_purchases
            if purchase.payment_status != "paid"
        ),
        paid_purchases_total=_sum_money(
            purchase.total_amount
            for purchase in active_purchases
            if purchase.payment_status == "paid"
        ),
        top_suppliers=supplier_totals[:TOP_RESULTS_LIMIT],
    )


def _build_production_summary(
    db: Session,
    active_batches: list[ProductionBatch],
    active_consumptions: list[ProductionMaterialConsumption],
) -> ManagementProductionSummary:
    active_batch_ids = [batch.id for batch in active_batches]
    applied_count = 0
    if active_batch_ids:
        applied_count = len(
            list(
                db.scalars(
                    select(ProductionInventoryApplication.id).where(
                        ProductionInventoryApplication.production_batch_id.in_(
                            active_batch_ids
                        ),
                        ProductionInventoryApplication.status == "active",
                    )
                )
            )
        )
    return ManagementProductionSummary(
        production_batches_count=len(active_batches),
        production_items_total_quantity=_sum_quantities(
            item.quantity_produced
            for batch in active_batches
            for item in batch.items
        ),
        production_waste_total_quantity=_sum_quantities(
            item.quantity_waste
            for batch in active_batches
            for item in batch.items
        ),
        production_applied_to_inventory_count=applied_count,
        material_consumptions_count=len(active_consumptions),
        material_consumptions_total_cost=_sum_money(
            consumption.total_material_cost
            for consumption in active_consumptions
        ),
    )


def _build_inventory_summary(db: Session) -> ManagementInventorySummary:
    active_locations = list(
        db.scalars(
            select(InventoryLocation)
            .where(InventoryLocation.is_active.is_(True))
            .order_by(InventoryLocation.id)
        )
    )
    active_products = list(
        db.scalars(
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.name, Product.id)
        )
    )
    active_location_ids = {location.id for location in active_locations}
    active_product_ids = {product.id for product in active_products}
    stocks = list(
        db.scalars(
            select(InventoryStock).where(
                InventoryStock.location_id.in_(active_location_ids),
                InventoryStock.product_id.in_(active_product_ids),
            )
        )
    ) if active_location_ids and active_product_ids else []
    totals: defaultdict[int, Decimal] = defaultdict(lambda: QUANTITY_ZERO)
    for stock in stocks:
        totals[stock.product_id] += stock.quantity_on_hand
    low_stock_items = [
        ManagementLowStockItem(
            product_id=product.id,
            product_sku=product.sku,
            product_name=product.name,
            total_stock_quantity=_quantity(totals[product.id]),
            alert_threshold=LOW_STOCK_THRESHOLD,
        )
        for product in active_products
        if totals[product.id] <= LOW_STOCK_THRESHOLD
    ]
    low_stock_items.sort(
        key=lambda item: (
            item.total_stock_quantity,
            item.product_name.casefold(),
            item.product_id,
        )
    )
    return ManagementInventorySummary(
        active_locations_count=len(active_locations),
        active_products_with_stock_count=sum(
            totals[product.id] > QUANTITY_ZERO for product in active_products
        ),
        total_stock_quantity=_sum_quantities(totals.values()),
        low_stock_items=low_stock_items,
    )


def _build_routes_summary(
    selected_loads: list[RouteLoad],
    selected_returns: list[RouteReturn],
    active_closures: list[RouteClosure],
    selected_receipts: list[RouteCashReceipt],
) -> ManagementRoutesSummary:
    active_receipts = [
        receipt for receipt in selected_receipts if receipt.status == "active"
    ]
    return ManagementRoutesSummary(
        route_loads_count=sum(load.status == "active" for load in selected_loads),
        route_returns_count=sum(
            route_return.status == "active" for route_return in selected_returns
        ),
        route_closures_count=len(active_closures),
        route_expected_cash_total=_sum_money(
            closure.expected_cash_total for closure in active_closures
        ),
        route_delivered_cash_total=_sum_money(
            closure.delivered_cash_total for closure in active_closures
        ),
        route_difference_total=_sum_money(
            closure.difference_amount for closure in active_closures
        ),
        route_cash_receipts_total=_sum_money(
            receipt.received_amount for receipt in active_receipts
        ),
    )


def _build_payroll_summary(
    selected_payroll_runs: list[PayrollRun],
) -> ManagementPayrollSummary:
    finalized_runs = [
        payroll_run
        for payroll_run in selected_payroll_runs
        if payroll_run.status in {"approved", "paid"}
    ]
    return ManagementPayrollSummary(
        payroll_runs_count=len(finalized_runs),
        gross_pay_total=_sum_money(run.gross_total for run in finalized_runs),
        deductions_total=_sum_money(
            run.total_deductions for run in finalized_runs
        ),
        net_pay_total=_sum_money(run.net_pay_total for run in finalized_runs),
        voided_payroll_runs_count=sum(
            run.status == "cancelled" for run in selected_payroll_runs
        ),
    )


def _build_charts(
    *,
    active_sales: list[Sale],
    active_payments: list[CreditPayment],
    cash_summaries: dict,
    active_expenses: list[OperatingExpense],
    selected_sessions: list,
    active_batches: list[ProductionBatch],
    supplier_totals: list[ManagementSupplierTotal],
) -> ManagementCharts:
    daily_sales_values: defaultdict[date, dict[str, Decimal]] = defaultdict(
        lambda: {
            "cash_sales_total": MONEY_ZERO,
            "credit_sales_total": MONEY_ZERO,
            "payments_total": MONEY_ZERO,
        }
    )
    for sale in active_sales:
        key = (
            "cash_sales_total"
            if sale.sale_type == "cash"
            else "credit_sales_total"
        )
        daily_sales_values[sale.sale_date][key] += sale.total_amount
    for payment in active_payments:
        daily_sales_values[payment.payment_date]["payments_total"] += payment.amount

    cash_expenses_by_date: dict[date, Decimal] = {
        cash_session.session_date: cash_summaries[
            cash_session.session_date
        ].total_post_count_expenses
        for cash_session in selected_sessions
    }
    operating_expenses_by_date: defaultdict[date, Decimal] = defaultdict(
        lambda: MONEY_ZERO
    )
    for expense in active_expenses:
        operating_expenses_by_date[expense.expense_date] += expense.amount

    products: dict[int, dict[str, str | Decimal]] = {}
    for batch in active_batches:
        for item in batch.items:
            product = products.setdefault(
                item.product_id,
                {
                    "name": item.product_name_snapshot,
                    "quantity": QUANTITY_ZERO,
                },
            )
            product["name"] = item.product_name_snapshot
            product["quantity"] = (
                Decimal(product["quantity"]) + item.quantity_produced
            )
    production_rows = [
        ManagementProductionProductPoint(
            product_id=product_id,
            product_name=str(values["name"]),
            quantity_produced=_quantity(Decimal(values["quantity"])),
        )
        for product_id, values in products.items()
    ]
    production_rows.sort(
        key=lambda item: (
            -item.quantity_produced,
            item.product_name.casefold(),
            item.product_id,
        )
    )

    return ManagementCharts(
        daily_sales=[
            ManagementDailySalesPoint(
                date=chart_date,
                cash_sales_total=_money(values["cash_sales_total"]),
                credit_sales_total=_money(values["credit_sales_total"]),
                payments_total=_money(values["payments_total"]),
            )
            for chart_date, values in sorted(daily_sales_values.items())
        ],
        daily_cash=[
            ManagementDailyCashPoint(
                date=chart_date,
                cash_total_counted=_money(summary.total_counted),
                cash_final_total=_money(summary.final_total),
            )
            for chart_date, summary in sorted(cash_summaries.items())
        ],
        daily_expenses=[
            ManagementDailyExpensesPoint(
                date=chart_date,
                operating_expenses_total=_money(
                    operating_expenses_by_date[chart_date]
                ),
                cash_expenses_total=_money(cash_expenses_by_date.get(
                    chart_date,
                    MONEY_ZERO,
                )),
            )
            for chart_date in sorted(
                set(operating_expenses_by_date) | set(cash_expenses_by_date)
            )
        ],
        production_by_product=production_rows,
        purchases_by_supplier=supplier_totals,
    )


def _build_alerts(
    *,
    cash: ManagementCashSummary,
    receivables: ManagementReceivablesSummary,
    inventory: ManagementInventorySummary,
    active_closures: list[RouteClosure],
    active_expenses: list[OperatingExpense],
    active_purchases: list[Purchase],
    payroll: ManagementPayrollSummary,
) -> list[ManagementAlert]:
    alerts: list[ManagementAlert] = []
    _append_warning(
        alerts,
        count=cash.open_cash_sessions_count,
        title="Cuadres abiertos",
        message=(
            f"Existen {cash.open_cash_sessions_count} cuadres abiertos "
            "en el período."
        ),
    )
    _append_warning(
        alerts,
        count=sum(
            closure.difference_amount < MONEY_ZERO
            for closure in active_closures
        ),
        title="Diferencias negativas en ruta",
        message="Existen cierres de ruta con faltantes en el período.",
    )
    _append_warning(
        alerts,
        count=len(inventory.low_stock_items),
        title="Stock bajo",
        message=(
            "Hay productos con stock total igual o menor a 5. "
            "Esta es una alerta básica, no un mínimo oficial."
        ),
    )
    _append_warning(
        alerts,
        count=receivables.overdue_customers_count,
        title="Cartera vencida",
        message="Hay clientes con saldos vencidos y pendientes de cobro.",
    )
    unpaid_expenses_count = sum(
        expense.payment_status != "paid" for expense in active_expenses
    )
    _append_warning(
        alerts,
        count=unpaid_expenses_count,
        title="Gastos operativos pendientes",
        message=(
            "Existen gastos operativos no pagados o parcialmente pagados "
            "en el período."
        ),
    )
    unpaid_purchases_count = sum(
        purchase.payment_status != "paid" for purchase in active_purchases
    )
    _append_warning(
        alerts,
        count=unpaid_purchases_count,
        title="Compras pendientes",
        message=(
            "Existen compras no pagadas o parcialmente pagadas en el período."
        ),
    )
    if payroll.payroll_runs_count:
        alerts.append(
            ManagementAlert(
                type="info",
                title="Nómina calculada",
                message=(
                    "Hay roles aprobados o pagados en el período. Consulta "
                    "nómina para revisar su estado y auditoría."
                ),
                count=payroll.payroll_runs_count,
            )
        )
    return alerts


def _append_warning(
    alerts: list[ManagementAlert],
    *,
    count: int,
    title: str,
    message: str,
) -> None:
    if count <= 0:
        return
    alerts.append(
        ManagementAlert(
            type="warning",
            title=title,
            message=message,
            count=count,
        )
    )


def _sum_money(values: Iterable[Decimal]) -> Decimal:
    return _money(sum(values, MONEY_ZERO))


def _sum_quantities(values: Iterable[Decimal]) -> Decimal:
    return _quantity(sum(values, QUANTITY_ZERO))


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def _quantity(value: Decimal) -> Decimal:
    return value.quantize(QUANTITY_QUANTUM, rounding=ROUND_HALF_UP)

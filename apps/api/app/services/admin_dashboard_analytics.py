from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.credit_payment import CreditPayment
from app.models.operating_expense import OperatingExpense
from app.models.sale import Sale
from app.models.simple_route import (
    SimpleRouteCollection,
    SimpleRouteSale,
    SimpleRouteSheet,
)
from app.schemas.admin_dashboard_analytics import (
    AdminBestSalesDay,
    AdminDailySalesPoint,
    AdminDashboardAnalytics,
    AdminSalesMixPoint,
    AdminSimpleRouteDailySalesPoint,
    AdminSimpleRouteRanking,
    AdminTopCustomer,
)
from app.services.simple_routes import get_analytics as get_simple_route_analytics

MONEY_ZERO = Decimal("0.00")
MONEY_QUANTUM = Decimal("0.01")
PERCENT_QUANTUM = Decimal("0.01")
TOP_CUSTOMERS_LIMIT = 5


def get_admin_dashboard_analytics(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> AdminDashboardAnalytics:
    period_start, period_end = _resolve_period(start_date, end_date)
    active_sales = list(
        db.scalars(
            select(Sale)
            .where(
                Sale.sale_date >= period_start,
                Sale.sale_date <= period_end,
                Sale.status == "active",
            )
            .order_by(Sale.sale_date, Sale.id)
        )
    )
    active_payments = list(
        db.scalars(
            select(CreditPayment).where(
                CreditPayment.payment_date >= period_start,
                CreditPayment.payment_date <= period_end,
                CreditPayment.status == "active",
            )
        )
    )
    active_expenses = list(
        db.scalars(
            select(OperatingExpense).where(
                OperatingExpense.expense_date >= period_start,
                OperatingExpense.expense_date <= period_end,
                OperatingExpense.status == "active",
            )
        )
    )

    cash_total = _sum_money(
        sale.total_amount for sale in active_sales if sale.sale_type == "cash"
    )
    credit_total = _sum_money(
        sale.total_amount for sale in active_sales if sale.sale_type == "credit"
    )
    official_sales_total = _money(cash_total + credit_total)
    official_collections_total = _sum_money(
        payment.amount for payment in active_payments
    )
    official_pending_total = _sum_money(
        sale.balance_amount
        for sale in active_sales
        if sale.sale_type == "credit"
    )
    route_analytics = get_simple_route_analytics(db, period_start, period_end)
    active_route_sales = _get_active_route_sales(
        db,
        period_start=period_start,
        period_end=period_end,
    )
    route_cash_sales_total = _sum_money(
        sale.total_amount
        for sale in active_route_sales
        if sale.sale_type == "cash"
    )
    route_credit_sales_total = _sum_money(
        sale.total_amount
        for sale in active_route_sales
        if sale.sale_type == "credit"
    )
    route_partial_sales_total = _sum_money(
        sale.total_amount
        for sale in active_route_sales
        if sale.sale_type == "partial"
    )
    route_paid_total = _sum_money(
        sale.paid_amount for sale in active_route_sales
    )
    route_pending_total = _get_route_pending_total(db, active_route_sales)
    route_collections_total = _money(
        route_analytics.total_collected - route_analytics.total_cash_sales
    )
    total_sales_with_routes = _money(
        official_sales_total + route_analytics.total_route_sales
    )
    daily_sales = _build_daily_sales(active_sales)
    top_customers = _build_top_customers(active_sales)
    period_days = (period_end - period_start).days + 1
    best_sales_day = (
        max(daily_sales, key=lambda item: item.total_sales_amount)
        if daily_sales
        else None
    )

    return AdminDashboardAnalytics(
        period_start=period_start,
        period_end=period_end,
        official_sales_amount=official_sales_total,
        official_cash_sales_amount=cash_total,
        official_credit_sales_amount=credit_total,
        simple_route_sales_amount=route_analytics.total_route_sales,
        total_sales_with_routes_amount=total_sales_with_routes,
        official_credit_collections_amount=official_collections_total,
        official_credit_pending_amount=official_pending_total,
        simple_route_cash_sales_amount=route_cash_sales_total,
        simple_route_credit_sales_amount=route_credit_sales_total,
        simple_route_partial_sales_amount=route_partial_sales_total,
        simple_route_paid_amount=route_paid_total,
        simple_route_pending_amount=route_pending_total,
        simple_route_collections_amount=route_collections_total,
        simple_route_expenses_amount=route_analytics.total_expenses,
        simple_route_expected_cash_amount=route_analytics.total_expected_cash,
        simple_route_cash_delivered_amount=route_analytics.total_delivered_cash,
        simple_route_cash_difference_amount=route_analytics.total_difference,
        simple_route_best_day=(
            AdminBestSalesDay(
                date=route_analytics.best_sales_day.route_date,
                amount=route_analytics.best_sales_day.total,
            )
            if route_analytics.best_sales_day is not None
            else None
        ),
        simple_route_daily_sales=[
            AdminSimpleRouteDailySalesPoint(
                date=item.route_date,
                amount=item.total,
            )
            for item in route_analytics.daily_trend
        ],
        simple_route_top_routes=[
            AdminSimpleRouteRanking(
                label=item.label,
                amount=item.total,
                count=item.count,
            )
            for item in route_analytics.top_routes
        ],
        simple_route_top_sellers=[
            AdminSimpleRouteRanking(
                label=item.label,
                amount=item.total,
                count=item.count,
            )
            for item in route_analytics.top_sellers
        ],
        simple_route_sheets_count=route_analytics.routes_count,
        simple_route_sheets_with_difference=len(
            route_analytics.routes_with_differences
        ),
        total_sales_amount=official_sales_total,
        cash_sales_amount=cash_total,
        credit_sales_amount=credit_total,
        collections_amount=official_collections_total,
        pending_credit_amount=official_pending_total,
        expenses_amount=_sum_money(
            expense.amount for expense in active_expenses
        ),
        net_amount=None,
        net_amount_note=(
            "No se calcula un neto: ventas registradas, cobros y gastos no "
            "representan la misma base de efectivo."
        ),
        best_sales_day=(
            AdminBestSalesDay(
                date=best_sales_day.date,
                amount=best_sales_day.total_sales_amount,
            )
            if best_sales_day is not None
            else None
        ),
        average_daily_sales=_money(official_sales_total / period_days),
        customers_served_count=len(
            {
                sale.customer_id
                for sale in active_sales
                if sale.customer_id is not None
            }
        ),
        top_customers=top_customers,
        daily_sales=daily_sales,
        sales_mix=_build_sales_mix(
            cash_total,
            credit_total,
            official_sales_total,
        ),
    )


def _get_active_route_sales(
    db: Session,
    *,
    period_start: date,
    period_end: date,
) -> list[SimpleRouteSale]:
    return list(
        db.scalars(
            select(SimpleRouteSale)
            .join(
                SimpleRouteSheet,
                SimpleRouteSheet.id == SimpleRouteSale.route_sheet_id,
            )
            .where(
                SimpleRouteSheet.route_date >= period_start,
                SimpleRouteSheet.route_date <= period_end,
                SimpleRouteSheet.status != "cancelled",
                SimpleRouteSale.status == "active",
            )
            .order_by(SimpleRouteSale.sale_date, SimpleRouteSale.id)
        )
    )


def _get_route_pending_total(
    db: Session,
    active_route_sales: list[SimpleRouteSale],
) -> Decimal:
    sale_ids = [sale.id for sale in active_route_sales]
    if not sale_ids:
        return MONEY_ZERO
    collections_by_sale: defaultdict[int, Decimal] = defaultdict(
        lambda: MONEY_ZERO
    )
    rows = db.execute(
        select(
            SimpleRouteCollection.simple_route_sale_id,
            SimpleRouteCollection.amount,
        )
        .join(
            SimpleRouteSheet,
            SimpleRouteSheet.id == SimpleRouteCollection.route_sheet_id,
        )
        .where(
            SimpleRouteCollection.simple_route_sale_id.in_(sale_ids),
            SimpleRouteSheet.status != "cancelled",
        )
    )
    for sale_id, amount in rows:
        if sale_id is not None:
            collections_by_sale[sale_id] += amount
    return _sum_money(
        max(MONEY_ZERO, sale.pending_amount - collections_by_sale[sale.id])
        for sale in active_route_sales
    )


def _resolve_period(
    start_date: date | None,
    end_date: date | None,
) -> tuple[date, date]:
    if start_date is None and end_date is None:
        today = date.today()
        return today.replace(day=1), today
    if start_date is None:
        start_date = end_date
    if end_date is None:
        end_date = start_date
    if start_date is None or end_date is None:
        raise ValueError("No se pudo resolver el rango de fechas.")
    if end_date < start_date:
        raise ValueError("La fecha hasta no puede ser menor que la fecha desde.")
    return start_date, end_date


def _build_daily_sales(active_sales: list[Sale]) -> list[AdminDailySalesPoint]:
    totals: defaultdict[date, dict[str, Decimal]] = defaultdict(
        lambda: {"cash": MONEY_ZERO, "credit": MONEY_ZERO}
    )
    for sale in active_sales:
        totals[sale.sale_date][sale.sale_type] += sale.total_amount
    return [
        AdminDailySalesPoint(
            date=sale_date,
            cash_sales_amount=_money(values["cash"]),
            credit_sales_amount=_money(values["credit"]),
            total_sales_amount=_money(values["cash"] + values["credit"]),
        )
        for sale_date, values in sorted(totals.items())
    ]


def _build_top_customers(active_sales: list[Sale]) -> list[AdminTopCustomer]:
    totals: defaultdict[int, Decimal] = defaultdict(lambda: MONEY_ZERO)
    counts: defaultdict[int, int] = defaultdict(int)
    names: dict[int, str] = {}
    for sale in active_sales:
        if sale.customer_id is None:
            continue
        totals[sale.customer_id] += sale.total_amount
        counts[sale.customer_id] += 1
        names[sale.customer_id] = sale.customer_name_snapshot
    rows = [
        AdminTopCustomer(
            customer_id=customer_id,
            customer_name=names[customer_id],
            sales_count=counts[customer_id],
            total_amount=_money(amount),
        )
        for customer_id, amount in totals.items()
    ]
    rows.sort(
        key=lambda item: (
            -item.total_amount,
            item.customer_name.casefold(),
            item.customer_id,
        )
    )
    return rows[:TOP_CUSTOMERS_LIMIT]


def _build_sales_mix(
    cash_total: Decimal,
    credit_total: Decimal,
    total_sales: Decimal,
) -> list[AdminSalesMixPoint]:
    def percentage(amount: Decimal) -> Decimal:
        if total_sales == MONEY_ZERO:
            return MONEY_ZERO
        return (amount * Decimal("100") / total_sales).quantize(
            PERCENT_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

    return [
        AdminSalesMixPoint(
            sale_type="cash",
            amount=cash_total,
            percentage=percentage(cash_total),
        ),
        AdminSalesMixPoint(
            sale_type="credit",
            amount=credit_total,
            percentage=percentage(credit_total),
        ),
    ]


def _sum_money(values) -> Decimal:
    return _money(sum(values, MONEY_ZERO))


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)

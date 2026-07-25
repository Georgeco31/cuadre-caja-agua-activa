from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class ManagementDashboardPeriod(BaseModel):
    date_from: date
    date_to: date


class ManagementCashSummary(BaseModel):
    cash_sessions_count: int
    cash_total_counted: Decimal
    cash_total_expenses_after_count: Decimal
    cash_final_total: Decimal
    open_cash_sessions_count: int
    closed_cash_sessions_count: int


class ManagementSalesSummary(BaseModel):
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    sales_total: Decimal
    active_sales_count: int
    voided_sales_count: int
    average_sale_amount: Decimal


class ManagementReceivablesSummary(BaseModel):
    credit_sales_total: Decimal
    payments_total: Decimal
    pending_balance_total: Decimal
    customers_with_balance_count: int
    overdue_balance_total: Decimal
    overdue_customers_count: int


class ManagementExpenseCategory(BaseModel):
    category_id: int
    category_name: str
    total_amount: Decimal


class ManagementOperatingExpensesSummary(BaseModel):
    operating_expenses_total: Decimal
    paid_expenses_total: Decimal
    unpaid_expenses_total: Decimal
    voided_expenses_count: int
    top_categories: list[ManagementExpenseCategory]


class ManagementSupplierTotal(BaseModel):
    supplier_id: int
    supplier_name: str
    total_amount: Decimal


class ManagementPurchasesSummary(BaseModel):
    purchases_total: Decimal
    active_purchases_count: int
    voided_purchases_count: int
    unpaid_purchases_total: Decimal
    paid_purchases_total: Decimal
    top_suppliers: list[ManagementSupplierTotal]


class ManagementProductionSummary(BaseModel):
    production_batches_count: int
    production_items_total_quantity: Decimal
    production_waste_total_quantity: Decimal
    production_applied_to_inventory_count: int
    material_consumptions_count: int
    material_consumptions_total_cost: Decimal


class ManagementLowStockItem(BaseModel):
    product_id: int
    product_sku: str | None
    product_name: str
    total_stock_quantity: Decimal
    alert_threshold: Decimal


class ManagementInventorySummary(BaseModel):
    active_locations_count: int
    active_products_with_stock_count: int
    total_stock_quantity: Decimal
    low_stock_items: list[ManagementLowStockItem]


class ManagementRoutesSummary(BaseModel):
    route_loads_count: int
    route_returns_count: int
    route_closures_count: int
    route_expected_cash_total: Decimal
    route_delivered_cash_total: Decimal
    route_difference_total: Decimal
    route_cash_receipts_total: Decimal


class ManagementPayrollSummary(BaseModel):
    payroll_runs_count: int
    gross_pay_total: Decimal
    deductions_total: Decimal
    net_pay_total: Decimal
    voided_payroll_runs_count: int


class ManagementDailySalesPoint(BaseModel):
    date: date
    cash_sales_total: Decimal
    credit_sales_total: Decimal
    payments_total: Decimal


class ManagementDailyCashPoint(BaseModel):
    date: date
    cash_total_counted: Decimal
    cash_final_total: Decimal


class ManagementDailyExpensesPoint(BaseModel):
    date: date
    operating_expenses_total: Decimal
    cash_expenses_total: Decimal


class ManagementProductionProductPoint(BaseModel):
    product_id: int
    product_name: str
    quantity_produced: Decimal


class ManagementCharts(BaseModel):
    daily_sales: list[ManagementDailySalesPoint]
    daily_cash: list[ManagementDailyCashPoint]
    daily_expenses: list[ManagementDailyExpensesPoint]
    production_by_product: list[ManagementProductionProductPoint]
    purchases_by_supplier: list[ManagementSupplierTotal]


class ManagementAlert(BaseModel):
    type: Literal["info", "warning"]
    title: str
    message: str
    count: int


class ManagementDashboard(BaseModel):
    period: ManagementDashboardPeriod
    cash: ManagementCashSummary
    sales: ManagementSalesSummary
    receivables: ManagementReceivablesSummary
    operating_expenses: ManagementOperatingExpensesSummary
    purchases: ManagementPurchasesSummary
    production: ManagementProductionSummary
    inventory: ManagementInventorySummary
    routes: ManagementRoutesSummary
    payroll: ManagementPayrollSummary
    charts: ManagementCharts
    alerts: list[ManagementAlert]

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    cash_sessions,
    credit_payments,
    customers,
    delivery_routes,
    denominations,
    employee_controls,
    employees,
    health,
    inventory,
    operating_expenses,
    payroll,
    pricing,
    products,
    production,
    production_material_consumptions,
    production_recipes,
    purchases,
    receivables,
    reports,
    route_cash_receipts,
    route_loads,
    route_closures,
    route_returns,
    sales,
    suppliers,
    vehicles,
)


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(cash_sessions.router)
api_router.include_router(credit_payments.router)
api_router.include_router(customers.router)
api_router.include_router(delivery_routes.router)
api_router.include_router(denominations.router)
api_router.include_router(employee_controls.router)
api_router.include_router(employees.router)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(inventory.router)
api_router.include_router(operating_expenses.router)
api_router.include_router(payroll.router)
api_router.include_router(payroll.employee_router)
api_router.include_router(pricing.router)
api_router.include_router(products.router)
api_router.include_router(production.router)
api_router.include_router(production_material_consumptions.router)
api_router.include_router(production_recipes.router)
api_router.include_router(purchases.router)
api_router.include_router(receivables.router)
api_router.include_router(reports.router)
api_router.include_router(route_cash_receipts.router)
api_router.include_router(route_loads.router)
api_router.include_router(route_closures.router)
api_router.include_router(route_returns.router)
api_router.include_router(sales.router)
api_router.include_router(suppliers.router)
api_router.include_router(vehicles.router)

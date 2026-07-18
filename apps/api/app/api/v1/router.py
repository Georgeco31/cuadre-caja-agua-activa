from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    cash_sessions,
    customers,
    delivery_routes,
    denominations,
    employees,
    health,
    products,
    reports,
)


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(cash_sessions.router)
api_router.include_router(customers.router)
api_router.include_router(delivery_routes.router)
api_router.include_router(denominations.router)
api_router.include_router(employees.router)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(products.router)
api_router.include_router(reports.router)

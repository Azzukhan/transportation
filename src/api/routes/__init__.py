"""Domain route exports."""

from src.api.routes.auth import router as auth_router
from src.api.routes.companies import router as companies_router
from src.api.routes.driver_cash_handovers import router as driver_cash_handovers_router
from src.api.routes.drivers import router as drivers_router
from src.api.routes.employee_salaries import router as employee_salaries_router
from src.api.routes.health import router as health_router
from src.api.routes.invoices import router as invoices_router
from src.api.routes.public import router as public_router
from src.api.routes.trips import router as trips_router

__all__ = [
    "auth_router",
    "health_router",
    "companies_router",
    "drivers_router",
    "driver_cash_handovers_router",
    "employee_salaries_router",
    "trips_router",
    "invoices_router",
    "public_router",
]

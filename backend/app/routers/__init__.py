from .auth import router as auth_router
from .users import router as users_router
from .zones import router as zones_router
from .bookings import router as bookings_router
from .admin import router as admin_router
from .achievements import router as achievements_router

__all__ = [
    "auth_router",
    "users_router",
    "zones_router",
    "bookings_router",
    "admin_router",
    "achievements_router"
]

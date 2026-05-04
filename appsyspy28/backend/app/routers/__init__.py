from .auth import router as auth_router
from .classes import router as classes_router
from .bookings import router as bookings_router
from .checkin import router as checkin_router
from .private_booking import router as private_router
from .cards import router as cards_router
from .admin import router as admin_router

__all__ = [
    "auth_router", "classes_router", "bookings_router",
    "checkin_router", "private_router", "cards_router", "admin_router"
]

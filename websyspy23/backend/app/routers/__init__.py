from .card import router as card_router
from .course import router as course_router
from .member import router as member_router
from .venue import router as venue_router
from .schedule import router as schedule_router

__all__ = [
    "card_router",
    "course_router",
    "member_router",
    "venue_router",
    "schedule_router"
]

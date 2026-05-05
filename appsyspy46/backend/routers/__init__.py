from .auth import router as auth_router
from .orders import router as orders_router
from .users import router as users_router
from .route import router as route_router
from .test import router as test_router

__all__ = ["auth_router", "orders_router", "users_router", "route_router", "test_router"]

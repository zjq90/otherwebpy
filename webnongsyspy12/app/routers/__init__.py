from .device import router as device_router
from .environment import router as environment_router
from .crop import router as crop_router
from .growth_record import router as growth_record_router
from .test import router as test_router

__all__ = ["device_router", "environment_router", "crop_router", "growth_record_router", "test_router"]

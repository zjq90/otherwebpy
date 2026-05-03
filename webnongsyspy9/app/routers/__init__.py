from .farm import router as farm_router
from .plot import router as plot_router
from .crop import router as crop_router
from .staff import router as staff_router

__all__ = ["farm_router", "plot_router", "crop_router", "staff_router"]

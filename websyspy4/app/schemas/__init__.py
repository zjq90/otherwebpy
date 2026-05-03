"""
Pydantic模型模块
用于API请求和响应的数据验证
"""

from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate
from app.schemas.notification import NotificationCreate, NotificationResponse

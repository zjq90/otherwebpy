"""
通用数据验证模型
定义API通用的响应结构和基础模型
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

# 定义泛型类型
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    通用API响应模型
    用于统一所有API的响应格式
    """
    code: int = Field(default=200, description="响应状态码，200表示成功")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": None,
                "timestamp": "2024-01-01T00:00:00"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    用于列表数据的分页响应
    """
    items: list[T] = Field(description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    令牌模型
    用于登录成功后返回的访问令牌
    """
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="令牌有效期（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class TokenData(BaseModel):
    """
    令牌数据模型
    用于存储从JWT令牌中解析出的用户信息
    """
    user_id: Optional[int] = Field(default=None, description="用户ID")
    username: Optional[str] = Field(default=None, description="用户名")
    role: Optional[str] = Field(default=None, description="用户角色")

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """
    消息响应模型
    用于简单的操作结果响应
    """
    message: str = Field(description="消息内容")
    success: bool = Field(default=True, description="是否成功")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功",
                "success": True
            }
        }


class LocationPoint(BaseModel):
    """
    地理位置点模型
    用于表示经纬度坐标
    """
    latitude: float = Field(description="纬度")
    longitude: float = Field(description="经度")
    address: Optional[str] = Field(default=None, description="地址描述")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": "北京市"
            }
        }

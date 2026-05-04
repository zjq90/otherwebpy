"""
通用Pydantic模型
定义API响应的通用格式
"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    通用API响应模型
    用于统一所有API的响应格式
    """
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        from_attributes = True


class SuccessResponse(ApiResponse[T]):
    """
    成功响应模型
    用于明确表示操作成功的响应
    """
    code: int = Field(default=200, description="成功状态码")


class ErrorResponse(BaseModel):
    """
    错误响应模型
    用于明确表示操作失败的响应
    """
    code: int = Field(default=400, description="错误状态码")
    message: str = Field(description="错误消息")
    detail: Optional[Any] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    用于列表查询的分页数据
    """
    items: list[T] = Field(description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页数量")
    total_pages: int = Field(description="总页数")
    
    class Config:
        from_attributes = True


class PageParams(BaseModel):
    """
    分页查询参数
    用于接收前端的分页请求参数
    """
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量，最大100")
    
    @property
    def offset(self) -> int:
        """
        计算SQL查询的offset
        """
        return (self.page - 1) * self.page_size

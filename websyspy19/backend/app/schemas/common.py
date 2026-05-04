"""
通用数据模式
定义通用的API响应模型，用于统一响应格式
"""

from typing import Any, Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field


# 定义泛型类型变量
T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型
    用于封装所有API的响应数据，保持统一的响应格�?
    """
    
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": {"key": "value"}
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    用于封装分页查询的响应数�?
    """
    
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[List[T]] = Field(default=None, description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页数量")
    total_pages: int = Field(default=0, description="总页�?)
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": [{"id": 1, "name": "示例数据"}],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10
            }
        }


class ErrorResponse(BaseModel):
    """
    错误响应模型
    用于封装错误响应数据
    """
    
    code: int = Field(default=500, description="错误状态码")
    message: str = Field(default="操作失败", description="错误消息")
    detail: Optional[Any] = Field(default=None, description="错误详情")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "参数错误",
                "detail": "用户名不能为�?
            }
        }


class SuccessResponse(BaseModel):
    """
    成功响应模型
    用于简单的成功操作响应，不返回数据
    """
    
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="操作成功", description="响应消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "删除成功"
            }
        }

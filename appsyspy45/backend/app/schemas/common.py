"""
通用响应模型
定义统一的API响应格式
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from datetime import datetime

# 通用类型变量
T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型
    """
    code: int = 200
    message: str = "成功"
    data: Optional[T] = None
    timestamp: datetime = datetime.now()
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "成功",
                "data": {"key": "value"},
                "timestamp": "2024-01-01T00:00:00"
            }
        }


class PageResponseModel(BaseModel, Generic[T]):
    """
    分页响应模型
    """
    code: int = 200
    message: str = "成功"
    data: Optional[dict] = None  # 包含 list, total, page, page_size
    timestamp: datetime = datetime.now()


def success(data: T = None, message: str = "成功") -> ResponseModel[T]:
    """
    成功响应
    """
    return ResponseModel(code=200, message=message, data=data)


def success_page(
    items: List[T], 
    total: int, 
    page: int = 1, 
    page_size: int = 10,
    message: str = "成功"
) -> PageResponseModel[T]:
    """
    分页成功响应
    """
    return PageResponseModel(
        code=200,
        message=message,
        data={
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


def error(code: int = 400, message: str = "错误", data: T = None) -> ResponseModel[T]:
    """
    错误响应
    """
    return ResponseModel(code=code, message=message, data=data)


# 常见的错误码和消息
ERROR_CODES = {
    400: "请求参数错误",
    401: "未授权，请先登录",
    403: "禁止访问",
    404: "资源不存在",
    500: "服务器内部错误",
    1001: "用户不存在",
    1002: "密码错误",
    1003: "手机号已注册",
    1004: "验证码错误或已过期",
    1005: "用户已禁用",
    2001: "订单不存在",
    2002: "订单状态不支持此操作",
    2003: "预约时间已过",
    3001: "积分不足",
    3002: "商品库存不足",
    3003: "兑换订单不存在",
}

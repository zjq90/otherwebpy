"""
操作日志数据模式
定义操作日志相关的Pydantic模型，用于数据验证和序列�?
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class OperationLogBase(BaseModel):
    """
    操作日志基础模型
    包含操作日志的基本信息字�?
    """
    
    operation_type: str = Field(..., max_length=50, description="操作类型")
    operation_name: str = Field(..., max_length=100, description="操作名称")
    operation_desc: Optional[str] = Field(None, description="操作详细描述")
    request_method: Optional[str] = Field(None, max_length=10, description="请求方法")
    request_url: Optional[str] = Field(None, max_length=500, description="请求URL")
    request_params: Optional[str] = Field(None, description="请求参数")
    request_ip: Optional[str] = Field(None, max_length=50, description="请求IP地址")
    user_agent: Optional[str] = Field(None, max_length=500, description="用户代理信息")
    response_status: Optional[int] = Field(None, description="响应状态码")
    response_data: Optional[str] = Field(None, description="响应数据")
    user_id: Optional[int] = Field(None, description="操作用户ID")
    username: Optional[str] = Field(None, max_length=50, description="操作用户�?)
    module: Optional[str] = Field(None, max_length=50, description="所属模�?)
    status: str = Field(default="success", max_length=20, description="操作状�?)
    error_message: Optional[str] = Field(None, description="错误信息")
    duration: Optional[int] = Field(None, description="操作耗时（毫秒）")


class OperationLogCreate(OperationLogBase):
    """
    操作日志创建模型
    用于创建新操作日志时的数据验�?
    """
    
    pass


class OperationLogResponse(OperationLogBase):
    """
    操作日志响应模型
    用于返回操作日志信息给前�?
    """
    
    id: int = Field(..., description="日志ID")
    created_at: datetime = Field(..., description="操作时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "operation_type": "login",
                "operation_name": "用户登录",
                "operation_desc": "用户admin登录系统",
                "request_method": "POST",
                "request_url": "/api/v1/auth/login",
                "request_params": '{"username":"admin"}',
                "request_ip": "127.0.0.1",
                "user_agent": "Mozilla/5.0...",
                "response_status": 200,
                "response_data": '{"code":200,"message":"登录成功"}',
                "user_id": 1,
                "username": "admin",
                "module": "auth",
                "status": "success",
                "error_message": None,
                "duration": 120,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class OperationLogQuery(BaseModel):
    """
    操作日志查询模型
    用于操作日志的分页查询和筛�?
    """
    
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    username: Optional[str] = Field(None, max_length=50, description="操作用户�?)
    operation_type: Optional[str] = Field(None, max_length=50, description="操作类型")
    module: Optional[str] = Field(None, max_length=50, description="所属模�?)
    status: Optional[str] = Field(None, max_length=20, description="操作状�?)
    start_time: Optional[datetime] = Field(None, description="开始时�?)
    end_time: Optional[datetime] = Field(None, description="结束时间")

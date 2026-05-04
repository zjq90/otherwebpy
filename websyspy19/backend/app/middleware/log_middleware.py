"""
日志中间�?
处理操作日志的自动记�?
"""

import json
import time
from typing import Callable, Optional
from fastapi import Request, Response, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db, SessionLocal
from app.crud.operation_log import operation_log_crud
from app.models.user import User
from app.middleware.auth_middleware import get_current_user_optional


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间�?
    自动记录所有HTTP请求的操作日�?
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        中间件核心处理方�?
        
        参数:
            request: HTTP请求对象
            call_next: 下一个处理函�?
        
        返回:
            HTTP响应对象
        """
        # 记录开始时�?
        start_time = time.time()
        
        # 获取请求信息
        request_method = request.method
        request_url = str(request.url.path)
        request_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # 获取请求参数
        request_params = {}
        try:
            # 获取查询参数
            query_params = dict(request.query_params)
            if query_params:
                request_params["query"] = query_params
            
            # 获取路径参数
            path_params = request.path_params
            if path_params:
                request_params["path"] = path_params
        except Exception:
            pass
        
        # 尝试获取请求体（仅针对非文件上传的POST/PUT请求�?
        request_body = None
        content_type = request.headers.get("content-type", "")
        if request_method in ["POST", "PUT", "PATCH"] and "application/json" in content_type:
            try:
                body = await request.json()
                # 隐藏敏感信息（如密码�?
                if "password" in body:
                    body["password"] = "***"
                if "new_password" in body:
                    body["new_password"] = "***"
                request_body = body
            except Exception:
                pass
        
        if request_body:
            request_params["body"] = request_body
        
        # 调用下一个处理函�?
        response = await call_next(request)
        
        # 计算处理时间
        duration = int((time.time() - start_time) * 1000)  # 转换为毫�?
        
        # 获取响应状态码
        response_status = response.status_code
        
        # 决定是否记录日志
        # 只记录API请求，忽略静态资源和文档
        if self._should_log(request_url, request_method):
            # 尝试获取当前用户
            try:
                # 这里我们需要手动创建一个数据库会话来获取用�?
                db = SessionLocal()
                try:
                    # 尝试从请求中获取用户信息
                    # 注意：这里不能直接使用Depends，需要手动处�?
                    user = None
                    auth_header = request.headers.get("authorization", "")
                    if auth_header.startswith("Bearer "):
                        token = auth_header[7:]
                        try:
                            from app.core.security import decode_access_token
                            from app.crud.user import user_crud
                            
                            payload = decode_access_token(token)
                            if payload:
                                user_id = payload.get("sub")
                                if user_id:
                                    user = user_crud.get_by_id(db, int(user_id))
                        except Exception:
                            pass
                    
                    # 确定操作类型和模�?
                    operation_type, module = self._determine_operation_type(
                        request_url, request_method, response_status
                    )
                    
                    # 生成操作名称
                    operation_name = self._generate_operation_name(
                        request_url, request_method, module
                    )
                    
                    # 确定操作状�?
                    status = "success" if response_status < 400 else "failed"
                    
                    # 创建操作日志
                    operation_log_crud.create_simple(
                        db=db,
                        operation_type=operation_type,
                        operation_name=operation_name,
                        operation_desc=f"{request_method} {request_url}",
                        request_method=request_method,
                        request_url=request_url,
                        request_params=json.dumps(request_params, ensure_ascii=False) if request_params else None,
                        request_ip=request_ip,
                        user_agent=user_agent,
                        response_status=response_status,
                        response_data=None,  # 不记录响应数据以避免性能问题
                        user_id=user.id if user else None,
                        username=user.username if user else None,
                        module=module,
                        status=status,
                        error_message=None,
                        duration=duration
                    )
                finally:
                    db.close()
            except Exception as e:
                # 记录日志失败不影响主流程
                print(f"记录操作日志失败: {e}")
        
        return response
    
    def _should_log(self, url: str, method: str) -> bool:
        """
        决定是否应该记录日志
        
        参数:
            url: 请求URL
            method: 请求方法
        
        返回:
            是否记录日志
        """
        # 忽略的路�?
        ignore_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static/",
        ]
        
        # 检查是否是忽略的路�?
        for path in ignore_paths:
            if url.startswith(path):
                return False
        
        # 只记录API请求
        if "/api/" in url:
            return True
        
        return False
    
    def _determine_operation_type(self, url: str, method: str, status_code: int) -> tuple:
        """
        根据URL和方法确定操作类型和模块
        
        参数:
            url: 请求URL
            method: 请求方法
            status_code: 响应状态码
        
        返回:
            (操作类型, 模块)
        """
        # 确定模块
        module = "other"
        if "/auth/" in url or "/login" in url:
            module = "auth"
        elif "/users/" in url:
            module = "user"
        elif "/roles/" in url:
            module = "role"
        elif "/permissions/" in url:
            module = "permission"
        elif "/logs/" in url or "/operation-logs/" in url:
            module = "log"
        elif "/test/" in url:
            module = "test"
        
        # 确定操作类型
        operation_type = "other"
        if "login" in url.lower():
            operation_type = "login"
        elif "logout" in url.lower():
            operation_type = "logout"
        elif method == "GET":
            operation_type = "read"
        elif method == "POST":
            operation_type = "create"
        elif method == "PUT" or method == "PATCH":
            operation_type = "update"
        elif method == "DELETE":
            operation_type = "delete"
        
        return operation_type, module
    
    def _generate_operation_name(self, url: str, method: str, module: str) -> str:
        """
        生成操作名称
        
        参数:
            url: 请求URL
            method: 请求方法
            module: 模块
        
        返回:
            操作名称
        """
        # 登录相关
        if "login" in url.lower():
            return "用户登录"
        if "logout" in url.lower():
            return "用户登出"
        if "current-user" in url.lower() and method == "GET":
            return "获取当前用户信息"
        if "permissions" in url.lower() and "me" in url.lower():
            return "获取当前用户权限"
        
        # 用户管理
        if module == "user":
            if method == "GET" and "/users/" in url and url.count("/") >= 4:
                return "查看用户详情"
            elif method == "GET":
                return "查看用户列表"
            elif method == "POST":
                return "创建用户"
            elif method == "PUT" or method == "PATCH":
                return "更新用户"
            elif method == "DELETE":
                return "删除用户"
        
        # 角色管理
        if module == "role":
            if method == "GET" and "/roles/" in url and url.count("/") >= 4:
                return "查看角色详情"
            elif method == "GET":
                return "查看角色列表"
            elif method == "POST":
                return "创建角色"
            elif method == "PUT" or method == "PATCH":
                return "更新角色"
            elif method == "DELETE":
                return "删除角色"
        
        # 权限管理
        if module == "permission":
            if method == "GET" and "/permissions/" in url and url.count("/") >= 4:
                return "查看权限详情"
            elif method == "GET":
                return "查看权限列表"
            elif method == "POST":
                return "创建权限"
            elif method == "PUT" or method == "PATCH":
                return "更新权限"
            elif method == "DELETE":
                return "删除权限"
        
        # 日志管理
        if module == "log":
            if method == "GET" and "/logs/" in url and url.count("/") >= 4:
                return "查看日志详情"
            elif method == "GET" and "statistics" in url.lower():
                return "获取日志统计"
            elif method == "GET":
                return "查看日志列表"
            elif method == "DELETE":
                return "删除日志"
        
        # 测试功能
        if module == "test":
            if "generate-data" in url.lower():
                return "生成测试数据"
            elif "cleanup" in url.lower():
                return "清理测试数据"
            elif "test-permission" in url.lower():
                return "权限测试"
        
        return f"{method} {url}"


def log_operation(
    operation_type: str,
    operation_name: str,
    module: str = "other",
    operation_desc: str = None,
    request_method: str = None,
    request_url: str = None,
    request_params: str = None,
    request_ip: str = None,
    user_agent: str = None,
    response_status: int = None,
    response_data: str = None,
    status: str = "success",
    error_message: str = None,
    duration: int = None
):
    """
    手动记录操作日志的装饰器/辅助函数
    用于在代码中手动记录特定操作的日�?
    
    参数:
        各种日志字段参数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 这里需要在函数执行后记录日�?
            # 实际使用时需要结合请求上下文
            return func(*args, **kwargs)
        return wrapper
    return decorator

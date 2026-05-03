"""
安全中间件模块
实现IP限流、黑名单拦截、请求频率控制等安全功能
作为FastAPI中间件在请求处理前执行
"""
import time
from typing import Callable, Awaitable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.config import settings
from app.utils.redis_client import RateLimiter, BlacklistCache, redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    限流中间件
    
    在请求进入路由处理前进行限流检查
    支持三级限流: 全局限流 > IP限流 > 用户限流
    """

    def __init__(
            self,
            app,
            global_limit: int = None,
            ip_limit: int = None,
            user_limit: int = None,
            exclude_paths: list = None
    ):
        """
        初始化限流中间件
        
        Args:
            app: FastAPI应用实例
            global_limit: 全局限流数
            ip_limit: IP限流数
            user_limit: 用户限流数
            exclude_paths: 排除限流的路径列表
        """
        super().__init__(app)
        self.global_limit = global_limit or settings.GLOBAL_RATE_LIMIT_PER_SECOND
        self.ip_limit = ip_limit or settings.IP_RATE_LIMIT_PER_SECOND
        self.user_limit = user_limit or settings.USER_RATE_LIMIT_PER_SECOND
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]

    async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Awaitable[JSONResponse]]
    ) -> JSONResponse:
        """
        处理请求的核心方法
        
        1. 检查是否在排除路径
        2. 检查全局限流
        3. 检查IP限流
        4. 通过后继续处理请求
        
        Args:
            request: FastAPI请求对象
            call_next: 下一个处理函数
            
        Returns:
            JSONResponse: 响应对象
        """
        # 获取请求路径
        path = request.url.path

        # 跳过排除路径
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return await call_next(request)

        # 获取客户端IP
        client_ip = self._get_client_ip(request)

        # 1. 检查全局限流
        global_allowed = await RateLimiter.check_global_limit(self.global_limit)
        if not global_allowed:
            logger.warning(f"全局限流触发，拒绝请求: IP={client_ip}, Path={path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "message": "系统繁忙，请稍后重试",
                    "data": None
                }
            )

        # 2. 检查IP限流
        ip_allowed = await RateLimiter.check_ip_limit(client_ip, self.ip_limit)
        if not ip_allowed:
            logger.warning(f"IP限流触发，拒绝请求: IP={client_ip}, Path={path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "message": "请求过于频繁，请稍后重试",
                    "data": None
                }
            )

        # 继续处理请求
        response = await call_next(request)
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """
        获取客户端真实IP地址
        
        优先从X-Forwarded-For或X-Real-IP获取
        否则使用直接连接的IP
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            str: 客户端IP地址
        """
        # 尝试从代理头获取
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # X-Forwarded-For可能包含多个IP，取第一个
            return x_forwarded_for.split(",")[0].strip()

        # 尝试从X-Real-IP获取
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

        # 使用直接连接的IP
        client = request.client
        if client:
            return client.host or "unknown"

        return "unknown"


class BlacklistMiddleware(BaseHTTPMiddleware):
    """
    黑名单中间件
    
    在请求进入路由处理前检查是否在黑名单中
    支持IP黑名单和用户ID黑名单
    """

    def __init__(
            self,
            app,
            exclude_paths: list = None
    ):
        """
        初始化黑名单中间件
        
        Args:
            app: FastAPI应用实例
            exclude_paths: 排除检查的路径列表
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/auth/login",
            "/api/auth/register"
        ]

    async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Awaitable[JSONResponse]]
    ) -> JSONResponse:
        """
        处理请求的核心方法
        
        Args:
            request: FastAPI请求对象
            call_next: 下一个处理函数
            
        Returns:
            JSONResponse: 响应对象
        """
        # 获取请求路径
        path = request.url.path

        # 跳过排除路径
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return await call_next(request)

        # 获取客户端IP
        client_ip = RateLimitMiddleware._get_client_ip(request)

        # 1. 检查IP黑名单
        ip_blacklisted = await BlacklistCache.check_ip_blacklist(client_ip)
        if ip_blacklisted:
            logger.warning(f"IP黑名单拦截: IP={client_ip}, Path={path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "code": 403,
                    "message": "您的访问被拒绝，请联系管理员",
                    "data": None
                }
            )

        # 继续处理请求
        # 用户黑名单检查将在认证后在路由处理中进行
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    记录请求的基本信息和处理时间
    用于监控和调试
    """

    async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Awaitable[JSONResponse]]
    ) -> JSONResponse:
        """
        处理请求的核心方法
        
        Args:
            request: FastAPI请求对象
            call_next: 下一个处理函数
            
        Returns:
            JSONResponse: 响应对象
        """
        # 记录请求开始时间
        start_time = time.time()

        # 获取请求信息
        method = request.method
        path = request.url.path
        client_ip = RateLimitMiddleware._get_client_ip(request)

        # 记录请求开始
        logger.info(f"请求开始: {method} {path} - IP: {client_ip}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = (time.time() - start_time) * 1000

            # 记录请求结果
            status_code = response.status_code
            logger.info(
                f"请求完成: {method} {path} - "
                f"状态码: {status_code} - "
                f"耗时: {process_time:.2f}ms - "
                f"IP: {client_ip}"
            )

            return response

        except Exception as e:
            # 记录异常
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"请求异常: {method} {path} - "
                f"错误: {str(e)} - "
                f"耗时: {process_time:.2f}ms - "
                f"IP: {client_ip}"
            )
            # 重新抛出异常让全局异常处理器处理
            raise

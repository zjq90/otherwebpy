"""
高并发抢单系统 - 主应用入口
FastAPI应用启动文件，包含应用初始化、中间件注册、路由注册等
"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.models.database import init_db, async_session_maker
from app.middlewares.security_middleware import (
    RateLimitMiddleware,
    BlacklistMiddleware,
    RequestLoggingMiddleware
)

# 导入路由
from app.routers import auth
from app.routers import product
from app.routers import order
from app.routers import seckill


# ==================== 生命周期管理 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    处理应用启动和关闭时的资源初始化和释放
    """
    logger.info("=" * 60)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    logger.info("=" * 60)

    # 1. 确保数据目录存在
    data_dir = Path("./data")
    logs_dir = Path("./logs")
    data_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    # 2. 初始化数据库
    logger.info("初始化数据库...")
    try:
        await init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")

    # 3. 预加载黑名单到Redis
    logger.info("预加载黑名单...")
    try:
        from app.utils.redis_client import BlacklistCache
        from sqlalchemy import select
        from app.models.models import Blacklist as DBBlacklist

        async with async_session_maker() as session:
            stmt = select(DBBlacklist).where(
                DBBlacklist.is_active == True,
                (DBBlacklist.expire_at == None) | (DBBlacklist.expire_at > datetime.utcnow())
            )
            result = await session.execute(stmt)
            blacklist_items = result.scalars().all()

            if blacklist_items:
                items = [
                    {"target_type": item.target_type, "target_value": item.target_value}
                    for item in blacklist_items
                ]
                await BlacklistCache.batch_load_blacklist(items)
                logger.info(f"已加载 {len(items)} 条黑名单记录")
            else:
                logger.info("黑名单为空，跳过加载")

    except Exception as e:
        logger.warning(f"黑名单预加载失败(可能Redis未启动): {str(e)}")

    # 4. 启动异步订单写入器
    logger.info("启动异步订单写入器...")
    try:
        from app.services.async_writer import async_order_writer
        await async_order_writer.start()
        logger.info("异步订单写入器启动完成")
    except Exception as e:
        logger.error(f"异步订单写入器启动失败: {str(e)}")

    logger.info("=" * 60)
    logger.info(f"{settings.APP_NAME} 启动完成!")
    logger.info(f"访问地址: http://localhost:8000")
    logger.info(f"API文档: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    # ==================== 应用关闭 ====================
    logger.info("=" * 60)
    logger.info("正在关闭应用...")

    # 停止异步订单写入器
    try:
        from app.services.async_writer import async_order_writer
        await async_order_writer.stop()
        logger.info("异步订单写入器已停止")
    except Exception as e:
        logger.error(f"异步订单写入器停止失败: {str(e)}")

    logger.info("应用已关闭")
    logger.info("=" * 60)


# ==================== 创建FastAPI应用 ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="高并发抢单系统 - 支持万级并发请求",
    lifespan=lifespan
)


# ==================== 配置CORS中间件 ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 注册自定义中间件 ====================

# 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 黑名单中间件
app.add_middleware(BlacklistMiddleware)

# 限流中间件
app.add_middleware(RateLimitMiddleware)


# ==================== 全局异常处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    
    捕获所有未处理的异常，返回统一格式的错误响应
    """
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "data": None
        }
    )


# ==================== 注册路由 ====================

# 认证路由
app.include_router(auth.router)

# 商品路由
app.include_router(product.router)

# 订单路由
app.include_router(order.router)

# 抢单路由
app.include_router(seckill.router)


# ==================== 健康检查接口 ====================

@app.get("/health")
async def health_check():
    """
    健康检查接口
    
    用于负载均衡器和监控系统检测应用状态
    """
    return {
        "code": 200,
        "message": "ok",
        "data": {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "timestamp": datetime.now().isoformat()
        }
    }


@app.get("/")
async def root():
    """
    根路径接口
    """
    return {
        "code": 200,
        "message": "欢迎使用高并发抢单系统",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health"
        }
    }


# ==================== 启动应用 ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1  # 开发模式使用单进程
    )

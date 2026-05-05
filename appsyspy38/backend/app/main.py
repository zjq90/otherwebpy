"""
多角色管理系统 - 主应用入口
FastAPI应用配置和路由注册
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import (
    auth_router, user_router,
    production_router, quality_router,
    material_router, transport_router,
    test_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 初始化数据库
    await init_db()
    print("数据库初始化完成")
    
    yield
    
    # 清理资源
    print("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="多角色管理系统 - 支持管理员、拌合站操作员、试验检测员、物资采购员、资源调度员等多角色",
    lifespan=lifespan,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router.router, prefix=settings.API_PREFIX)
app.include_router(user_router.router, prefix=settings.API_PREFIX)
app.include_router(production_router.router, prefix=settings.API_PREFIX)
app.include_router(quality_router.router, prefix=settings.API_PREFIX)
app.include_router(material_router.router, prefix=settings.API_PREFIX)
app.include_router(transport_router.router, prefix=settings.API_PREFIX)
app.include_router(test_router.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """
    根路径 - 返回系统信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "api_docs": f"{settings.API_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy"}

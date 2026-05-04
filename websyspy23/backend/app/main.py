"""
FastAPI 主应用入口
创建FastAPI应用实例，注册路由和中间件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from .config import settings
from .database import init_db
from .routers import card_router, course_router, member_router, venue_router, schedule_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库
    """
    # 启动时执行
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成")
    yield
    # 关闭时执行
    print("应用正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="会员管理系统 - 支持卡项管理、课程管理、会员管理等功能",
    lifespan=lifespan
)

# 配置CORS中间件
# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(card_router)
app.include_router(course_router)
app.include_router(member_router)
app.include_router(venue_router)
app.include_router(schedule_router)


@app.get("/", tags=["根路径"])
def root():
    """
    根路径访问
    返回系统基本信息
    """
    return {
        "message": "欢迎使用会员管理系统",
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """
    健康检查接口
    用于监控系统状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

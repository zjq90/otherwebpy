from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import coach, member, lesson, performance, test_data

"""
健身私教管理系统 - 主应用入口
基于 FastAPI 的 RESTful API 服务
"""


def create_tables():
    """
    初始化数据库表
    在应用启动时调用
    """
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时：创建数据库表
    - 关闭时：清理资源
    """
    # 启动时执行
    create_tables()
    print("数据库表创建完成")
    yield
    # 关闭时执行
    print("应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="健身私教管理系统 API - 支持教练档案管理、私教课管理、业绩追踪等功能",
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(coach.router)
app.include_router(member.router)
app.include_router(lesson.router)
app.include_router(performance.router)
app.include_router(test_data.router)


@app.get("/", tags=["根路径"])
def root():
    """
    根路径接口
    返回应用基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "运行中",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }


@app.get("/api/health", tags=["健康检查"])
def health_check():
    """
    健康检查接口
    用于监控服务状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


from datetime import datetime

# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

"""
智慧农业监测系统 - 主入口文件
技术栈: Python + FastAPI + SQLite + Bootstrap V4
功能: 环境数据采集、生长状态记录、AI辅助诊断
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import (
    device_router,
    environment_router,
    crop_router,
    growth_record_router,
    test_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 初始化数据库
    init_db()
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    yield
    # 关闭时的清理操作
    print("应用关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智慧农业监测系统 - 环境数据采集与生长状态记录",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册API路由
api_prefix = settings.API_PREFIX
app.include_router(device_router, prefix=api_prefix)
app.include_router(environment_router, prefix=api_prefix)
app.include_router(crop_router, prefix=api_prefix)
app.include_router(growth_record_router, prefix=api_prefix)
app.include_router(test_router, prefix=api_prefix)


@app.get("/", response_class=HTMLResponse)
async def index():
    """
    首页路由
    返回前端首页
    """
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

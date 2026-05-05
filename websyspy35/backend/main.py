from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from app.core.config import settings
from app.core.database import init_db
from app.routers import equipment, monitoring, maintenance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用程序生命周期管理
    启动时初始化数据库
    """
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="工业设备监测管理系统 - 后端API服务",
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(equipment.router)
app.include_router(monitoring.router)
app.include_router(maintenance.router)


@app.get("/", tags=["根路径"])
def root():
    """
    根路径，返回系统基本信息
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
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

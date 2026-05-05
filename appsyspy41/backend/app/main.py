"""
设备管理系统API主应用
基于FastAPI的设备监控、保养管理和故障报修系统
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.database.init_db import init_database
from app.routers import device, maintenance, fault, auth
from app.routers import test_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 检查数据库是否存在，不存在则初始化
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'device_management.db')
    if not os.path.exists(db_path):
        print("初始化数据库...")
        init_database()
    
    print("应用启动完成")
    yield
    # 关闭时的清理工作
    print("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="设备管理系统API",
    description="设备状态监控、保养任务管理、故障报修处理系统",
    version="1.0.0",
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

# 注册路由
app.include_router(auth.router)
app.include_router(device.router)
app.include_router(maintenance.router)
app.include_router(fault.router)
app.include_router(test_helper.router)


@app.get("/")
async def root():
    """
    根路径接口
    返回系统基本信息
    """
    return {
        "name": "设备管理系统API",
        "version": "1.0.0",
        "description": "设备状态监控、保养任务管理、故障报修处理系统",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

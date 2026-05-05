"""
混凝土质量追溯系统后端API
使用FastAPI框架开发
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import (
    auth_router, materials_router, inspections_router,
    productions_router, alerts_router, trace_router, test_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 初始化数据库
    init_db()
    print("数据库初始化完成")
    
    # 检查是否有默认用户，如果没有则创建
    try:
        from sqlalchemy.orm import Session
        from database import SessionLocal
        from models.models import User
        from core.security import get_password_hash
        
        db = SessionLocal()
        
        # 检查管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                real_name="系统管理员",
                role="admin",
                phone="13800138000",
                email="admin@example.com"
            )
            db.add(admin)
        
        # 检查检验员用户
        inspector = db.query(User).filter(User.username == "inspector").first()
        if not inspector:
            inspector = User(
                username="inspector",
                password_hash=get_password_hash("123456"),
                real_name="张三",
                role="inspector",
                phone="13800138001",
                email="inspector@example.com"
            )
            db.add(inspector)
        
        db.commit()
        db.close()
        print("默认用户创建完成")
        print("管理员账号: admin / admin123")
        print("检验员账号: inspector / 123456")
    except Exception as e:
        print(f"创建默认用户时出错: {e}")
    
    yield
    
    # 关闭时的清理操作
    print("应用关闭")


app = FastAPI(
    title="混凝土质量追溯系统API",
    description="基于FastAPI的混凝土质量追溯系统后端服务",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(materials_router)
app.include_router(inspections_router)
app.include_router(productions_router)
app.include_router(alerts_router)
app.include_router(trace_router)
app.include_router(test_router, prefix="/api/test", tags=["测试功能"])


@app.get("/", summary="根路径")
async def root():
    """
    根路径，返回系统信息
    """
    return {
        "message": "混凝土质量追溯系统API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "timestamp": "2026-05-05T00:00:00"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

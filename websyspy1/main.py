"""
主应用入口文件
FastAPI应用的入口点，包含路由注册、中间件配置等
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from contextlib import asynccontextmanager

from database import engine, Base, get_db
from config import STATIC_DIR, TEMPLATES_DIR

# 导入路由模块
from routers import auth, users, products, services, cases, documents, key_applications, pages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时创建数据库表
    """
    # 创建所有数据库表
    Base.metadata.create_all(bind=engine)
    yield


# 创建FastAPI应用实例
app = FastAPI(
    title="企业展示系统",
    description="基于FastAPI+SQLite+Bootstrap的企业展示系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 配置模板引擎
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(products.router, prefix="/api/products", tags=["产品"])
app.include_router(services.router, prefix="/api/services", tags=["服务"])
app.include_router(cases.router, prefix="/api/cases", tags=["案例"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档"])
app.include_router(key_applications.router, prefix="/api/key-applications", tags=["秘钥申请"])
app.include_router(pages.router, tags=["页面"])


@app.get("/")
def read_root():
    """
    根路径接口
    返回系统基本信息
    """
    return {
        "name": "企业展示系统",
        "version": "1.0.0",
        "description": "基于FastAPI+SQLite+Bootstrap的企业展示系统",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

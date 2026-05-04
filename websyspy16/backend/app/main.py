"""
物业信息管理系统主应用
基于FastAPI的后端服务，提供RESTful API接口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import engine, Base
from app.routers import property_projects, properties, owners, dashboard, test_data


def create_tables():
    """
    创建数据库表
    """
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时创建数据库表
    create_tables()
    yield
    # 关闭时的清理操作


# 创建FastAPI应用实例
app = FastAPI(
    title="物业信息管理系统",
    description="一个基于FastAPI的物业信息管理系统，支持物业项目、房产信息、业主信息等管理功能",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(dashboard.router)
app.include_router(property_projects.router)
app.include_router(properties.router)
app.include_router(owners.router)
app.include_router(test_data.router)


@app.get("/", tags=["根路径"])
def root():
    """
    根路径，返回系统欢迎信息
    """
    return {
        "message": "欢迎使用物业信息管理系统API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

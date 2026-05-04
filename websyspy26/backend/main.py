"""
会员管理系统主应用
基于 FastAPI 的后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from config.database import init_db
from routers import member, promotion, reminder, test


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 应用启动时初始化数据库
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")
    yield
    # 应用关闭时的清理工作
    print("应用正在关闭...")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="一个功能完整的会员管理系统，支持促销活动管理和续费提醒功能",
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
app.include_router(member.router)
app.include_router(promotion.router)
app.include_router(reminder.router)
app.include_router(test.router)


@app.get("/", tags=["根路径"])
def root():
    """
    根路径接口
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "欢迎使用会员管理系统API",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


from datetime import datetime

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

"""
FastAPI主应用入口文件
配置应用并注册所有路由
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import init_db
from .routers import (
    user_router, body_measurement_router, exercise_router,
    training_log_router, goal_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 启动时执行
    init_db()
    yield
    # 关闭时执行（可选）


# 创建FastAPI应用实例
app = FastAPI(
    title="健身App API",
    description="健身管理系统后端API，包含体测记录、训练日志、目标设定等功能",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(user_router)
app.include_router(body_measurement_router)
app.include_router(exercise_router)
app.include_router(training_log_router)
app.include_router(goal_router)


@app.get("/", tags=["根路径"])
def root():
    """
    根路径API
    返回应用基本信息
    """
    return {
        "message": "欢迎使用健身App API",
        "version": "1.0.0",
        "docs": "/docs",  # Swagger UI文档地址
        "redoc": "/redoc"  # ReDoc文档地址
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """
    健康检查接口
    用于监控服务状态
    """
    return {
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

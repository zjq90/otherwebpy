"""
混凝土生产管理系统 - 主应用入口
使用FastAPI框架构建RESTful API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db
from .routers import production_router, cost_router, environment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库
    """
    # 初始化数据库
    init_db()
    yield


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
    混凝土生产管理系统 - 后端API服务
    
    ## 功能模块
    - **生产数据分析**: 统计日/月产量、设备利用率、能耗指标
    - **成本核算与利润分析**: 自动归集原材料、人工、能耗等成本，生成单方混凝土毛利报表
    - **环保合规监管**: 集成粉尘、噪音、废水排放监测模块，超标自动报警
    
    ## 技术栈
    - 后端框架: FastAPI
    - 数据库: SQLite
    - ORM: SQLAlchemy
    - API文档: OpenAPI (自动生成)
    """,
    lifespan=lifespan
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
app.include_router(production_router)
app.include_router(cost_router)
app.include_router(environment_router)


@app.get("/", tags=["首页"])
def root():
    """
    根路径接口
    返回系统基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
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


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

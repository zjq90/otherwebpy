"""
物业综合管理系统 - 主应用入口
使用FastAPI框架，提供RESTful API接口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.database import init_db
from app.models import *  # 导入所有模型，确保SQLAlchemy能创建所有表
from app.routers import equipment, decoration, contract

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    物业综合管理系统API文档
    
    包含以下功能模块：
    - 工程维保管理：设备台账、巡检计划、保养计划、故障维修
    - 装修管理：装修申请、押金管理、装修巡检
    - 合同与供应商管理：供应商管理、合同管理、付款记录、服务质量评估
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
# 允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    equipment.router,
    prefix=f"{settings.API_V1_STR}/equipment",
    tags=["工程维保管理"]
)

app.include_router(
    decoration.router,
    prefix=f"{settings.API_V1_STR}/decoration",
    tags=["装修管理"]
)

app.include_router(
    contract.router,
    prefix=f"{settings.API_V1_STR}/contract",
    tags=["合同与供应商管理"]
)

@app.on_event("startup")
def startup_event():
    """
    应用启动时执行
    初始化数据库表
    """
    init_db()

@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def root():
    """
    根路径重定向到API文档
    """
    return "/docs"

@app.get("/health", tags=["系统"])
def health_check():
    """
    健康检查接口
    用于验证服务是否正常运行
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "name": settings.PROJECT_NAME
    }

@app.get("/api/info", tags=["系统"])
def get_api_info():
    """
    获取API信息
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_version": "v1",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": f"{settings.API_V1_STR}/openapi.json"
        }
    }

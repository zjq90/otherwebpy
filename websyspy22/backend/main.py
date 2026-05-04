"""
健身房会员管理系统 - 主应用入口
基于 FastAPI + SQLite + SQLAlchemy
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, engine, Base

# 导入路由
from app.routers import members, archive, level, status, test

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    logger.info(f"正在启动 {settings.APP_NAME} v{settings.APP_VERSION}...")
    
    # 初始化数据库
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    
    logger.info(f"{settings.APP_NAME} 启动成功")
    yield
    
    # 关闭时清理
    logger.info(f"{settings.APP_NAME} 正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="健身房会员管理系统后端API，支持会员信息采集、档案管理、等级权益、状态管理等功能",
    lifespan=lifespan,
    contact={
        "name": "开发团队",
        "email": "dev@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应改为具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证异常
    """
    logger.warning(f"请求验证失败: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "detail": exc.errors(),
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理通用异常
    """
    logger.error(f"系统异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请稍后重试",
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    )


# 注册路由
app.include_router(members.router)
app.include_router(archive.router)
app.include_router(level.router)
app.include_router(status.router)
app.include_router(test.router)


# 根路由
@app.get("/", tags=["系统"])
async def root():
    """
    系统首页，返回基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "features": [
            "会员信息采集（线上/线下渠道）",
            "实名认证（手机号/人脸识别）",
            "档案管理（体测数据/运动目标/消费记录/课程参与）",
            "等级与权益（铜/银/金三级体系）",
            "状态管理（冻结/解冻/注销）",
            "短信通知（状态变更/消费通知）",
            "测试数据生成",
            "OpenAPI 文档"
        ]
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


# 运行入口
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

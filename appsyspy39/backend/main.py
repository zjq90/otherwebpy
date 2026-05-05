"""
混凝土生产管理系统API - 主入口文件

技术栈:
- 后端框架: FastAPI
- 数据库: SQLite (异步)
- ORM: SQLAlchemy 2.0+
- 认证: JWT (python-jose)
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db, close_db
from app.routers import (
    auth_router,
    tasks_router,
    formulas_router,
    feeding_router,
    mixing_router,
    test_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时初始化数据库连接
    关闭时清理资源
    """
    # 启动时执行
    print(f"正在启动 {settings.APP_NAME} v{settings.APP_VERSION}...")
    await init_db()
    print("数据库初始化完成")
    yield
    # 关闭时执行
    print("正在关闭数据库连接...")
    await close_db()
    print(f"{settings.APP_NAME} 已停止")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    混凝土生产管理系统API接口文档
    
    ## 主要功能模块
    - **认证管理**: 用户登录、注册、密码修改
    - **任务管理**: 生产任务的CRUD、接单、开始、完成
    - **配方管理**: 配合比配方的CRUD、参数微调
    - **投料监控**: 投料记录管理、偏差计算、预警
    - **搅拌记录**: 搅拌过程记录、异常管理
    
    ## 技术特点
    - 基于FastAPI的异步API
    - SQLAlchemy 2.0异步ORM
    - JWT令牌认证
    - 完整的OpenAPI文档
    """,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "认证管理", "description": "用户认证相关接口"},
        {"name": "任务管理", "description": "生产任务管理接口"},
        {"name": "配方管理", "description": "配合比配方管理接口"},
        {"name": "投料监控", "description": "投料记录和偏差监控接口"},
        {"name": "搅拌过程记录", "description": "搅拌过程记录接口"},
        {"name": "测试工具", "description": "测试数据生成和管理接口"}
    ]
)


# 配置CORS中间件 - 允许跨域请求（用于uniapp前端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 自定义异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证错误
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
            "details": None
        }
    )


# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(formulas_router, prefix="/api")
app.include_router(feeding_router, prefix="/api")
app.include_router(mixing_router, prefix="/api")
app.include_router(test_router, prefix="/api")


# 健康检查接口
@app.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口
    用于监控服务是否正常运行
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected"
    }


# 根路径重定向到API文档
@app.get("/", include_in_schema=False)
async def root():
    """
    根路径重定向到API文档
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

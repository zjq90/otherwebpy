"""
运输管理系统API主入口文件
使用FastAPI构建的异步RESTful API服务
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

from app.config import settings
from app.database import init_db
from app.routers import (
    auth_router,
    users_router,
    vehicles_router,
    transport_tasks_router,
    locations_router,
    task_updates_router,
    test_router,
)


# 确保必要的目录在应用启动前已创建
# 这是关键：StaticFiles挂载时要求目录必须存在
def ensure_directories():
    """
    确保必要的目录存在
    在应用启动和StaticFiles挂载之前调用
    """
    # 上传目录
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 子目录
    (upload_dir / "unload_photos").mkdir(parents=True, exist_ok=True)
    (upload_dir / "general").mkdir(parents=True, exist_ok=True)


# 立即执行目录创建
ensure_directories()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库
    """
    # 初始化数据库
    await init_db()
    
    yield
    
    # 应用关闭时的清理工作（如果需要）
    pass


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="运输管理系统API - 支持车辆位置监控、运输任务分配、运输状态更新等功能",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（用于访问上传的文件）
app.mount(
    f"/{settings.UPLOAD_DIR}",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads"
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    处理未捕获的异常并返回统一格式的错误响应
    """
    if settings.DEBUG:
        # 调试模式下返回详细错误信息
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": str(exc),
                "data": None,
                "detail": str(exc.__class__.__name__),
            }
        )
    else:
        # 生产环境下返回通用错误信息
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None,
            }
        )


# 注册路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(vehicles_router)
app.include_router(transport_tasks_router)
app.include_router(locations_router)
app.include_router(task_updates_router)
app.include_router(test_router)


# 根路径
@app.get("/")
async def root():
    """
    根路径接口
    返回系统基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        }
    }


# 健康检查接口
@app.get("/health")
async def health_check():
    """
    健康检查接口
    用于检查服务是否正常运行
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


from datetime import datetime

# 启动说明
if __name__ == "__main__":
    import uvicorn
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           运输管理系统 API 服务启动中...                         ║
╠══════════════════════════════════════════════════════════════╣
║  服务名称: {settings.APP_NAME:<47}║
║  版本号:   {settings.APP_VERSION:<47}║
║  调试模式: {'开启' if settings.DEBUG else '关闭':<47}║
╠══════════════════════════════════════════════════════════════╣
║  访问地址:                                                        ║
║  - 主服务:     http://localhost:8000/                          ║
║  - Swagger:    http://localhost:8000/docs                      ║
║  - ReDoc:      http://localhost:8000/redoc                     ║
║  - OpenAPI:    http://localhost:8000/openapi.json              ║
╠══════════════════════════════════════════════════════════════╣
║  测试辅助接口:                                                    ║
║  - 初始化数据库: POST /api/test/init-db                         ║
║  - 生成测试数据: POST /api/test/generate-test-data              ║
║  - 系统状态:    GET  /api/test/system-status                    ║
║  - 清除数据:    DELETE /api/test/clear-test-data                ║
╠══════════════════════════════════════════════════════════════╣
║  测试账号:                                                        ║
║  - 管理员:   admin / 123456                                      ║
║  - 调度员:   dispatcher1 / 123456                                ║
║  - 司机:     driver1 / 123456                                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )

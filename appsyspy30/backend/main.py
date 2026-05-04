"""
健身社交系统主应用入口
使用 FastAPI 构建后端 API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import init_db
from app.routers import auth, posts, friends, challenges, invitations

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="健身社交系统后端API，支持动态广场、好友系统、挑战活动、邀请有礼等功能",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "errors": exc.errors()
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
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc)
        }
    )


# 注册路由
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(posts.router, prefix=settings.API_PREFIX)
app.include_router(friends.router, prefix=settings.API_PREFIX)
app.include_router(challenges.router, prefix=settings.API_PREFIX)
app.include_router(invitations.router, prefix=settings.API_PREFIX)


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时初始化数据库
    """
    init_db()
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} 启动成功")
    print(f"📚 API 文档地址: http://localhost:8000{settings.API_PREFIX}/docs")


# 根路径健康检查
@app.get("/", tags=["健康检查"])
async def health_check():
    """
    健康检查接口
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ok",
        "api_prefix": settings.API_PREFIX
    }


@app.get("/health", tags=["健康检查"])
async def health():
    """
    健康检查接口
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

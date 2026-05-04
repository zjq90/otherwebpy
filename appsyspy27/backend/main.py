"""
会员管理系统API主入口文件
使用FastAPI框架构建RESTful API服务
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.database import init_db
from app.routers import auth, card, order, consumption, test


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    # 启动时执行
    print(f"正在初始化 {settings.APP_NAME} v{settings.APP_VERSION}...")
    init_db()
    print("数据库初始化完成")
    yield
    # 关闭时执行
    print("应用正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    会员管理系统API服务
    
    ## 功能模块
    - **认证管理**: 用户注册、登录、微信登录、资料编辑
    - **会员卡管理**: 卡类型查询、用户卡包管理
    - **订单管理**: 订单创建、支付、查询
    - **消费记录**: 消费记录查询、月度账单、统计分析
    - **测试功能**: 测试数据生成、健康检查
    
    ## 认证方式
    使用JWT Bearer Token进行认证，登录成功后获取access_token，
    在后续请求的Header中添加: Authorization: Bearer <token>
    """,
    lifespan=lifespan,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证错误
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "参数验证失败",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理
    """
    if settings.DEBUG:
        import traceback
        detail = traceback.format_exc()
    else:
        detail = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": detail if settings.DEBUG else None
        }
    )


# 注册路由
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(card.router, prefix=settings.API_PREFIX)
app.include_router(order.router, prefix=settings.API_PREFIX)
app.include_router(consumption.router, prefix=settings.API_PREFIX)
app.include_router(test.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["根路径"])
async def root():
    """
    根路径，返回服务基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": f"{settings.API_PREFIX}/docs",
        "openapi": f"{settings.API_PREFIX}/openapi.json"
    }


@app.get("/health", tags=["健康检查"])
async def health():
    """
    健康检查接口
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

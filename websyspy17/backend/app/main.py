from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, service_request, activity

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="社区管理系统 API - 支持客户服务管理和社区文化管理",
    openapi_tags=[
        {"name": "认证", "description": "用户注册、登录、认证相关接口"},
        {"name": "服务请求", "description": "报修、投诉、咨询等服务请求管理"},
        {"name": "社区活动", "description": "社区活动发布、报名管理"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(service_request.router)
app.include_router(activity.router)


@app.get("/", tags=["首页"])
def root():
    """
    API 根路径
    
    返回系统基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["系统"])
def health_check():
    """
    健康检查接口
    
    用于检查系统是否正常运行
    """
    return {"status": "healthy"}

"""
库存管理系统API主入口
使用FastAPI创建Web应用，配置中间件和路由
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, get_db
from app.routers import (
    auth_router,
    inventory_router,
    purchase_router,
    supplier_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="库存管理系统后端API，支持库存查询、采购申请、供应商管理等功能",
    lifespan=lifespan,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=settings.API_PREFIX)
app.include_router(inventory_router.router, prefix=settings.API_PREFIX)
app.include_router(purchase_router.router, prefix=settings.API_PREFIX)
app.include_router(supplier_router.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """根路径重定向到API文档"""
    return RedirectResponse(url=f"{settings.API_PREFIX}/docs")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

"""
农产品溯源与认证管理系统
主应用入口文件

功能模块：
1. 全程溯源 - 为每批农产品生成唯一二维码
2. 检测与认证 - 记录检测结果，管理认证证书有效期

技术栈：
- 后端：Python + FastAPI + SQLAlchemy
- 数据库：SQLite
- 前端：Bootstrap V4 + HTML + JavaScript
"""
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, get_db, init_db
from app.routers import products, batches, planting_records, agrochemical_usages, test_results, certificates, traceability, test_data, statistics
from app import crud


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
    version=settings.APP_VERSION,
    description="农产品溯源与认证管理系统 - 支持全程溯源、检测结果记录、认证证书管理",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板引擎
templates = Jinja2Templates(directory="templates")

# 注册API路由
app.include_router(products.router, prefix="/api")
app.include_router(batches.router, prefix="/api")
app.include_router(planting_records.router, prefix="/api")
app.include_router(agrochemical_usages.router, prefix="/api")
app.include_router(test_results.router, prefix="/api")
app.include_router(certificates.router, prefix="/api")
app.include_router(traceability.router, prefix="/api")
app.include_router(test_data.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")


# 页面路由 - 首页
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    首页
    显示系统概览和导航菜单
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": settings.APP_NAME}
    )


# 页面路由 - 产品管理
@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """
    产品管理页面
    """
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "title": "产品管理 - " + settings.APP_NAME}
    )


# 页面路由 - 批次管理
@app.get("/batches", response_class=HTMLResponse)
async def batches_page(request: Request):
    """
    批次管理页面
    """
    return templates.TemplateResponse(
        "batches.html",
        {"request": request, "title": "批次管理 - " + settings.APP_NAME}
    )


# 页面路由 - 种植记录管理
@app.get("/planting-records", response_class=HTMLResponse)
async def planting_records_page(request: Request):
    """
    种植记录管理页面
    """
    return templates.TemplateResponse(
        "planting_records.html",
        {"request": request, "title": "种植记录管理 - " + settings.APP_NAME}
    )


# 页面路由 - 农资使用管理
@app.get("/agrochemical-usages", response_class=HTMLResponse)
async def agrochemical_usages_page(request: Request):
    """
    农资使用管理页面
    """
    return templates.TemplateResponse(
        "agrochemical_usages.html",
        {"request": request, "title": "农资使用管理 - " + settings.APP_NAME}
    )


# 页面路由 - 检测结果管理
@app.get("/test-results", response_class=HTMLResponse)
async def test_results_page(request: Request):
    """
    检测结果管理页面
    """
    return templates.TemplateResponse(
        "test_results.html",
        {"request": request, "title": "检测结果管理 - " + settings.APP_NAME}
    )


# 页面路由 - 认证证书管理
@app.get("/certificates", response_class=HTMLResponse)
async def certificates_page(request: Request):
    """
    认证证书管理页面
    """
    return templates.TemplateResponse(
        "certificates.html",
        {"request": request, "title": "认证证书管理 - " + settings.APP_NAME}
    )


# 页面路由 - 溯源查询
@app.get("/traceability", response_class=HTMLResponse)
async def traceability_page(request: Request):
    """
    溯源查询页面
    """
    return templates.TemplateResponse(
        "traceability.html",
        {"request": request, "title": "溯源查询 - " + settings.APP_NAME}
    )


# 页面路由 - 溯源详情（消费者扫码后访问）
@app.get("/traceability/view/{batch_number}", response_class=HTMLResponse)
async def traceability_view_page(
    request: Request,
    batch_number: str
):
    """
    溯源详情查看页面
    消费者扫码后跳转到此页面
    """
    return templates.TemplateResponse(
        "traceability_view.html",
        {
            "request": request,
            "title": "溯源详情 - " + settings.APP_NAME,
            "batch_number": batch_number
        }
    )


# 健康检查接口
@app.get("/health")
async def health_check():
    """
    健康检查接口
    用于监控服务状态
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    # 启动应用服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

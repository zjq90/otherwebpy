"""
智慧农业管理系统主应用入口
使用FastAPI框架构建，提供RESTful API服务
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import (
    planting_plan_router,
    farm_operation_router,
    fertilization_irrigation_router,
    pest_disease_control_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库
    """
    # 启动时执行
    print("=" * 60)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print("=" * 60)
    
    # 初始化数据库
    print("\n正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")
    
    print("\n" + "=" * 60)
    print(f"{settings.APP_NAME} 启动成功！")
    print(f"API文档地址: http://localhost:8000/docs")
    print(f"API备用文档: http://localhost:8000/redoc")
    print("=" * 60)
    
    yield
    
    # 关闭时执行
    print("\n" + "=" * 60)
    print(f"{settings.APP_NAME} 已关闭")
    print("=" * 60)


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智慧农业管理系统 - 支持种植计划管理、农事作业记录、精准施肥灌溉、病虫害防治等功能",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载静态文件目录
static_dir = settings.STATIC_DIR
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    # 如果静态目录不存在，创建它
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 配置模板引擎
templates_dir = settings.TEMPLATES_DIR
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)


# 注册API路由
API_PREFIX = settings.API_PREFIX

app.include_router(planting_plan_router, prefix=API_PREFIX)
app.include_router(farm_operation_router, prefix=API_PREFIX)
app.include_router(fertilization_irrigation_router, prefix=API_PREFIX)
app.include_router(pest_disease_control_router, prefix=API_PREFIX)


# 根路由 - 首页
@app.get("/", response_class=HTMLResponse, tags=["页面路由"])
async def index(request: Request):
    """
    系统首页
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.APP_NAME, "app_version": settings.APP_VERSION}
    )


# 种植计划管理页面
@app.get("/planting-plans", response_class=HTMLResponse, tags=["页面路由"])
async def planting_plans_page(request: Request):
    """
    种植计划管理页面
    """
    return templates.TemplateResponse(
        "planting_plans.html",
        {"request": request, "app_name": settings.APP_NAME}
    )


# 农事作业记录页面
@app.get("/farm-operations", response_class=HTMLResponse, tags=["页面路由"])
async def farm_operations_page(request: Request):
    """
    农事作业记录页面
    """
    return templates.TemplateResponse(
        "farm_operations.html",
        {"request": request, "app_name": settings.APP_NAME}
    )


# 精准施肥与灌溉页面
@app.get("/fertilization-irrigations", response_class=HTMLResponse, tags=["页面路由"])
async def fertilization_irrigations_page(request: Request):
    """
    精准施肥与灌溉页面
    """
    return templates.TemplateResponse(
        "fertilization_irrigations.html",
        {"request": request, "app_name": settings.APP_NAME}
    )


# 病虫害防治管理页面
@app.get("/pest-disease-controls", response_class=HTMLResponse, tags=["页面路由"])
async def pest_disease_controls_page(request: Request):
    """
    病虫害防治管理页面
    """
    return templates.TemplateResponse(
        "pest_disease_controls.html",
        {"request": request, "app_name": settings.APP_NAME}
    )


# 健康检查接口
@app.get("/health", tags=["系统接口"])
async def health_check():
    """
    健康检查接口
    用于监控系统运行状态
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


# API信息接口
@app.get("/api/info", tags=["系统接口"])
async def api_info():
    """
    获取API信息
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_PREFIX,
        "description": "智慧农业管理系统API",
        "endpoints": {
            "种植计划管理": f"{API_PREFIX}/planting-plans",
            "农事作业记录": f"{API_PREFIX}/farm-operations",
            "精准施肥灌溉": f"{API_PREFIX}/fertilization-irrigations",
            "病虫害防治": f"{API_PREFIX}/pest-disease-controls"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

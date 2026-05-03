"""
农业报表系统主应用
使用FastAPI框架构建
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import (
    API_PREFIX, API_TITLE, API_DESCRIPTION, API_VERSION,
    ALLOWED_ORIGINS, STATIC_DIR, TEMPLATE_DIR
)
from database import init_db
from routers import auth, crops, plots, production, financial, environment


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 确保必要的目录存在
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 初始化数据库
    await init_db()
    
    yield


# 创建FastAPI应用
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 配置模板
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# 注册路由
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(crops.router, prefix=API_PREFIX)
app.include_router(plots.router, prefix=API_PREFIX)
app.include_router(production.router, prefix=API_PREFIX)
app.include_router(financial.router, prefix=API_PREFIX)
app.include_router(environment.router, prefix=API_PREFIX)


# 前端页面路由
@app.get("/")
async def index(request: Request):
    """
    首页
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    """
    登录页面
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard")
async def dashboard_page(request: Request):
    """
    仪表板页面
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/crops")
async def crops_page(request: Request):
    """
    作物管理页面
    """
    return templates.TemplateResponse("crops.html", {"request": request})


@app.get("/plots")
async def plots_page(request: Request):
    """
    地块管理页面
    """
    return templates.TemplateResponse("plots.html", {"request": request})


@app.get("/production")
async def production_page(request: Request):
    """
    生产管理页面
    """
    return templates.TemplateResponse("production.html", {"request": request})


@app.get("/financial")
async def financial_page(request: Request):
    """
    财务管理页面
    """
    return templates.TemplateResponse("financial.html", {"request": request})


@app.get("/environment")
async def environment_page(request: Request):
    """
    环境管理页面
    """
    return templates.TemplateResponse("environment.html", {"request": request})


@app.get("/reports/production")
async def production_report_page(request: Request):
    """
    生产报表页面
    """
    return templates.TemplateResponse("report_production.html", {"request": request})


@app.get("/reports/financial")
async def financial_report_page(request: Request):
    """
    财务报表页面
    """
    return templates.TemplateResponse("report_financial.html", {"request": request})


@app.get("/reports/environment")
async def environment_report_page(request: Request):
    """
    环境报表页面
    """
    return templates.TemplateResponse("report_environment.html", {"request": request})


# 健康检查
@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy", "version": API_VERSION}

"""
门禁考勤管理系统主入口
使用FastAPI构建的Web应用
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import create_directories
from database import init_db
from routers import staff, device, access_record, attendance, test


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时创建目录和初始化数据库
    """
    # 创建必要的目录
    create_directories()
    # 初始化数据库
    init_db()
    yield


# 创建FastAPI应用
app = FastAPI(
    title="门禁考勤管理系统",
    description="基于FastAPI的门禁考勤管理系统，支持人脸识别、出入记录、考勤管理等功能",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 注册路由
app.include_router(staff.router)
app.include_router(device.router)
app.include_router(access_record.router)
app.include_router(attendance.router)
app.include_router(test.router)


# 页面路由
@app.get("/")
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/staff")
async def staff_page(request: Request):
    """工作人员管理页面"""
    return templates.TemplateResponse("staff/index.html", {"request": request})


@app.get("/device")
async def device_page(request: Request):
    """设备管理页面"""
    return templates.TemplateResponse("device/index.html", {"request": request})


@app.get("/access")
async def access_page(request: Request):
    """出入记录页面"""
    return templates.TemplateResponse("access/index.html", {"request": request})


@app.get("/attendance")
async def attendance_page(request: Request):
    """考勤管理页面"""
    return templates.TemplateResponse("attendance/index.html", {"request": request})


@app.get("/test")
async def test_page(request: Request):
    """系统测试页面"""
    return templates.TemplateResponse("test/index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

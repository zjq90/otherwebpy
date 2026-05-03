"""
租借预约系统主入口文件
技术栈：Python + SQLite + FastAPI + Bootstrap 5
功能：租借预约、消息通知、数据导出
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# 导入路由
from app.routers import users, products, categories, reservations, notifications, exports

# 创建数据库表
from app.database import Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="租借预约系统",
    description="一个完整的租借预约管理系统，支持用户预约、消息通知和数据导出功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(products.router, prefix="/api/products", tags=["产品管理"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类管理"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["预约管理"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["消息通知"])
app.include_router(exports.router, prefix="/api/exports", tags=["数据导出"])

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def index():
    """
    系统首页
    """
    return FileResponse("templates/index.html")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """
    登录页面
    """
    return FileResponse("templates/login.html")

@app.get("/products", response_class=HTMLResponse)
async def products_page():
    """
    产品列表页面
    """
    return FileResponse("templates/products.html")

@app.get("/reservations", response_class=HTMLResponse)
async def reservations_page():
    """
    预约管理页面
    """
    return FileResponse("templates/reservations.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """
    管理员页面
    """
    return FileResponse("templates/admin.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

"""
健身俱乐部APP系统 - 主应用入口
使用FastAPI构建的RESTful API服务
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import List

from config import settings
from database import engine, get_db, init_db
from models import Base, User, UserRole
from utils import get_password_hash, get_current_active_user
from schemas import ResponseModel

# 导入路由
from routers import (
    auth, users, coaches, courses, bookings,
    messages, chat, reviews, recommendations, products, preferences, test
)

# ========================================
# 应用生命周期管理
# ========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    在应用启动时初始化数据库，关闭时清理资源
    """
    # 启动时执行
    print(f"正在启动 {settings.APP_NAME}...")
    
    # 初始化数据库表
    init_db()
    
    # 创建默认管理员账户
    db = next(get_db())
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                email="admin@gym.com",
                phone="13800138000",
                real_name="系统管理员",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("默认管理员账户创建成功: admin / admin123")
    except Exception as e:
        print(f"创建默认管理员失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    print(f"{settings.APP_NAME} 启动成功!")
    print(f"API文档地址: http://localhost:{settings.SERVER_PORT}/docs")
    
    yield
    
    # 关闭时执行
    print(f"{settings.APP_NAME} 正在关闭...")

# ========================================
# 创建FastAPI应用实例
# ========================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="健身俱乐部APP系统后端API，支持智能推荐、消息中心、在线客服、服务评价等功能",
    lifespan=lifespan,
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================
# 配置CORS中间件
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# 挂载静态文件目录
# ========================================

# 创建静态文件目录（如果不存在）
import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ========================================
# 注册路由
# ========================================

# 认证路由
app.include_router(
    auth.router,
    prefix=f"/api/{settings.API_VERSION}/auth",
    tags=["认证管理"]
)

# 用户路由
app.include_router(
    users.router,
    prefix=f"/api/{settings.API_VERSION}/users",
    tags=["用户管理"]
)

# 教练路由
app.include_router(
    coaches.router,
    prefix=f"/api/{settings.API_VERSION}/coaches",
    tags=["教练管理"]
)

# 课程路由
app.include_router(
    courses.router,
    prefix=f"/api/{settings.API_VERSION}/courses",
    tags=["课程管理"]
)

# 预约路由
app.include_router(
    bookings.router,
    prefix=f"/api/{settings.API_VERSION}/bookings",
    tags=["预约管理"]
)

# 消息路由
app.include_router(
    messages.router,
    prefix=f"/api/{settings.API_VERSION}/messages",
    tags=["消息中心"]
)

# 聊天路由
app.include_router(
    chat.router,
    prefix=f"/api/{settings.API_VERSION}/chat",
    tags=["在线客服"]
)

# 评价路由
app.include_router(
    reviews.router,
    prefix=f"/api/{settings.API_VERSION}/reviews",
    tags=["服务评价"]
)

# 推荐路由
app.include_router(
    recommendations.router,
    prefix=f"/api/{settings.API_VERSION}/recommendations",
    tags=["智能推荐"]
)

# 产品路由
app.include_router(
    products.router,
    prefix=f"/api/{settings.API_VERSION}/products",
    tags=["营养产品"]
)

# 偏好路由
app.include_router(
    preferences.router,
    prefix=f"/api/{settings.API_VERSION}/preferences",
    tags=["会员偏好"]
)

# 测试路由
app.include_router(
    test.router,
    prefix=f"/api/{settings.API_VERSION}/test",
    tags=["测试功能"]
)

# ========================================
# 根路由
# ========================================

@app.get("/", response_class=HTMLResponse, tags=["首页"])
async def root():
    """
    系统首页
    """
    return f"""
    <html>
        <head>
            <title>{settings.APP_NAME}</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .container {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #333; margin-bottom: 20px; }}
                .links {{ margin-top: 30px; }}
                .links a {{ display: inline-block; margin: 10px; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; transition: all 0.3s; }}
                .links a:hover {{ background: #764ba2; transform: translateY(-2px); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏋️ {settings.APP_NAME}</h1>
                <p>版本: {settings.API_VERSION}</p>
                <p>后端API服务运行中...</p>
                <div class="links">
                    <a href="/docs">API 文档 (Swagger UI)</a>
                    <a href="/redoc">API 文档 (ReDoc)</a>
                </div>
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    默认管理员账号: admin / admin123</p>
            </div>
        </body>
    </html>
    """

@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    健康检查接口
    用于监控服务是否正常运行
    """
    return ResponseModel(
        code=200,
        message="服务运行正常",
        data={
            "app_name": settings.APP_NAME,
            "version": settings.API_VERSION,
            "status": "healthy"
        }
    )

# ========================================
# 启动应用
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )

"""
CD管理系统主应用文件
使用FastAPI框架构建
"""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from config import STATIC_DIR, TEMPLATES_DIR, HOST, PORT, DEBUG
from routers.auth import router as auth_router, get_current_user_optional, get_current_user_required
from routers.categories import router as categories_router
from routers.cds import router as cds_router
from routers.borrow import router as borrow_router
from routers.stats import router as stats_router
from utils.database import execute_query


# 初始化模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    print("CD管理系统启动中...")
    print(f"服务器地址: http://{HOST}:{PORT}")
    print("测试账号:")
    print("  管理员: admin / admin123")
    print("  普通用户: user1 / user123")
    yield
    print("CD管理系统已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="CD管理系统",
    description="一个基于FastAPI+SQLite+Bootstrap的CD管理系统",
    version="1.0.0",
    lifespan=lifespan
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 注册路由
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(cds_router)
app.include_router(borrow_router)
app.include_router(stats_router)


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    首页
    """
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # 获取一些统计数据用于首页展示
    # 统计总CD数量
    cd_count = execute_query(
        "SELECT COUNT(*) as count FROM cds",
        fetchone=True
    )
    
    # 统计总分类数量
    category_count = execute_query(
        "SELECT COUNT(*) as count FROM categories",
        fetchone=True
    )
    
    # 统计借出中的CD数量
    borrowed_count = execute_query(
        "SELECT COUNT(*) as count FROM borrow_records WHERE status = 'borrowed'",
        fetchone=True
    )
    
    # 统计可用库存
    available_stock = execute_query(
        "SELECT SUM(available_quantity) as total FROM cds",
        fetchone=True
    )
    
    # 获取最近的借还记录
    recent_records = execute_query(
        """
        SELECT br.*, c.title as cd_title, u.username as user_name
        FROM borrow_records br
        JOIN cds c ON br.cd_id = c.id
        JOIN users u ON br.user_id = u.id
        ORDER BY br.borrow_date DESC
        LIMIT 5
        """
    )
    
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": {
                "total_cds": cd_count[0]["count"] if cd_count else 0,
                "total_categories": category_count[0]["count"] if category_count else 0,
                "borrowed_cds": borrowed_count[0]["count"] if borrowed_count else 0,
                "available_stock": available_stock[0]["total"] if available_stock and available_stock[0]["total"] else 0
            },
            "recent_records": recent_records or []
        }
    )


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """
    404错误处理
    """
    current_user = get_current_user_optional(request)
    return templates.TemplateResponse(
        "errors/404.html",
        {
            "request": request,
            "current_user": current_user
        },
        status_code=404
    )


@app.exception_handler(403)
async def forbidden_exception_handler(request: Request, exc):
    """
    403错误处理
    """
    current_user = get_current_user_optional(request)
    return templates.TemplateResponse(
        "errors/403.html",
        {
            "request": request,
            "current_user": current_user
        },
        status_code=403
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )

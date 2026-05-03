"""
农场管理系统 - 主应用入口
使用FastAPI + SQLAlchemy + SQLite
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import init_db, get_db
from app.routers import farm_router, plot_router, crop_router, staff_router
from app.routers.role import router as role_router
from app.crud.role import role_crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库和默认角色
    """
    # 启动时执行
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")
    
    # 初始化默认角色
    print("正在初始化默认角色...")
    db = next(get_db())
    try:
        roles = role_crud.init_default_roles(db)
        print(f"已初始化 {len(roles)} 个系统角色")
    except Exception as e:
        print(f"初始化角色时出错: {e}")
    finally:
        db.close()
    print("角色初始化完成！")
    
    yield
    # 关闭时执行（如果需要）


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="农场管理系统 - 用于管理农场信息、地块、作物和人员",
    lifespan=lifespan,
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板目录
templates = Jinja2Templates(directory="templates")

# 注册API路由
app.include_router(farm_router)
app.include_router(plot_router)
app.include_router(crop_router)
app.include_router(staff_router)
app.include_router(role_router)


# 前端页面路由
@app.get("/", tags=["页面"])
async def index(request: Request):
    """
    首页
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/farms", tags=["页面"])
async def farms_page(request: Request):
    """
    农场管理页面
    """
    return templates.TemplateResponse("farms.html", {"request": request})


@app.get("/plots", tags=["页面"])
async def plots_page(request: Request):
    """
    地块管理页面
    """
    return templates.TemplateResponse("plots.html", {"request": request})


@app.get("/crops", tags=["页面"])
async def crops_page(request: Request):
    """
    作物档案页面
    """
    return templates.TemplateResponse("crops.html", {"request": request})


@app.get("/staff", tags=["页面"])
async def staff_page(request: Request):
    """
    人员管理页面
    """
    return templates.TemplateResponse("staff.html", {"request": request})


@app.get("/roles", tags=["页面"])
async def roles_page(request: Request):
    """
    角色管理页面
    """
    return templates.TemplateResponse("roles.html", {"request": request})


@app.get("/test", tags=["页面"])
async def test_page(request: Request):
    """
    测试页面
    """
    return templates.TemplateResponse("test.html", {"request": request})


if __name__ == "__main__":
    # 运行开发服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

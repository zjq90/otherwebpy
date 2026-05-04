"""
物业管理系统主应用文件
FastAPI应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import fee_items, properties, bills, reminders, invoices, test


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时的清理操作


app = FastAPI(
    title="物业管理系统 API",
    description="""
    物业管理系统后端API服务
    
    主要功能模块：
    - 费用项目设置：物业费、停车费、水电公摊、维修基金等
    - 房产管理：房产信息、业主信息
    - 账单管理：自动计费、账单生成、缴费管理
    - 催缴管理：逾期提醒、催缴记录
    - 票据管理：电子发票、收据开具
    - 财务对接：收入归集、报表统计
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(fee_items.router)
app.include_router(properties.router)
app.include_router(bills.router)
app.include_router(reminders.router)
app.include_router(invoices.router)
app.include_router(test.router)


@app.get("/", summary="系统根路径", tags=["系统"])
def root():
    """
    系统根路径，返回系统信息
    """
    return {
        "message": "物业管理系统 API 服务运行中",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/api/health", summary="健康检查", tags=["系统"])
def health_check():
    """
    健康检查接口，用于监控服务状态
    """
    return {
        "status": "healthy",
        "timestamp": "2026-05-04T00:00:00"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

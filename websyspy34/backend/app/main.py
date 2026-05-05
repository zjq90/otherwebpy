from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

from app.database import engine, Base
from app.routers import formulas, production, monitoring
from app import test_data

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="混凝土生产管理系统",
    description="基于FastAPI的混凝土生产管理系统后端API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(formulas.router)
app.include_router(production.router)
app.include_router(monitoring.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="混凝土生产管理系统 API",
        version="1.0.0",
        description="""
        # 混凝土生产管理系统 API 文档
        
        ## 功能模块
        
        ### 1. 配方管理
        - 配方的增删改查
        - 配方参数调整与历史记录
        
        ### 2. 生产计划与调度
        - 生产计划管理
        - 生产任务单管理
        - 资源（搅拌车、铲车等）管理与分配
        - 并行调度优化
        
        ### 3. 实时生产监控
        - 生产状态实时监控
        - 生产日志记录
        - 异常预警管理
        - 生产数据统计
        
        ## 认证说明
        当前版本暂未启用认证，所有API均可直接访问。
        """,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", summary="根路径", tags=["系统"])
def root():
    return {
        "message": "混凝土生产管理系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", summary="健康检查", tags=["系统"])
def health_check():
    return {"status": "healthy"}


@app.post("/init-test-data", summary="初始化测试数据", tags=["系统"])
def initialize_test_data():
    """
    初始化测试数据，用于功能测试
    """
    try:
        test_data.init_all_test_data()
        return {"message": "测试数据初始化成功", "status": "success"}
    except Exception as e:
        return {"message": f"测试数据初始化失败: {str(e)}", "status": "error"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

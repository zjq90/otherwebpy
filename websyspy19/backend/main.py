"""
权限管理系统 - 主应用入�?
基于 FastAPI 的后端服�?
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.middleware.log_middleware import LoggingMiddleware


def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    # 导入所有模型以确保它们被注�?
    from app.models.user import User
    from app.models.role import Role
    from app.models.permission import Permission
    from app.models.operation_log import OperationLog
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)


def init_data(db):
    """
    初始化基础数据
    创建默认角色、权限和超级管理员账�?
    """
    from app.core.security import get_password_hash
    from app.models.role import Role
    from app.models.permission import Permission
    from app.models.user import User
    
    # 检查是否已经初始化�?
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        return
    
    # 创建默认权限
    permissions_data = [
        # 用户管理权限
        {"name": "查看用户列表", "code": "user:read", "module": "user", "action": "read", "is_system": True},
        {"name": "创建用户", "code": "user:create", "module": "user", "action": "create", "is_system": True},
        {"name": "更新用户", "code": "user:update", "module": "user", "action": "update", "is_system": True},
        {"name": "删除用户", "code": "user:delete", "module": "user", "action": "delete", "is_system": True},
        
        # 角色管理权限
        {"name": "查看角色列表", "code": "role:read", "module": "role", "action": "read", "is_system": True},
        {"name": "创建角色", "code": "role:create", "module": "role", "action": "create", "is_system": True},
        {"name": "更新角色", "code": "role:update", "module": "role", "action": "update", "is_system": True},
        {"name": "删除角色", "code": "role:delete", "module": "role", "action": "delete", "is_system": True},
        
        # 权限管理权限
        {"name": "查看权限列表", "code": "permission:read", "module": "permission", "action": "read", "is_system": True},
        {"name": "创建权限", "code": "permission:create", "module": "permission", "action": "create", "is_system": True},
        {"name": "更新权限", "code": "permission:update", "module": "permission", "action": "update", "is_system": True},
        {"name": "删除权限", "code": "permission:delete", "module": "permission", "action": "delete", "is_system": True},
        
        # 日志管理权限
        {"name": "查看操作日志", "code": "log:read", "module": "log", "action": "read", "is_system": True},
        {"name": "删除操作日志", "code": "log:delete", "module": "log", "action": "delete", "is_system": True},
        
        # 测试功能权限
        {"name": "生成测试数据", "code": "test:generate", "module": "test", "action": "create", "is_system": True},
        {"name": "清理测试数据", "code": "test:cleanup", "module": "test", "action": "delete", "is_system": True},
    ]
    
    permissions = {}
    for perm_data in permissions_data:
        perm = Permission(**perm_data)
        db.add(perm)
        db.flush()
        permissions[perm_data["code"]] = perm
    
    # 创建默认角色
    roles_data = [
        {
            "name": "超级管理",
            "code": "superadmin",
            "description": "系统超级管理员，拥有所有权",
            "is_system": True,
            "permissions": list(permissions.values())
        },
        {
            "name": "管理",
            "code": "admin",
            "description": "系统管理员，可以管理用户和角",
            "is_system": True,
            "permissions": [
                permissions["user:read"],
                permissions["user:create"],
                permissions["user:update"],
                permissions["user:delete"],
                permissions["role:read"],
                permissions["role:create"],
                permissions["role:update"],
                permissions["role:delete"],
                permissions["log:read"],
            ]
        },
        {
            "name": "财务",
            "code": "finance",
            "description": "财务人员，可以查看财务相关数",
            "is_system": True,
            "permissions": [
                permissions["user:read"],
            ]
        },
        {
            "name": "维修",
            "code": "maintenance",
            "description": "维修人员，可以查看维修相关数",
            "is_system": True,
            "permissions": [
                permissions["user:read"],
            ]
        },
        {
            "name": "前台",
            "code": "reception",
            "description": "前台人员，可以查看和管理基础数据",
            "is_system": True,
            "permissions": [
                permissions["user:read"],
            ]
        },
    ]
    
    for role_data in roles_data:
        role_permissions = role_data.pop("permissions", [])
        role = Role(**role_data)
        role.permissions = role_permissions
        db.add(role)
        db.flush()
        
        # 保存角色引用用于后续创建管理�?
        if role.code == "superadmin":
            superadmin_role = role
    
    # 创建超级管理员账�?
    admin_user = User(
        username="admin",
        email="admin@example.com",
        phone="13800138000",
        full_name="系统管理",
        is_active=True,
        is_superuser=True,
        hashed_password=get_password_hash("admin123")
    )
    admin_user.roles = [superadmin_role]
    db.add(admin_user)
    
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库和基础数据
    """
    # 初始化数据库
    init_db()
    
    # 初始化基础数据
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        init_data(db)
    finally:
        db.close()
    
    yield
    
    # 应用关闭时的清理工作
    pass


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于 FastAPI + SQLite 的权限管理系",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# 添加 CORS 中间�?
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加日志中间�?
app.add_middleware(LoggingMiddleware)


# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求参数验证异常处理
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "参数验证失败",
            "detail": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "服务器内部错",
            "detail": str(exc)
        }
    )


# 包含 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


# 健康检查端�?
@app.get("/health", summary="健康检")
def health_check():
    """
    健康检查接�?
    用于检查服务是否正常运�?
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME
    }


# 根路径重定向到文�?
@app.get("/", include_in_schema=False)
def root():
    """
    根路径重定向�?API 文档
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    
    # 启动开发服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

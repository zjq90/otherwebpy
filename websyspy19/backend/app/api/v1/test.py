"""
测试功能相关API路由
提供测试数据生成、权限测试、接口测试等功能
"""

from typing import Any, List, Optional
from datetime import datetime, timedelta
import random
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.config import settings
from app.crud.user import user_crud
from app.crud.role import role_crud
from app.crud.permission import permission_crud
from app.crud.operation_log import operation_log_crud
from app.models.user import User, user_role
from app.models.role import Role
from app.models.permission import Permission
from app.models.operation_log import OperationLog
from app.schemas.common import ResponseModel, SuccessResponse
from app.middleware.auth_middleware import require_permission, get_current_active_user


router = APIRouter()


@router.post("/generate-data", response_model=ResponseModel[dict], summary="生成测试数据")
def generate_test_data(
    user_count: int = Query(10, ge=1, le=100, description="生成用户数量"),
    log_count: int = Query(50, ge=1, le=1000, description="生成操作日志数量"),
    current_user: User = Depends(require_permission("test:generate")),
    db: Session = Depends(get_db)
) -> Any:
    """
    生成测试数据
    
    需�?`test:generate` 权限
    
    参数:
        user_count: 生成用户数量
        log_count: 生成操作日志数量
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        生成结果
    """
    created_users = 0
    created_logs = 0
    
    # 生成测试用户
    first_names = ["�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?,
                   "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?]
    last_names = ["�?, "�?, "�?, "秀�?, "�?, "�?, "�?, "�?, "�?, "�?,
                  "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?, "秀�?, "�?]
    roles = db.query(Role).filter(Role.is_active == True).all()
    
    for i in range(user_count):
        # 生成用户�?
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = first_name + last_name
        username = f"test_user_{i+1:03d}"
        
        # 检查用户名是否已存�?
        if user_crud.get_by_username(db, username=username):
            continue
        
        # 创建用户
        hashed_password = get_password_hash("123456")
        user = User(
            username=username,
            email=f"{username}@example.com",
            phone=f"138{random.randint(10000000, 99999999)}",
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            hashed_password=hashed_password,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        db.add(user)
        db.flush()
        
        # 随机分配角色
        if roles:
            # 随机选择1-2个角�?
            selected_roles = random.sample(roles, min(random.randint(1, 2), len(roles)))
            user.roles = selected_roles
        
        db.commit()
        created_users += 1
    
    # 生成测试操作日志
    operation_types = ["login", "logout", "read", "create", "update", "delete"]
    operation_names = {
        "login": "用户登录",
        "logout": "用户登出",
        "read": "查看数据",
        "create": "创建数据",
        "update": "更新数据",
        "delete": "删除数据"
    }
    modules = ["auth", "user", "role", "permission", "log", "other"]
    statuses = ["success", "failed"]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    ]
    
    # 获取所有用户用于关联日�?
    all_users = db.query(User).filter(User.is_active == True).all()
    
    for i in range(log_count):
        operation_type = random.choice(operation_types)
        module = random.choice(modules)
        status = "success" if random.random() > 0.1 else "failed"
        
        # 随机选择一个用户（可能为空，模拟未登录操作�?
        user = random.choice(all_users) if all_users and random.random() > 0.2 else None
        
        # 生成随机时间（过�?0天内�?
        created_at = datetime.utcnow() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        log = OperationLog(
            operation_type=operation_type,
            operation_name=operation_names.get(operation_type, "其他操作"),
            operation_desc=f"测试操作日志 #{i+1}",
            request_method=random.choice(["GET", "POST", "PUT", "DELETE"]) if operation_type not in ["login", "logout"] else "POST",
            request_url=f"/api/v1/{module}/",
            request_params=json.dumps({"test": True, "data": f"test_data_{i}"}),
            request_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            user_agent=random.choice(user_agents),
            response_status=200 if status == "success" else random.choice([400, 401, 403, 404, 500]),
            response_data=None,
            user_id=user.id if user else None,
            username=user.username if user else None,
            module=module,
            status=status,
            error_message="测试错误信息" if status == "failed" else None,
            duration=random.randint(10, 500),
            created_at=created_at
        )
        db.add(log)
        created_logs += 1
    
    db.commit()
    
    return ResponseModel(
        code=200,
        message="测试数据生成成功",
        data={
            "created_users": created_users,
            "created_logs": created_logs,
            "default_password": "123456"
        }
    )


@router.post("/cleanup-test-data", response_model=SuccessResponse, summary="清理测试数据")
def cleanup_test_data(
    current_user: User = Depends(require_permission("test:cleanup")),
    db: Session = Depends(get_db)
) -> Any:
    """
    清理测试数据
    
    注意：此操作只会删除测试用户和测试日志，不会删除系统内置数据
    
    需�?`test:cleanup` 权限
    
    参数:
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        清理结果
    """
    import json
    # 删除测试用户（用户名�?test_user_ 开头）
    test_users = db.query(User).filter(User.username.like("test_user_%")).all()
    deleted_users = len(test_users)
    for user in test_users:
        # 解除角色关联
        user.roles = []
        db.delete(user)
    
    # 删除测试操作日志（包�?test_ 字样的描述）
    test_logs = db.query(OperationLog).filter(OperationLog.operation_desc.like("%测试%")).all()
    deleted_logs = len(test_logs)
    for log in test_logs:
        db.delete(log)
    
    db.commit()
    
    return SuccessResponse(
        code=200,
        message=f"成功清理测试数据：删�?{deleted_users} 个测试用户，{deleted_logs} 条测试日�?
    )


@router.get("/test-permission", response_model=ResponseModel[dict], summary="权限测试接口")
def test_permission(
    required_permission: str = Query(..., description="需要测试的权限代码"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    测试当前用户是否拥有指定权限
    
    此接口用于测试权限系统是否正常工�?
    
    参数:
        required_permission: 需要测试的权限代码
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        权限检查结�?
    """
    # 检查权�?
    has_permission = current_user.has_permission(required_permission)
    
    # 获取用户的所有权�?
    user_permissions = []
    if current_user.is_superuser:
        user_permissions = ["*（超级管理员，拥有所有权限）"]
    else:
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.append(perm.code)
    
    return ResponseModel(
        code=200,
        message="权限检查完�?,
        data={
            "user_id": current_user.id,
            "username": current_user.username,
            "is_superuser": current_user.is_superuser,
            "required_permission": required_permission,
            "has_permission": has_permission,
            "user_permissions": list(set(user_permissions))
        }
    )


@router.get("/system-info", response_model=ResponseModel[dict], summary="获取系统信息")
def get_system_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取系统基本信息
    
    包括用户统计、角色统计、权限统计、日志统计等
    
    参数:
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        系统信息
    """
    # 用户统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    superusers = db.query(User).filter(User.is_superuser == True).count()
    
    # 角色统计
    total_roles = db.query(Role).count()
    active_roles = db.query(Role).filter(Role.is_active == True).count()
    system_roles = db.query(Role).filter(Role.is_system == True).count()
    
    # 权限统计
    total_permissions = db.query(Permission).count()
    active_permissions = db.query(Permission).filter(Permission.is_active == True).count()
    system_permissions = db.query(Permission).filter(Permission.is_system == True).count()
    
    # 日志统计
    total_logs = db.query(OperationLog).count()
    success_logs = db.query(OperationLog).filter(OperationLog.status == "success").count()
    failed_logs = db.query(OperationLog).filter(OperationLog.status == "failed").count()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "users": {
                "total": total_users,
                "active": active_users,
                "superusers": superusers
            },
            "roles": {
                "total": total_roles,
                "active": active_roles,
                "system": system_roles
            },
            "permissions": {
                "total": total_permissions,
                "active": active_permissions,
                "system": system_permissions
            },
            "logs": {
                "total": total_logs,
                "success": success_logs,
                "failed": failed_logs
            },
            "system_version": settings.VERSION,
            "project_name": settings.PROJECT_NAME
        }
    )

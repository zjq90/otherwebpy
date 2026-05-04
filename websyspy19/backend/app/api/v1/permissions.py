"""
权限管理相关API路由
处理权限的增删改�?
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.permission import permission_crud
from app.models.user import User
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.common import ResponseModel, PaginatedResponse, SuccessResponse
from app.middleware.auth_middleware import require_permission


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[dict], summary="获取权限列表")
def get_permissions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（权限名称、代码、描述）"),
    module: Optional[str] = Query(None, description="模块筛�?),
    current_user: User = Depends(require_permission("permission:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    分页获取权限列表
    
    需�?`permission:read` 权限
    
    参数:
        page: 页码
        page_size: 每页数量
        keyword: 搜索关键�?
        module: 模块筛�?
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        分页的权限列�?
    """
    # 计算跳过的记录数
    skip = (page - 1) * page_size
    
    # 获取权限列表
    permissions, total = permission_crud.get_multi(
        db, skip=skip, limit=page_size, keyword=keyword, module=module
    )
    
    # 构建响应数据
    permission_data = []
    for perm in permissions:
        permission_data.append({
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "description": perm.description,
            "module": perm.module,
            "action": perm.action,
            "is_active": perm.is_active,
            "is_system": perm.is_system,
            "created_at": perm.created_at,
            "updated_at": perm.updated_at
        })
    
    # 计算总页�?
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data=permission_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/all", response_model=ResponseModel[List[dict]], summary="获取所有权�?)
def get_all_permissions(
    module: Optional[str] = Query(None, description="模块筛�?),
    current_user: User = Depends(require_permission("permission:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取所有权限（不分页）
    
    需�?`permission:read` 权限
    
    参数:
        module: 模块筛�?
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        所有权限列�?
    """
    # 获取所有权�?
    permissions, total = permission_crud.get_multi(db, skip=0, limit=1000, module=module)
    
    # 构建响应数据
    permission_data = []
    for perm in permissions:
        permission_data.append({
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "description": perm.description,
            "module": perm.module,
            "action": perm.action,
            "is_active": perm.is_active
        })
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=permission_data
    )


@router.get("/modules", response_model=ResponseModel[List[str]], summary="获取所有权限模�?)
def get_permission_modules(
    current_user: User = Depends(require_permission("permission:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取所有权限模块名�?
    
    需�?`permission:read` 权限
    
    参数:
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        模块名称列表
    """
    modules = permission_crud.get_all_modules(db)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=modules
    )


@router.get("/{permission_id}", response_model=ResponseModel[PermissionResponse], summary="获取权限详情")
def get_permission(
    permission_id: int,
    current_user: User = Depends(require_permission("permission:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单个权限的详细信�?
    
    需�?`permission:read` 权限
    
    参数:
        permission_id: 权限ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        权限详细信息
    """
    # 获取权限
    permission = permission_crud.get_by_id(db, permission_id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存�?
        )
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=permission
    )


@router.post("/", response_model=ResponseModel[dict], summary="创建权限")
def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_permission("permission:create")),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新权�?
    
    需�?`permission:create` 权限
    
    参数:
        permission_data: 权限创建数据
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        创建的权限信�?
    """
    # 检查权限代码是否已存在
    if permission_crud.get_by_code(db, code=permission_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限代码已存�?
        )
    
    # 创建权限
    permission = permission_crud.create(db, obj_in=permission_data)
    
    # 构建响应数据
    permission_response = {
        "id": permission.id,
        "name": permission.name,
        "code": permission.code,
        "description": permission.description,
        "module": permission.module,
        "action": permission.action,
        "is_active": permission.is_active,
        "created_at": permission.created_at
    }
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data=permission_response
    )


@router.put("/{permission_id}", response_model=ResponseModel[dict], summary="更新权限")
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    current_user: User = Depends(require_permission("permission:update")),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新权限信息
    
    需�?`permission:update` 权限
    
    参数:
        permission_id: 权限ID
        permission_data: 权限更新数据
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        更新后的权限信息
    """
    # 获取权限
    permission = permission_crud.get_by_id(db, permission_id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存�?
        )
    
    # 系统内置权限不能修改
    if permission.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统内置权限不能修改"
        )
    
    # 检查权限代码是否已被其他权限使�?
    if permission_data.code and permission_data.code != permission.code:
        existing_permission = permission_crud.get_by_code(db, code=permission_data.code)
        if existing_permission and existing_permission.id != permission_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限代码已存�?
            )
    
    # 更新权限
    permission = permission_crud.update(db, db_obj=permission, obj_in=permission_data)
    
    # 构建响应数据
    permission_response = {
        "id": permission.id,
        "name": permission.name,
        "code": permission.code,
        "description": permission.description,
        "module": permission.module,
        "action": permission.action,
        "is_active": permission.is_active,
        "updated_at": permission.updated_at
    }
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data=permission_response
    )


@router.delete("/{permission_id}", response_model=SuccessResponse, summary="删除权限")
def delete_permission(
    permission_id: int,
    current_user: User = Depends(require_permission("permission:delete")),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除权限
    
    需�?`permission:delete` 权限
    
    参数:
        permission_id: 权限ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        成功响应
    """
    # 获取权限
    permission = permission_crud.get_by_id(db, permission_id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存�?
        )
    
    # 系统内置权限不能删除
    if permission.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统内置权限不能删除"
        )
    
    # 检查权限是否被角色使用
    if permission.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该权限已被角色使用，不能删除"
        )
    
    # 删除权限
    permission_crud.remove(db, permission_id=permission_id)
    
    return SuccessResponse(
        code=200,
        message="删除成功"
    )

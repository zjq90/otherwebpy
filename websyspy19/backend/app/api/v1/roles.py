"""
角色管理相关API路由
处理角色的增删改查、权限分配等
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.role import role_crud
from app.crud.permission import permission_crud
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.common import ResponseModel, PaginatedResponse, SuccessResponse
from app.middleware.auth_middleware import require_permission


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[dict], summary="获取角色列表")
def get_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（角色名称、代码、描述）"),
    current_user: User = Depends(require_permission("role:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    分页获取角色列表
    
    需�?`role:read` 权限
    
    参数:
        page: 页码
        page_size: 每页数量
        keyword: 搜索关键�?
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        分页的角色列�?
    """
    # 计算跳过的记录数
    skip = (page - 1) * page_size
    
    # 获取角色列表
    roles, total = role_crud.get_multi(db, skip=skip, limit=page_size, keyword=keyword)
    
    # 构建响应数据
    role_data = []
    for role in roles:
        role_data.append({
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "is_active": role.is_active,
            "is_system": role.is_system,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
            "permissions": [
                {"id": perm.id, "name": perm.name, "code": perm.code}
                for perm in role.permissions
            ]
        })
    
    # 计算总页�?
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data=role_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/all", response_model=ResponseModel[List[dict]], summary="获取所有角�?)
def get_all_roles(
    current_user: User = Depends(require_permission("role:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取所有角色（不分页）
    
    需�?`role:read` 权限
    
    参数:
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        所有角色列�?
    """
    # 获取所有角�?
    roles, total = role_crud.get_multi(db, skip=0, limit=1000)
    
    # 构建响应数据
    role_data = []
    for role in roles:
        role_data.append({
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "is_active": role.is_active
        })
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=role_data
    )


@router.get("/{role_id}", response_model=ResponseModel[dict], summary="获取角色详情")
def get_role(
    role_id: int,
    current_user: User = Depends(require_permission("role:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单个角色的详细信�?
    
    需�?`role:read` 权限
    
    参数:
        role_id: 角色ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        角色详细信息
    """
    # 获取角色
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存�?
        )
    
    # 构建响应数据
    role_data = {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_active": role.is_active,
        "is_system": role.is_system,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "permissions": [
            {
                "id": perm.id,
                "name": perm.name,
                "code": perm.code,
                "description": perm.description,
                "module": perm.module,
                "action": perm.action
            }
            for perm in role.permissions
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=role_data
    )


@router.post("/", response_model=ResponseModel[dict], summary="创建角色")
def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permission("role:create")),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新角�?
    
    需�?`role:create` 权限
    
    参数:
        role_data: 角色创建数据
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        创建的角色信�?
    """
    # 检查角色代码是否已存在
    if role_crud.get_by_code(db, code=role_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色代码已存�?
        )
    
    # 创建角色
    role = role_crud.create(db, obj_in=role_data)
    
    # 构建响应数据
    role_response = {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_active": role.is_active,
        "created_at": role.created_at
    }
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data=role_response
    )


@router.put("/{role_id}", response_model=ResponseModel[dict], summary="更新角色")
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permission("role:update")),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新角色信息
    
    需�?`role:update` 权限
    
    参数:
        role_id: 角色ID
        role_data: 角色更新数据
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        更新后的角色信息
    """
    # 获取角色
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存�?
        )
    
    # 系统内置角色不能修改
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统内置角色不能修改"
        )
    
    # 检查角色代码是否已被其他角色使�?
    if role_data.code and role_data.code != role.code:
        existing_role = role_crud.get_by_code(db, code=role_data.code)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色代码已存�?
            )
    
    # 更新角色
    role = role_crud.update(db, db_obj=role, obj_in=role_data)
    
    # 构建响应数据
    role_response = {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_active": role.is_active,
        "updated_at": role.updated_at
    }
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data=role_response
    )


@router.delete("/{role_id}", response_model=SuccessResponse, summary="删除角色")
def delete_role(
    role_id: int,
    current_user: User = Depends(require_permission("role:delete")),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除角色
    
    需�?`role:delete` 权限
    
    参数:
        role_id: 角色ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        成功响应
    """
    # 获取角色
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存�?
        )
    
    # 系统内置角色不能删除
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统内置角色不能删除"
        )
    
    # 检查角色是否被用户使用
    if role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该角色已被用户使用，不能删除"
        )
    
    # 删除角色
    role_crud.remove(db, role_id=role_id)
    
    return SuccessResponse(
        code=200,
        message="删除成功"
    )


@router.post("/{role_id}/permissions", response_model=ResponseModel[dict], summary="分配角色权限")
def assign_permissions(
    role_id: int,
    permission_ids: List[int],
    current_user: User = Depends(require_permission("role:update")),
    db: Session = Depends(get_db)
) -> Any:
    """
    为角色分配权�?
    
    需�?`role:update` 权限
    
    参数:
        role_id: 角色ID
        permission_ids: 权限ID列表
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        更新后的角色权限信息
    """
    # 获取角色
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存�?
        )
    
    # 获取所有权�?
    from app.models.permission import Permission
    permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    
    # 检查是否所有权限都存在
    if len(permissions) != len(permission_ids):
        existing_ids = [perm.id for perm in permissions]
        missing_ids = [pid for pid in permission_ids if pid not in existing_ids]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"权限不存�? {missing_ids}"
        )
    
    # 更新角色权限
    role.permissions = permissions
    db.commit()
    db.refresh(role)
    
    # 构建响应数据
    response_data = {
        "role_id": role.id,
        "role_name": role.name,
        "role_code": role.code,
        "permissions": [
            {"id": perm.id, "name": perm.name, "code": perm.code}
            for perm in role.permissions
        ]
    }
    
    return ResponseModel(
        code=200,
        message="权限分配成功",
        data=response_data
    )

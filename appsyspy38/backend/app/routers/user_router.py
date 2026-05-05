"""
用户管理相关API路由
包含用户CRUD、角色管理、权限管理等功能
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from ..database import get_db
from ..models.user_models import User, Role, Permission
from ..schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserWithPermission,
    RoleCreate, RoleResponse, PermissionCreate, PermissionResponse,
    ApiResponse, PaginatedResponse
)
from ..utils.security import (
    get_password_hash, get_current_user, require_role, is_admin
)

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建用户（管理员权限）
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    result = await db.execute(select(User).where(User.phone == user_data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已存在"
        )
    
    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone,
        is_first_login=True
    )
    
    # 分配角色
    if user_data.role_codes:
        result = await db.execute(
            select(Role).where(Role.code.in_(user_data.role_codes))
        )
        roles = result.scalars().all()
        user.roles = list(roles)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 重新查询带角色的用户
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user.id)
    )
    user = result.scalar_one_or_none()
    
    return UserResponse.model_validate(user)


@router.get("", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表（管理员权限）
    """
    # 构建查询条件
    query = select(User).options(selectinload(User.roles))
    
    if keyword:
        query = query.where(
            (User.username.contains(keyword)) |
            (User.phone.contains(keyword)) |
            (User.real_name.contains(keyword))
        )
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    user_responses = [UserResponse.model_validate(u) for u in users]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=user_responses
    )


@router.get("/{user_id}", response_model=UserWithPermission)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户详情（管理员权限）
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取权限列表
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    
    user_response = UserWithPermission.model_validate(user)
    user_response.permissions = list(permissions)
    
    return user_response


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息（管理员权限）
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新字段
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户（管理员权限）
    注意：实际项目中通常使用软删除
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录用户"
        )
    
    # 软删除：禁用用户
    user.is_active = False
    user.updated_at = datetime.utcnow()
    await db.commit()
    
    return ApiResponse(message="用户已禁用")


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建角色（管理员权限）
    """
    result = await db.execute(select(Role).where(Role.code == role_data.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色代码已存在"
        )
    
    role = Role(**role_data.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return RoleResponse.model_validate(role)


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取角色列表
    """
    result = await db.execute(select(Role).where(Role.is_active == True))
    roles = result.scalars().all()
    
    return [RoleResponse.model_validate(r) for r in roles]


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建权限（管理员权限）
    """
    result = await db.execute(select(Permission).where(Permission.code == permission_data.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限代码已存在"
        )
    
    permission = Permission(**permission_data.model_dump())
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    
    return PermissionResponse.model_validate(permission)


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取权限列表（管理员权限）
    """
    result = await db.execute(select(Permission))
    permissions = result.scalars().all()
    
    return [PermissionResponse.model_validate(p) for p in permissions]


@router.post("/roles/{role_id}/permissions", response_model=ApiResponse)
async def assign_permissions_to_role(
    role_id: int,
    permission_ids: List[int],
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    为角色分配权限（管理员权限）
    """
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 查询权限
    result = await db.execute(
        select(Permission).where(Permission.id.in_(permission_ids))
    )
    permissions = result.scalars().all()
    
    # 更新角色权限
    role.permissions = list(permissions)
    role.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return ApiResponse(message="权限分配成功")


@router.post("/users/{user_id}/roles", response_model=ApiResponse)
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    为用户分配角色（管理员权限）
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 查询角色
    result = await db.execute(
        select(Role).where(Role.id.in_(role_ids))
    )
    roles = result.scalars().all()
    
    # 更新用户角色
    user.roles = list(roles)
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return ApiResponse(message="角色分配成功")

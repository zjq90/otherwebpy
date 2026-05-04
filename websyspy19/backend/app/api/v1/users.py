"""
用户管理相关API路由
处理用户的增删改查、角色分配等
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.user import user_crud
from app.crud.role import role_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles
from app.schemas.common import ResponseModel, PaginatedResponse, SuccessResponse
from app.middleware.auth_middleware import get_current_active_user, require_permission


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[dict], summary="获取用户列表")
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户名、邮箱、手机号、真实姓名）"),
    current_user: User = Depends(require_permission("user:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    分页获取用户列表
    
    需�?`user:read` 权限
    
    参数:
        page: 页码
        page_size: 每页数量
        keyword: 搜索关键�?
        current_user: 当前登录用户（自动获取）
        db: 数据库会�?
    
    返回:
        分页的用户列�?
    """
    # 计算跳过的记录数
    skip = (page - 1) * page_size
    
    # 获取用户列表
    users, total = user_crud.get_multi(db, skip=skip, limit=page_size, keyword=keyword)
    
    # 构建响应数据
    user_data = []
    for user in users:
        user_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
            "roles": [
                {"id": role.id, "name": role.name, "code": role.code}
                for role in user.roles
            ]
        })
    
    # 计算总页�?
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data=user_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=ResponseModel[UserWithRoles], summary="获取用户详情")
def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单个用户的详细信�?
    
    需�?`user:read` 权限
    
    参数:
        user_id: 用户ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        用户详细信息
    """
    # 获取用户
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存�?
        )
    
    # 构建响应数据
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "description": role.description
            }
            for role in user.roles
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=user_data
    )


@router.post("/", response_model=ResponseModel[dict], summary="创建用户")
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("user:create")),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新用�?
    
    需�?`user:create` 权限
    
    参数:
        user_data: 用户创建数据
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        创建的用户信�?
    """
    # 检查用户名是否已存�?
    if user_crud.get_by_username(db, username=user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email and user_crud.get_by_email(db, email=user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 检查手机号是否已存�?
    if user_data.phone and user_crud.get_by_phone(db, phone=user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被注�?
        )
    
    # 创建用户
    user = user_crud.create(db, obj_in=user_data)
    
    # 构建响应数据
    user_response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at
    }
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data=user_response
    )


@router.put("/{user_id}", response_model=ResponseModel[dict], summary="更新用户")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_permission("user:update")),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新用户信息
    
    需�?`user:update` 权限
    
    参数:
        user_id: 用户ID
        user_data: 用户更新数据
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        更新后的用户信息
    """
    # 获取用户
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存�?
        )
    
    # 不能更新自己的超级管理员状�?
    if user_id == current_user.id and user_data.is_superuser is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能修改自己的管理员状�?
        )
    
    # 检查用户名是否已被其他用户使用
    if user_data.username and user_data.username != user.username:
        existing_user = user_crud.get_by_username(db, username=user_data.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 检查邮箱是否已被其他用户使�?
    if user_data.email and user_data.email != user.email:
        existing_user = user_crud.get_by_email(db, email=user_data.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 检查手机号是否已被其他用户使用
    if user_data.phone and user_data.phone != user.phone:
        existing_user = user_crud.get_by_phone(db, phone=user_data.phone)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注�?
            )
    
    # 更新用户
    user = user_crud.update(db, db_obj=user, obj_in=user_data)
    
    # 构建响应数据
    user_response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "updated_at": user.updated_at
    }
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data=user_response
    )


@router.delete("/{user_id}", response_model=SuccessResponse, summary="删除用户")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:delete")),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除用户
    
    需�?`user:delete` 权限
    
    参数:
        user_id: 用户ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        成功响应
    """
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    # 获取用户
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存�?
        )
    
    # 删除用户
    user_crud.remove(db, user_id=user_id)
    
    return SuccessResponse(
        code=200,
        message="删除成功"
    )


@router.post("/{user_id}/roles", response_model=ResponseModel[dict], summary="分配用户角色")
def assign_roles(
    user_id: int,
    role_ids: List[int],
    current_user: User = Depends(require_permission("user:update")),
    db: Session = Depends(get_db)
) -> Any:
    """
    为用户分配角�?
    
    需�?`user:update` 权限
    
    参数:
        user_id: 用户ID
        role_ids: 角色ID列表
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        更新后的用户角色信息
    """
    # 获取用户
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存�?
        )
    
    # 获取所有角�?
    roles = db.query(User.__table__.c.id).filter(User.id.in_(role_ids)).all()
    # 这里需要修改，应该查询Role�?
    from app.models.role import Role
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    
    # 检查是否所有角色都存在
    if len(roles) != len(role_ids):
        existing_ids = [role.id for role in roles]
        missing_ids = [rid for rid in role_ids if rid not in existing_ids]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色不存�? {missing_ids}"
        )
    
    # 更新用户角色
    user.roles = roles
    db.commit()
    db.refresh(user)
    
    # 构建响应数据
    response_data = {
        "user_id": user.id,
        "username": user.username,
        "roles": [
            {"id": role.id, "name": role.name, "code": role.code}
            for role in user.roles
        ]
    }
    
    return ResponseModel(
        code=200,
        message="角色分配成功",
        data=response_data
    )

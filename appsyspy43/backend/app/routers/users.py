"""
用户管理路由模块
处理用户的增删改查等管理操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    DriverSimpleResponse,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.security import (
    get_password_hash,
    get_current_user,
    require_admin,
    require_dispatcher,
)

router = APIRouter(
    prefix="/api/users",
    tags=["用户管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("", response_model=ApiResponse[UserResponse], dependencies=[Depends(require_admin)])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新用户
    仅管理员可以创建用户
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
    
    # 检查司机角色是否提供驾驶证号
    if user_data.role == UserRole.DRIVER and not user_data.driver_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="司机角色必须提供驾驶证号"
        )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        phone=user_data.phone,
        role=user_data.role,
        driver_license=user_data.driver_license,
        status=UserStatus.IDLE if user_data.role == UserRole.DRIVER else UserStatus.ACTIVE,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    user_response = UserResponse.model_validate(new_user)
    return ApiResponse(
        code=200,
        message="用户创建成功",
        data=user_response,
    )


@router.get("", response_model=ApiResponse[PaginatedResponse[UserResponse]])
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    role: Optional[UserRole] = Query(None, description="用户角色筛选"),
    status: Optional[UserStatus] = Query(None, description="用户状态筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户名、姓名、手机号）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户列表
    支持分页、角色筛选、状态筛选和关键词搜索
    """
    # 构建查询条件
    query = select(User).where(User.is_deleted == False)
    
    # 角色筛选
    if role:
        query = query.where(User.role == role)
    
    # 状态筛选
    if status:
        query = query.where(User.status == status)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                User.username.contains(keyword),
                User.real_name.contains(keyword),
                User.phone.contains(keyword),
            )
        )
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    # 构建响应
    user_responses = [UserResponse.model_validate(user) for user in users]
    paginated_response = PaginatedResponse(
        items=user_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=paginated_response,
    )


@router.get("/drivers", response_model=ApiResponse[list[DriverSimpleResponse]])
async def get_available_drivers(
    status: Optional[UserStatus] = Query(None, description="司机状态筛选"),
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取司机列表
    用于任务分配时选择司机
    """
    query = select(User).where(
        User.is_deleted == False,
        User.role == UserRole.DRIVER,
    )
    
    if status:
        query = query.where(User.status == status)
    
    query = query.order_by(User.created_at.desc())
    result = await db.execute(query)
    drivers = result.scalars().all()
    
    driver_responses = [DriverSimpleResponse.model_validate(driver) for driver in drivers]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=driver_responses,
    )


@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个用户详情
    """
    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_response = UserResponse.model_validate(user)
    return ApiResponse(
        code=200,
        message="获取成功",
        data=user_response,
    )


@router.put("/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新用户信息
    管理员可以更新所有用户，普通用户只能更新自己的信息
    """
    # 检查权限：管理员可以更新所有用户，普通用户只能更新自己
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法更新其他用户信息"
        )
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户信息
    update_data = user_data.model_dump(exclude_unset=True)
    
    # 处理密码更新
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    # 检查手机号是否已被其他用户使用
    if "phone" in update_data and update_data["phone"] != user.phone:
        result = await db.execute(
            select(User).where(
                User.phone == update_data["phone"],
                User.id != user_id,
                User.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被使用"
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    user_response = UserResponse.model_validate(user)
    return ApiResponse(
        code=200,
        message="更新成功",
        data=user_response,
    )


@router.delete("/{user_id}", response_model=ApiResponse[dict], dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除用户（软删除）
    仅管理员可以删除用户
    """
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 软删除
    user.is_deleted = True
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功",
        data={},
    )

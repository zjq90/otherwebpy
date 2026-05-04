"""
用户管理路由模块
处理用户信息的查询、更新、禁用等管理操作
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from models import User, UserRole
from schemas import (
    UserResponse, UserUpdate, ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取用户列表（管理员权限）
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    role: Optional[UserRole] = Query(None, description="用户角色筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户名、姓名、手机号）"),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    
    需要管理员或工作人员权限
    支持分页、角色筛选和关键词搜索
    
    Args:
        page: 页码
        page_size: 每页数量
        role: 用户角色筛选
        keyword: 搜索关键词
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的用户列表
    """
    # 构建查询
    query = db.query(User)
    
    # 角色筛选
    if role:
        query = query.filter(User.role == role)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.real_name.contains(keyword)) |
            (User.phone.contains(keyword))
        )
    
    # 按创建时间倒序排列
    query = query.order_by(User.created_at.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    users_response = [UserResponse.model_validate(user) for user in paginated.items]
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"users": [u.model_dump() for u in users_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取用户详情
# ========================================

@router.get("/{user_id}", response_model=ResponseModel)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详情
    
    用户可以查看自己的信息
    管理员和工作人员可以查看所有用户信息
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含用户信息的响应
    """
    # 权限检查：只能查看自己的信息，或者管理员/工作人员可以查看所有
    if (current_user.id != user_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.STAFF]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该用户信息"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_response = UserResponse.model_validate(user)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"user": user_response.model_dump()}
    )

# ========================================
# 更新用户信息
# ========================================

@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    用户可以更新自己的信息
    管理员可以更新所有用户的信息
    
    Args:
        user_id: 用户ID
        user_data: 更新数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后用户信息的响应
    """
    # 权限检查
    if (current_user.id != user_id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该用户信息"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查手机号是否已被其他用户使用
    if user_data.phone and user_data.phone != user.phone:
        existing_phone = db.query(User).filter(
            User.phone == user_data.phone,
            User.id != user_id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被使用"
            )
    
    # 检查邮箱是否已被其他用户使用
    if user_data.email and user_data.email != user.email:
        existing_email = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 更新用户信息
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    user_response = UserResponse.model_validate(user)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={"user": user_response.model_dump()}
    )

# ========================================
# 禁用/启用用户（管理员权限）
# ========================================

@router.put("/{user_id}/toggle-status", response_model=ResponseModel)
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    切换用户状态（禁用/启用）
    
    需要管理员权限
    不能禁用自己的账户
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    # 不能禁用自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的账户"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 切换状态
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    status_text = "启用" if user.is_active else "禁用"
    user_response = UserResponse.model_validate(user)
    
    return ResponseModel(
        code=200,
        message=f"用户已{status_text}",
        data={"user": user_response.model_dump()}
    )

# ========================================
# 删除用户（管理员权限）
# ========================================

@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    删除用户
    
    需要管理员权限
    不能删除自己的账户
    
    Args:
        user_id: 用户ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除用户（级联删除相关数据）
    db.delete(user)
    db.commit()
    
    return ResponseModel(
        code=200,
        message="用户已删除",
        data=None
    )

# ========================================
# 获取当前用户统计信息
# ========================================

@router.get("/me/statistics", response_model=ResponseModel)
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的统计信息
    
    包括预约数量、未读消息数等
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含统计信息的响应
    """
    from models import Booking, Message, Review
    
    # 统计预约数量
    booking_count = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).count()
    
    # 统计未读消息数
    unread_message_count = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.is_read == False
    ).count()
    
    # 统计评价数量
    review_count = db.query(Review).filter(
        Review.user_id == current_user.id
    ).count()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "booking_count": booking_count,
            "unread_message_count": unread_message_count,
            "review_count": review_count
        }
    )

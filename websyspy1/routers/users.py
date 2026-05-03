"""
用户管理路由模块
提供用户列表、详情、更新、删除等管理功能
（仅管理员可访问）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from database import get_db
from models import User
from schemas import UserResponse, ApiResponse, PaginatedResponse
from routers.auth import get_current_admin_user
from config import PAGE_SIZE

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def get_users(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    username: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    获取用户列表接口（管理员专用）
    支持分页、用户名搜索、邮箱搜索、状态过滤
    
    参数:
        page: 页码
        page_size: 每页数量
        username: 用户名搜索关键词
        email: 邮箱搜索关键词
        is_active: 是否激活
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 用户列表数据
    """
    # 构建查询
    query = db.query(User)
    
    # 用户名过滤
    if username:
        query = query.filter(User.username.contains(username))
    
    # 邮箱过滤
    if email:
        query = query.filter(User.email.contains(email))
    
    # 状态过滤
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    # 转换为响应模型
    user_responses = [UserResponse.from_orm(user) for user in users]
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": user_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/{user_id}", response_model=ApiResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    获取用户详情接口（管理员专用）
    
    参数:
        user_id: 用户ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 用户详情
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"user": UserResponse.from_orm(user)}
    )


@router.put("/{user_id}/toggle-active", response_model=ApiResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    切换用户激活状态接口（管理员专用）
    用于启用或禁用用户账号
    
    参数:
        user_id: 用户ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能禁用自己
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的账号"
        )
    
    # 切换状态
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return ApiResponse(
        success=True,
        message=f"用户已{'激活' if user.is_active else '禁用'}",
        data={"user": UserResponse.from_orm(user)}
    )


@router.put("/{user_id}/toggle-admin", response_model=ApiResponse)
def toggle_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    切换用户管理员权限接口（管理员专用）
    
    参数:
        user_id: 用户ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能取消自己的管理员权限
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能取消自己的管理员权限"
        )
    
    # 切换权限
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    
    return ApiResponse(
        success=True,
        message=f"用户已{'成为' if user.is_admin else '取消'}管理员",
        data={"user": UserResponse.from_orm(user)}
    )


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    删除用户接口（管理员专用）
    
    参数:
        user_id: 用户ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="用户已删除"
    )

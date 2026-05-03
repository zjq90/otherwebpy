"""
秘钥申请管理路由模块
提供秘钥申请的创建、查询、审核等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from datetime import datetime, timedelta

from database import get_db
from models import KeyApplication, User
from schemas import KeyApplicationCreate, KeyApplicationUpdate, KeyApplicationResponse, ApiResponse
from routers.auth import get_current_active_user, get_current_admin_user
from security import generate_api_key
from config import PAGE_SIZE

router = APIRouter()


@router.post("/", response_model=ApiResponse)
def create_application(
    app_data: KeyApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建秘钥申请接口（登录用户专用）
    
    参数:
        app_data: 申请数据
        db: 数据库会话
        current_user: 当前登录用户
    
    返回:
        ApiResponse: 创建结果
    """
    existing_pending = db.query(KeyApplication).filter(
        KeyApplication.user_id == current_user.id,
        KeyApplication.status == "pending"
    ).first()
    
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已有待审核的秘钥申请，请等待审核"
        )
    
    new_application = KeyApplication(
        user_id=current_user.id,
        application_type=app_data.application_type,
        company_name=app_data.company_name,
        website=app_data.website,
        use_case=app_data.use_case,
        expected_calls=app_data.expected_calls,
        status="pending"
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    return ApiResponse(
        success=True,
        message="秘钥申请提交成功",
        data={"application": KeyApplicationResponse.from_orm(new_application)}
    )


@router.get("/my-applications", response_model=ApiResponse)
def get_my_applications(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的秘钥申请列表（登录用户专用）
    
    参数:
        page: 页码
        page_size: 每页数量
        status: 状态过滤
        db: 数据库会话
        current_user: 当前登录用户
    
    返回:
        ApiResponse: 申请列表数据
    """
    query = db.query(KeyApplication).filter(KeyApplication.user_id == current_user.id)
    
    if status:
        query = query.filter(KeyApplication.status == status)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    applications = query.order_by(KeyApplication.created_at.desc()).offset(offset).limit(page_size).all()
    
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    app_responses = [KeyApplicationResponse.from_orm(app) for app in applications]
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": app_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/", response_model=ApiResponse)
def get_all_applications(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    获取所有秘钥申请列表（管理员专用）
    
    参数:
        page: 页码
        page_size: 每页数量
        status: 状态过滤
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 申请列表数据
    """
    query = db.query(KeyApplication)
    
    if status:
        query = query.filter(KeyApplication.status == status)
    
    total = query.count()
    
    offset = (page - 1) * page_size
    applications = query.order_by(KeyApplication.created_at.desc()).offset(offset).limit(page_size).all()
    
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    app_responses = []
    for app in applications:
        app_response = KeyApplicationResponse.from_orm(app)
        user = db.query(User).filter(User.id == app.user_id).first()
        app_response_dict = app_response.model_dump()
        app_response_dict['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        } if user else None
        app_responses.append(app_response_dict)
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": app_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/{application_id}", response_model=ApiResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取秘钥申请详情接口
    管理员可查看所有申请，普通用户只能查看自己的申请
    
    参数:
        application_id: 申请ID
        db: 数据库会话
        current_user: 当前登录用户
    
    返回:
        ApiResponse: 申请详情
    """
    application = db.query(KeyApplication).filter(KeyApplication.id == application_id).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    
    if not current_user.is_admin and application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此申请"
        )
    
    app_response = KeyApplicationResponse.from_orm(application)
    user = db.query(User).filter(User.id == application.user_id).first()
    app_response_dict = app_response.model_dump()
    app_response_dict['user'] = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    } if user else None
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"application": app_response_dict}
    )


@router.put("/{application_id}/review", response_model=ApiResponse)
def review_application(
    application_id: int,
    review_data: KeyApplicationUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    审核秘钥申请接口（管理员专用）
    通过时自动生成秘钥
    
    参数:
        application_id: 申请ID
        review_data: 审核数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 审核结果
    """
    application = db.query(KeyApplication).filter(KeyApplication.id == application_id).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    
    if application.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此申请已被审核"
        )
    
    if review_data.status:
        application.status = review_data.status
        application.review_notes = review_data.review_notes
        
        if review_data.status == "approved":
            application.api_key = generate_api_key()
            application.valid_until = datetime.now() + timedelta(days=365)
    
    db.commit()
    db.refresh(application)
    
    return ApiResponse(
        success=True,
        message=f"申请已{'通过' if application.status == 'approved' else '拒绝'}",
        data={"application": KeyApplicationResponse.from_orm(application)}
    )


@router.delete("/{application_id}", response_model=ApiResponse)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除秘钥申请接口
    管理员可删除所有申请，普通用户只能删除自己的待审核申请
    
    参数:
        application_id: 申请ID
        db: 数据库会话
        current_user: 当前登录用户
    
    返回:
        ApiResponse: 删除结果
    """
    application = db.query(KeyApplication).filter(KeyApplication.id == application_id).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    
    if not current_user.is_admin:
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此申请"
            )
        if application.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能删除待审核的申请"
            )
    
    db.delete(application)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="申请已删除"
    )

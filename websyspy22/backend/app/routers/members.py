"""
会员管理API路由
提供会员信息采集、查询、更新、删除等功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.database import get_db
from app.models.member import Member, MemberStatus, RegistrationChannel
from app.schemas.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    VerificationRequest,
    PhoneVerificationCodeRequest,
)
from app.schemas.common import (
    ApiResponse,
    SuccessResponse,
    PaginatedResponse,
    PageParams,
)
from app.services.verification_service import verification_service
from app.services.level_service import level_service

router = APIRouter(
    prefix="/api/members",
    tags=["会员管理"],
    responses={404: {"description": "未找到"}},
)


@router.post(
    "",
    response_model=ApiResponse[MemberResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新增会员",
    description="创建新会员，支持线上（官网）和线下（前台录入）两种渠道",
)
def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db),
):
    """
    创建新会员
    - **member_data**: 会员信息
    """
    # 检查手机号是否已存在
    existing_member = db.query(Member).filter(Member.phone == member_data.phone).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"手机号 {member_data.phone} 已被注册"
        )
    
    # 检查身份证号是否已存在（如果提供）
    if member_data.id_card:
        existing_by_id = db.query(Member).filter(Member.id_card == member_data.id_card).first()
        if existing_by_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"身份证号 {member_data.id_card} 已被注册"
            )
    
    # 创建会员对象
    new_member = Member(
        **member_data.model_dump(),
        status=MemberStatus.ACTIVE,
        is_verified=0,
        current_level="bronze",
        total_consumption=0,
        total_visits=0,
    )
    
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return ApiResponse(
        code=201,
        message="会员创建成功",
        data=MemberResponse.model_validate(new_member)
    )


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[MemberListResponse]],
    summary="获取会员列表",
    description="分页查询会员列表，支持按姓名、手机号、状态、等级等条件筛选",
)
def get_members(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（姓名/手机号）"),
    status: Optional[MemberStatus] = Query(None, description="账户状态"),
    level: Optional[str] = Query(None, description="会员等级"),
    registration_channel: Optional[RegistrationChannel] = Query(None, description="注册渠道"),
    is_verified: Optional[int] = Query(None, description="是否实名认证：0-否，1-是"),
    db: Session = Depends(get_db),
):
    """
    获取会员列表
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    - **keyword**: 搜索关键词，支持姓名和手机号模糊搜索
    - **status**: 账户状态筛选
    - **level**: 会员等级筛选
    - **registration_channel**: 注册渠道筛选
    - **is_verified**: 实名认证状态筛选
    """
    # 构建查询
    query = db.query(Member)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                Member.name.contains(keyword),
                Member.phone.contains(keyword)
            )
        )
    
    # 状态筛选
    if status:
        query = query.filter(Member.status == status)
    
    # 等级筛选
    if level:
        query = query.filter(Member.current_level == level)
    
    # 注册渠道筛选
    if registration_channel:
        query = query.filter(Member.registration_channel == registration_channel)
    
    # 实名认证状态筛选
    if is_verified is not None:
        query = query.filter(Member.is_verified == is_verified)
    
    # 获取总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    members = query.order_by(Member.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[MemberListResponse.model_validate(m) for m in members],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/{member_id}",
    response_model=ApiResponse[MemberResponse],
    summary="获取会员详情",
    description="根据会员ID获取会员详细信息",
)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
):
    """
    获取会员详情
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=MemberResponse.model_validate(member)
    )


@router.put(
    "/{member_id}",
    response_model=ApiResponse[MemberResponse],
    summary="更新会员信息",
    description="更新会员的基本信息",
)
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
):
    """
    更新会员信息
    - **member_id**: 会员ID
    - **member_data**: 更新的会员信息
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 检查手机号是否已被其他会员使用
    if member_data.phone and member_data.phone != member.phone:
        existing = db.query(Member).filter(
            Member.phone == member_data.phone,
            Member.id != member_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"手机号 {member_data.phone} 已被其他会员使用"
            )
    
    # 更新字段
    update_data = member_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    
    db.commit()
    db.refresh(member)
    
    return ApiResponse(
        code=200,
        message="会员信息更新成功",
        data=MemberResponse.model_validate(member)
    )


@router.delete(
    "/{member_id}",
    response_model=SuccessResponse,
    summary="删除会员",
    description="删除指定会员（逻辑删除，实际修改状态为已注销）",
)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
):
    """
    删除会员（逻辑删除）
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 逻辑删除：修改状态为已注销
    member.status = MemberStatus.CANCELLED
    member.status_reason = "手动删除"
    db.commit()
    
    return SuccessResponse(
        code=200,
        message="会员已注销",
        data=None
    )


@router.post(
    "/send-verification-code",
    response_model=ApiResponse[dict],
    summary="发送实名认证验证码",
    description="向指定手机号发送实名认证验证码（测试环境会返回验证码）",
)
def send_verification_code(
    request: PhoneVerificationCodeRequest,
    db: Session = Depends(get_db),
):
    """
    发送实名认证验证码
    - **request**: 包含手机号和验证码用途
    """
    result = verification_service.send_verification_code(request.phone)
    
    return ApiResponse(
        code=200,
        message=result.get("message", "验证码已发送"),
        data=result
    )


@router.post(
    "/{member_id}/verify",
    response_model=ApiResponse[dict],
    summary="会员实名认证",
    description="支持手机号验证和人脸识别两种实名认证方式",
)
def verify_member(
    member_id: int,
    request: VerificationRequest,
    db: Session = Depends(get_db),
):
    """
    会员实名认证
    - **member_id**: 会员ID
    - **request**: 认证请求，包含认证方式和认证数据
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 根据认证方式处理
    if request.verification_method.value == "phone":
        if not request.verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号验证需要提供验证码"
            )
        result = verification_service.verify_phone(db, member, request.verification_code)
    elif request.verification_method.value == "face":
        if not request.face_image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="人脸识别验证需要提供人脸图像数据"
            )
        result = verification_service.verify_face(db, member, request.face_image_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的认证方式"
        )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "认证失败")
        )
    
    return ApiResponse(
        code=200,
        message=result.get("message", "认证成功"),
        data=result
    )


@router.get(
    "/{member_id}/verification-status",
    response_model=ApiResponse[dict],
    summary="获取会员认证状态",
    description="查询会员的实名认证状态",
)
def get_verification_status(
    member_id: int,
    db: Session = Depends(get_db),
):
    """
    获取会员认证状态
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    status_info = verification_service.check_verification_status(member)
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=status_info
    )

"""
邀请有礼路由模块
处理邀请记录、奖励状态查询等功能
"""
from typing import List, Optional
import random
import string
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Invitation
from app.schemas import (
    InvitationCreate, InvitationResponse, InvitationCode,
    APIResponse, PaginatedResponse
)
from app.auth import get_current_active_user
from math import ceil

router = APIRouter(prefix="/invitations", tags=["邀请有礼"])


def generate_unique_invite_code(db: Session, length: int = 8) -> str:
    """
    生成唯一的邀请码
    
    Args:
        db: 数据库会话
        length: 邀请码长度
        
    Returns:
        str: 唯一的邀请码
    """
    chars = string.ascii_uppercase + string.digits
    
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        # 检查是否已存在
        existing = db.query(Invitation).filter(Invitation.invite_code == code).first()
        if not existing:
            return code


@router.get("/my-code", response_model=APIResponse, summary="获取我的邀请码")
async def get_my_invite_code(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的邀请码
    如果没有则生成一个
    """
    # 检查是否已有未使用的邀请码
    existing_invitation = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id,
        Invitation.status == "pending",
        Invitation.invitee_id == None
    ).first()
    
    if existing_invitation:
        return APIResponse(
            code=200,
            message="success",
            data={"invite_code": existing_invitation.invite_code}
        )
    
    # 生成新的邀请码
    invite_code = generate_unique_invite_code(db)
    
    # 创建邀请记录
    new_invitation = Invitation(
        inviter_id=current_user.id,
        invite_code=invite_code,
        status="pending",
        reward_points=200  # 默认邀请奖励积分
    )
    
    db.add(new_invitation)
    db.commit()
    
    return APIResponse(
        code=200,
        message="success",
        data={"invite_code": invite_code}
    )


@router.post("/create", response_model=InvitationResponse, summary="发起邀请")
async def create_invitation(
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发起邀请（通过手机号或邮箱）
    
    - **invitee_phone**: 被邀请者手机号
    - **invitee_email**: 被邀请者邮箱
    """
    # 至少需要一个联系方式
    if not invitation_data.invitee_phone and not invitation_data.invitee_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供被邀请者的手机号或邮箱"
        )
    
    # 生成邀请码
    invite_code = generate_unique_invite_code(db)
    
    # 创建邀请记录
    new_invitation = Invitation(
        inviter_id=current_user.id,
        invite_code=invite_code,
        invitee_phone=invitation_data.invitee_phone,
        invitee_email=invitation_data.invitee_email,
        status="pending",
        reward_points=200
    )
    
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)
    
    return InvitationResponse.from_orm(new_invitation)


@router.get("/sent", response_model=PaginatedResponse, summary="获取我发出的邀请记录")
async def get_my_sent_invitations(
    status: Optional[str] = Query(None, description="邀请状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户发出的邀请记录列表
    
    - **status**: 状态筛选 (pending, registered, subscribed, rewarded)
    """
    query = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id
    )
    
    if status:
        query = query.filter(Invitation.status == status)
    
    query = query.order_by(desc(Invitation.created_at))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    invitations = query.offset((page - 1) * page_size).limit(page_size).all()
    
    responses = []
    for inv in invitations:
        response = InvitationResponse.from_orm(inv)
        if inv.invitee:
            response.invitee = inv.invitee
        responses.append(response)
    
    return PaginatedResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/received", response_model=PaginatedResponse, summary="获取我收到的邀请记录")
async def get_my_received_invitations(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户收到的邀请记录列表
    """
    query = db.query(Invitation).filter(
        Invitation.invitee_id == current_user.id
    )
    
    if status:
        query = query.filter(Invitation.status == status)
    
    query = query.order_by(desc(Invitation.created_at))
    
    total = query.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    invitations = query.offset((page - 1) * page_size).limit(page_size).all()
    
    responses = []
    for inv in invitations:
        response = InvitationResponse.from_orm(inv)
        responses.append(response)
    
    return PaginatedResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{invitation_id}", response_model=InvitationResponse, summary="获取邀请详情")
async def get_invitation_detail(
    invitation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取单条邀请记录详情
    """
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请记录不存在"
        )
    
    # 检查权限：只能查看自己的邀请记录
    if invitation.inviter_id != current_user.id and invitation.invitee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此邀请记录"
        )
    
    response = InvitationResponse.from_orm(invitation)
    if invitation.invitee:
        response.invitee = invitation.invitee
    
    return response


@router.post("/verify/{invite_code}", response_model=APIResponse, summary="验证邀请码")
async def verify_invite_code(
    invite_code: str,
    db: Session = Depends(get_db)
):
    """
    验证邀请码是否有效
    用于注册时验证邀请码
    """
    invitation = db.query(Invitation).filter(
        Invitation.invite_code == invite_code.upper()
    ).first()
    
    if not invitation:
        return APIResponse(
            code=404,
            message="邀请码不存在",
            data={"valid": False}
        )
    
    if invitation.status != "pending":
        return APIResponse(
            code=400,
            message="邀请码已被使用",
            data={"valid": False}
        )
    
    return APIResponse(
        code=200,
        message="邀请码有效",
        data={
            "valid": True,
            "inviter_id": invitation.inviter_id,
            "reward_points": invitation.reward_points
        }
    )


@router.post("/claim-reward/{invitation_id}", response_model=APIResponse, summary="领取邀请奖励")
async def claim_invitation_reward(
    invitation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    领取邀请奖励
    当被邀请者办卡后，邀请者可以领取奖励
    """
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.inviter_id == current_user.id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请记录不存在"
        )
    
    if invitation.status != "subscribed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="被邀请者尚未办卡，无法领取奖励"
        )
    
    if invitation.status == "rewarded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="奖励已领取"
        )
    
    # 发放奖励积分
    current_user.points += invitation.reward_points
    invitation.status = "rewarded"
    
    db.commit()
    
    return APIResponse(
        code=200,
        message="奖励领取成功",
        data={
            "points_awarded": invitation.reward_points,
            "new_points_balance": current_user.points
        }
    )


@router.get("/stats/overview", response_model=APIResponse, summary="获取邀请统计")
async def get_invitation_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取邀请统计信息
    """
    # 总邀请数
    total_invitations = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id
    ).count()
    
    # 已注册数
    registered_count = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id,
        Invitation.status.in_(["registered", "subscribed", "rewarded"])
    ).count()
    
    # 已办卡数
    subscribed_count = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id,
        Invitation.status.in_(["subscribed", "rewarded"])
    ).count()
    
    # 已领取奖励数
    rewarded_count = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id,
        Invitation.status == "rewarded"
    ).count()
    
    # 累计获得积分
    total_points_earned = db.query(Invitation).filter(
        Invitation.inviter_id == current_user.id,
        Invitation.status == "rewarded"
    ).with_entities(Invitation.reward_points).all()
    
    total_points = sum(p[0] for p in total_points_earned)
    
    return APIResponse(
        code=200,
        message="success",
        data={
            "total_invitations": total_invitations,
            "registered_count": registered_count,
            "subscribed_count": subscribed_count,
            "rewarded_count": rewarded_count,
            "total_points_earned": total_points
        }
    )

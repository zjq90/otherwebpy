"""
会员管理API路由模块
提供会员的增删改查、会籍管理等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date

from database import get_db
from models import Member
from schemas import MemberCreate, MemberUpdate, MemberResponse, ApiResponse, PaginatedResponse

# 创建路由实例
router = APIRouter(
    prefix="/api/members",
    tags=["会员管理"]
)


@router.get("/", response_model=PaginatedResponse, summary="获取会员列表")
def get_members(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（会员编号、姓名、手机号）"),
    status: Optional[str] = Query(None, description="会员状态"),
    db: Session = Depends(get_db)
):
    """
    分页获取会员列表，支持搜索和筛选
    
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    - **keyword**: 搜索关键词，支持会员编号、姓名、手机号
    - **status**: 会员状态筛选
    """
    # 构建查询
    query = db.query(Member)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                Member.member_no.contains(keyword),
                Member.name.contains(keyword),
                Member.phone.contains(keyword)
            )
        )
    
    # 状态筛选
    if status:
        query = query.filter(Member.status == status)
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    members = query.order_by(Member.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 转换为响应模型
    items = [MemberResponse.model_validate(member).model_dump() for member in members]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{member_id}", response_model=MemberResponse, summary="根据ID获取会员详情")
def get_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    """
    根据会员ID获取会员详细信息
    
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    return member


@router.post("/", response_model=MemberResponse, summary="创建新会员")
def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db)
):
    """
    创建新会员
    
    - **member_data**: 会员信息
    """
    # 检查会员编号是否已存在
    existing = db.query(Member).filter(Member.member_no == member_data.member_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"会员编号 {member_data.member_no} 已存在")
    
    # 检查卡号是否已存在
    if member_data.card_no:
        existing_card = db.query(Member).filter(Member.card_no == member_data.card_no).first()
        if existing_card:
            raise HTTPException(status_code=400, detail=f"卡号 {member_data.card_no} 已被使用")
    
    # 检查二维码是否已存在
    if member_data.qr_code:
        existing_qr = db.query(Member).filter(Member.qr_code == member_data.qr_code).first()
        if existing_qr:
            raise HTTPException(status_code=400, detail=f"二维码已被使用")
    
    # 创建会员
    new_member = Member(**member_data.model_dump())
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return new_member


@router.put("/{member_id}", response_model=MemberResponse, summary="更新会员信息")
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db)
):
    """
    更新会员信息
    
    - **member_id**: 会员ID
    - **member_data**: 需要更新的会员信息
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    # 更新字段
    update_data = member_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    
    db.commit()
    db.refresh(member)
    
    return member


@router.delete("/{member_id}", response_model=ApiResponse, summary="删除会员")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    """
    删除会员（逻辑删除，将状态设为suspended）
    
    - **member_id**: 会员ID
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    # 逻辑删除：将状态设为暂停
    member.status = "suspended"
    db.commit()
    
    return ApiResponse(
        success=True,
        message=f"会员 {member.name} 已停用",
        data={"member_id": member_id, "member_name": member.name}
    )


@router.get("/validate/{identifier}", response_model=ApiResponse, summary="验证会员有效性")
def validate_member(
    identifier: str,
    db: Session = Depends(get_db)
):
    """
    验证会员有效性，支持通过会员编号、卡号、二维码查询
    
    - **identifier**: 识别标识（会员编号、卡号、二维码）
    """
    # 查询会员
    member = db.query(Member).filter(
        or_(
            Member.member_no == identifier,
            Member.card_no == identifier,
            Member.qr_code == identifier
        )
    ).first()
    
    if not member:
        return ApiResponse(
            success=False,
            message="会员不存在",
            data={"valid": False}
        )
    
    # 检查会籍是否有效
    today = date.today()
    is_valid = True
    fail_reason = None
    
    if member.status != "active":
        is_valid = False
        fail_reason = f"会员状态异常: {member.status}"
    elif member.membership_end < today:
        is_valid = False
        fail_reason = "会籍已过期"
    
    return ApiResponse(
        success=is_valid,
        message=fail_reason if fail_reason else "会员有效",
        data={
            "valid": is_valid,
            "member_id": member.id,
            "member_name": member.name,
            "member_no": member.member_no,
            "membership_type": member.membership_type,
            "membership_end": member.membership_end.isoformat(),
            "balance": member.balance
        }
    )


@router.post("/recharge/{member_id}", response_model=ApiResponse, summary="会员充值")
def recharge_member(
    member_id: int,
    amount: float = Query(..., gt=0, description="充值金额"),
    gift_amount: float = Query(0.0, ge=0, description="赠送金额"),
    db: Session = Depends(get_db)
):
    """
    给会员账户充值
    
    - **member_id**: 会员ID
    - **amount**: 充值金额
    - **gift_amount**: 赠送金额
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    if member.status != "active":
        raise HTTPException(status_code=400, detail="会员状态异常，无法充值")
    
    # 记录充值前余额
    balance_before = member.balance
    
    # 更新余额
    member.balance += amount + gift_amount
    
    db.commit()
    db.refresh(member)
    
    return ApiResponse(
        success=True,
        message="充值成功",
        data={
            "member_id": member_id,
            "member_name": member.name,
            "recharge_amount": amount,
            "gift_amount": gift_amount,
            "balance_before": balance_before,
            "balance_after": member.balance
        }
    )

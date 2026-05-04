"""
会员管理API路由
包含会员、会员卡和课程预约的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models import Member, MemberCard, CourseBooking, Card, CourseSchedule, CardType
from ..schemas import (
    MemberBase, MemberCreate, MemberUpdate, MemberResponse,
    MemberCardBase, MemberCardCreate, MemberCardUpdate, MemberCardResponse,
    CourseBookingBase, CourseBookingCreate, CourseBookingUpdate, CourseBookingResponse
)

# 创建API路由实例
router = APIRouter(prefix="/api/v1/members", tags=["会员管理"])


def enhance_member_card(member_card: MemberCard, db: Session) -> MemberCard:
    """
    为会员卡添加额外信息：卡名称、卡类型名称
    """
    # 获取卡项信息
    card = db.execute(
        select(Card).where(Card.id == member_card.card_id)
    ).scalar_one_or_none()
    
    if card:
        member_card.card_name = card.name
        # 获取卡类型信息
        card_type = db.execute(
            select(CardType).where(CardType.id == card.card_type_id)
        ).scalar_one_or_none()
        if card_type:
            member_card.card_type_name = card_type.name
    
    return member_card


def enhance_member_cards(member_cards: List[MemberCard], db: Session) -> List[MemberCard]:
    """
    为会员卡列表添加额外信息
    """
    for mc in member_cards:
        enhance_member_card(mc, db)
    return member_cards


def generate_member_no() -> str:
    """
    生成会员编号
    格式：M + 时间戳 + 随机字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:4].upper()
    return f"M{timestamp}{random_str}"


def generate_card_no() -> str:
    """
    生成会员卡编号
    格式：C + 时间戳 + 随机字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:4].upper()
    return f"C{timestamp}{random_str}"


def generate_booking_no() -> str:
    """
    生成预约编号
    格式：B + 时间戳 + 随机字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:4].upper()
    return f"B{timestamp}{random_str}"


# ==================== 会员相关接口 ====================

@router.post("", response_model=MemberResponse, summary="创建会员")
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """
    创建新的会员
    
    Args:
        member: 会员创建数据
        db: 数据库会话
    
    Returns:
        创建的会员信息
    """
    # 检查手机号码是否已存在
    existing = db.execute(
        select(Member).where(Member.phone == member.phone)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"手机号码 '{member.phone}' 已被注册")
    
    # 生成会员编号
    member_data = member.model_dump()
    member_data["member_no"] = generate_member_no()
    
    # 创建新会员
    db_member = Member(**member_data)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.get("", response_model=List[MemberResponse], summary="获取会员列表")
def get_members(
    status: Optional[str] = Query(None, description="会员状态"),
    keyword: Optional[str] = Query(None, description="搜索关键词(姓名/手机)"),
    db: Session = Depends(get_db)
):
    """
    获取会员列表
    
    Args:
        status: 会员状态筛选
        keyword: 搜索关键词
        db: 数据库会话
    
    Returns:
        会员列表
    """
    query = select(Member)
    
    if status is not None:
        query = query.where(Member.status == status)
    if keyword is not None:
        query = query.where(
            Member.name.contains(keyword) | Member.phone.contains(keyword)
        )
    
    query = query.order_by(Member.id.desc())
    
    members = db.execute(query).scalars().all()
    return members


@router.get("/{member_id}", response_model=MemberResponse, summary="获取会员详情")
def get_member(member_id: int, db: Session = Depends(get_db)):
    """
    获取会员详情
    
    Args:
        member_id: 会员ID
        db: 数据库会话
    
    Returns:
        会员详情
    """
    member = db.execute(
        select(Member).where(Member.id == member_id)
    ).scalar_one_or_none()
    
    if member is None:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    return member


@router.put("/{member_id}", response_model=MemberResponse, summary="更新会员")
def update_member(
    member_id: int, 
    member: MemberUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新会员信息
    
    Args:
        member_id: 会员ID
        member: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的会员信息
    """
    db_member = db.execute(
        select(Member).where(Member.id == member_id)
    ).scalar_one_or_none()
    
    if db_member is None:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    # 如果更新了手机号码，检查是否已存在
    update_data = member.model_dump(exclude_unset=True)
    if "phone" in update_data and update_data["phone"] != db_member.phone:
        existing = db.execute(
            select(Member).where(Member.phone == update_data["phone"], Member.id != member_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail=f"手机号码 '{update_data['phone']}' 已被注册")
    
    # 更新字段
    for key, value in update_data.items():
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/{member_id}", summary="删除会员")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """
    删除会员
    
    Args:
        member_id: 会员ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_member = db.execute(
        select(Member).where(Member.id == member_id)
    ).scalar_one_or_none()
    
    if db_member is None:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    db.delete(db_member)
    db.commit()
    return {"message": "删除成功", "id": member_id}


# ==================== 会员卡相关接口 ====================

@router.get("/cards", response_model=List[MemberCardResponse], summary="获取会员卡列表")
def get_all_member_cards(
    member_id: Optional[int] = Query(None, description="会员ID筛选"),
    status: Optional[str] = Query(None, description="会员卡状态"),
    db: Session = Depends(get_db)
):
    """
    获取所有会员卡列表（支持按会员ID筛选）
    
    Args:
        member_id: 会员ID筛选
        status: 会员卡状态筛选
        db: 数据库会话
    
    Returns:
        会员卡列表
    """
    query = select(MemberCard)
    
    if member_id is not None:
        query = query.where(MemberCard.member_id == member_id)
    if status is not None:
        query = query.where(MemberCard.status == status)
    
    query = query.order_by(MemberCard.id.desc())
    
    member_cards = db.execute(query).scalars().all()
    return enhance_member_cards(member_cards, db)


@router.post("/cards", response_model=MemberCardResponse, summary="创建会员卡")
def create_member_card(member_card: MemberCardCreate, db: Session = Depends(get_db)):
    """
    为会员创建会员卡
    
    Args:
        member_card: 会员卡创建数据
        db: 数据库会话
    
    Returns:
        创建的会员卡信息
    """
    # 检查会员是否存在
    member = db.execute(
        select(Member).where(Member.id == member_card.member_id)
    ).scalar_one_or_none()
    
    if member is None:
        raise HTTPException(status_code=400, detail=f"会员ID {member_card.member_id} 不存在")
    
    # 检查卡项是否存在
    card = db.execute(
        select(Card).where(Card.id == member_card.card_id)
    ).scalar_one_or_none()
    
    if card is None:
        raise HTTPException(status_code=400, detail=f"卡项ID {member_card.card_id} 不存在")
    
    # 生成会员卡编号
    member_card_data = member_card.model_dump()
    member_card_data["card_no"] = generate_card_no()
    
    # 如果没有指定开始日期，使用今天
    if member_card_data.get("start_date") is None:
        member_card_data["start_date"] = date.today()
    
    # 如果没有指定购买价格，使用卡项的价格
    if member_card_data.get("purchase_price") is None:
        member_card_data["purchase_price"] = card.price if card.price else 0
    
    # 根据卡类型设置默认值
    if card.valid_count is not None and member_card_data.get("total_count") is None:
        member_card_data["total_count"] = card.valid_count
        member_card_data["remaining_count"] = card.valid_count
    if card.stored_amount is not None and member_card_data.get("balance") is None:
        member_card_data["balance"] = card.stored_amount
    if card.bonus_amount is not None:
        member_card_data["bonus_balance"] = card.bonus_amount
    
    # 创建新会员卡
    db_member_card = MemberCard(**member_card_data)
    db.add(db_member_card)
    db.commit()
    db.refresh(db_member_card)
    
    return enhance_member_card(db_member_card, db)


@router.get("/cards/{member_id}", response_model=List[MemberCardResponse], summary="获取会员的会员卡列表")
def get_member_cards(
    member_id: int,
    status: Optional[str] = Query(None, description="会员卡状态"),
    db: Session = Depends(get_db)
):
    """
    获取会员的会员卡列表
    
    Args:
        member_id: 会员ID
        status: 会员卡状态筛选
        db: 数据库会话
    
    Returns:
        会员卡列表
    """
    query = select(MemberCard).where(MemberCard.member_id == member_id)
    
    if status is not None:
        query = query.where(MemberCard.status == status)
    
    query = query.order_by(MemberCard.id.desc())
    
    member_cards = db.execute(query).scalars().all()
    return enhance_member_cards(member_cards, db)


# ==================== 课程预约相关接口 ====================

@router.post("/bookings", response_model=CourseBookingResponse, summary="创建课程预约")
def create_booking(booking: CourseBookingCreate, db: Session = Depends(get_db)):
    """
    创建课程预约
    
    Args:
        booking: 课程预约创建数据
        db: 数据库会话
    
    Returns:
        创建的课程预约信息
    """
    # 检查会员是否存在
    member = db.execute(
        select(Member).where(Member.id == booking.member_id)
    ).scalar_one_or_none()
    
    if member is None:
        raise HTTPException(status_code=400, detail=f"会员ID {booking.member_id} 不存在")
    
    # 检查课程排期是否存在
    schedule = db.execute(
        select(CourseSchedule).where(CourseSchedule.id == booking.schedule_id)
    ).scalar_one_or_none()
    
    if schedule is None:
        raise HTTPException(status_code=400, detail=f"排期ID {booking.schedule_id} 不存在")
    
    # 检查是否已预约
    existing_booking = db.execute(
        select(CourseBooking).where(
            CourseBooking.member_id == booking.member_id,
            CourseBooking.schedule_id == booking.schedule_id,
            CourseBooking.status != "cancelled"
        )
    ).scalar_one_or_none()
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="该会员已预约此课程")
    
    # 检查容量
    max_cap = schedule.max_capacity if schedule.max_capacity else 20
    if schedule.booked_count >= max_cap:
        raise HTTPException(status_code=400, detail="课程预约已满")
    
    # 生成预约编号
    booking_data = booking.model_dump()
    booking_data["booking_no"] = generate_booking_no()
    
    # 创建新预约
    db_booking = CourseBooking(**booking_data)
    db.add(db_booking)
    
    # 更新已预约人数
    schedule.booked_count += 1
    
    db.commit()
    db.refresh(db_booking)
    
    return db_booking


@router.get("/bookings/{member_id}", response_model=List[CourseBookingResponse], summary="获取会员的预约列表")
def get_member_bookings(
    member_id: int,
    status: Optional[str] = Query(None, description="预约状态"),
    db: Session = Depends(get_db)
):
    """
    获取会员的课程预约列表
    
    Args:
        member_id: 会员ID
        status: 预约状态筛选
        db: 数据库会话
    
    Returns:
        预约列表
    """
    query = select(CourseBooking).where(CourseBooking.member_id == member_id)
    
    if status is not None:
        query = query.where(CourseBooking.status == status)
    
    query = query.order_by(CourseBooking.booking_time.desc())
    
    bookings = db.execute(query).scalars().all()
    return bookings


@router.put("/bookings/{booking_id}/cancel", summary="取消预约")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    取消课程预约
    
    Args:
        booking_id: 预约ID
        db: 数据库会话
    
    Returns:
        取消结果
    """
    db_booking = db.execute(
        select(CourseBooking).where(CourseBooking.id == booking_id)
    ).scalar_one_or_none()
    
    if db_booking is None:
        raise HTTPException(status_code=404, detail=f"预约ID {booking_id} 不存在")
    
    if db_booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="该预约已取消")
    
    # 更新预约状态
    db_booking.status = "cancelled"
    db_booking.cancel_time = datetime.now()
    
    # 更新已预约人数
    schedule = db.execute(
        select(CourseSchedule).where(CourseSchedule.id == db_booking.schedule_id)
    ).scalar_one_or_none()
    
    if schedule and schedule.booked_count > 0:
        schedule.booked_count -= 1
    
    db.commit()
    return {"message": "取消成功", "id": booking_id}

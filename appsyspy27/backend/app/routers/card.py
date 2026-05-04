"""
会员卡路由模块
包含会员卡类型查询、用户卡包管理等接口
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.user import User
from app.models.card import CardType, UserCard
from app.models.order import ConsumptionRecord
from app.schemas.card import (
    CardTypeResponse, UserCardResponse, CardUsageRecord
)
from app.utils.security import get_current_user
from app.utils.helpers import format_duration

router = APIRouter(prefix="/cards", tags=["会员卡管理"])


@router.get("/types", response_model=List[CardTypeResponse], summary="获取会员卡类型列表")
def get_card_types(
    category: Optional[str] = Query(None, description="卡类型分类"),
    is_on_sale: Optional[bool] = Query(True, description="是否仅显示在售"),
    db: Session = Depends(get_db)
):
    """
    获取所有会员卡类型列表
    
    - **category**: 可选，按分类筛选（YEAR, COUNT, DURATION, LESSON）
    - **is_on_sale**: 可选，是否仅显示在售卡类型
    """
    query = db.query(CardType)
    
    if category:
        query = query.filter(CardType.category == category)
    if is_on_sale is not None:
        query = query.filter(CardType.is_on_sale == is_on_sale)
    
    card_types = query.order_by(CardType.sort_order.desc(), CardType.id).all()
    
    return [CardTypeResponse.model_validate(ct) for ct in card_types]


@router.get("/types/{card_type_id}", response_model=CardTypeResponse, summary="获取会员卡类型详情")
def get_card_type_detail(
    card_type_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定会员卡类型的详细信息
    
    - **card_type_id**: 卡类型ID
    """
    card_type = db.query(CardType).filter(CardType.id == card_type_id).first()
    
    if not card_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会员卡类型不存在"
        )
    
    return CardTypeResponse.model_validate(card_type)


@router.get("/my", response_model=List[UserCardResponse], summary="获取我的卡包")
def get_my_cards(
    status: Optional[str] = Query(None, description="卡状态筛选"),
    only_valid: bool = Query(False, description="是否只显示有效卡"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有会员卡
    
    - **status**: 可选，按状态筛选（ACTIVE, EXPIRED, USED_UP, FROZEN）
    - **only_valid**: 可选，是否只显示有效卡
    """
    query = db.query(UserCard).filter(UserCard.user_id == current_user.id)
    
    if status:
        query = query.filter(UserCard.status == status)
    
    user_cards = query.order_by(UserCard.created_at.desc()).all()
    
    # 构建响应数据
    result = []
    for user_card in user_cards:
        card_type = user_card.card_type
        
        # 检查是否有效
        is_valid = user_card.is_valid()
        
        # 如果只需要有效卡且当前卡无效，则跳过
        if only_valid and not is_valid:
            continue
        
        # 更新状态（如果已过期或用完）
        if user_card.status == "ACTIVE":
            if user_card.expire_time and date.today() > user_card.expire_time:
                user_card.status = "EXPIRED"
                db.commit()
            elif user_card.remaining_count is not None and user_card.remaining_count <= 0:
                user_card.status = "USED_UP"
                db.commit()
            elif user_card.remaining_duration is not None and user_card.remaining_duration <= 0:
                user_card.status = "USED_UP"
                db.commit()
        
        response_data = UserCardResponse(
            id=user_card.id,
            user_id=user_card.user_id,
            card_type_id=user_card.card_type_id,
            card_number=user_card.card_number,
            display_name=user_card.display_name or card_type.name,
            card_type_name=card_type.name,
            card_category=card_type.category,
            purchase_time=user_card.purchase_time,
            activate_time=user_card.activate_time,
            expire_time=user_card.expire_time,
            remaining_count=user_card.remaining_count,
            total_count=user_card.total_count,
            remaining_duration=user_card.remaining_duration,
            total_duration=user_card.total_duration,
            status=user_card.status,
            is_valid=is_valid,
            usage_scope=card_type.usage_scope,
            created_at=user_card.created_at
        )
        result.append(response_data)
    
    return result


@router.get("/my/{user_card_id}", response_model=UserCardResponse, summary="获取我的会员卡详情")
def get_my_card_detail(
    user_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户指定会员卡的详细信息
    
    - **user_card_id**: 用户卡ID
    """
    user_card = db.query(UserCard).filter(
        UserCard.id == user_card_id,
        UserCard.user_id == current_user.id
    ).first()
    
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会员卡不存在或不属于当前用户"
        )
    
    card_type = user_card.card_type
    
    return UserCardResponse(
        id=user_card.id,
        user_id=user_card.user_id,
        card_type_id=user_card.card_type_id,
        card_number=user_card.card_number,
        display_name=user_card.display_name or card_type.name,
        card_type_name=card_type.name,
        card_category=card_type.category,
        purchase_time=user_card.purchase_time,
        activate_time=user_card.activate_time,
        expire_time=user_card.expire_time,
        remaining_count=user_card.remaining_count,
        total_count=user_card.total_count,
        remaining_duration=user_card.remaining_duration,
        total_duration=user_card.total_duration,
        status=user_card.status,
        is_valid=user_card.is_valid(),
        usage_scope=card_type.usage_scope,
        created_at=user_card.created_at
    )


@router.get("/my/{user_card_id}/usage-records", response_model=List[CardUsageRecord], summary="获取会员卡使用记录")
def get_card_usage_records(
    user_card_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定会员卡的使用记录
    
    - **user_card_id**: 用户卡ID
    - **page**: 页码
    - **page_size**: 每页数量
    """
    # 验证会员卡归属
    user_card = db.query(UserCard).filter(
        UserCard.id == user_card_id,
        UserCard.user_id == current_user.id
    ).first()
    
    if not user_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会员卡不存在或不属于当前用户"
        )
    
    # 查询使用记录
    records = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_card_id == user_card_id,
        ConsumptionRecord.user_id == current_user.id
    ).order_by(
        ConsumptionRecord.created_at.desc()
    ).offset(
        (page - 1) * page_size
    ).limit(
        page_size
    ).all()
    
    return [
        CardUsageRecord(
            id=r.id,
            title=r.title,
            record_type=r.record_type,
            count_before=r.count_before,
            count_after=r.count_after,
            duration_used=r.duration_used,
            store_name=r.store_name,
            operator_name=r.operator_name,
            created_at=r.created_at
        ) for r in records
    ]

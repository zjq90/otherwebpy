"""
卡项管理API路由
包含卡类型和卡项的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from ..database import get_db
from ..models import CardType, Card
from ..schemas import (
    CardTypeBase, CardTypeCreate, CardTypeUpdate, CardTypeResponse,
    CardBase, CardCreate, CardUpdate, CardResponse
)

# 创建API路由实例
router = APIRouter(prefix="/api/v1/cards", tags=["卡项管理"])


# ==================== 卡类型相关接口 ====================

@router.post("/types", response_model=CardTypeResponse, summary="创建卡类型")
def create_card_type(card_type: CardTypeCreate, db: Session = Depends(get_db)):
    """
    创建新的卡类型
    
    Args:
        card_type: 卡类型创建数据
        db: 数据库会话
    
    Returns:
        创建的卡类型信息
    """
    # 检查卡类型代码是否已存在
    existing = db.execute(
        select(CardType).where(CardType.code == card_type.code)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"卡类型代码 '{card_type.code}' 已存在")
    
    # 创建新卡类型
    db_card_type = CardType(**card_type.model_dump())
    db.add(db_card_type)
    db.commit()
    db.refresh(db_card_type)
    return db_card_type


@router.get("/types", response_model=List[CardTypeResponse], summary="获取卡类型列表")
def get_card_types(
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db)
):
    """
    获取卡类型列表
    
    Args:
        is_active: 是否启用的筛选条件
        db: 数据库会话
    
    Returns:
        卡类型列表
    """
    query = select(CardType)
    if is_active is not None:
        query = query.where(CardType.is_active == is_active)
    query = query.order_by(CardType.id)
    
    card_types = db.execute(query).scalars().all()
    return card_types


@router.get("/types/{card_type_id}", response_model=CardTypeResponse, summary="获取卡类型详情")
def get_card_type(card_type_id: int, db: Session = Depends(get_db)):
    """
    获取卡类型详情
    
    Args:
        card_type_id: 卡类型ID
        db: 数据库会话
    
    Returns:
        卡类型详情
    """
    card_type = db.execute(
        select(CardType).where(CardType.id == card_type_id)
    ).scalar_one_or_none()
    
    if card_type is None:
        raise HTTPException(status_code=404, detail=f"卡类型ID {card_type_id} 不存在")
    
    return card_type


@router.put("/types/{card_type_id}", response_model=CardTypeResponse, summary="更新卡类型")
def update_card_type(
    card_type_id: int, 
    card_type: CardTypeUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新卡类型信息
    
    Args:
        card_type_id: 卡类型ID
        card_type: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的卡类型信息
    """
    db_card_type = db.execute(
        select(CardType).where(CardType.id == card_type_id)
    ).scalar_one_or_none()
    
    if db_card_type is None:
        raise HTTPException(status_code=404, detail=f"卡类型ID {card_type_id} 不存在")
    
    # 更新字段
    update_data = card_type.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_card_type, key, value)
    
    db.commit()
    db.refresh(db_card_type)
    return db_card_type


@router.delete("/types/{card_type_id}", summary="删除卡类型")
def delete_card_type(card_type_id: int, db: Session = Depends(get_db)):
    """
    删除卡类型
    
    Args:
        card_type_id: 卡类型ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_card_type = db.execute(
        select(CardType).where(CardType.id == card_type_id)
    ).scalar_one_or_none()
    
    if db_card_type is None:
        raise HTTPException(status_code=404, detail=f"卡类型ID {card_type_id} 不存在")
    
    # 检查是否有关联的卡项
    card_count = db.execute(
        select(Card).where(Card.card_type_id == card_type_id)
    ).scalars().all()
    
    if card_count:
        raise HTTPException(
            status_code=400, 
            detail=f"卡类型ID {card_type_id} 有关联的卡项，无法删除"
        )
    
    db.delete(db_card_type)
    db.commit()
    return {"message": "删除成功", "id": card_type_id}


# ==================== 卡项相关接口 ====================

@router.post("", response_model=CardResponse, summary="创建卡项")
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    """
    创建新的卡项
    
    Args:
        card: 卡项创建数据
        db: 数据库会话
    
    Returns:
        创建的卡项信息
    """
    # 检查卡类型是否存在
    card_type = db.execute(
        select(CardType).where(CardType.id == card.card_type_id)
    ).scalar_one_or_none()
    
    if card_type is None:
        raise HTTPException(status_code=400, detail=f"卡类型ID {card.card_type_id} 不存在")
    
    # 创建新卡项
    db_card = Card(**card.model_dump())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    # 关联查询卡类型信息
    db_card.card_type = card_type
    return db_card


@router.get("", response_model=List[CardResponse], summary="获取卡项列表")
def get_cards(
    card_type_id: Optional[int] = Query(None, description="卡类型ID"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db)
):
    """
    获取卡项列表
    
    Args:
        card_type_id: 卡类型ID筛选
        is_active: 是否启用筛选
        db: 数据库会话
    
    Returns:
        卡项列表
    """
    query = select(Card)
    if card_type_id is not None:
        query = query.where(Card.card_type_id == card_type_id)
    if is_active is not None:
        query = query.where(Card.is_active == is_active)
    query = query.order_by(Card.sort_order, Card.id)
    
    cards = db.execute(query).scalars().all()
    return cards


@router.get("/{card_id}", response_model=CardResponse, summary="获取卡项详情")
def get_card(card_id: int, db: Session = Depends(get_db)):
    """
    获取卡项详情
    
    Args:
        card_id: 卡项ID
        db: 数据库会话
    
    Returns:
        卡项详情
    """
    card = db.execute(
        select(Card).where(Card.id == card_id)
    ).scalar_one_or_none()
    
    if card is None:
        raise HTTPException(status_code=404, detail=f"卡项ID {card_id} 不存在")
    
    return card


@router.put("/{card_id}", response_model=CardResponse, summary="更新卡项")
def update_card(
    card_id: int, 
    card: CardUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新卡项信息
    
    Args:
        card_id: 卡项ID
        card: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的卡项信息
    """
    db_card = db.execute(
        select(Card).where(Card.id == card_id)
    ).scalar_one_or_none()
    
    if db_card is None:
        raise HTTPException(status_code=404, detail=f"卡项ID {card_id} 不存在")
    
    # 如果更新了卡类型ID，检查卡类型是否存在
    update_data = card.model_dump(exclude_unset=True)
    if "card_type_id" in update_data:
        card_type = db.execute(
            select(CardType).where(CardType.id == update_data["card_type_id"])
        ).scalar_one_or_none()
        if card_type is None:
            raise HTTPException(status_code=400, detail=f"卡类型ID {update_data['card_type_id']} 不存在")
    
    # 更新字段
    for key, value in update_data.items():
        setattr(db_card, key, value)
    
    db.commit()
    db.refresh(db_card)
    return db_card


@router.delete("/{card_id}", summary="删除卡项")
def delete_card(card_id: int, db: Session = Depends(get_db)):
    """
    删除卡项
    
    Args:
        card_id: 卡项ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_card = db.execute(
        select(Card).where(Card.id == card_id)
    ).scalar_one_or_none()
    
    if db_card is None:
        raise HTTPException(status_code=404, detail=f"卡项ID {card_id} 不存在")
    
    db.delete(db_card)
    db.commit()
    return {"message": "删除成功", "id": card_id}

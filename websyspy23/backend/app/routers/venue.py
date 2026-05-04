"""
场地管理API路由
包含场地的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from ..database import get_db
from ..models import Venue, CourseSchedule
from ..schemas import VenueBase, VenueCreate, VenueUpdate, VenueResponse

# 创建API路由实例
router = APIRouter(prefix="/api/v1/venues", tags=["场地管理"])


@router.post("", response_model=VenueResponse, summary="创建场地")
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
    """
    创建新的场地
    
    Args:
        venue: 场地创建数据
        db: 数据库会话
    
    Returns:
        创建的场地信息
    """
    # 检查场地代码是否已存在
    existing = db.execute(
        select(Venue).where(Venue.code == venue.code)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"场地代码 '{venue.code}' 已存在")
    
    # 创建新场地
    db_venue = Venue(**venue.model_dump())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue


@router.get("", response_model=List[VenueResponse], summary="获取场地列表")
def get_venues(
    is_active: Optional[bool] = Query(None, description="是否启用"),
    venue_type: Optional[str] = Query(None, description="场地类型"),
    db: Session = Depends(get_db)
):
    """
    获取场地列表
    
    Args:
        is_active: 是否启用筛选
        venue_type: 场地类型筛选
        db: 数据库会话
    
    Returns:
        场地列表
    """
    query = select(Venue)
    if is_active is not None:
        query = query.where(Venue.is_active == is_active)
    if venue_type is not None:
        query = query.where(Venue.venue_type == venue_type)
    query = query.order_by(Venue.sort_order, Venue.id)
    
    venues = db.execute(query).scalars().all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse, summary="获取场地详情")
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """
    获取场地详情
    
    Args:
        venue_id: 场地ID
        db: 数据库会话
    
    Returns:
        场地详情
    """
    venue = db.execute(
        select(Venue).where(Venue.id == venue_id)
    ).scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(status_code=404, detail=f"场地ID {venue_id} 不存在")
    
    return venue


@router.put("/{venue_id}", response_model=VenueResponse, summary="更新场地")
def update_venue(
    venue_id: int, 
    venue: VenueUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新场地信息
    
    Args:
        venue_id: 场地ID
        venue: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的场地信息
    """
    db_venue = db.execute(
        select(Venue).where(Venue.id == venue_id)
    ).scalar_one_or_none()
    
    if db_venue is None:
        raise HTTPException(status_code=404, detail=f"场地ID {venue_id} 不存在")
    
    # 如果更新了场地代码，检查是否已存在
    update_data = venue.model_dump(exclude_unset=True)
    if "code" in update_data:
        existing = db.execute(
            select(Venue).where(Venue.code == update_data["code"], Venue.id != venue_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail=f"场地代码 '{update_data['code']}' 已存在")
    
    # 更新字段
    for key, value in update_data.items():
        setattr(db_venue, key, value)
    
    db.commit()
    db.refresh(db_venue)
    return db_venue


@router.delete("/{venue_id}", summary="删除场地")
def delete_venue(venue_id: int, db: Session = Depends(get_db)):
    """
    删除场地
    
    Args:
        venue_id: 场地ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_venue = db.execute(
        select(Venue).where(Venue.id == venue_id)
    ).scalar_one_or_none()
    
    if db_venue is None:
        raise HTTPException(status_code=404, detail=f"场地ID {venue_id} 不存在")
    
    # 检查是否有关联的课程排期
    schedule_count = db.execute(
        select(CourseSchedule).where(CourseSchedule.venue_id == venue_id)
    ).scalars().all()
    
    if schedule_count:
        raise HTTPException(
            status_code=400, 
            detail=f"场地ID {venue_id} 有关联的排期，无法删除"
        )
    
    db.delete(db_venue)
    db.commit()
    return {"message": "删除成功", "id": venue_id}

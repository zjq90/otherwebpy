"""
房产信息管理API路由
实现房产信息的增删改查功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Property as PropertyModel
from app.schemas import (
    Property as PropertySchema,
    PropertyCreate as PropertyCreateSchema,
    PropertyUpdate as PropertyUpdateSchema,
)

router = APIRouter(
    prefix="/api/properties",
    tags=["房产信息管理"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", response_model=List[PropertySchema], summary="获取房产列表")
def get_properties(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    is_active: Optional[bool] = Query(None, description="是否启用过滤"),
    building: Optional[str] = Query(None, description="楼栋号筛选"),
    owner_name: Optional[str] = Query(None, description="业主姓名筛选"),
    db: Session = Depends(get_db)
):
    """
    获取所有房产信息列表，支持分页和筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **is_active**: 按启用状态筛选
    - **building**: 按楼栋号筛选
    - **owner_name**: 按业主姓名筛选（模糊查询）
    """
    query = db.query(PropertyModel)
    
    if is_active is not None:
        query = query.filter(PropertyModel.is_active == is_active)
    if building:
        query = query.filter(PropertyModel.building.like(f"%{building}%"))
    if owner_name:
        query = query.filter(PropertyModel.owner_name.like(f"%{owner_name}%"))
    
    properties = query.order_by(PropertyModel.created_at.desc()).offset(skip).limit(limit).all()
    return properties


@router.get("/{property_id}", response_model=PropertySchema, summary="获取单个房产信息")
def get_property(property_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个房产信息详情
    
    - **property_id**: 房产ID
    """
    property_obj = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if property_obj is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    return property_obj


@router.post("/", response_model=PropertySchema, summary="创建房产信息")
def create_property(
    property_data: PropertyCreateSchema,
    db: Session = Depends(get_db)
):
    """
    创建新的房产信息
    
    - **property_data**: 房产信息
    """
    # 检查房产编号是否已存在
    existing = db.query(PropertyModel).filter(
        PropertyModel.property_number == property_data.property_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="房产编号已存在")
    
    db_property = PropertyModel(**property_data.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


@router.put("/{property_id}", response_model=PropertySchema, summary="更新房产信息")
def update_property(
    property_id: int,
    property_data: PropertyUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    更新房产信息
    
    - **property_id**: 房产ID
    - **property_data**: 更新的房产信息
    """
    db_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    
    # 只更新传入的字段
    update_data = property_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_property, key, value)
    
    db.commit()
    db.refresh(db_property)
    return db_property


@router.delete("/{property_id}", summary="删除房产信息")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    """
    删除房产信息（逻辑删除，实际改为禁用）
    
    - **property_id**: 房产ID
    """
    db_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    
    # 逻辑删除：设置为禁用状态
    db_property.is_active = False
    db.commit()
    
    return {"message": "房产信息已禁用", "id": property_id}


@router.post("/{property_id}/toggle", response_model=PropertySchema, summary="切换房产启用状态")
def toggle_property_status(property_id: int, db: Session = Depends(get_db)):
    """
    切换房产的启用/禁用状态
    
    - **property_id**: 房产ID
    """
    db_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    
    db_property.is_active = not db_property.is_active
    db.commit()
    db.refresh(db_property)
    return db_property


@router.get("/search/by-number/{property_number}", response_model=PropertySchema, summary="按房产编号查询")
def get_property_by_number(property_number: str, db: Session = Depends(get_db)):
    """
    根据房产编号查询房产信息
    
    - **property_number**: 房产编号
    """
    property_obj = db.query(PropertyModel).filter(
        PropertyModel.property_number == property_number
    ).first()
    if property_obj is None:
        raise HTTPException(status_code=404, detail="房产信息不存在")
    return property_obj

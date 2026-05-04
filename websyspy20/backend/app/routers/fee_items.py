"""
费用项目管理API路由
实现费用项目的增删改查功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FeeItem as FeeItemModel
from app.schemas import (
    FeeItem as FeeItemSchema,
    FeeItemCreate as FeeItemCreateSchema,
    FeeItemUpdate as FeeItemUpdateSchema,
)

router = APIRouter(
    prefix="/api/fee-items",
    tags=["费用项目管理"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", response_model=List[FeeItemSchema], summary="获取费用项目列表")
def get_fee_items(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    is_active: Optional[bool] = Query(None, description="是否启用过滤"),
    db: Session = Depends(get_db)
):
    """
    获取所有费用项目列表，支持分页和筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **is_active**: 按启用状态筛选
    """
    query = db.query(FeeItemModel)
    
    if is_active is not None:
        query = query.filter(FeeItemModel.is_active == is_active)
    
    fee_items = query.order_by(FeeItemModel.created_at.desc()).offset(skip).limit(limit).all()
    return fee_items


@router.get("/{fee_item_id}", response_model=FeeItemSchema, summary="获取单个费用项目")
def get_fee_item(fee_item_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个费用项目详情
    
    - **fee_item_id**: 费用项目ID
    """
    fee_item = db.query(FeeItemModel).filter(FeeItemModel.id == fee_item_id).first()
    if fee_item is None:
        raise HTTPException(status_code=404, detail="费用项目不存在")
    return fee_item


@router.post("/", response_model=FeeItemSchema, summary="创建费用项目")
def create_fee_item(
    fee_item: FeeItemCreateSchema,
    db: Session = Depends(get_db)
):
    """
    创建新的费用项目
    
    - **fee_item**: 费用项目信息
    """
    # 检查编码是否已存在
    existing = db.query(FeeItemModel).filter(FeeItemModel.code == fee_item.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="费用项目编码已存在")
    
    db_fee_item = FeeItemModel(**fee_item.dict())
    db.add(db_fee_item)
    db.commit()
    db.refresh(db_fee_item)
    return db_fee_item


@router.put("/{fee_item_id}", response_model=FeeItemSchema, summary="更新费用项目")
def update_fee_item(
    fee_item_id: int,
    fee_item: FeeItemUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    更新费用项目信息
    
    - **fee_item_id**: 费用项目ID
    - **fee_item**: 更新的费用项目信息
    """
    db_fee_item = db.query(FeeItemModel).filter(FeeItemModel.id == fee_item_id).first()
    if db_fee_item is None:
        raise HTTPException(status_code=404, detail="费用项目不存在")
    
    # 只更新传入的字段
    update_data = fee_item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_fee_item, key, value)
    
    db.commit()
    db.refresh(db_fee_item)
    return db_fee_item


@router.delete("/{fee_item_id}", summary="删除费用项目")
def delete_fee_item(fee_item_id: int, db: Session = Depends(get_db)):
    """
    删除费用项目（逻辑删除，实际改为禁用）
    
    - **fee_item_id**: 费用项目ID
    """
    db_fee_item = db.query(FeeItemModel).filter(FeeItemModel.id == fee_item_id).first()
    if db_fee_item is None:
        raise HTTPException(status_code=404, detail="费用项目不存在")
    
    # 逻辑删除：设置为禁用状态
    db_fee_item.is_active = False
    db.commit()
    
    return {"message": "费用项目已禁用", "id": fee_item_id}


@router.post("/{fee_item_id}/toggle", response_model=FeeItemSchema, summary="切换费用项目启用状态")
def toggle_fee_item_status(fee_item_id: int, db: Session = Depends(get_db)):
    """
    切换费用项目的启用/禁用状态
    
    - **fee_item_id**: 费用项目ID
    """
    db_fee_item = db.query(FeeItemModel).filter(FeeItemModel.id == fee_item_id).first()
    if db_fee_item is None:
        raise HTTPException(status_code=404, detail="费用项目不存在")
    
    db_fee_item.is_active = not db_fee_item.is_active
    db.commit()
    db.refresh(db_fee_item)
    return db_fee_item

"""
批次管理API路由
提供农产品批次的增删改查功能，包括二维码生成
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db
from app.utils.qrcode_generator import generate_qrcode_for_batch

# 创建路由实例
router = APIRouter(
    prefix="/batches",
    tags=["批次管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=schemas.Batch, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch_in: schemas.BatchCreate,
    db: Session = Depends(get_db)
):
    """
    创建新批次
    
    Args:
        batch_in: 批次创建数据
        db: 数据库会话
        
    Returns:
        创建的批次对象
    """
    # 检查关联的产品是否存在
    product = crud.product.get(db, id=batch_in.product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联的产品不存在"
        )
    
    # 检查批次编号是否已存在
    existing_batch = crud.batch.get_by_batch_number(db, batch_number=batch_in.batch_number)
    if existing_batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="批次编号已存在"
        )
    
    # 创建批次
    batch = crud.batch.create(db, obj_in=batch_in.model_dump())
    
    # 为批次生成二维码
    batch = generate_qrcode_for_batch(db, batch.id)
    
    return batch


@router.get("/", response_model=List[schemas.Batch])
def read_batches(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取批次列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        product_id: 可选，按产品ID筛选
        db: 数据库会话
        
    Returns:
        批次列表
    """
    if product_id:
        batches = crud.batch.get_by_product_id(
            db, product_id=product_id, skip=skip, limit=limit
        )
    else:
        batches = crud.batch.get_multi(db, skip=skip, limit=limit)
    return batches


@router.get("/{batch_id}", response_model=schemas.Batch)
def read_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个批次
    
    Args:
        batch_id: 批次ID
        db: 数据库会话
        
    Returns:
        批次对象
    """
    batch = crud.batch.get(db, id=batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    return batch


@router.get("/{batch_id}/details", response_model=schemas.BatchWithDetails)
def read_batch_with_details(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    获取批次详情（包含关联数据）
    
    Args:
        batch_id: 批次ID
        db: 数据库会话
        
    Returns:
        批次详情对象
    """
    batch = crud.batch.get_with_details(db, id=batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    return batch


@router.get("/number/{batch_number}", response_model=schemas.Batch)
def read_batch_by_number(
    batch_number: str,
    db: Session = Depends(get_db)
):
    """
    根据批次编号获取批次
    
    Args:
        batch_number: 批次编号
        db: 数据库会话
        
    Returns:
        批次对象
    """
    batch = crud.batch.get_by_batch_number(db, batch_number=batch_number)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    return batch


@router.put("/{batch_id}", response_model=schemas.Batch)
def update_batch(
    batch_id: int,
    batch_in: schemas.BatchUpdate,
    db: Session = Depends(get_db)
):
    """
    更新批次信息
    
    Args:
        batch_id: 批次ID
        batch_in: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的批次对象
    """
    batch = crud.batch.get(db, id=batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    # 如果更新了产品ID，检查新产品是否存在
    update_data = batch_in.model_dump(exclude_unset=True)
    if "product_id" in update_data:
        product = crud.product.get(db, id=update_data["product_id"])
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的产品不存在"
            )
    
    # 如果更新了批次编号，检查新编号是否已存在
    if "batch_number" in update_data:
        existing_batch = crud.batch.get_by_batch_number(db, batch_number=update_data["batch_number"])
        if existing_batch and existing_batch.id != batch_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="批次编号已存在"
            )
    
    # 更新批次
    batch = crud.batch.update(db, db_obj=batch, obj_in=update_data)
    return batch


@router.delete("/{batch_id}", response_model=schemas.Batch)
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    删除批次
    
    Args:
        batch_id: 批次ID
        db: 数据库会话
        
    Returns:
        被删除的批次对象
    """
    batch = crud.batch.get(db, id=batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    # 检查是否有关联数据
    planting_records = crud.planting_record.get_by_batch_id(db, batch_id=batch_id, limit=1)
    if planting_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该批次有关联的种植记录，无法删除"
        )
    
    agrochemical_usages = crud.agrochemical_usage.get_by_batch_id(db, batch_id=batch_id, limit=1)
    if agrochemical_usages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该批次有关联的农资使用记录，无法删除"
        )
    
    test_results = crud.test_result.get_by_batch_id(db, batch_id=batch_id, limit=1)
    if test_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该批次有关联的检测结果，无法删除"
        )
    
    # 删除批次
    batch = crud.batch.remove(db, id=batch_id)
    return batch

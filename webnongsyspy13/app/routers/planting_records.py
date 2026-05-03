"""
种植记录API路由
提供种植记录的增删改查功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

# 创建路由实例
router = APIRouter(
    prefix="/planting-records",
    tags=["种植记录管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=schemas.PlantingRecord, status_code=status.HTTP_201_CREATED)
def create_planting_record(
    record_in: schemas.PlantingRecordCreate,
    db: Session = Depends(get_db)
):
    """
    创建新种植记录
    
    Args:
        record_in: 种植记录创建数据
        db: 数据库会话
        
    Returns:
        创建的种植记录对象
    """
    # 检查关联的批次是否存在
    batch = crud.batch.get(db, id=record_in.batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联的批次不存在"
        )
    
    # 创建种植记录
    record = crud.planting_record.create(db, obj_in=record_in.model_dump())
    return record


@router.get("/", response_model=List[schemas.PlantingRecord])
def read_planting_records(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取种植记录列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        batch_id: 可选，按批次ID筛选
        db: 数据库会话
        
    Returns:
        种植记录列表
    """
    if batch_id:
        records = crud.planting_record.get_by_batch_id(
            db, batch_id=batch_id, skip=skip, limit=limit
        )
    else:
        records = crud.planting_record.get_multi(db, skip=skip, limit=limit)
    return records


@router.get("/{record_id}", response_model=schemas.PlantingRecord)
def read_planting_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个种植记录
    
    Args:
        record_id: 种植记录ID
        db: 数据库会话
        
    Returns:
        种植记录对象
    """
    record = crud.planting_record.get(db, id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="种植记录不存在"
        )
    return record


@router.put("/{record_id}", response_model=schemas.PlantingRecord)
def update_planting_record(
    record_id: int,
    record_in: schemas.PlantingRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新种植记录
    
    Args:
        record_id: 种植记录ID
        record_in: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的种植记录对象
    """
    record = crud.planting_record.get(db, id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="种植记录不存在"
        )
    
    # 如果更新了批次ID，检查新批次是否存在
    update_data = record_in.model_dump(exclude_unset=True)
    if "batch_id" in update_data:
        batch = crud.batch.get(db, id=update_data["batch_id"])
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的批次不存在"
            )
    
    # 更新种植记录
    record = crud.planting_record.update(db, db_obj=record, obj_in=update_data)
    return record


@router.delete("/{record_id}", response_model=schemas.PlantingRecord)
def delete_planting_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    删除种植记录
    
    Args:
        record_id: 种植记录ID
        db: 数据库会话
        
    Returns:
        被删除的种植记录对象
    """
    record = crud.planting_record.get(db, id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="种植记录不存在"
        )
    
    # 删除种植记录
    record = crud.planting_record.remove(db, id=record_id)
    return record

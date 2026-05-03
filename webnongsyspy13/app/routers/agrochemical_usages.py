"""
农资使用记录API路由
提供农资使用记录的增删改查功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

# 创建路由实例
router = APIRouter(
    prefix="/agrochemical-usages",
    tags=["农资使用管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=schemas.AgrochemicalUsage, status_code=status.HTTP_201_CREATED)
def create_agrochemical_usage(
    usage_in: schemas.AgrochemicalUsageCreate,
    db: Session = Depends(get_db)
):
    """
    创建新农资使用记录
    
    Args:
        usage_in: 农资使用记录创建数据
        db: 数据库会话
        
    Returns:
        创建的农资使用记录对象
    """
    # 检查关联的批次是否存在
    batch = crud.batch.get(db, id=usage_in.batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联的批次不存在"
        )
    
    # 创建农资使用记录
    usage = crud.agrochemical_usage.create(db, obj_in=usage_in.model_dump())
    return usage


@router.get("/", response_model=List[schemas.AgrochemicalUsage])
def read_agrochemical_usages(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取农资使用记录列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        batch_id: 可选，按批次ID筛选
        db: 数据库会话
        
    Returns:
        农资使用记录列表
    """
    if batch_id:
        usages = crud.agrochemical_usage.get_by_batch_id(
            db, batch_id=batch_id, skip=skip, limit=limit
        )
    else:
        usages = crud.agrochemical_usage.get_multi(db, skip=skip, limit=limit)
    return usages


@router.get("/{usage_id}", response_model=schemas.AgrochemicalUsage)
def read_agrochemical_usage(
    usage_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个农资使用记录
    
    Args:
        usage_id: 农资使用记录ID
        db: 数据库会话
        
    Returns:
        农资使用记录对象
    """
    usage = crud.agrochemical_usage.get(db, id=usage_id)
    if usage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="农资使用记录不存在"
        )
    return usage


@router.put("/{usage_id}", response_model=schemas.AgrochemicalUsage)
def update_agrochemical_usage(
    usage_id: int,
    usage_in: schemas.AgrochemicalUsageUpdate,
    db: Session = Depends(get_db)
):
    """
    更新农资使用记录
    
    Args:
        usage_id: 农资使用记录ID
        usage_in: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的农资使用记录对象
    """
    usage = crud.agrochemical_usage.get(db, id=usage_id)
    if usage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="农资使用记录不存在"
        )
    
    # 如果更新了批次ID，检查新批次是否存在
    update_data = usage_in.model_dump(exclude_unset=True)
    if "batch_id" in update_data:
        batch = crud.batch.get(db, id=update_data["batch_id"])
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的批次不存在"
            )
    
    # 更新农资使用记录
    usage = crud.agrochemical_usage.update(db, db_obj=usage, obj_in=update_data)
    return usage


@router.delete("/{usage_id}", response_model=schemas.AgrochemicalUsage)
def delete_agrochemical_usage(
    usage_id: int,
    db: Session = Depends(get_db)
):
    """
    删除农资使用记录
    
    Args:
        usage_id: 农资使用记录ID
        db: 数据库会话
        
    Returns:
        被删除的农资使用记录对象
    """
    usage = crud.agrochemical_usage.get(db, id=usage_id)
    if usage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="农资使用记录不存在"
        )
    
    # 删除农资使用记录
    usage = crud.agrochemical_usage.remove(db, id=usage_id)
    return usage

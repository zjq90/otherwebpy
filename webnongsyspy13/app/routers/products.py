"""
产品管理API路由
提供农产品的增删改查功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db

# 创建路由实例
router = APIRouter(
    prefix="/products",
    tags=["产品管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    创建新产品
    
    Args:
        product_in: 产品创建数据
        db: 数据库会话
        
    Returns:
        创建的产品对象
    """
    # 检查产品名称是否已存在
    existing_product = crud.product.get_by_name(db, name=product_in.name)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品名称已存在"
        )
    
    # 创建产品
    product = crud.product.create(db, obj_in=product_in.model_dump())
    return product


@router.get("/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取产品列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        db: 数据库会话
        
    Returns:
        产品列表
    """
    products = crud.product.get_multi(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个产品
    
    Args:
        product_id: 产品ID
        db: 数据库会话
        
    Returns:
        产品对象
    """
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    return product


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    更新产品信息
    
    Args:
        product_id: 产品ID
        product_in: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的产品对象
    """
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    # 如果更新了名称，检查新名称是否已存在
    update_data = product_in.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing_product = crud.product.get_by_name(db, name=update_data["name"])
        if existing_product and existing_product.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="产品名称已存在"
            )
    
    # 更新产品
    product = crud.product.update(db, db_obj=product, obj_in=update_data)
    return product


@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    删除产品
    
    Args:
        product_id: 产品ID
        db: 数据库会话
        
    Returns:
        被删除的产品对象
    """
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    # 检查是否有关联的批次
    batches = crud.batch.get_by_product_id(db, product_id=product_id, limit=1)
    if batches:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该产品有关联的批次，无法删除"
        )
    
    # 删除产品
    product = crud.product.remove(db, id=product_id)
    return product


@router.get("/search/", response_model=List[schemas.Product])
def search_products(
    keyword: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    搜索产品
    
    Args:
        keyword: 搜索关键词
        skip: 跳过的记录数
        limit: 返回的最大记录数
        db: 数据库会话
        
    Returns:
        符合条件的产品列表
    """
    products = crud.product.search(db, keyword=keyword, skip=skip, limit=limit)
    return products

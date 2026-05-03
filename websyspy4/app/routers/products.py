"""
产品管理路由
包含产品的增删改查等API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.routers.users import get_current_user, get_current_admin

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建产品（管理员权限）
    
    Args:
        product_data: 产品数据
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        ProductResponse: 创建的产品信息
    """
    category = db.query(Category).filter(
        Category.id == product_data.category_id,
        Category.is_deleted == False
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类不存在"
        )
    
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        category_id=product_data.category_id,
        daily_rent=product_data.daily_rent,
        deposit=product_data.deposit,
        stock_quantity=product_data.stock_quantity,
        available_quantity=product_data.available_quantity or product_data.stock_quantity,
        image_url=product_data.image_url,
        status=product_data.status,
        is_hot=product_data.is_hot
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product.to_dict()


@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None, description="分类ID"),
    is_hot: Optional[bool] = Query(None, description="是否热门"),
    status: Optional[int] = Query(None, description="产品状态"),
    db: Session = Depends(get_db)
):
    """
    获取产品列表（所有人可访问）
    
    Args:
        skip: 跳过的数量
        limit: 返回的最大数量
        category_id: 分类ID过滤
        is_hot: 是否热门过滤
        status: 产品状态过滤
        db: 数据库会话
        
    Returns:
        List[ProductResponse]: 产品列表
    """
    query = db.query(Product).filter(Product.is_deleted == False)
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if is_hot is not None:
        query = query.filter(Product.is_hot == is_hot)
    if status is not None:
        query = query.filter(Product.status == status)
    
    products = query.offset(skip).limit(limit).all()
    
    return [product.to_dict() for product in products]


@router.get("/hot", response_model=List[ProductResponse])
def get_hot_products(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取热门产品列表
    
    Args:
        limit: 返回的最大数量
        db: 数据库会话
        
    Returns:
        List[ProductResponse]: 热门产品列表
    """
    products = db.query(Product).filter(
        Product.is_deleted == False,
        Product.is_hot == True,
        Product.status == 1
    ).limit(limit).all()
    
    return [product.to_dict() for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取产品详情
    
    Args:
        product_id: 产品ID
        db: 数据库会话
        
    Returns:
        ProductResponse: 产品信息
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    return product.to_dict()


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新产品信息（管理员权限）
    
    Args:
        product_id: 产品ID
        product_data: 更新的数据
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        ProductResponse: 更新后的产品信息
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return product.to_dict()


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除产品（软删除，管理员权限）
    
    Args:
        product_id: 产品ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 删除成功提示
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    product.is_deleted = True
    db.commit()
    
    return {"message": "产品删除成功"}

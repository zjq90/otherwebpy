"""
产品管理路由模块
提供产品的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductUpdate, ProductResponse, ApiResponse
from routers.auth import get_current_admin_user
from config import PAGE_SIZE

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def get_products(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取产品列表接口（公开访问）
    支持分页、分类过滤、关键词搜索
    
    参数:
        page: 页码
        page_size: 每页数量
        category: 产品分类
        keyword: 搜索关键词
        db: 数据库会话
    
    返回:
        ApiResponse: 产品列表数据
    """
    # 构建查询，只查询上架的产品
    query = db.query(Product).filter(Product.is_active == True)
    
    # 分类过滤
    if category:
        query = query.filter(Product.category == category)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Product.name.contains(keyword)) |
            (Product.description.contains(keyword))
        )
    
    # 计算总数
    total = query.count()
    
    # 分页，按排序权重降序，创建时间降序
    offset = (page - 1) * page_size
    products = query.order_by(
        Product.sort_order.desc(),
        Product.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    # 转换为响应模型
    product_responses = [ProductResponse.from_orm(product) for product in products]
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": product_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/{product_id}", response_model=ApiResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    获取产品详情接口（公开访问）
    
    参数:
        product_id: 产品ID
        db: 数据库会话
    
    返回:
        ApiResponse: 产品详情
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在或已下架"
        )
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"product": ProductResponse.from_orm(product)}
    )


@router.post("/", response_model=ApiResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    创建产品接口（管理员专用）
    
    参数:
        product_data: 产品数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 创建结果
    """
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        content=product_data.content,
        image_url=product_data.image_url,
        price=product_data.price,
        category=product_data.category,
        sort_order=product_data.sort_order or 0,
        is_active=True
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return ApiResponse(
        success=True,
        message="产品创建成功",
        data={"product": ProductResponse.from_orm(new_product)}
    )


@router.put("/{product_id}", response_model=ApiResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    更新产品接口（管理员专用）
    
    参数:
        product_id: 产品ID
        product_data: 产品更新数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 更新结果
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    # 更新字段
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return ApiResponse(
        success=True,
        message="产品更新成功",
        data={"product": ProductResponse.from_orm(product)}
    )


@router.delete("/{product_id}", response_model=ApiResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    删除产品接口（管理员专用）
    
    参数:
        product_id: 产品ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 删除结果
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    db.delete(product)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="产品已删除"
    )


@router.put("/{product_id}/toggle-active", response_model=ApiResponse)
def toggle_product_active(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    切换产品上架状态接口（管理员专用）
    
    参数:
        product_id: 产品ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    product.is_active = not product.is_active
    db.commit()
    db.refresh(product)
    
    return ApiResponse(
        success=True,
        message=f"产品已{'上架' if product.is_active else '下架'}",
        data={"product": ProductResponse.from_orm(product)}
    )

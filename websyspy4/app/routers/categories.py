"""
分类管理路由
包含产品分类的增删改查等API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.routers.users import get_current_user, get_current_admin

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建产品分类（管理员权限）
    
    Args:
        category_data: 分类数据
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        CategoryResponse: 创建的分类信息
        
    Raises:
        HTTPException: 分类名称已存在
    """
    existing_category = db.query(Category).filter(
        Category.name == category_data.name,
        Category.is_deleted == False
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称已存在"
        )
    
    new_category = Category(
        name=category_data.name,
        description=category_data.description,
        sort_order=category_data.sort_order or 0
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category.to_dict()


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取分类列表（所有人可访问）
    
    Args:
        skip: 跳过的数量
        limit: 返回的最大数量
        db: 数据库会话
        
    Returns:
        List[CategoryResponse]: 分类列表
    """
    categories = db.query(Category).filter(
        Category.is_deleted == False
    ).order_by(Category.sort_order.asc()).offset(skip).limit(limit).all()
    
    return [category.to_dict() for category in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_by_id(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取分类详情
    
    Args:
        category_id: 分类ID
        db: 数据库会话
        
    Returns:
        CategoryResponse: 分类信息
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    return category.to_dict()


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新分类信息（管理员权限）
    
    Args:
        category_id: 分类ID
        category_data: 更新的数据
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        CategoryResponse: 更新后的分类信息
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    update_data = category_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    
    return category.to_dict()


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除分类（软删除，管理员权限）
    
    Args:
        category_id: 分类ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 删除成功提示
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_deleted == False
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    category.is_deleted = True
    db.commit()
    
    return {"message": "分类删除成功"}

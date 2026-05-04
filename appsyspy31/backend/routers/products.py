"""
营养产品路由模块
处理营养产品的增删改查、分类筛选、推荐等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from models import User, UserRole, NutritionProduct, NutritionProductCategory
from schemas import (
    NutritionProductCreate, NutritionProductUpdate, NutritionProductResponse,
    ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取营养产品列表
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[NutritionProductCategory] = Query(None, description="产品分类筛选"),
    is_recommended: Optional[bool] = Query(None, description="是否推荐筛选"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: Optional[str] = Query(None, description="排序方式: price_asc, price_desc, sales_desc, rating_desc"),
    db: Session = Depends(get_db)
):
    """
    获取营养产品列表
    
    支持分页、分类筛选、价格区间、关键词搜索、排序
    所有用户都可以查看产品列表
    
    Args:
        page: 页码
        page_size: 每页数量
        category: 产品分类筛选
        is_recommended: 是否推荐筛选
        min_price: 最低价格
        max_price: 最高价格
        keyword: 搜索关键词
        sort_by: 排序方式
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的产品列表
    """
    query = db.query(NutritionProduct).filter(NutritionProduct.is_active == True)
    
    if category:
        query = query.filter(NutritionProduct.category == category)
    
    if is_recommended is not None:
        query = query.filter(NutritionProduct.is_recommended == is_recommended)
    
    if min_price is not None:
        query = query.filter(NutritionProduct.price >= min_price)
    
    if max_price is not None:
        query = query.filter(NutritionProduct.price <= max_price)
    
    if keyword:
        query = query.filter(
            (NutritionProduct.name.contains(keyword)) |
            (NutritionProduct.brand.contains(keyword)) |
            (NutritionProduct.description.contains(keyword))
        )
    
    if sort_by:
        if sort_by == 'price_asc':
            query = query.order_by(NutritionProduct.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(NutritionProduct.price.desc())
        elif sort_by == 'sales_desc':
            query = query.order_by(NutritionProduct.sales_count.desc())
        elif sort_by == 'rating_desc':
            query = query.order_by(NutritionProduct.rating.desc())
    else:
        query = query.order_by(NutritionProduct.is_recommended.desc(), NutritionProduct.sales_count.desc())
    
    paginated = paginate_query(query, page, page_size)
    
    products_response = [
        NutritionProductResponse.model_validate(product).model_dump()
        for product in paginated.items
    ]
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"products": products_response},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取产品详情
# ========================================

@router.get("/{product_id}", response_model=ResponseModel)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    获取产品详情
    
    Args:
        product_id: 产品ID
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含产品信息的响应
    """
    product = db.query(NutritionProduct).filter(
        NutritionProduct.id == product_id,
        NutritionProduct.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在或已下架"
        )
    
    product_response = NutritionProductResponse.model_validate(product)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"product": product_response.model_dump()}
    )

# ========================================
# 创建产品（管理员/工作人员权限）
# ========================================

@router.post("", response_model=ResponseModel)
async def create_product(
    product_data: NutritionProductCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    创建新营养产品
    
    需要管理员或工作人员权限
    
    Args:
        product_data: 产品数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新产品信息的响应
    """
    existing_product = db.query(NutritionProduct).filter(
        NutritionProduct.name == product_data.name,
        NutritionProduct.brand == product_data.brand
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该品牌的产品名称已存在"
        )
    
    new_product = NutritionProduct(
        name=product_data.name,
        brand=product_data.brand,
        category=product_data.category,
        description=product_data.description,
        price=product_data.price,
        original_price=product_data.original_price,
        stock=product_data.stock,
        unit=product_data.unit,
        suitable_for=product_data.suitable_for,
        benefits=product_data.benefits,
        usage_method=product_data.usage_method,
        image_url=product_data.image_url,
        image_urls=product_data.image_urls,
        is_recommended=product_data.is_recommended,
        is_active=True
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    product_response = NutritionProductResponse.model_validate(new_product)
    
    return ResponseModel(
        code=200,
        message="产品创建成功",
        data={"product": product_response.model_dump()}
    )

# ========================================
# 更新产品（管理员/工作人员权限）
# ========================================

@router.put("/{product_id}", response_model=ResponseModel)
async def update_product(
    product_id: int,
    product_data: NutritionProductUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    更新产品信息
    
    需要管理员或工作人员权限
    
    Args:
        product_id: 产品ID
        product_data: 更新数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后产品信息的响应
    """
    product = db.query(NutritionProduct).filter(
        NutritionProduct.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    if 'name' in update_data or 'brand' in update_data:
        check_name = update_data.get('name', product.name)
        check_brand = update_data.get('brand', product.brand)
        
        existing_product = db.query(NutritionProduct).filter(
            NutritionProduct.name == check_name,
            NutritionProduct.brand == check_brand,
            NutritionProduct.id != product_id
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该品牌的产品名称已存在"
            )
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    product_response = NutritionProductResponse.model_validate(product)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={"product": product_response.model_dump()}
    )

# ========================================
# 上架/下架产品（管理员/工作人员权限）
# ========================================

@router.put("/{product_id}/toggle-status", response_model=ResponseModel)
async def toggle_product_status(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    切换产品状态（上架/下架）
    
    需要管理员或工作人员权限
    
    Args:
        product_id: 产品ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    product = db.query(NutritionProduct).filter(
        NutritionProduct.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    product.is_active = not product.is_active
    db.commit()
    db.refresh(product)
    
    status_text = "上架" if product.is_active else "下架"
    product_response = NutritionProductResponse.model_validate(product)
    
    return ResponseModel(
        code=200,
        message=f"产品已{status_text}",
        data={"product": product_response.model_dump()}
    )

# ========================================
# 设置/取消推荐产品（管理员/工作人员权限）
# ========================================

@router.put("/{product_id}/toggle-recommended", response_model=ResponseModel)
async def toggle_product_recommended(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    切换产品推荐状态
    
    需要管理员或工作人员权限
    
    Args:
        product_id: 产品ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    product = db.query(NutritionProduct).filter(
        NutritionProduct.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    product.is_recommended = not product.is_recommended
    db.commit()
    db.refresh(product)
    
    status_text = "推荐" if product.is_recommended else "取消推荐"
    product_response = NutritionProductResponse.model_validate(product)
    
    return ResponseModel(
        code=200,
        message=f"产品已{status_text}",
        data={"product": product_response.model_dump()}
    )

# ========================================
# 删除产品（管理员权限）
# ========================================

@router.delete("/{product_id}", response_model=ResponseModel)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    删除产品
    
    需要管理员权限
    软删除：设置is_active为False
    
    Args:
        product_id: 产品ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    product = db.query(NutritionProduct).filter(
        NutritionProduct.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    product.is_active = False
    db.commit()
    
    return ResponseModel(
        code=200,
        message="产品已删除",
        data=None
    )

# ========================================
# 获取产品分类列表
# ========================================

@router.get("/categories/list", response_model=ResponseModel)
async def get_product_categories():
    """
    获取所有营养产品分类
    
    Returns:
        ResponseModel: 包含产品分类列表的响应
    """
    categories = [
        {"value": category.value, "label": get_category_label(category.value)}
        for category in NutritionProductCategory
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"categories": categories}
    )

def get_category_label(value: str) -> str:
    """获取分类标签"""
    labels = {
        'protein': '蛋白粉',
        'vitamin': '维生素',
        'supplement': '运动补剂',
        'meal_replacement': '代餐',
        'energy': '能量补充'
    }
    return labels.get(value, value)

# ========================================
# 获取推荐产品列表
# ========================================

@router.get("/list/recommended", response_model=ResponseModel)
async def get_recommended_products(
    limit: int = Query(10, ge=1, le=20, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取推荐产品列表
    
    用于首页推荐展示
    
    Args:
        limit: 返回数量
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含推荐产品列表的响应
    """
    products = db.query(NutritionProduct).filter(
        NutritionProduct.is_active == True,
        NutritionProduct.is_recommended == True
    ).order_by(
        NutritionProduct.sales_count.desc()
    ).limit(limit).all()
    
    products_response = [
        NutritionProductResponse.model_validate(product).model_dump()
        for product in products
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"products": products_response}
    )

# ========================================
# 获取热门产品列表
# ========================================

@router.get("/list/popular", response_model=ResponseModel)
async def get_popular_products(
    limit: int = Query(10, ge=1, le=20, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取热门产品列表
    
    按销量排序
    
    Args:
        limit: 返回数量
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含热门产品列表的响应
    """
    products = db.query(NutritionProduct).filter(
        NutritionProduct.is_active == True
    ).order_by(
        NutritionProduct.sales_count.desc()
    ).limit(limit).all()
    
    products_response = [
        NutritionProductResponse.model_validate(product).model_dump()
        for product in products
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"products": products_response}
    )

# ========================================
# 获取产品统计信息（管理员/工作人员权限）
# ========================================

@router.get("/stats/overview", response_model=ResponseModel)
async def get_product_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    获取产品统计信息
    
    需要管理员或工作人员权限
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含统计信息的响应
    """
    total_products = db.query(NutritionProduct).count()
    active_products = db.query(NutritionProduct).filter(
        NutritionProduct.is_active == True
    ).count()
    recommended_products = db.query(NutritionProduct).filter(
        NutritionProduct.is_recommended == True
    ).count()
    out_of_stock = db.query(NutritionProduct).filter(
        NutritionProduct.stock == 0
    ).count()
    
    category_stats = []
    for category in NutritionProductCategory:
        count = db.query(NutritionProduct).filter(
            NutritionProduct.category == category,
            NutritionProduct.is_active == True
        ).count()
        category_stats.append({
            'category': category.value,
            'label': get_category_label(category.value),
            'count': count
        })
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            'total': total_products,
            'active': active_products,
            'recommended': recommended_products,
            'out_of_stock': out_of_stock,
            'category_stats': category_stats
        }
    )

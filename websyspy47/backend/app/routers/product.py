from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.product import Product, PointsRule, PointsExchange
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    PointsRuleCreate, PointsRuleUpdate, PointsRuleResponse,
    PointsExchangeCreate, PointsExchangeUpdate, PointsExchangeResponse
)
from app.schemas.common import ApiResponse, PageResult

router = APIRouter(prefix="/products", tags=["商品与积分管理"])

@router.post("/", response_model=ApiResponse[ProductResponse])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    创建积分商品
    """
    if product.product_code:
        existing = db.query(Product).filter(Product.product_code == product.product_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="商品编码已存在")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return ApiResponse(data=db_product)

@router.get("/{product_id}", response_model=ApiResponse[ProductResponse])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    获取商品详情
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ApiResponse(data=product)

@router.get("/", response_model=ApiResponse[PageResult[ProductResponse]])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    product_name: Optional[str] = None,
    product_code: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取商品列表（分页）
    """
    query = db.query(Product)
    
    if product_name:
        query = query.filter(Product.product_name.like(f"%{product_name}%"))
    if product_code:
        query = query.filter(Product.product_code.like(f"%{product_code}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if status is not None:
        query = query.filter(Product.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    products = query.order_by(Product.sort.asc(), Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[ProductResponse](
        list=products,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/{product_id}", response_model=ApiResponse[ProductResponse])
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """
    更新商品信息
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return ApiResponse(data=product)

@router.delete("/{product_id}", response_model=ApiResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    删除商品（软删除-下架）
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    product.status = 0
    db.commit()
    return ApiResponse(message="商品已下架")

@router.post("/points-rules/", response_model=ApiResponse[PointsRuleResponse])
def create_points_rule(rule: PointsRuleCreate, db: Session = Depends(get_db)):
    """
    创建积分规则
    """
    db_rule = PointsRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return ApiResponse(data=db_rule)

@router.get("/points-rules/", response_model=ApiResponse[PageResult[PointsRuleResponse]])
def list_points_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取积分规则列表
    """
    query = db.query(PointsRule)
    
    if category_id:
        query = query.filter(PointsRule.category_id == category_id)
    if status is not None:
        query = query.filter(PointsRule.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    rules = query.order_by(PointsRule.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[PointsRuleResponse](
        list=rules,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/points-rules/{rule_id}", response_model=ApiResponse[PointsRuleResponse])
def update_points_rule(rule_id: int, rule_update: PointsRuleUpdate, db: Session = Depends(get_db)):
    """
    更新积分规则
    """
    rule = db.query(PointsRule).filter(PointsRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="积分规则不存在")
    
    update_data = rule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    db.commit()
    db.refresh(rule)
    return ApiResponse(data=rule)

@router.get("/points-exchanges/", response_model=ApiResponse[PageResult[PointsExchangeResponse]])
def list_points_exchanges(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    product_id: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取积分兑换记录列表
    """
    query = db.query(PointsExchange)
    
    if user_id:
        query = query.filter(PointsExchange.user_id == user_id)
    if product_id:
        query = query.filter(PointsExchange.product_id == product_id)
    if status is not None:
        query = query.filter(PointsExchange.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    exchanges = query.order_by(PointsExchange.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[PointsExchangeResponse](
        list=exchanges,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/points-exchanges/{exchange_id}", response_model=ApiResponse[PointsExchangeResponse])
def update_points_exchange(exchange_id: int, exchange_update: PointsExchangeUpdate, db: Session = Depends(get_db)):
    """
    更新积分兑换记录（发货等操作）
    """
    exchange = db.query(PointsExchange).filter(PointsExchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="兑换记录不存在")
    
    update_data = exchange_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exchange, key, value)
    
    db.commit()
    db.refresh(exchange)
    return ApiResponse(data=exchange)

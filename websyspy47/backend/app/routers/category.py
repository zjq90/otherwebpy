from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.category import ClothingCategory, PricingRule
from app.schemas.category import (
    ClothingCategoryCreate, ClothingCategoryUpdate, ClothingCategoryResponse,
    PricingRuleCreate, PricingRuleUpdate, PricingRuleResponse
)
from app.schemas.common import ApiResponse, PageResult

router = APIRouter(prefix="/categories", tags=["价格与分类管理"])

@router.post("/", response_model=ApiResponse[ClothingCategoryResponse])
def create_category(category: ClothingCategoryCreate, db: Session = Depends(get_db)):
    """
    创建衣物分类
    """
    if category.code:
        existing = db.query(ClothingCategory).filter(ClothingCategory.code == category.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="分类编码已存在")
    
    db_category = ClothingCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return ApiResponse(data=db_category)

@router.get("/{category_id}", response_model=ApiResponse[ClothingCategoryResponse])
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    获取分类详情
    """
    category = db.query(ClothingCategory).filter(ClothingCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return ApiResponse(data=category)

@router.get("/", response_model=ApiResponse[List[ClothingCategoryResponse]])
def list_categories(
    parent_id: Optional[int] = Query(0),
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取分类列表
    """
    query = db.query(ClothingCategory).filter(ClothingCategory.parent_id == parent_id)
    
    if status is not None:
        query = query.filter(ClothingCategory.status == status)
    
    categories = query.order_by(ClothingCategory.sort.asc(), ClothingCategory.id.asc()).all()
    return ApiResponse(data=categories)

@router.put("/{category_id}", response_model=ApiResponse[ClothingCategoryResponse])
def update_category(category_id: int, category_update: ClothingCategoryUpdate, db: Session = Depends(get_db)):
    """
    更新分类信息
    """
    category = db.query(ClothingCategory).filter(ClothingCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return ApiResponse(data=category)

@router.delete("/{category_id}", response_model=ApiResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    删除分类（软删除）
    """
    category = db.query(ClothingCategory).filter(ClothingCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    category.status = 0
    db.commit()
    return ApiResponse(message="分类已禁用")

@router.post("/pricing-rules/", response_model=ApiResponse[PricingRuleResponse])
def create_pricing_rule(rule: PricingRuleCreate, db: Session = Depends(get_db)):
    """
    创建计价规则
    """
    existing = db.query(PricingRule).filter(PricingRule.category_id == rule.category_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该分类已有计价规则")
    
    db_rule = PricingRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return ApiResponse(data=db_rule)

@router.get("/pricing-rules/{rule_id}", response_model=ApiResponse[PricingRuleResponse])
def get_pricing_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    获取计价规则详情
    """
    rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="计价规则不存在")
    return ApiResponse(data=rule)

@router.get("/pricing-rules/", response_model=ApiResponse[PageResult[PricingRuleResponse]])
def list_pricing_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    pricing_type: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取计价规则列表
    """
    query = db.query(PricingRule)
    
    if category_id:
        query = query.filter(PricingRule.category_id == category_id)
    if pricing_type is not None:
        query = query.filter(PricingRule.pricing_type == pricing_type)
    if status is not None:
        query = query.filter(PricingRule.status == status)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    rules = query.order_by(PricingRule.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = PageResult[PricingRuleResponse](
        list=rules,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/pricing-rules/{rule_id}", response_model=ApiResponse[PricingRuleResponse])
def update_pricing_rule(rule_id: int, rule_update: PricingRuleUpdate, db: Session = Depends(get_db)):
    """
    更新计价规则
    """
    rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="计价规则不存在")
    
    update_data = rule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    db.commit()
    db.refresh(rule)
    return ApiResponse(data=rule)

@router.delete("/pricing-rules/{rule_id}", response_model=ApiResponse)
def delete_pricing_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    删除计价规则（软删除）
    """
    rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="计价规则不存在")
    
    rule.status = 0
    db.commit()
    return ApiResponse(message="计价规则已禁用")

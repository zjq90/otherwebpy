from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.models import Formula, FormulaAdjustment, FormulaStatus
from app.schemas.schemas import (
    Formula as FormulaSchema,
    FormulaCreate,
    FormulaUpdate,
    FormulaAdjustment as FormulaAdjustmentSchema,
    FormulaAdjustmentCreate
)

router = APIRouter(prefix="/api/formulas", tags=["配方管理"])


@router.get("/", response_model=List[FormulaSchema], summary="获取配方列表")
def get_formulas(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    concrete_type: Optional[str] = Query(None, description="混凝土类型"),
    strength_grade: Optional[str] = Query(None, description="强度等级"),
    status: Optional[FormulaStatus] = Query(None, description="状态"),
    db: Session = Depends(get_db)
):
    """
    获取配方列表，支持分页和筛选
    
    - **skip**: 跳过的记录数，用于分页
    - **limit**: 返回的最大记录数
    - **keyword**: 搜索关键词，匹配配方编码、名称
    - **concrete_type**: 按混凝土类型筛选
    - **strength_grade**: 按强度等级筛选
    - **status**: 按状态筛选
    """
    query = db.query(Formula)
    
    if keyword:
        query = query.filter(
            or_(
                Formula.formula_code.contains(keyword),
                Formula.formula_name.contains(keyword)
            )
        )
    if concrete_type:
        query = query.filter(Formula.concrete_type == concrete_type)
    if strength_grade:
        query = query.filter(Formula.strength_grade == strength_grade)
    if status:
        query = query.filter(Formula.status == status)
    
    formulas = query.order_by(Formula.created_at.desc()).offset(skip).limit(limit).all()
    return formulas


@router.get("/{formula_id}", response_model=FormulaSchema, summary="获取配方详情")
def get_formula(formula_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取配方详情
    
    - **formula_id**: 配方ID
    """
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="配方不存在")
    return formula


@router.post("/", response_model=FormulaSchema, summary="创建配方")
def create_formula(formula: FormulaCreate, db: Session = Depends(get_db)):
    """
    创建新配方
    
    - **formula**: 配方数据
    """
    existing = db.query(Formula).filter(Formula.formula_code == formula.formula_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="配方编码已存在")
    
    db_formula = Formula(**formula.dict())
    db_formula.created_at = datetime.utcnow()
    db_formula.updated_at = datetime.utcnow()
    
    db.add(db_formula)
    db.commit()
    db.refresh(db_formula)
    return db_formula


@router.put("/{formula_id}", response_model=FormulaSchema, summary="更新配方")
def update_formula(formula_id: int, formula: FormulaUpdate, db: Session = Depends(get_db)):
    """
    更新配方信息
    
    - **formula_id**: 配方ID
    - **formula**: 更新的配方数据
    """
    db_formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not db_formula:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    update_data = formula.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_formula, key, value)
    
    db_formula.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_formula)
    return db_formula


@router.delete("/{formula_id}", summary="删除配方")
def delete_formula(formula_id: int, db: Session = Depends(get_db)):
    """
    删除配方（软删除，将状态设为INACTIVE）
    
    - **formula_id**: 配方ID
    """
    db_formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not db_formula:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    db_formula.status = FormulaStatus.INACTIVE
    db_formula.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "配方已删除", "formula_id": formula_id}


@router.post("/{formula_id}/adjust", response_model=FormulaAdjustmentSchema, summary="调整配方参数")
def adjust_formula(formula_id: int, adjustment: FormulaAdjustmentCreate, db: Session = Depends(get_db)):
    """
    调整配方参数并记录调整日志
    
    - **formula_id**: 配方ID
    - **adjustment**: 调整数据
    """
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    adjustment.formula_id = formula_id
    
    if adjustment.original_cement is None:
        adjustment.original_cement = formula.cement
    if adjustment.original_sand is None:
        adjustment.original_sand = formula.sand
    if adjustment.original_gravel is None:
        adjustment.original_gravel = formula.gravel
    if adjustment.original_water is None:
        adjustment.original_water = formula.water
    if adjustment.original_admixture is None:
        adjustment.original_admixture = formula.admixture
    if adjustment.original_fly_ash is None:
        adjustment.original_fly_ash = formula.fly_ash
    if adjustment.original_mineral_powder is None:
        adjustment.original_mineral_powder = formula.mineral_powder
    
    db_adjustment = FormulaAdjustment(**adjustment.dict())
    db_adjustment.created_at = datetime.utcnow()
    
    db.add(db_adjustment)
    
    if adjustment.adjusted_cement is not None:
        formula.cement = adjustment.adjusted_cement
    if adjustment.adjusted_sand is not None:
        formula.sand = adjustment.adjusted_sand
    if adjustment.adjusted_gravel is not None:
        formula.gravel = adjustment.adjusted_gravel
    if adjustment.adjusted_water is not None:
        formula.water = adjustment.adjusted_water
    if adjustment.adjusted_admixture is not None:
        formula.admixture = adjustment.adjusted_admixture
    if adjustment.adjusted_fly_ash is not None:
        formula.fly_ash = adjustment.adjusted_fly_ash
    if adjustment.adjusted_mineral_powder is not None:
        formula.mineral_powder = adjustment.adjusted_mineral_powder
    
    formula.version += 1
    formula.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_adjustment)
    
    return db_adjustment


@router.get("/{formula_id}/adjustments", response_model=List[FormulaAdjustmentSchema], summary="获取配方调整历史")
def get_formula_adjustments(formula_id: int, db: Session = Depends(get_db)):
    """
    获取配方的调整历史记录
    
    - **formula_id**: 配方ID
    """
    formula = db.query(Formula).filter(Formula.id == formula_id).first()
    if not formula:
        raise HTTPException(status_code=404, detail="配方不存在")
    
    adjustments = db.query(FormulaAdjustment).filter(
        FormulaAdjustment.formula_id == formula_id
    ).order_by(FormulaAdjustment.created_at.desc()).all()
    
    return adjustments

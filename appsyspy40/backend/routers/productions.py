"""
生产记录路由
包含生产记录、配方管理等功能
"""
from datetime import datetime
from typing import Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user, require_admin
from models.models import User, ProductionFormula, ProductionRecord, FeedingRecord
from schemas.schemas import (
    ProductionFormulaCreate, ProductionFormulaResponse,
    ProductionRecordCreate, ProductionRecordResponse,
    FeedingRecordCreate, FeedingRecordResponse,
    ApiResponse, PaginatedResponse
)


router = APIRouter(prefix="/api/productions", tags=["生产记录"])


def generate_production_no() -> str:
    """
    生成生产单号
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    return f"PRO{date_str}{now.microsecond:06d}"


def generate_qr_code() -> str:
    """
    生成二维码标识
    格式：QR + 时间戳 + 随机数
    """
    import random
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"QR{timestamp}{random_num}"


# ==================== 生产配方管理 ====================

@router.post("/formulas", response_model=ApiResponse, summary="添加生产配方")
async def create_formula(
    formula_data: ProductionFormulaCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    添加新的生产配方
    需要管理员权限
    """
    # 检查配方编码是否已存在
    existing_formula = db.query(ProductionFormula).filter(
        ProductionFormula.formula_code == formula_data.formula_code
    ).first()
    if existing_formula:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配方编码已存在"
        )
    
    new_formula = ProductionFormula(**formula_data.model_dump())
    db.add(new_formula)
    db.commit()
    db.refresh(new_formula)
    
    return ApiResponse(
        code=200,
        message="添加成功",
        data={"formula": ProductionFormulaResponse.model_validate(new_formula).model_dump()}
    )


@router.get("/formulas", response_model=PaginatedResponse, summary="获取配方列表")
async def get_formulas(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    concrete_grade: Optional[str] = Query(None, description="混凝土强度等级"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分页获取生产配方列表
    """
    query = db.query(ProductionFormula).filter(ProductionFormula.is_active == True)
    
    if concrete_grade:
        query = query.filter(ProductionFormula.concrete_grade == concrete_grade)
    
    total = query.count()
    formulas = query.order_by(ProductionFormula.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    formula_list = [ProductionFormulaResponse.model_validate(f).model_dump() for f in formulas]
    
    return PaginatedResponse(
        code=200,
        message="success",
        data={"items": formula_list},
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/formulas/{formula_id}", response_model=ApiResponse, summary="获取配方详情")
async def get_formula(
    formula_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取配方详情
    """
    formula = db.query(ProductionFormula).filter(ProductionFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配方不存在"
        )
    
    return ApiResponse(
        code=200,
        message="success",
        data={"formula": ProductionFormulaResponse.model_validate(formula).model_dump()}
    )


@router.put("/formulas/{formula_id}", response_model=ApiResponse, summary="更新配方")
async def update_formula(
    formula_id: int,
    formula_data: ProductionFormulaCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新生产配方
    需要管理员权限
    """
    formula = db.query(ProductionFormula).filter(ProductionFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配方不存在"
        )
    
    # 检查配方编码是否被其他配方使用
    if formula_data.formula_code != formula.formula_code:
        existing = db.query(ProductionFormula).filter(
            ProductionFormula.formula_code == formula_data.formula_code,
            ProductionFormula.id != formula_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="配方编码已存在"
            )
    
    # 更新字段
    update_data = formula_data.model_dump()
    for key, value in update_data.items():
        setattr(formula, key, value)
    
    db.commit()
    db.refresh(formula)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"formula": ProductionFormulaResponse.model_validate(formula).model_dump()}
    )


@router.delete("/formulas/{formula_id}", response_model=ApiResponse, summary="删除配方")
async def delete_formula(
    formula_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    删除生产配方（软删除）
    需要管理员权限
    """
    formula = db.query(ProductionFormula).filter(ProductionFormula.id == formula_id).first()
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配方不存在"
        )
    
    # 检查是否有关联的生产记录
    records = db.query(ProductionRecord).filter(
        ProductionRecord.formula_id == formula_id
    ).first()
    
    if records:
        # 软删除
        formula.is_active = False
        db.commit()
        return ApiResponse(
            code=200,
            message="配方已标记为不激活（存在关联生产记录，无法物理删除）"
        )
    
    # 物理删除
    db.delete(formula)
    db.commit()
    
    return ApiResponse(code=200, message="删除成功")


# ==================== 生产记录管理 ====================

@router.post("/records", response_model=ApiResponse, summary="创建生产记录")
async def create_production(
    production_data: ProductionRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的生产记录
    自动生成二维码标识
    """
    # 检查配方是否存在
    formula = db.query(ProductionFormula).filter(
        ProductionFormula.id == production_data.formula_id
    ).first()
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产配方不存在"
        )
    
    # 生成生产单号和二维码
    production_no = generate_production_no()
    qr_code = generate_qr_code()
    
    # 检查搅拌时间是否达标
    status_val = "正常"
    if production_data.mix_duration < production_data.target_mix_duration:
        status_val = "异常"
    
    # 创建生产记录
    new_production = ProductionRecord(
        production_no=production_no,
        formula_id=production_data.formula_id,
        qr_code=qr_code,
        truck_no=production_data.truck_no,
        mix_volume=production_data.mix_volume,
        mix_duration=production_data.mix_duration,
        target_mix_duration=production_data.target_mix_duration,
        feeding_data=production_data.feeding_data,
        status=status_val,
        operator_id=current_user.id
    )
    
    db.add(new_production)
    db.commit()
    db.refresh(new_production)
    new_production.formula = formula
    
    return ApiResponse(
        code=200,
        message="生产记录创建成功",
        data={
            "production": ProductionRecordResponse.model_validate(new_production).model_dump(),
            "qr_code": qr_code
        }
    )


@router.get("/records", response_model=PaginatedResponse, summary="获取生产记录列表")
async def get_productions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="生产状态"),
    truck_no: Optional[str] = Query(None, description="罐车编号"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分页获取生产记录列表
    """
    query = db.query(ProductionRecord)
    
    if status:
        query = query.filter(ProductionRecord.status == status)
    if truck_no:
        query = query.filter(ProductionRecord.truck_no.contains(truck_no))
    
    total = query.count()
    productions = query.order_by(ProductionRecord.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # 关联配方信息
    production_list = []
    for prod in productions:
        prod.formula = db.query(ProductionFormula).filter(
            ProductionFormula.id == prod.formula_id
        ).first()
        production_list.append(ProductionRecordResponse.model_validate(prod).model_dump())
    
    return PaginatedResponse(
        code=200,
        message="success",
        data={"items": production_list},
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/records/{production_id}", response_model=ApiResponse, summary="获取生产记录详情")
async def get_production(
    production_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取生产记录详情
    """
    production = db.query(ProductionRecord).filter(
        ProductionRecord.id == production_id
    ).first()
    if not production:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    # 关联配方和投料记录
    production.formula = db.query(ProductionFormula).filter(
        ProductionFormula.id == production.formula_id
    ).first()
    
    feeding_records = db.query(FeedingRecord).filter(
        FeedingRecord.production_id == production.id
    ).all()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "production": ProductionRecordResponse.model_validate(production).model_dump(),
            "feeding_records": [FeedingRecordResponse.model_validate(fr).model_dump() for fr in feeding_records]
        }
    )


@router.get("/qr/{qr_code}", response_model=ApiResponse, summary="通过二维码查询生产记录")
async def get_production_by_qr(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    通过二维码标识查询生产记录
    用于质量追溯
    """
    production = db.query(ProductionRecord).filter(
        ProductionRecord.qr_code == qr_code
    ).first()
    if not production:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对应的生产记录"
        )
    
    production.formula = db.query(ProductionFormula).filter(
        ProductionFormula.id == production.formula_id
    ).first()
    
    return ApiResponse(
        code=200,
        message="success",
        data={"production": ProductionRecordResponse.model_validate(production).model_dump()}
    )


# ==================== 投料记录管理 ====================

@router.post("/feeding", response_model=ApiResponse, summary="添加投料记录")
async def create_feeding(
    feeding_data: FeedingRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加投料记录
    自动计算偏差
    """
    # 计算偏差
    deviation = feeding_data.actual_amount - feeding_data.target_amount
    deviation_percent = (deviation / feeding_data.target_amount * 100) if feeding_data.target_amount != 0 else 0
    
    new_feeding = FeedingRecord(
        production_id=feeding_data.production_id,
        material_type=feeding_data.material_type,
        target_amount=feeding_data.target_amount,
        actual_amount=feeding_data.actual_amount,
        deviation=deviation,
        deviation_percent=deviation_percent
    )
    
    db.add(new_feeding)
    db.commit()
    db.refresh(new_feeding)
    
    return ApiResponse(
        code=200,
        message="投料记录添加成功",
        data={"feeding": FeedingRecordResponse.model_validate(new_feeding).model_dump()}
    )


@router.get("/feeding/{production_id}", response_model=ApiResponse, summary="获取生产记录的投料记录")
async def get_feeding_by_production(
    production_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定生产记录的所有投料记录
    """
    feeding_records = db.query(FeedingRecord).filter(
        FeedingRecord.production_id == production_id
    ).all()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "feeding_records": [FeedingRecordResponse.model_validate(fr).model_dump() for fr in feeding_records]
        }
    )

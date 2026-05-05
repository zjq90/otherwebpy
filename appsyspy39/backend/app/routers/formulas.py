"""
配方管理路由 - 处理配合比配方的CRUD操作
包括配方列表、配方调用、参数微调等功能
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models import Formula, FormulaAdjustment, Task, User
from app.schemas import (
    FormulaCreate,
    FormulaUpdate,
    FormulaResponse,
    FormulaListResponse,
    FormulaAdjustmentCreate,
    FormulaAdjustmentResponse,
    SuccessResponse
)
from app.core.auth import get_current_user, require_role
from app.config import settings

router = APIRouter(prefix="/formulas", tags=["配方管理"])


@router.get("", response_model=FormulaListResponse, summary="获取配方列表")
async def get_formulas(
    concrete_grade: Optional[str] = Query(None, description="混凝土标号筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    is_standard: Optional[bool] = Query(None, description="是否标准配方"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取配方列表，支持分页和筛选
    
    Args:
        concrete_grade: 混凝土标号筛选
        keyword: 关键词搜索（配方名称、编号）
        is_active: 是否启用
        is_standard: 是否标准配方
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        FormulaListResponse: 配方列表
    """
    # 构建查询条件
    query = select(Formula)
    
    # 混凝土标号筛选
    if concrete_grade:
        query = query.where(Formula.concrete_grade == concrete_grade)
    
    # 启用状态筛选
    if is_active is not None:
        query = query.where(Formula.is_active == is_active)
    
    # 标准配方筛选
    if is_standard is not None:
        query = query.where(Formula.is_standard == is_standard)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Formula.formula_name.contains(keyword),
                Formula.formula_code.contains(keyword),
                Formula.concrete_grade.contains(keyword)
            )
        )
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    query = query.order_by(Formula.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    formulas = result.scalars().all()
    
    # 构建响应
    formula_responses = [FormulaResponse.model_validate(f) for f in formulas]
    
    return FormulaListResponse(
        total=total,
        formulas=formula_responses
    )


@router.get("/search", response_model=FormulaListResponse, summary="快速检索配方")
async def search_formulas(
    keyword: str = Query(..., description="搜索关键词（标号、名称、编号）"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    快速检索配方 - 用于生产过程中快速调用配方
    
    只返回启用状态的标准配方
    
    Args:
        keyword: 搜索关键词
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        FormulaListResponse: 配方列表
    """
    # 只查询启用的标准配方
    query = select(Formula).where(
        Formula.is_active == True,
        Formula.is_standard == True
    )
    
    # 关键词搜索
    query = query.where(
        or_(
            Formula.formula_name.contains(keyword),
            Formula.formula_code.contains(keyword),
            Formula.concrete_grade.contains(keyword)
        )
    )
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    query = query.order_by(Formula.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    formulas = result.scalars().all()
    
    formula_responses = [FormulaResponse.model_validate(f) for f in formulas]
    
    return FormulaListResponse(
        total=total,
        formulas=formula_responses
    )


@router.get("/{formula_id}", response_model=FormulaResponse, summary="获取配方详情")
async def get_formula(
    formula_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取配方详情
    
    Args:
        formula_id: 配方ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        FormulaResponse: 配方详情
    """
    result = await db.execute(
        select(Formula).where(Formula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配方不存在"
        )
    
    return FormulaResponse.model_validate(formula)


@router.post("", response_model=FormulaResponse, summary="创建配方（管理员功能）")
async def create_formula(
    formula_data: FormulaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    创建新配方 - 仅管理员可操作
    
    Args:
        formula_data: 配方创建数据
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        FormulaResponse: 创建的配方
    """
    # 检查配方编号是否已存在
    existing = await db.execute(
        select(Formula).where(Formula.formula_code == formula_data.formula_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配方编号已存在"
        )
    
    # 创建配方
    new_formula = Formula(
        formula_name=formula_data.formula_name,
        formula_code=formula_data.formula_code,
        concrete_grade=formula_data.concrete_grade,
        water_cement_ratio=formula_data.water_cement_ratio,
        slump=formula_data.slump,
        cement=formula_data.cement,
        water=formula_data.water,
        sand=formula_data.sand,
        stone=formula_data.stone,
        admixture=formula_data.admixture,
        admixture_type=formula_data.admixture_type,
        fly_ash=formula_data.fly_ash or 0,
        mineral_powder=formula_data.mineral_powder or 0,
        is_active=formula_data.is_active if formula_data.is_active is not None else True,
        is_standard=formula_data.is_standard if formula_data.is_standard is not None else True,
        remarks=formula_data.remarks
    )
    
    db.add(new_formula)
    await db.commit()
    await db.refresh(new_formula)
    
    return FormulaResponse.model_validate(new_formula)


@router.put("/{formula_id}", response_model=FormulaResponse, summary="更新配方（管理员功能）")
async def update_formula(
    formula_id: int,
    formula_data: FormulaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    更新配方信息 - 仅管理员可操作
    
    Args:
        formula_id: 配方ID
        formula_data: 更新数据
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        FormulaResponse: 更新后的配方
    """
    result = await db.execute(
        select(Formula).where(Formula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配方不存在"
        )
    
    # 更新字段
    update_data = formula_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(formula, key, value)
    
    await db.commit()
    await db.refresh(formula)
    
    return FormulaResponse.model_validate(formula)


@router.post("/adjust", response_model=FormulaAdjustmentResponse, summary="配方参数微调")
async def adjust_formula(
    adjustment_data: FormulaAdjustmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    配方参数微调
    
    - 记录配方调整历史
    - 调整记录自动同步至后台
    - 需要关联到具体任务
    
    Args:
        adjustment_data: 调整数据
        db: 数据库会话
        current_user: 当前登录用户（操作员）
    
    Returns:
        FormulaAdjustmentResponse: 调整记录
    """
    # 验证任务是否存在且属于当前用户
    task_result = await db.execute(
        select(Task).where(Task.id == adjustment_data.task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限：只有接单人可以调整配方
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有接单人可以调整配方"
        )
    
    # 检查任务状态
    if task.status not in ["accepted", "in_progress"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法调整配方"
        )
    
    # 获取基础配方
    formula_result = await db.execute(
        select(Formula).where(Formula.id == adjustment_data.base_formula_id)
    )
    base_formula = formula_result.scalar_one_or_none()
    
    if not base_formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="基础配方不存在"
        )
    
    # 计算原外加剂掺量百分比（如果有）
    orig_admixture_dosage = None
    if base_formula.admixture and base_formula.cement > 0:
        orig_admixture_dosage = (base_formula.admixture / base_formula.cement) * 100
    
    # 计算新外加剂掺量百分比
    new_admixture_dosage = adjustment_data.new_admixture_dosage
    if adjustment_data.new_admixture and adjustment_data.new_cement and not new_admixture_dosage:
        if adjustment_data.new_cement > 0:
            new_admixture_dosage = (adjustment_data.new_admixture / adjustment_data.new_cement) * 100
    
    # 创建调整记录
    new_adjustment = FormulaAdjustment(
        task_id=adjustment_data.task_id,
        base_formula_id=adjustment_data.base_formula_id,
        operator_id=current_user.id,
        
        # 原参数
        orig_water_cement_ratio=base_formula.water_cement_ratio,
        orig_cement=base_formula.cement,
        orig_water=base_formula.water,
        orig_sand=base_formula.sand,
        orig_stone=base_formula.stone,
        orig_admixture=base_formula.admixture,
        orig_admixture_dosage=orig_admixture_dosage,
        
        # 新参数
        new_water_cement_ratio=adjustment_data.new_water_cement_ratio or base_formula.water_cement_ratio,
        new_cement=adjustment_data.new_cement or base_formula.cement,
        new_water=adjustment_data.new_water or base_formula.water,
        new_sand=adjustment_data.new_sand or base_formula.sand,
        new_stone=adjustment_data.new_stone or base_formula.stone,
        new_admixture=adjustment_data.new_admixture or base_formula.admixture,
        new_admixture_dosage=new_admixture_dosage,
        
        # 调整原因
        adjustment_reason=adjustment_data.adjustment_reason,
        remarks=adjustment_data.remarks
    )
    
    db.add(new_adjustment)
    await db.commit()
    await db.refresh(new_adjustment)
    
    return FormulaAdjustmentResponse.model_validate(new_adjustment)


@router.get("/adjustments/task/{task_id}", summary="获取任务的配方调整历史")
async def get_task_adjustments(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定任务的配方调整历史
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        dict: 调整历史列表
    """
    # 验证任务权限
    task_result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 非管理员只能查看自己的任务
    if current_user.role != "admin" and task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此任务的调整历史"
        )
    
    # 查询调整历史
    result = await db.execute(
        select(FormulaAdjustment)
        .where(FormulaAdjustment.task_id == task_id)
        .order_by(FormulaAdjustment.created_at.desc())
    )
    adjustments = result.scalars().all()
    
    return {
        "task_id": task_id,
        "total": len(adjustments),
        "adjustments": [
            {
                "id": a.id,
                "base_formula_id": a.base_formula_id,
                "adjustment_reason": a.adjustment_reason,
                
                # 原参数
                "orig": {
                    "water_cement_ratio": a.orig_water_cement_ratio,
                    "cement": a.orig_cement,
                    "water": a.orig_water,
                    "sand": a.orig_sand,
                    "stone": a.orig_stone,
                    "admixture": a.orig_admixture,
                    "admixture_dosage": a.orig_admixture_dosage
                },
                
                # 新参数
                "new": {
                    "water_cement_ratio": a.new_water_cement_ratio,
                    "cement": a.new_cement,
                    "water": a.new_water,
                    "sand": a.new_sand,
                    "stone": a.new_stone,
                    "admixture": a.new_admixture,
                    "admixture_dosage": a.new_admixture_dosage
                },
                
                "created_at": a.created_at
            }
            for a in adjustments
        ]
    }


@router.delete("/{formula_id}", response_model=SuccessResponse, summary="删除配方（管理员功能）")
async def delete_formula(
    formula_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    删除配方 - 仅管理员可操作
    
    Args:
        formula_id: 配方ID
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        SuccessResponse: 操作结果
    """
    result = await db.execute(
        select(Formula).where(Formula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配方不存在"
        )
    
    # 检查是否有关联任务
    task_result = await db.execute(
        select(Task).where(Task.formula_id == formula_id).limit(1)
    )
    if task_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该配方有关联任务，无法删除"
        )
    
    await db.delete(formula)
    await db.commit()
    
    return SuccessResponse(message="配方删除成功")

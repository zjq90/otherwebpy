"""
种植计划管理API路由
提供种植计划的增删改查、进度跟踪等功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models import PlantingPlan
from backend.app.models.planting_plan import PlanTypeEnum, PlanStatusEnum
from backend.app.schemas.planting_plan import (
    PlantingPlanCreate,
    PlantingPlanUpdate,
    PlantingPlanResponse,
    PlantingPlanListResponse,
)

# 创建路由
router = APIRouter(
    prefix="/planting-plans",
    tags=["种植计划管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=PlantingPlanResponse, status_code=status.HTTP_201_CREATED)
def create_planting_plan(
    plan_data: PlantingPlanCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的种植计划
    
    参数:
        plan_data: 种植计划创建数据
        db: 数据库会话
    
    返回:
        创建的种植计划详情
    
    异常:
        HTTPException: 计划编号已存在时抛出400错误
    """
    # 检查计划编号是否已存在
    existing_plan = db.query(PlantingPlan).filter(
        PlantingPlan.plan_code == plan_data.plan_code
    ).first()
    
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"计划编号 {plan_data.plan_code} 已存在"
        )
    
    # 创建种植计划
    db_plan = PlantingPlan(**plan_data.model_dump())
    
    # 自动计算目标总产量
    db_plan.calculate_target_total_yield()
    
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    return db_plan


@router.get("/", response_model=PlantingPlanListResponse)
def get_planting_plans(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    year: Optional[int] = Query(None, description="筛选年度"),
    plan_type: Optional[str] = Query(None, description="筛选计划类型"),
    crop_type: Optional[str] = Query(None, description="筛选作物种类"),
    status: Optional[str] = Query(None, description="筛选状态"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    分页查询种植计划列表
    
    参数:
        page: 页码，从1开始
        page_size: 每页数量，最大100
        year: 按年度筛选
        plan_type: 按计划类型筛选
        crop_type: 按作物种类筛选
        status: 按状态筛选
        keyword: 关键词搜索（计划名称、作物种类、地点）
        db: 数据库会话
    
    返回:
        包含分页信息的种植计划列表
    """
    # 构建查询
    query = db.query(PlantingPlan)
    
    # 应用筛选条件
    if year:
        query = query.filter(PlantingPlan.year == year)
    
    if plan_type:
        try:
            plan_type_enum = PlanTypeEnum(plan_type)
            query = query.filter(PlantingPlan.plan_type == plan_type_enum)
        except ValueError:
            pass
    
    if crop_type:
        query = query.filter(PlantingPlan.crop_type.contains(crop_type))
    
    if status:
        try:
            status_enum = PlanStatusEnum(status)
            query = query.filter(PlantingPlan.status == status_enum)
        except ValueError:
            pass
    
    if keyword:
        query = query.filter(
            or_(
                PlantingPlan.plan_name.contains(keyword),
                PlantingPlan.crop_type.contains(keyword),
                PlantingPlan.location.contains(keyword),
                PlantingPlan.plan_code.contains(keyword)
            )
        )
    
    # 获取总记录数
    total = query.count()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 执行分页查询
    items = query.order_by(PlantingPlan.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{plan_id}", response_model=PlantingPlanResponse)
def get_planting_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取种植计划详情
    
    参数:
        plan_id: 种植计划ID
        db: 数据库会话
    
    返回:
        种植计划详情
    
    异常:
        HTTPException: 计划不存在时抛出404错误
    """
    plan = db.query(PlantingPlan).filter(PlantingPlan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"种植计划 ID {plan_id} 不存在"
        )
    
    return plan


@router.put("/{plan_id}", response_model=PlantingPlanResponse)
def update_planting_plan(
    plan_id: int,
    plan_data: PlantingPlanUpdate,
    db: Session = Depends(get_db)
):
    """
    更新种植计划
    
    参数:
        plan_id: 种植计划ID
        plan_data: 更新数据
        db: 数据库会话
    
    返回:
        更新后的种植计划详情
    
    异常:
        HTTPException: 计划不存在时抛出404错误
    """
    db_plan = db.query(PlantingPlan).filter(PlantingPlan.id == plan_id).first()
    
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"种植计划 ID {plan_id} 不存在"
        )
    
    # 更新字段
    update_data = plan_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    # 重新计算产量
    if "planting_area" in update_data or "target_yield_per_mu" in update_data:
        db_plan.calculate_target_total_yield()
    
    if "planting_area" in update_data or "actual_yield_per_mu" in update_data:
        db_plan.calculate_actual_total_yield()
    
    db.commit()
    db.refresh(db_plan)
    
    return db_plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planting_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    删除种植计划
    
    参数:
        plan_id: 种植计划ID
        db: 数据库会话
    
    异常:
        HTTPException: 计划不存在时抛出404错误
    """
    db_plan = db.query(PlantingPlan).filter(PlantingPlan.id == plan_id).first()
    
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"种植计划 ID {plan_id} 不存在"
        )
    
    db.delete(db_plan)
    db.commit()


@router.patch("/{plan_id}/progress", response_model=PlantingPlanResponse)
def update_plan_progress(
    plan_id: int,
    progress: float = Query(..., ge=0, le=100, description="进度百分比（0-100）"),
    db: Session = Depends(get_db)
):
    """
    更新种植计划执行进度
    
    参数:
        plan_id: 种植计划ID
        progress: 进度百分比（0-100）
        db: 数据库会话
    
    返回:
        更新后的种植计划详情
    """
    db_plan = db.query(PlantingPlan).filter(PlantingPlan.id == plan_id).first()
    
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"种植计划 ID {plan_id} 不存在"
        )
    
    # 使用模型方法更新进度
    from decimal import Decimal
    db_plan.update_progress(Decimal(str(progress)))
    
    db.commit()
    db.refresh(db_plan)
    
    return db_plan


@router.get("/statistics/summary")
def get_plan_statistics(
    year: Optional[int] = Query(None, description="年度筛选"),
    db: Session = Depends(get_db)
):
    """
    获取种植计划统计数据
    
    参数:
        year: 年度筛选（可选）
        db: 数据库会话
    
    返回:
        统计数据，包括：
        - 按作物种类统计
        - 按状态统计
        - 总面积和总产量
    """
    query = db.query(PlantingPlan)
    
    if year:
        query = query.filter(PlantingPlan.year == year)
    
    plans = query.all()
    
    # 统计数据
    crop_stats = {}
    status_stats = {}
    total_area = 0
    total_target_yield = 0
    total_actual_yield = 0
    
    for plan in plans:
        # 按作物种类统计
        crop = plan.crop_type
        if crop not in crop_stats:
            crop_stats[crop] = {
                "count": 0,
                "area": 0,
                "target_yield": 0,
                "actual_yield": 0
            }
        crop_stats[crop]["count"] += 1
        crop_stats[crop]["area"] += float(plan.planting_area) if plan.planting_area else 0
        crop_stats[crop]["target_yield"] += float(plan.target_total_yield) if plan.target_total_yield else 0
        crop_stats[crop]["actual_yield"] += float(plan.actual_total_yield) if plan.actual_total_yield else 0
        
        # 按状态统计
        status_val = plan.status.value if plan.status else "未知"
        if status_val not in status_stats:
            status_stats[status_val] = 0
        status_stats[status_val] += 1
        
        # 总面积和总产量
        total_area += float(plan.planting_area) if plan.planting_area else 0
        total_target_yield += float(plan.target_total_yield) if plan.target_total_yield else 0
        total_actual_yield += float(plan.actual_total_yield) if plan.actual_total_yield else 0
    
    return {
        "year": year,
        "total_plans": len(plans),
        "total_area": round(total_area, 2),
        "total_target_yield": round(total_target_yield, 2),
        "total_actual_yield": round(total_actual_yield, 2),
        "crop_statistics": crop_stats,
        "status_statistics": status_stats
    }


@router.get("/stats")
def get_plan_stats(
    year: Optional[int] = Query(None, description="年度筛选"),
    db: Session = Depends(get_db)
):
    """
    获取种植计划统计数据（前端调用别名）
    与 /statistics/summary 功能相同，方便前端调用
    """
    return get_plan_statistics(year=year, db=db)

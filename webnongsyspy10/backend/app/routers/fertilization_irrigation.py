"""
精准施肥与灌溉API路由
提供施肥灌溉记录的增删改查、计划对比分析等功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models import FertilizationIrrigation
from backend.app.models.fertilization_irrigation import FertilizerTypeEnum, IrrigationTypeEnum, WaterSourceEnum
from backend.app.schemas.fertilization_irrigation import (
    FertilizationIrrigationCreate,
    FertilizationIrrigationUpdate,
    FertilizationIrrigationResponse,
    FertilizationIrrigationListResponse,
)

# 创建路由
router = APIRouter(
    prefix="/fertilization-irrigations",
    tags=["精准施肥与灌溉"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=FertilizationIrrigationResponse, status_code=status.HTTP_201_CREATED)
def create_fertilization_irrigation(
    record_data: FertilizationIrrigationCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的施肥灌溉记录
    
    参数:
        record_data: 记录创建数据
        db: 数据库会话
    
    返回:
        创建的记录详情
    
    异常:
        HTTPException: 记录编号已存在时抛出400错误
    """
    # 检查记录编号是否已存在
    existing = db.query(FertilizationIrrigation).filter(
        FertilizationIrrigation.record_code == record_data.record_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"记录编号 {record_data.record_code} 已存在"
        )
    
    # 创建记录
    db_record = FertilizationIrrigation(**record_data.model_dump())
    
    # 自动计算总量和偏差
    db_record.calculate_totals()
    db_record.calculate_deviations()
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.get("/", response_model=FertilizationIrrigationListResponse)
def get_fertilization_irrigations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    record_type: Optional[str] = Query(None, description="筛选记录类型：施肥/灌溉/水肥一体化"),
    crop_type: Optional[str] = Query(None, description="筛选作物种类"),
    plot_location: Optional[str] = Query(None, description="筛选作业地块"),
    is_fertigation: Optional[int] = Query(None, description="是否水肥一体化"),
    is_according_to_plan: Optional[int] = Query(None, description="是否符合计划"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    分页查询施肥灌溉记录列表
    
    参数:
        page: 页码，从1开始
        page_size: 每页数量，最大100
        record_type: 按记录类型筛选
        crop_type: 按作物种类筛选
        plot_location: 按作业地块筛选
        is_fertigation: 是否水肥一体化
        is_according_to_plan: 是否符合计划
        start_date: 开始日期
        end_date: 结束日期
        keyword: 关键词搜索
        db: 数据库会话
    
    返回:
        包含分页信息的记录列表
    """
    # 构建查询
    query = db.query(FertilizationIrrigation)
    
    # 应用筛选条件
    if record_type:
        query = query.filter(FertilizationIrrigation.record_type.contains(record_type))
    
    if crop_type:
        query = query.filter(FertilizationIrrigation.crop_type.contains(crop_type))
    
    if plot_location:
        query = query.filter(FertilizationIrrigation.plot_location.contains(plot_location))
    
    if is_fertigation is not None:
        query = query.filter(FertilizationIrrigation.is_fertigation == is_fertigation)
    
    if is_according_to_plan is not None:
        query = query.filter(FertilizationIrrigation.is_according_to_plan == is_according_to_plan)
    
    if start_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(FertilizationIrrigation.record_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(FertilizationIrrigation.record_date <= end_dt)
        except ValueError:
            pass
    
    if keyword:
        query = query.filter(
            or_(
                FertilizationIrrigation.record_code.contains(keyword),
                FertilizationIrrigation.crop_type.contains(keyword),
                FertilizationIrrigation.plot_location.contains(keyword),
                FertilizationIrrigation.planned_fertilizer_name.contains(keyword),
                FertilizationIrrigation.actual_fertilizer_name.contains(keyword)
            )
        )
    
    # 获取总记录数
    total = query.count()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 执行分页查询
    items = query.order_by(FertilizationIrrigation.record_date.desc(), FertilizationIrrigation.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{record_id}", response_model=FertilizationIrrigationResponse)
def get_fertilization_irrigation(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取施肥灌溉记录详情
    
    参数:
        record_id: 记录ID
        db: 数据库会话
    
    返回:
        记录详情
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    record = db.query(FertilizationIrrigation).filter(FertilizationIrrigation.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"施肥灌溉记录 ID {record_id} 不存在"
        )
    
    return record


@router.put("/{record_id}", response_model=FertilizationIrrigationResponse)
def update_fertilization_irrigation(
    record_id: int,
    record_data: FertilizationIrrigationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新施肥灌溉记录
    
    参数:
        record_id: 记录ID
        record_data: 更新数据
        db: 数据库会话
    
    返回:
        更新后的记录详情
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    db_record = db.query(FertilizationIrrigation).filter(FertilizationIrrigation.id == record_id).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"施肥灌溉记录 ID {record_id} 不存在"
        )
    
    # 更新字段
    update_data = record_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新计算总量和偏差
    db_record.calculate_totals()
    db_record.calculate_deviations()
    
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fertilization_irrigation(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    删除施肥灌溉记录
    
    参数:
        record_id: 记录ID
        db: 数据库会话
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    db_record = db.query(FertilizationIrrigation).filter(FertilizationIrrigation.id == record_id).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"施肥灌溉记录 ID {record_id} 不存在"
        )
    
    db.delete(db_record)
    db.commit()


@router.get("/statistics/comparison")
def get_comparison_statistics(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    crop_type: Optional[str] = Query(None, description="作物种类筛选"),
    db: Session = Depends(get_db)
):
    """
    获取计划与实际对比分析统计数据
    
    参数:
        start_date: 开始日期
        end_date: 结束日期
        crop_type: 作物种类筛选
        db: 数据库会话
    
    返回:
        统计数据，包括：
        - 计划与实际施肥量对比
        - 计划与实际灌溉量对比
        - 偏差分析
    """
    query = db.query(FertilizationIrrigation)
    
    # 应用筛选条件
    if crop_type:
        query = query.filter(FertilizationIrrigation.crop_type.contains(crop_type))
    
    if start_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(FertilizationIrrigation.record_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(FertilizationIrrigation.record_date <= end_dt)
        except ValueError:
            pass
    
    records = query.all()
    
    # 统计数据
    total_planned_fertilizer = 0
    total_actual_fertilizer = 0
    total_planned_irrigation = 0
    total_actual_irrigation = 0
    count_according_to_plan = 0
    count_not_according_to_plan = 0
    
    # 按作物类型统计
    crop_stats = {}
    
    for record in records:
        # 总量统计
        total_planned_fertilizer += float(record.planned_total_fertilizer) if record.planned_total_fertilizer else 0
        total_actual_fertilizer += float(record.actual_total_fertilizer) if record.actual_total_fertilizer else 0
        total_planned_irrigation += float(record.planned_total_irrigation) if record.planned_total_irrigation else 0
        total_actual_irrigation += float(record.actual_total_irrigation) if record.actual_total_irrigation else 0
        
        # 是否符合计划
        if record.is_according_to_plan == 1:
            count_according_to_plan += 1
        else:
            count_not_according_to_plan += 1
        
        # 按作物统计
        if record.crop_type:
            crop = record.crop_type
            if crop not in crop_stats:
                crop_stats[crop] = {
                    "count": 0,
                    "planned_fertilizer": 0,
                    "actual_fertilizer": 0,
                    "planned_irrigation": 0,
                    "actual_irrigation": 0
                }
            crop_stats[crop]["count"] += 1
            crop_stats[crop]["planned_fertilizer"] += float(record.planned_total_fertilizer) if record.planned_total_fertilizer else 0
            crop_stats[crop]["actual_fertilizer"] += float(record.actual_total_fertilizer) if record.actual_total_fertilizer else 0
            crop_stats[crop]["planned_irrigation"] += float(record.planned_total_irrigation) if record.planned_total_irrigation else 0
            crop_stats[crop]["actual_irrigation"] += float(record.actual_total_irrigation) if record.actual_total_irrigation else 0
    
    # 计算整体偏差
    fertilizer_deviation = 0
    irrigation_deviation = 0
    
    if total_planned_fertilizer > 0:
        fertilizer_deviation = round((total_actual_fertilizer - total_planned_fertilizer) / total_planned_fertilizer * 100, 2)
    
    if total_planned_irrigation > 0:
        irrigation_deviation = round((total_actual_irrigation - total_planned_irrigation) / total_planned_irrigation * 100, 2)
    
    return {
        "total_records": len(records),
        "fertilizer": {
            "planned_total": round(total_planned_fertilizer, 3),
            "actual_total": round(total_actual_fertilizer, 3),
            "deviation_percent": fertilizer_deviation
        },
        "irrigation": {
            "planned_total": round(total_planned_irrigation, 3),
            "actual_total": round(total_actual_irrigation, 3),
            "deviation_percent": irrigation_deviation
        },
        "compliance": {
            "according_to_plan": count_according_to_plan,
            "not_according_to_plan": count_not_according_to_plan,
            "compliance_rate": round(count_according_to_plan / len(records) * 100, 2) if records else 0
        },
        "crop_statistics": crop_stats
    }


@router.get("/stats")
def get_fertilization_irrigation_stats(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    crop_type: Optional[str] = Query(None, description="作物种类筛选"),
    db: Session = Depends(get_db)
):
    """
    获取施肥灌溉统计数据（前端调用别名）
    与 /statistics/comparison 功能相同，方便前端调用
    """
    return get_comparison_statistics(start_date=start_date, end_date=end_date, crop_type=crop_type, db=db)

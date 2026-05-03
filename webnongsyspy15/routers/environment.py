"""
环境记录管理路由
处理环境资源记录的增删改查和环境报表
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from database import get_db
from models import EnvironmentRecord, Plot, User
from schemas import (
    EnvironmentRecordCreate, EnvironmentRecordUpdate, EnvironmentRecordResponse,
    EnvironmentReportRequest, APIResponse, PaginatedResponse
)
from routers.auth import get_current_active_user
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由
router = APIRouter(prefix="/environment", tags=["环境管理"])


@router.get("", response_model=PaginatedResponse)
async def get_environment_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量"),
    plot_id: Optional[int] = Query(None, description="地块ID筛选"),
    year: Optional[int] = Query(None, description="年份筛选"),
    month: Optional[int] = Query(None, description="月份筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取环境记录列表
    支持分页和筛选
    """
    # 构建查询
    query = select(EnvironmentRecord).options(
        selectinload(EnvironmentRecord.plot)
    )
    
    # 筛选条件
    if plot_id:
        query = query.where(EnvironmentRecord.plot_id == plot_id)
    if year:
        query = query.where(EnvironmentRecord.year == year)
    if month:
        query = query.where(EnvironmentRecord.month == month)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(
        EnvironmentRecord.record_date.desc()
    )
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 转换为响应模型
    record_responses = [EnvironmentRecordResponse.model_validate(record) for record in records]
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        success=True,
        message="获取成功",
        data=record_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{record_id}", response_model=EnvironmentRecordResponse)
async def get_environment_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个环境记录详情
    """
    query = select(EnvironmentRecord).options(
        selectinload(EnvironmentRecord.plot)
    ).where(EnvironmentRecord.id == record_id)
    
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="环境记录不存在"
        )
    
    return record


@router.post("", response_model=APIResponse)
async def create_environment_record(
    record_data: EnvironmentRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新环境记录
    """
    # 验证地块是否存在
    plot_query = select(Plot).where(Plot.id == record_data.plot_id)
    plot_result = await db.execute(plot_query)
    if not plot_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="地块不存在"
        )
    
    # 创建新记录
    new_record = EnvironmentRecord(**record_data.model_dump())
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return APIResponse(
        success=True,
        message="创建成功",
        data={"record_id": new_record.id}
    )


@router.put("/{record_id}", response_model=APIResponse)
async def update_environment_record(
    record_id: int,
    record_data: EnvironmentRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新环境记录
    """
    query = select(EnvironmentRecord).where(EnvironmentRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="环境记录不存在"
        )
    
    # 更新字段
    update_data = record_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    
    await db.commit()
    
    return APIResponse(
        success=True,
        message="更新成功"
    )


@router.delete("/{record_id}", response_model=APIResponse)
async def delete_environment_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除环境记录
    """
    query = select(EnvironmentRecord).where(EnvironmentRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="环境记录不存在"
        )
    
    await db.delete(record)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="删除成功"
    )


@router.post("/report", response_model=APIResponse)
async def generate_environment_report(
    report_request: EnvironmentReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成环境报表
    水资源、能源、农资使用效率分析
    """
    # 构建查询条件
    query = select(EnvironmentRecord).options(
        selectinload(EnvironmentRecord.plot)
    )
    
    conditions = []
    if report_request.plot_id:
        conditions.append(EnvironmentRecord.plot_id == report_request.plot_id)
    if report_request.year:
        conditions.append(EnvironmentRecord.year == report_request.year)
    if report_request.month:
        conditions.append(EnvironmentRecord.month == report_request.month)
    if report_request.start_date:
        conditions.append(EnvironmentRecord.record_date >= report_request.start_date)
    if report_request.end_date:
        conditions.append(EnvironmentRecord.record_date <= report_request.end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(EnvironmentRecord.record_date)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 统计数据
    total_records = len(records)
    
    # 水资源统计
    total_water_usage = sum(r.water_usage for r in records)
    total_water_cost = sum(r.water_cost for r in records)
    
    # 能源统计
    total_electricity_usage = sum(r.electricity_usage for r in records)
    total_electricity_cost = sum(r.electricity_cost for r in records)
    total_fuel_usage = sum(r.fuel_usage for r in records)
    total_fuel_cost = sum(r.fuel_cost for r in records)
    
    # 农资统计
    total_fertilizer_usage = sum(r.fertilizer_usage for r in records)
    total_fertilizer_cost = sum(r.fertilizer_cost for r in records)
    total_pesticide_usage = sum(r.pesticide_usage for r in records)
    total_pesticide_cost = sum(r.pesticide_cost for r in records)
    total_seed_usage = sum(r.seed_usage for r in records)
    total_seed_cost = sum(r.seed_cost for r in records)
    
    # 总成本
    total_environment_cost = (
        total_water_cost + total_electricity_cost + total_fuel_cost +
        total_fertilizer_cost + total_pesticide_cost + total_seed_cost
    )
    
    # 按地块统计
    by_plot = {}
    for r in records:
        plot_name = r.plot.name if r.plot else "未知"
        if plot_name not in by_plot:
            by_plot[plot_name] = {
                "count": 0,
                "water_usage": 0.0,
                "water_cost": 0.0,
                "electricity_usage": 0.0,
                "electricity_cost": 0.0,
                "fuel_usage": 0.0,
                "fuel_cost": 0.0,
                "fertilizer_usage": 0.0,
                "fertilizer_cost": 0.0,
                "pesticide_usage": 0.0,
                "pesticide_cost": 0.0,
                "seed_usage": 0.0,
                "seed_cost": 0.0,
                "total_cost": 0.0
            }
        by_plot[plot_name]["count"] += 1
        by_plot[plot_name]["water_usage"] += r.water_usage
        by_plot[plot_name]["water_cost"] += r.water_cost
        by_plot[plot_name]["electricity_usage"] += r.electricity_usage
        by_plot[plot_name]["electricity_cost"] += r.electricity_cost
        by_plot[plot_name]["fuel_usage"] += r.fuel_usage
        by_plot[plot_name]["fuel_cost"] += r.fuel_cost
        by_plot[plot_name]["fertilizer_usage"] += r.fertilizer_usage
        by_plot[plot_name]["fertilizer_cost"] += r.fertilizer_cost
        by_plot[plot_name]["pesticide_usage"] += r.pesticide_usage
        by_plot[plot_name]["pesticide_cost"] += r.pesticide_cost
        by_plot[plot_name]["seed_usage"] += r.seed_usage
        by_plot[plot_name]["seed_cost"] += r.seed_cost
        by_plot[plot_name]["total_cost"] += (
            r.water_cost + r.electricity_cost + r.fuel_cost +
            r.fertilizer_cost + r.pesticide_cost + r.seed_cost
        )
    
    # 按年份统计
    by_year = {}
    for r in records:
        year = str(r.year)
        if year not in by_year:
            by_year[year] = {
                "count": 0,
                "water_usage": 0.0,
                "water_cost": 0.0,
                "electricity_usage": 0.0,
                "electricity_cost": 0.0,
                "fuel_usage": 0.0,
                "fuel_cost": 0.0,
                "fertilizer_usage": 0.0,
                "fertilizer_cost": 0.0,
                "pesticide_usage": 0.0,
                "pesticide_cost": 0.0,
                "seed_usage": 0.0,
                "seed_cost": 0.0,
                "total_cost": 0.0
            }
        by_year[year]["count"] += 1
        by_year[year]["water_usage"] += r.water_usage
        by_year[year]["water_cost"] += r.water_cost
        by_year[year]["electricity_usage"] += r.electricity_usage
        by_year[year]["electricity_cost"] += r.electricity_cost
        by_year[year]["fuel_usage"] += r.fuel_usage
        by_year[year]["fuel_cost"] += r.fuel_cost
        by_year[year]["fertilizer_usage"] += r.fertilizer_usage
        by_year[year]["fertilizer_cost"] += r.fertilizer_cost
        by_year[year]["pesticide_usage"] += r.pesticide_usage
        by_year[year]["pesticide_cost"] += r.pesticide_cost
        by_year[year]["seed_usage"] += r.seed_usage
        by_year[year]["seed_cost"] += r.seed_cost
        by_year[year]["total_cost"] += (
            r.water_cost + r.electricity_cost + r.fuel_cost +
            r.fertilizer_cost + r.pesticide_cost + r.seed_cost
        )
    
    # 计算平均指标
    avg_water_usage = round(total_water_usage / total_records, 2) if total_records > 0 else 0
    avg_electricity_usage = round(total_electricity_usage / total_records, 2) if total_records > 0 else 0
    avg_fuel_usage = round(total_fuel_usage / total_records, 2) if total_records > 0 else 0
    
    # 成本结构分析
    cost_structure = {
        "water_cost": round(total_water_cost, 2),
        "electricity_cost": round(total_electricity_cost, 2),
        "fuel_cost": round(total_fuel_cost, 2),
        "fertilizer_cost": round(total_fertilizer_cost, 2),
        "pesticide_cost": round(total_pesticide_cost, 2),
        "seed_cost": round(total_seed_cost, 2)
    }
    
    # 计算各成本占比
    if total_environment_cost > 0:
        cost_percentage = {
            "water_cost": round((total_water_cost / total_environment_cost) * 100, 2),
            "electricity_cost": round((total_electricity_cost / total_environment_cost) * 100, 2),
            "fuel_cost": round((total_fuel_cost / total_environment_cost) * 100, 2),
            "fertilizer_cost": round((total_fertilizer_cost / total_environment_cost) * 100, 2),
            "pesticide_cost": round((total_pesticide_cost / total_environment_cost) * 100, 2),
            "seed_cost": round((total_seed_cost / total_environment_cost) * 100, 2)
        }
    else:
        cost_percentage = {k: 0 for k in cost_structure}
    
    return APIResponse(
        success=True,
        message="报表生成成功",
        data={
            "summary": {
                "total_records": total_records,
                "total_water_usage": round(total_water_usage, 2),
                "total_water_cost": round(total_water_cost, 2),
                "total_electricity_usage": round(total_electricity_usage, 2),
                "total_electricity_cost": round(total_electricity_cost, 2),
                "total_fuel_usage": round(total_fuel_usage, 2),
                "total_fuel_cost": round(total_fuel_cost, 2),
                "total_fertilizer_usage": round(total_fertilizer_usage, 2),
                "total_fertilizer_cost": round(total_fertilizer_cost, 2),
                "total_pesticide_usage": round(total_pesticide_usage, 2),
                "total_pesticide_cost": round(total_pesticide_cost, 2),
                "total_seed_usage": round(total_seed_usage, 2),
                "total_seed_cost": round(total_seed_cost, 2),
                "total_environment_cost": round(total_environment_cost, 2),
                "avg_water_usage": avg_water_usage,
                "avg_electricity_usage": avg_electricity_usage,
                "avg_fuel_usage": avg_fuel_usage
            },
            "cost_structure": cost_structure,
            "cost_percentage": cost_percentage,
            "by_plot": by_plot,
            "by_year": by_year,
            "records": [
                {
                    "id": r.id,
                    "plot_name": r.plot.name if r.plot else None,
                    "record_date": str(r.record_date),
                    "year": r.year,
                    "month": r.month,
                    "water_usage": r.water_usage,
                    "water_cost": r.water_cost,
                    "electricity_usage": r.electricity_usage,
                    "electricity_cost": r.electricity_cost,
                    "fuel_usage": r.fuel_usage,
                    "fuel_cost": r.fuel_cost,
                    "fertilizer_usage": r.fertilizer_usage,
                    "fertilizer_cost": r.fertilizer_cost,
                    "pesticide_usage": r.pesticide_usage,
                    "pesticide_cost": r.pesticide_cost,
                    "seed_usage": r.seed_usage,
                    "seed_cost": r.seed_cost
                }
                for r in records
            ]
        }
    )


@router.get("/statistics/summary", response_model=APIResponse)
async def get_environment_statistics(
    year: Optional[int] = Query(None, description="年份，不指定则统计所有"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取环境统计摘要
    """
    query = select(EnvironmentRecord)
    if year:
        query = query.where(EnvironmentRecord.year == year)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 统计数据
    total_records = len(records)
    total_water_usage = sum(r.water_usage for r in records)
    total_water_cost = sum(r.water_cost for r in records)
    total_electricity_usage = sum(r.electricity_usage for r in records)
    total_electricity_cost = sum(r.electricity_cost for r in records)
    total_fuel_usage = sum(r.fuel_usage for r in records)
    total_fuel_cost = sum(r.fuel_cost for r in records)
    total_fertilizer_usage = sum(r.fertilizer_usage for r in records)
    total_fertilizer_cost = sum(r.fertilizer_cost for r in records)
    total_pesticide_usage = sum(r.pesticide_usage for r in records)
    total_pesticide_cost = sum(r.pesticide_cost for r in records)
    total_seed_usage = sum(r.seed_usage for r in records)
    total_seed_cost = sum(r.seed_cost for r in records)
    
    # 按月统计
    monthly_stats = {}
    for r in records:
        month_key = f"{r.year}-{r.month:02d}"
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {
                "water_usage": 0.0,
                "water_cost": 0.0,
                "electricity_usage": 0.0,
                "electricity_cost": 0.0,
                "fuel_usage": 0.0,
                "fuel_cost": 0.0,
                "fertilizer_usage": 0.0,
                "fertilizer_cost": 0.0,
                "pesticide_usage": 0.0,
                "pesticide_cost": 0.0,
                "seed_usage": 0.0,
                "seed_cost": 0.0
            }
        monthly_stats[month_key]["water_usage"] += r.water_usage
        monthly_stats[month_key]["water_cost"] += r.water_cost
        monthly_stats[month_key]["electricity_usage"] += r.electricity_usage
        monthly_stats[month_key]["electricity_cost"] += r.electricity_cost
        monthly_stats[month_key]["fuel_usage"] += r.fuel_usage
        monthly_stats[month_key]["fuel_cost"] += r.fuel_cost
        monthly_stats[month_key]["fertilizer_usage"] += r.fertilizer_usage
        monthly_stats[month_key]["fertilizer_cost"] += r.fertilizer_cost
        monthly_stats[month_key]["pesticide_usage"] += r.pesticide_usage
        monthly_stats[month_key]["pesticide_cost"] += r.pesticide_cost
        monthly_stats[month_key]["seed_usage"] += r.seed_usage
        monthly_stats[month_key]["seed_cost"] += r.seed_cost
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={
            "total_records": total_records,
            "water": {
                "total_usage": round(total_water_usage, 2),
                "total_cost": round(total_water_cost, 2)
            },
            "electricity": {
                "total_usage": round(total_electricity_usage, 2),
                "total_cost": round(total_electricity_cost, 2)
            },
            "fuel": {
                "total_usage": round(total_fuel_usage, 2),
                "total_cost": round(total_fuel_cost, 2)
            },
            "fertilizer": {
                "total_usage": round(total_fertilizer_usage, 2),
                "total_cost": round(total_fertilizer_cost, 2)
            },
            "pesticide": {
                "total_usage": round(total_pesticide_usage, 2),
                "total_cost": round(total_pesticide_cost, 2)
            },
            "seed": {
                "total_usage": round(total_seed_usage, 2),
                "total_cost": round(total_seed_cost, 2)
            },
            "monthly_stats": dict(sorted(monthly_stats.items()))
        }
    )

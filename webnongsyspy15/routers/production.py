"""
生产记录管理路由
处理生产记录的增删改查和生产报表
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from database import get_db
from models import ProductionRecord, Crop, Plot, User
from schemas import (
    ProductionRecordCreate, ProductionRecordUpdate, ProductionRecordResponse,
    ProductionReportRequest, APIResponse, PaginatedResponse
)
from routers.auth import get_current_active_user
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由
router = APIRouter(prefix="/production", tags=["生产管理"])


@router.get("", response_model=PaginatedResponse)
async def get_production_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量"),
    crop_id: Optional[int] = Query(None, description="作物ID筛选"),
    plot_id: Optional[int] = Query(None, description="地块ID筛选"),
    year: Optional[int] = Query(None, description="年份筛选"),
    season: Optional[str] = Query(None, description="季节筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取生产记录列表
    支持分页和筛选
    """
    # 构建查询
    query = select(ProductionRecord).options(
        selectinload(ProductionRecord.crop),
        selectinload(ProductionRecord.plot)
    )
    
    # 筛选条件
    if crop_id:
        query = query.where(ProductionRecord.crop_id == crop_id)
    if plot_id:
        query = query.where(ProductionRecord.plot_id == plot_id)
    if year:
        query = query.where(ProductionRecord.year == year)
    if season:
        query = query.where(ProductionRecord.season == season)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(ProductionRecord.created_at.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 转换为响应模型
    record_responses = [ProductionRecordResponse.model_validate(record) for record in records]
    
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


@router.get("/{record_id}", response_model=ProductionRecordResponse)
async def get_production_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个生产记录详情
    """
    query = select(ProductionRecord).options(
        selectinload(ProductionRecord.crop),
        selectinload(ProductionRecord.plot)
    ).where(ProductionRecord.id == record_id)
    
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    return record


@router.post("", response_model=APIResponse)
async def create_production_record(
    record_data: ProductionRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新生产记录
    """
    # 验证作物和地块是否存在
    crop_query = select(Crop).where(Crop.id == record_data.crop_id)
    crop_result = await db.execute(crop_query)
    if not crop_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="作物不存在"
        )
    
    plot_query = select(Plot).where(Plot.id == record_data.plot_id)
    plot_result = await db.execute(plot_query)
    if not plot_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="地块不存在"
        )
    
    # 计算收入和利润（如果没有提供）
    data = record_data.model_dump()
    if data.get("revenue", 0) == 0 and data.get("yield_amount", 0) > 0 and data.get("selling_price", 0) > 0:
        data["revenue"] = round(data["yield_amount"] * data["selling_price"], 2)
    
    if data.get("profit", 0) == 0 and data.get("revenue", 0) > 0:
        data["profit"] = round(data["revenue"] - data.get("input_cost", 0), 2)
    
    # 创建新记录
    new_record = ProductionRecord(**data)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return APIResponse(
        success=True,
        message="创建成功",
        data={"record_id": new_record.id}
    )


@router.put("/{record_id}", response_model=APIResponse)
async def update_production_record(
    record_id: int,
    record_data: ProductionRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新生产记录
    """
    query = select(ProductionRecord).where(ProductionRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    # 更新字段
    update_data = record_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    
    # 重新计算收入和利润
    if record.yield_amount > 0 and record.selling_price > 0:
        record.revenue = round(record.yield_amount * record.selling_price, 2)
    if record.revenue > 0:
        record.profit = round(record.revenue - record.input_cost, 2)
    
    await db.commit()
    
    return APIResponse(
        success=True,
        message="更新成功"
    )


@router.delete("/{record_id}", response_model=APIResponse)
async def delete_production_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除生产记录
    """
    query = select(ProductionRecord).where(ProductionRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    await db.delete(record)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="删除成功"
    )


@router.post("/report", response_model=APIResponse)
async def generate_production_report(
    report_request: ProductionReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成生产报表
    按作物、地块、时间段分析产量、投入成本、收益
    """
    # 构建查询条件
    query = select(ProductionRecord).options(
        selectinload(ProductionRecord.crop),
        selectinload(ProductionRecord.plot)
    )
    
    conditions = []
    if report_request.crop_id:
        conditions.append(ProductionRecord.crop_id == report_request.crop_id)
    if report_request.plot_id:
        conditions.append(ProductionRecord.plot_id == report_request.plot_id)
    if report_request.year:
        conditions.append(ProductionRecord.year == report_request.year)
    if report_request.season:
        conditions.append(ProductionRecord.season == report_request.season)
    if report_request.start_date:
        conditions.append(ProductionRecord.planting_date >= report_request.start_date)
    if report_request.end_date:
        conditions.append(ProductionRecord.planting_date <= report_request.end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(ProductionRecord.year, ProductionRecord.season)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 统计数据
    total_records = len(records)
    total_yield = sum(r.yield_amount for r in records)
    total_input_cost = sum(r.input_cost for r in records)
    total_revenue = sum(r.revenue for r in records)
    total_profit = sum(r.profit for r in records)
    
    # 按作物统计
    by_crop = {}
    for r in records:
        crop_name = r.crop.name if r.crop else "未知"
        if crop_name not in by_crop:
            by_crop[crop_name] = {
                "count": 0,
                "total_yield": 0.0,
                "total_input_cost": 0.0,
                "total_revenue": 0.0,
                "total_profit": 0.0
            }
        by_crop[crop_name]["count"] += 1
        by_crop[crop_name]["total_yield"] += r.yield_amount
        by_crop[crop_name]["total_input_cost"] += r.input_cost
        by_crop[crop_name]["total_revenue"] += r.revenue
        by_crop[crop_name]["total_profit"] += r.profit
    
    # 按地块统计
    by_plot = {}
    for r in records:
        plot_name = r.plot.name if r.plot else "未知"
        if plot_name not in by_plot:
            by_plot[plot_name] = {
                "count": 0,
                "total_yield": 0.0,
                "total_input_cost": 0.0,
                "total_revenue": 0.0,
                "total_profit": 0.0
            }
        by_plot[plot_name]["count"] += 1
        by_plot[plot_name]["total_yield"] += r.yield_amount
        by_plot[plot_name]["total_input_cost"] += r.input_cost
        by_plot[plot_name]["total_revenue"] += r.revenue
        by_plot[plot_name]["total_profit"] += r.profit
    
    # 按年份统计
    by_year = {}
    for r in records:
        year = str(r.year)
        if year not in by_year:
            by_year[year] = {
                "count": 0,
                "total_yield": 0.0,
                "total_input_cost": 0.0,
                "total_revenue": 0.0,
                "total_profit": 0.0
            }
        by_year[year]["count"] += 1
        by_year[year]["total_yield"] += r.yield_amount
        by_year[year]["total_input_cost"] += r.input_cost
        by_year[year]["total_revenue"] += r.revenue
        by_year[year]["total_profit"] += r.profit
    
    # 按季节统计
    by_season = {}
    for r in records:
        season = r.season or "未知"
        if season not in by_season:
            by_season[season] = {
                "count": 0,
                "total_yield": 0.0,
                "total_input_cost": 0.0,
                "total_revenue": 0.0,
                "total_profit": 0.0
            }
        by_season[season]["count"] += 1
        by_season[season]["total_yield"] += r.yield_amount
        by_season[season]["total_input_cost"] += r.input_cost
        by_season[season]["total_revenue"] += r.revenue
        by_season[season]["total_profit"] += r.profit
    
    # 计算平均指标
    avg_yield = round(total_yield / total_records, 2) if total_records > 0 else 0
    avg_input_cost = round(total_input_cost / total_records, 2) if total_records > 0 else 0
    avg_revenue = round(total_revenue / total_records, 2) if total_records > 0 else 0
    avg_profit = round(total_profit / total_records, 2) if total_records > 0 else 0
    
    # 利润率
    profit_rate = round((total_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0
    
    return APIResponse(
        success=True,
        message="报表生成成功",
        data={
            "summary": {
                "total_records": total_records,
                "total_yield": round(total_yield, 2),
                "total_input_cost": round(total_input_cost, 2),
                "total_revenue": round(total_revenue, 2),
                "total_profit": round(total_profit, 2),
                "avg_yield": avg_yield,
                "avg_input_cost": avg_input_cost,
                "avg_revenue": avg_revenue,
                "avg_profit": avg_profit,
                "profit_rate": profit_rate
            },
            "by_crop": by_crop,
            "by_plot": by_plot,
            "by_year": by_year,
            "by_season": by_season,
            "records": [
                {
                    "id": r.id,
                    "crop_name": r.crop.name if r.crop else None,
                    "plot_name": r.plot.name if r.plot else None,
                    "planting_date": str(r.planting_date),
                    "harvest_date": str(r.harvest_date) if r.harvest_date else None,
                    "season": r.season,
                    "year": r.year,
                    "yield_amount": r.yield_amount,
                    "input_cost": r.input_cost,
                    "revenue": r.revenue,
                    "profit": r.profit
                }
                for r in records
            ]
        }
    )


@router.get("/statistics/summary", response_model=APIResponse)
async def get_production_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取生产统计摘要
    """
    query = select(ProductionRecord)
    result = await db.execute(query)
    records = result.scalars().all()
    
    total_records = len(records)
    total_yield = sum(r.yield_amount for r in records)
    total_input_cost = sum(r.input_cost for r in records)
    total_revenue = sum(r.revenue for r in records)
    total_profit = sum(r.profit for r in records)
    
    # 按年份统计
    yearly_stats = {}
    for r in records:
        year = str(r.year)
        if year not in yearly_stats:
            yearly_stats[year] = {
                "yield": 0.0,
                "input_cost": 0.0,
                "revenue": 0.0,
                "profit": 0.0
            }
        yearly_stats[year]["yield"] += r.yield_amount
        yearly_stats[year]["input_cost"] += r.input_cost
        yearly_stats[year]["revenue"] += r.revenue
        yearly_stats[year]["profit"] += r.profit
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={
            "total_records": total_records,
            "total_yield": round(total_yield, 2),
            "total_input_cost": round(total_input_cost, 2),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "yearly_stats": yearly_stats
        }
    )

"""
地块管理路由
处理地块的增删改查操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from database import get_db
from models import Plot, User
from schemas import (
    PlotCreate, PlotUpdate, PlotResponse, 
    APIResponse, PaginatedResponse
)
from routers.auth import get_current_active_user
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由
router = APIRouter(prefix="/plots", tags=["地块管理"])


@router.get("", response_model=PaginatedResponse)
async def get_plots(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    soil_type: Optional[str] = Query(None, description="土壤类型筛选"),
    irrigation_type: Optional[str] = Query(None, description="灌溉方式筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取地块列表
    支持分页、搜索和筛选
    """
    # 构建查询
    query = select(Plot)
    
    # 搜索关键词
    if keyword:
        query = query.where(
            or_(
                Plot.name.contains(keyword),
                Plot.code.contains(keyword),
                Plot.location.contains(keyword),
                Plot.description.contains(keyword)
            )
        )
    
    # 土壤类型筛选
    if soil_type:
        query = query.where(Plot.soil_type == soil_type)
    
    # 灌溉方式筛选
    if irrigation_type:
        query = query.where(Plot.irrigation_type == irrigation_type)
    
    # 启用状态筛选
    if is_active is not None:
        query = query.where(Plot.is_active == is_active)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Plot.created_at.desc())
    
    result = await db.execute(query)
    plots = result.scalars().all()
    
    # 转换为响应模型
    plot_responses = [PlotResponse.model_validate(plot) for plot in plots]
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        success=True,
        message="获取成功",
        data=plot_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/all", response_model=APIResponse)
async def get_all_plots(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有启用的地块
    用于下拉选择等场景
    """
    query = select(Plot).where(Plot.is_active == True).order_by(Plot.name)
    result = await db.execute(query)
    plots = result.scalars().all()
    
    plot_responses = [PlotResponse.model_validate(plot) for plot in plots]
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={"plots": [plot.model_dump() for plot in plot_responses]}
    )


@router.get("/{plot_id}", response_model=PlotResponse)
async def get_plot(
    plot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个地块详情
    """
    query = select(Plot).where(Plot.id == plot_id)
    result = await db.execute(query)
    plot = result.scalar_one_or_none()
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地块不存在"
        )
    
    return plot


@router.post("", response_model=APIResponse)
async def create_plot(
    plot_data: PlotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新地块
    """
    # 检查编号是否已存在
    query = select(Plot).where(Plot.code == plot_data.code)
    result = await db.execute(query)
    existing_plot = result.scalar_one_or_none()
    
    if existing_plot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="地块编号已存在"
        )
    
    # 创建新地块
    new_plot = Plot(**plot_data.model_dump())
    db.add(new_plot)
    await db.commit()
    await db.refresh(new_plot)
    
    return APIResponse(
        success=True,
        message="创建成功",
        data={"plot_id": new_plot.id}
    )


@router.put("/{plot_id}", response_model=APIResponse)
async def update_plot(
    plot_id: int,
    plot_data: PlotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新地块信息
    """
    query = select(Plot).where(Plot.id == plot_id)
    result = await db.execute(query)
    plot = result.scalar_one_or_none()
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地块不存在"
        )
    
    # 检查编号是否与其他地块重复
    update_data = plot_data.model_dump(exclude_unset=True)
    if "code" in update_data:
        code_query = select(Plot).where(
            Plot.code == update_data["code"],
            Plot.id != plot_id
        )
        code_result = await db.execute(code_query)
        if code_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地块编号已存在"
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(plot, key, value)
    
    await db.commit()
    
    return APIResponse(
        success=True,
        message="更新成功"
    )


@router.delete("/{plot_id}", response_model=APIResponse)
async def delete_plot(
    plot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除地块（逻辑删除）
    """
    query = select(Plot).where(Plot.id == plot_id)
    result = await db.execute(query)
    plot = result.scalar_one_or_none()
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地块不存在"
        )
    
    # 逻辑删除
    plot.is_active = False
    await db.commit()
    
    return APIResponse(
        success=True,
        message="删除成功"
    )


@router.post("/{plot_id}/restore", response_model=APIResponse)
async def restore_plot(
    plot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    恢复已删除的地块
    """
    query = select(Plot).where(Plot.id == plot_id)
    result = await db.execute(query)
    plot = result.scalar_one_or_none()
    
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地块不存在"
        )
    
    plot.is_active = True
    await db.commit()
    
    return APIResponse(
        success=True,
        message="恢复成功"
    )


@router.get("/statistics/area", response_model=APIResponse)
async def get_area_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取地块面积统计
    """
    query = select(Plot).where(Plot.is_active == True)
    result = await db.execute(query)
    plots = result.scalars().all()
    
    total_area = sum(plot.area for plot in plots)
    count = len(plots)
    
    # 按土壤类型统计
    soil_type_stats = {}
    for plot in plots:
        if plot.soil_type:
            if plot.soil_type not in soil_type_stats:
                soil_type_stats[plot.soil_type] = {"count": 0, "area": 0.0}
            soil_type_stats[plot.soil_type]["count"] += 1
            soil_type_stats[plot.soil_type]["area"] += plot.area
    
    # 按灌溉方式统计
    irrigation_stats = {}
    for plot in plots:
        if plot.irrigation_type:
            if plot.irrigation_type not in irrigation_stats:
                irrigation_stats[plot.irrigation_type] = {"count": 0, "area": 0.0}
            irrigation_stats[plot.irrigation_type]["count"] += 1
            irrigation_stats[plot.irrigation_type]["area"] += plot.area
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={
            "total_count": count,
            "total_area": round(total_area, 2),
            "avg_area": round(total_area / count, 2) if count > 0 else 0,
            "soil_type_stats": soil_type_stats,
            "irrigation_stats": irrigation_stats
        }
    )

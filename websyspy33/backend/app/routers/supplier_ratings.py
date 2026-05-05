# -*- coding: utf-8 -*-
"""
供应商评级API路由
==================
提供供应商评级的增删改查接口
对供应商的供货及时性、材料质量建立评分机制
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import SupplierRating, Supplier, MaterialInspection
from app.schemas import SupplierRatingCreate, SupplierRatingUpdate, SupplierRatingResponse

router = APIRouter()


@router.get("/", response_model=List[SupplierRatingResponse], summary="获取供应商评级列表")
async def get_supplier_ratings(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    rating_period: Optional[str] = Query(None, description="评级周期筛选"),
    rating_level: Optional[str] = Query(None, description="评级等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商评级列表，支持分页和筛选
    """
    query = select(SupplierRating)
    
    if keyword:
        query = query.where(
            (SupplierRating.rating_no.like(f"%{keyword}%")) |
            (SupplierRating.rating_period.like(f"%{keyword}%"))
        )
    
    if supplier_id:
        query = query.where(SupplierRating.supplier_id == supplier_id)
    
    if rating_period:
        query = query.where(SupplierRating.rating_period == rating_period)
    
    if rating_level:
        query = query.where(SupplierRating.rating_level == rating_level)
    
    if status:
        query = query.where(SupplierRating.status == status)
    
    query = query.order_by(SupplierRating.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    ratings = result.scalars().all()
    
    return ratings


@router.get("/count", response_model=int, summary="获取供应商评级总数")
async def get_supplier_ratings_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    rating_period: Optional[str] = Query(None, description="评级周期筛选"),
    rating_level: Optional[str] = Query(None, description="评级等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商评级总数
    """
    query = select(func.count(SupplierRating.id))
    
    if keyword:
        query = query.where(
            (SupplierRating.rating_no.like(f"%{keyword}%")) |
            (SupplierRating.rating_period.like(f"%{keyword}%"))
        )
    
    if supplier_id:
        query = query.where(SupplierRating.supplier_id == supplier_id)
    
    if rating_period:
        query = query.where(SupplierRating.rating_period == rating_period)
    
    if rating_level:
        query = query.where(SupplierRating.rating_level == rating_level)
    
    if status:
        query = query.where(SupplierRating.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/rating-levels", response_model=List[str], summary="获取评级等级选项")
async def get_rating_levels():
    """
    获取所有评级等级选项，用于下拉选择
    A级: 90-100分
    B级: 75-89分
    C级: 60-74分
    D级: 0-59分
    """
    return ["A级", "B级", "C级", "D级"]


@router.get("/{rating_id}", response_model=SupplierRatingResponse, summary="获取单个供应商评级")
async def get_supplier_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取供应商评级详情
    """
    query = select(SupplierRating).where(SupplierRating.id == rating_id)
    result = await db.execute(query)
    rating = result.scalar_one_or_none()
    
    if rating is None:
        raise HTTPException(status_code=404, detail=f"供应商评级 ID: {rating_id} 不存在")
    
    return rating


@router.post("/", response_model=SupplierRatingResponse, status_code=201, summary="创建供应商评级")
async def create_supplier_rating(
    rating: SupplierRatingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的供应商评级
    """
    # 检查评级编号是否已存在
    query = select(SupplierRating).where(SupplierRating.rating_no == rating.rating_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"评级编号 {rating.rating_no} 已存在")
    
    # 检查供应商是否存在
    supplier_query = select(Supplier).where(Supplier.id == rating.supplier_id)
    supplier_result = await db.execute(supplier_query)
    supplier = supplier_result.scalar_one_or_none()
    if supplier is None:
        raise HTTPException(status_code=400, detail=f"供应商 ID: {rating.supplier_id} 不存在")
    
    new_rating = SupplierRating(**rating.model_dump())
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    
    return new_rating


@router.put("/{rating_id}", response_model=SupplierRatingResponse, summary="更新供应商评级")
async def update_supplier_rating(
    rating_id: int,
    rating: SupplierRatingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新供应商评级
    """
    query = select(SupplierRating).where(SupplierRating.id == rating_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"供应商评级 ID: {rating_id} 不存在")
    
    update_data = rating.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{rating_id}", status_code=204, summary="删除供应商评级")
async def delete_supplier_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除供应商评级
    """
    query = select(SupplierRating).where(SupplierRating.id == rating_id)
    result = await db.execute(query)
    rating = result.scalar_one_or_none()
    
    if rating is None:
        raise HTTPException(status_code=404, detail=f"供应商评级 ID: {rating_id} 不存在")
    
    await db.delete(rating)
    await db.commit()


@router.post("/{rating_id}/activate", response_model=SupplierRatingResponse, summary="生效评级")
async def activate_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    将评级标记为已生效
    """
    query = select(SupplierRating).where(SupplierRating.id == rating_id)
    result = await db.execute(query)
    rating = result.scalar_one_or_none()
    
    if rating is None:
        raise HTTPException(status_code=404, detail=f"供应商评级 ID: {rating_id} 不存在")
    
    rating.status = "已生效"
    
    await db.commit()
    await db.refresh(rating)
    
    return rating


@router.post("/calculate/{supplier_id}", summary="计算供应商评级")
async def calculate_supplier_rating(
    supplier_id: int,
    rating_period: str,
    rater: str,
    db: AsyncSession = Depends(get_db)
):
    """
    根据原材料检验数据自动计算供应商评级
    评分规则：
    - 材料质量评分 (0-40分)：基于检验合格率
    - 供货及时性评分 (0-30分)：基于准时率
    - 价格合理性评分 (0-20分)：简化为固定值
    - 售后服务评分 (0-10分)：简化为固定值
    """
    from datetime import date, datetime
    
    # 检查供应商是否存在
    supplier_query = select(Supplier).where(Supplier.id == supplier_id)
    supplier_result = await db.execute(supplier_query)
    supplier = supplier_result.scalar_one_or_none()
    if supplier is None:
        raise HTTPException(status_code=404, detail=f"供应商 ID: {supplier_id} 不存在")
    
    # 获取该供应商的检验记录
    inspection_query = select(MaterialInspection).where(
        MaterialInspection.supplier_id == supplier_id
    )
    inspection_result = await db.execute(inspection_query)
    inspections = inspection_result.scalars().all()
    
    inspection_count = len(inspections)
    
    # 计算合格率
    if inspection_count > 0:
        pass_count = sum(1 for i in inspections if i.is_qualified)
        pass_rate = (pass_count / inspection_count) * 100
    else:
        pass_rate = 100.0
    
    # 计算评分
    # 材料质量评分：合格率 100% = 40分，每降低1%扣1分
    quality_score = max(0, 40 - (100 - pass_rate) * 0.4)
    
    # 简化其他评分
    delivery_score = 30.0  # 假设供货及时
    price_score = 18.0     # 假设价格合理
    service_score = 9.0    # 假设服务良好
    
    # 计算总分
    total_score = round(quality_score + delivery_score + price_score + service_score, 2)
    
    # 确定评级等级
    if total_score >= 90:
        rating_level = "A级"
    elif total_score >= 75:
        rating_level = "B级"
    elif total_score >= 60:
        rating_level = "C级"
    else:
        rating_level = "D级"
    
    # 生成评级编号
    rating_no = f"SR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建评级记录
    new_rating = SupplierRating(
        rating_no=rating_no,
        supplier_id=supplier_id,
        rating_period=rating_period,
        rating_date=date.today(),
        quality_score=round(quality_score, 2),
        delivery_score=delivery_score,
        price_score=price_score,
        service_score=service_score,
        total_score=total_score,
        rating_level=rating_level,
        inspection_count=inspection_count,
        pass_rate=round(pass_rate, 2),
        delivery_count=0,
        on_time_rate=100.0,
        remark="系统自动计算生成",
        rater=rater,
        status="草稿"
    )
    
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    
    return new_rating

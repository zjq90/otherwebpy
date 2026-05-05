# -*- coding: utf-8 -*-
"""
生产批次API路由
================
提供生产批次的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import ProductionBatch, MixDesign
from app.schemas import ProductionBatchCreate, ProductionBatchUpdate, ProductionBatchResponse

router = APIRouter()


@router.get("/", response_model=List[ProductionBatchResponse], summary="获取生产批次列表")
async def get_production_batches(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    mix_design_id: Optional[int] = Query(None, description="配比设计ID筛选"),
    strength_grade: Optional[str] = Query(None, description="强度等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产批次列表，支持分页和筛选
    """
    query = select(ProductionBatch)
    
    if keyword:
        query = query.where(
            (ProductionBatch.batch_no.like(f"%{keyword}%")) |
            (ProductionBatch.project_name.like(f"%{keyword}%")) |
            (ProductionBatch.construction_site.like(f"%{keyword}%"))
        )
    
    if mix_design_id:
        query = query.where(ProductionBatch.mix_design_id == mix_design_id)
    
    if strength_grade:
        query = query.where(ProductionBatch.strength_grade == strength_grade)
    
    if status:
        query = query.where(ProductionBatch.status == status)
    
    query = query.order_by(ProductionBatch.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    batches = result.scalars().all()
    
    return batches


@router.get("/count", response_model=int, summary="获取生产批次总数")
async def get_production_batches_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    mix_design_id: Optional[int] = Query(None, description="配比设计ID筛选"),
    strength_grade: Optional[str] = Query(None, description="强度等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产批次总数
    """
    query = select(func.count(ProductionBatch.id))
    
    if keyword:
        query = query.where(
            (ProductionBatch.batch_no.like(f"%{keyword}%")) |
            (ProductionBatch.project_name.like(f"%{keyword}%")) |
            (ProductionBatch.construction_site.like(f"%{keyword}%"))
        )
    
    if mix_design_id:
        query = query.where(ProductionBatch.mix_design_id == mix_design_id)
    
    if strength_grade:
        query = query.where(ProductionBatch.strength_grade == strength_grade)
    
    if status:
        query = query.where(ProductionBatch.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/{batch_id}", response_model=ProductionBatchResponse, summary="获取单个生产批次")
async def get_production_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取生产批次详情
    """
    query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    result = await db.execute(query)
    batch = result.scalar_one_or_none()
    
    if batch is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    return batch


@router.post("/", response_model=ProductionBatchResponse, status_code=201, summary="创建生产批次")
async def create_production_batch(
    batch: ProductionBatchCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的生产批次
    """
    # 检查生产批号是否已存在
    query = select(ProductionBatch).where(ProductionBatch.batch_no == batch.batch_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"生产批号 {batch.batch_no} 已存在")
    
    # 检查配比设计是否存在
    mix_query = select(MixDesign).where(MixDesign.id == batch.mix_design_id)
    mix_result = await db.execute(mix_query)
    mix_design = mix_result.scalar_one_or_none()
    if mix_design is None:
        raise HTTPException(status_code=400, detail=f"配比设计 ID: {batch.mix_design_id} 不存在")
    
    new_batch = ProductionBatch(**batch.model_dump())
    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)
    
    return new_batch


@router.put("/{batch_id}", response_model=ProductionBatchResponse, summary="更新生产批次")
async def update_production_batch(
    batch_id: int,
    batch: ProductionBatchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新生产批次
    """
    query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    update_data = batch.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{batch_id}", status_code=204, summary="删除生产批次")
async def delete_production_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除生产批次
    """
    query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    result = await db.execute(query)
    batch = result.scalar_one_or_none()
    
    if batch is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    await db.delete(batch)
    await db.commit()


@router.post("/{batch_id}/start", response_model=ProductionBatchResponse, summary="开始生产")
async def start_production(
    batch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    开始生产，更新状态为生产中
    """
    from datetime import datetime
    
    query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    result = await db.execute(query)
    batch = result.scalar_one_or_none()
    
    if batch is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    if batch.status != "待生产":
        raise HTTPException(status_code=400, detail="只能开始待生产状态的批次")
    
    batch.status = "生产中"
    batch.production_start = datetime.now()
    
    await db.commit()
    await db.refresh(batch)
    
    return batch


@router.post("/{batch_id}/finish", response_model=ProductionBatchResponse, summary="完成生产")
async def finish_production(
    batch_id: int,
    actual_volume: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    完成生产，更新状态为已完成
    """
    from datetime import datetime
    
    query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    result = await db.execute(query)
    batch = result.scalar_one_or_none()
    
    if batch is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    if batch.status != "生产中":
        raise HTTPException(status_code=400, detail="只能完成生产中状态的批次")
    
    batch.status = "已完成"
    batch.production_end = datetime.now()
    if actual_volume:
        batch.actual_volume = actual_volume
    
    await db.commit()
    await db.refresh(batch)
    
    return batch

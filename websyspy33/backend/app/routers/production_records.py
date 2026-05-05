# -*- coding: utf-8 -*-
"""
生产记录API路由
================
提供生产记录的增删改查接口
实时采集搅拌时间、投料顺序、水胶比等关键参数
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import ProductionRecord, ProductionBatch
from app.schemas import ProductionRecordCreate, ProductionRecordUpdate, ProductionRecordResponse

router = APIRouter()


@router.get("/", response_model=List[ProductionRecordResponse], summary="获取生产记录列表")
async def get_production_records(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    batch_id: Optional[int] = Query(None, description="生产批次ID筛选"),
    is_normal: Optional[bool] = Query(None, description="是否正常筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产记录列表，支持分页和筛选
    """
    query = select(ProductionRecord)
    
    if batch_id:
        query = query.where(ProductionRecord.batch_id == batch_id)
    
    if is_normal is not None:
        query = query.where(ProductionRecord.is_normal == is_normal)
    
    query = query.order_by(ProductionRecord.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return records


@router.get("/count", response_model=int, summary="获取生产记录总数")
async def get_production_records_count(
    batch_id: Optional[int] = Query(None, description="生产批次ID筛选"),
    is_normal: Optional[bool] = Query(None, description="是否正常筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产记录总数
    """
    query = select(func.count(ProductionRecord.id))
    
    if batch_id:
        query = query.where(ProductionRecord.batch_id == batch_id)
    
    if is_normal is not None:
        query = query.where(ProductionRecord.is_normal == is_normal)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/batch/{batch_id}", response_model=List[ProductionRecordResponse], summary="获取批次的所有生产记录")
async def get_batch_records(
    batch_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定批次的所有生产记录
    """
    query = select(ProductionRecord).where(
        ProductionRecord.batch_id == batch_id
    ).order_by(ProductionRecord.mix_no).offset(skip).limit(limit)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return records


@router.get("/{record_id}", response_model=ProductionRecordResponse, summary="获取单个生产记录")
async def get_production_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取生产记录详情
    """
    query = select(ProductionRecord).where(ProductionRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if record is None:
        raise HTTPException(status_code=404, detail=f"生产记录 ID: {record_id} 不存在")
    
    return record


@router.post("/", response_model=ProductionRecordResponse, status_code=201, summary="创建生产记录")
async def create_production_record(
    record: ProductionRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的生产记录
    实时采集搅拌时间、投料顺序、水胶比等关键参数
    """
    # 检查记录编号是否已存在
    query = select(ProductionRecord).where(ProductionRecord.record_no == record.record_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"记录编号 {record.record_no} 已存在")
    
    # 检查生产批次是否存在
    batch_query = select(ProductionBatch).where(ProductionBatch.id == record.batch_id)
    batch_result = await db.execute(batch_query)
    batch = batch_result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=400, detail=f"生产批次 ID: {record.batch_id} 不存在")
    
    # 检查该批次的盘数序号是否已存在
    mix_query = select(ProductionRecord).where(
        (ProductionRecord.batch_id == record.batch_id) &
        (ProductionRecord.mix_no == record.mix_no)
    )
    mix_result = await db.execute(mix_query)
    mix_existing = mix_result.scalar_one_or_none()
    if mix_existing:
        raise HTTPException(status_code=400, detail=f"批次 {record.batch_id} 的第 {record.mix_no} 盘记录已存在")
    
    new_record = ProductionRecord(**record.model_dump())
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return new_record


@router.put("/{record_id}", response_model=ProductionRecordResponse, summary="更新生产记录")
async def update_production_record(
    record_id: int,
    record: ProductionRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新生产记录
    """
    query = select(ProductionRecord).where(ProductionRecord.id == record_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"生产记录 ID: {record_id} 不存在")
    
    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{record_id}", status_code=204, summary="删除生产记录")
async def delete_production_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除生产记录
    """
    query = select(ProductionRecord).where(ProductionRecord.id == record_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    
    if record is None:
        raise HTTPException(status_code=404, detail=f"生产记录 ID: {record_id} 不存在")
    
    await db.delete(record)
    await db.commit()


@router.get("/batch/{batch_id}/statistics", summary="获取批次生产统计")
async def get_batch_statistics(
    batch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定批次的生产统计信息
    """
    # 检查批次是否存在
    batch_query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    batch_result = await db.execute(batch_query)
    batch = batch_result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    # 获取该批次的所有生产记录
    query = select(ProductionRecord).where(ProductionRecord.batch_id == batch_id)
    result = await db.execute(query)
    records = result.scalars().all()
    
    if not records:
        return {
            "batch_id": batch_id,
            "batch_no": batch.batch_no,
            "total_records": 0,
            "message": "该批次暂无生产记录"
        }
    
    # 计算统计数据
    total_records = len(records)
    normal_count = sum(1 for r in records if r.is_normal)
    abnormal_count = total_records - normal_count
    
    # 计算水胶比的平均偏差
    avg_deviation = sum(r.deviation_rate for r in records) / total_records if total_records > 0 else 0
    
    # 计算平均搅拌时间
    avg_mixing_time = sum(r.mixing_time for r in records) / total_records if total_records > 0 else 0
    
    return {
        "batch_id": batch_id,
        "batch_no": batch.batch_no,
        "total_records": total_records,
        "normal_count": normal_count,
        "abnormal_count": abnormal_count,
        "normal_rate": round(normal_count / total_records * 100, 2) if total_records > 0 else 0,
        "avg_water_cement_ratio_deviation": round(avg_deviation, 4),
        "avg_mixing_time": round(avg_mixing_time, 1),
    }

# -*- coding: utf-8 -*-
"""
成品试块API路由
================
提供成品试块的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import TestBlock, ProductionBatch
from app.schemas import TestBlockCreate, TestBlockUpdate, TestBlockResponse

router = APIRouter()


@router.get("/", response_model=List[TestBlockResponse], summary="获取试块列表")
async def get_test_blocks(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    batch_id: Optional[int] = Query(None, description="生产批次ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取试块列表，支持分页和筛选
    """
    query = select(TestBlock)
    
    if keyword:
        query = query.where(
            (TestBlock.block_no.like(f"%{keyword}%"))
        )
    
    if batch_id:
        query = query.where(TestBlock.batch_id == batch_id)
    
    if status:
        query = query.where(TestBlock.status == status)
    
    query = query.order_by(TestBlock.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    blocks = result.scalars().all()
    
    return blocks


@router.get("/count", response_model=int, summary="获取试块总数")
async def get_test_blocks_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    batch_id: Optional[int] = Query(None, description="生产批次ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取试块总数
    """
    query = select(func.count(TestBlock.id))
    
    if keyword:
        query = query.where(
            (TestBlock.block_no.like(f"%{keyword}%"))
        )
    
    if batch_id:
        query = query.where(TestBlock.batch_id == batch_id)
    
    if status:
        query = query.where(TestBlock.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/status-options", response_model=List[str], summary="获取状态选项")
async def get_status_options():
    """
    获取所有状态选项，用于下拉选择
    """
    return ["待试验", "已试验", "已作废"]


@router.get("/{block_id}", response_model=TestBlockResponse, summary="获取单个试块")
async def get_test_block(
    block_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取试块详情
    """
    query = select(TestBlock).where(TestBlock.id == block_id)
    result = await db.execute(query)
    block = result.scalar_one_or_none()
    
    if block is None:
        raise HTTPException(status_code=404, detail=f"试块 ID: {block_id} 不存在")
    
    return block


@router.post("/", response_model=TestBlockResponse, status_code=201, summary="创建试块")
async def create_test_block(
    block: TestBlockCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的试块记录
    """
    # 检查试块编号是否已存在
    query = select(TestBlock).where(TestBlock.block_no == block.block_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"试块编号 {block.block_no} 已存在")
    
    # 检查生产批次是否存在
    batch_query = select(ProductionBatch).where(ProductionBatch.id == block.batch_id)
    batch_result = await db.execute(batch_query)
    batch = batch_result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=400, detail=f"生产批次 ID: {block.batch_id} 不存在")
    
    new_block = TestBlock(**block.model_dump())
    db.add(new_block)
    await db.commit()
    await db.refresh(new_block)
    
    return new_block


@router.put("/{block_id}", response_model=TestBlockResponse, summary="更新试块")
async def update_test_block(
    block_id: int,
    block: TestBlockUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新试块记录
    """
    query = select(TestBlock).where(TestBlock.id == block_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"试块 ID: {block_id} 不存在")
    
    update_data = block.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{block_id}", status_code=204, summary="删除试块")
async def delete_test_block(
    block_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除试块记录
    """
    query = select(TestBlock).where(TestBlock.id == block_id)
    result = await db.execute(query)
    block = result.scalar_one_or_none()
    
    if block is None:
        raise HTTPException(status_code=404, detail=f"试块 ID: {block_id} 不存在")
    
    await db.delete(block)
    await db.commit()


@router.post("/{block_id}/mark-tested", response_model=TestBlockResponse, summary="标记为已试验")
async def mark_block_tested(
    block_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    标记试块为已试验状态
    """
    query = select(TestBlock).where(TestBlock.id == block_id)
    result = await db.execute(query)
    block = result.scalar_one_or_none()
    
    if block is None:
        raise HTTPException(status_code=404, detail=f"试块 ID: {block_id} 不存在")
    
    block.status = "已试验"
    
    await db.commit()
    await db.refresh(block)
    
    return block


@router.post("/{block_id}/mark-void", response_model=TestBlockResponse, summary="标记为已作废")
async def mark_block_void(
    block_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    标记试块为已作废状态
    """
    query = select(TestBlock).where(TestBlock.id == block_id)
    result = await db.execute(query)
    block = result.scalar_one_or_none()
    
    if block is None:
        raise HTTPException(status_code=404, detail=f"试块 ID: {block_id} 不存在")
    
    block.status = "已作废"
    
    await db.commit()
    await db.refresh(block)
    
    return block

# -*- coding: utf-8 -*-
"""
强度检测API路由
================
提供强度检测的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import StrengthTest, TestBlock
from app.schemas import StrengthTestCreate, StrengthTestUpdate, StrengthTestResponse

router = APIRouter()


@router.get("/", response_model=List[StrengthTestResponse], summary="获取强度检测列表")
async def get_strength_tests(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    block_id: Optional[int] = Query(None, description="试块ID筛选"),
    result: Optional[str] = Query(None, description="结果筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取强度检测列表，支持分页和筛选
    """
    query = select(StrengthTest)
    
    if keyword:
        query = query.where(
            (StrengthTest.test_no.like(f"%{keyword}%"))
        )
    
    if block_id:
        query = query.where(StrengthTest.block_id == block_id)
    
    if result:
        query = query.where(StrengthTest.result == result)
    
    if status:
        query = query.where(StrengthTest.status == status)
    
    query = query.order_by(StrengthTest.created_at.desc()).offset(skip).limit(limit)
    
    result_set = await db.execute(query)
    tests = result_set.scalars().all()
    
    return tests


@router.get("/count", response_model=int, summary="获取强度检测总数")
async def get_strength_tests_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    block_id: Optional[int] = Query(None, description="试块ID筛选"),
    result: Optional[str] = Query(None, description="结果筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取强度检测总数
    """
    query = select(func.count(StrengthTest.id))
    
    if keyword:
        query = query.where(
            (StrengthTest.test_no.like(f"%{keyword}%"))
        )
    
    if block_id:
        query = query.where(StrengthTest.block_id == block_id)
    
    if result:
        query = query.where(StrengthTest.result == result)
    
    if status:
        query = query.where(StrengthTest.status == status)
    
    result_set = await db.execute(query)
    count = result_set.scalar_one()
    
    return count


@router.get("/{test_id}", response_model=StrengthTestResponse, summary="获取单个强度检测")
async def get_strength_test(
    test_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取强度检测详情
    """
    query = select(StrengthTest).where(StrengthTest.id == test_id)
    result = await db.execute(query)
    test = result.scalar_one_or_none()
    
    if test is None:
        raise HTTPException(status_code=404, detail=f"强度检测 ID: {test_id} 不存在")
    
    return test


@router.post("/", response_model=StrengthTestResponse, status_code=201, summary="创建强度检测")
async def create_strength_test(
    test: StrengthTestCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的强度检测记录
    """
    # 检查试验编号是否已存在
    query = select(StrengthTest).where(StrengthTest.test_no == test.test_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"试验编号 {test.test_no} 已存在")
    
    # 检查试块是否存在
    block_query = select(TestBlock).where(TestBlock.id == test.block_id)
    block_result = await db.execute(block_query)
    block = block_result.scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=400, detail=f"试块 ID: {test.block_id} 不存在")
    
    new_test = StrengthTest(**test.model_dump())
    db.add(new_test)
    await db.commit()
    await db.refresh(new_test)
    
    return new_test


@router.put("/{test_id}", response_model=StrengthTestResponse, summary="更新强度检测")
async def update_strength_test(
    test_id: int,
    test: StrengthTestUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新强度检测记录
    """
    query = select(StrengthTest).where(StrengthTest.id == test_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"强度检测 ID: {test_id} 不存在")
    
    update_data = test.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{test_id}", status_code=204, summary="删除强度检测")
async def delete_strength_test(
    test_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除强度检测记录
    """
    query = select(StrengthTest).where(StrengthTest.id == test_id)
    result = await db.execute(query)
    test = result.scalar_one_or_none()
    
    if test is None:
        raise HTTPException(status_code=404, detail=f"强度检测 ID: {test_id} 不存在")
    
    await db.delete(test)
    await db.commit()


@router.post("/{test_id}/submit", response_model=StrengthTestResponse, summary="提交检测")
async def submit_strength_test(
    test_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    提交检测记录，状态从草稿变为已提交
    """
    query = select(StrengthTest).where(StrengthTest.id == test_id)
    result = await db.execute(query)
    test = result.scalar_one_or_none()
    
    if test is None:
        raise HTTPException(status_code=404, detail=f"强度检测 ID: {test_id} 不存在")
    
    if test.status != "草稿":
        raise HTTPException(status_code=400, detail="只能提交草稿状态的检测记录")
    
    test.status = "已提交"
    
    await db.commit()
    await db.refresh(test)
    
    return test


@router.post("/{test_id}/review", response_model=StrengthTestResponse, summary="审核检测")
async def review_strength_test(
    test_id: int,
    reviewer: str,
    db: AsyncSession = Depends(get_db)
):
    """
    审核检测记录
    """
    from datetime import date
    
    query = select(StrengthTest).where(StrengthTest.id == test_id)
    result = await db.execute(query)
    test = result.scalar_one_or_none()
    
    if test is None:
        raise HTTPException(status_code=404, detail=f"强度检测 ID: {test_id} 不存在")
    
    if test.status != "已提交":
        raise HTTPException(status_code=400, detail="只能审核已提交的检测记录")
    
    test.status = "已审核"
    test.reviewed_by = reviewer
    test.review_date = date.today()
    
    await db.commit()
    await db.refresh(test)
    
    return test

# -*- coding: utf-8 -*-
"""
配比设计API路由
================
提供配比设计的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import MixDesign
from app.schemas import MixDesignCreate, MixDesignUpdate, MixDesignResponse

router = APIRouter()


@router.get("/", response_model=List[MixDesignResponse], summary="获取配比设计列表")
async def get_mix_designs(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    strength_grade: Optional[str] = Query(None, description="强度等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取配比设计列表，支持分页和筛选
    """
    query = select(MixDesign)
    
    if keyword:
        query = query.where(
            (MixDesign.design_no.like(f"%{keyword}%")) |
            (MixDesign.mix_name.like(f"%{keyword}%"))
        )
    
    if strength_grade:
        query = query.where(MixDesign.strength_grade == strength_grade)
    
    if status:
        query = query.where(MixDesign.status == status)
    
    if is_active is not None:
        query = query.where(MixDesign.is_active == is_active)
    
    query = query.order_by(MixDesign.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    designs = result.scalars().all()
    
    return designs


@router.get("/count", response_model=int, summary="获取配比设计总数")
async def get_mix_designs_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    strength_grade: Optional[str] = Query(None, description="强度等级筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取配比设计总数
    """
    query = select(func.count(MixDesign.id))
    
    if keyword:
        query = query.where(
            (MixDesign.design_no.like(f"%{keyword}%")) |
            (MixDesign.mix_name.like(f"%{keyword}%"))
        )
    
    if strength_grade:
        query = query.where(MixDesign.strength_grade == strength_grade)
    
    if status:
        query = query.where(MixDesign.status == status)
    
    if is_active is not None:
        query = query.where(MixDesign.is_active == is_active)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/strength-grades", response_model=List[str], summary="获取所有强度等级")
async def get_strength_grades(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有强度等级，用于下拉选择
    """
    query = select(MixDesign.strength_grade).distinct()
    result = await db.execute(query)
    grades = result.scalars().all()
    
    return list(grades)


@router.get("/{design_id}", response_model=MixDesignResponse, summary="获取单个配比设计")
async def get_mix_design(
    design_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取配比设计详情
    """
    query = select(MixDesign).where(MixDesign.id == design_id)
    result = await db.execute(query)
    design = result.scalar_one_or_none()
    
    if design is None:
        raise HTTPException(status_code=404, detail=f"配比设计 ID: {design_id} 不存在")
    
    return design


@router.post("/", response_model=MixDesignResponse, status_code=201, summary="创建配比设计")
async def create_mix_design(
    design: MixDesignCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的配比设计
    """
    # 检查设计编号是否已存在
    query = select(MixDesign).where(MixDesign.design_no == design.design_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"设计编号 {design.design_no} 已存在")
    
    new_design = MixDesign(**design.model_dump())
    db.add(new_design)
    await db.commit()
    await db.refresh(new_design)
    
    return new_design


@router.put("/{design_id}", response_model=MixDesignResponse, summary="更新配比设计")
async def update_mix_design(
    design_id: int,
    design: MixDesignUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新配比设计
    """
    query = select(MixDesign).where(MixDesign.id == design_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"配比设计 ID: {design_id} 不存在")
    
    update_data = design.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{design_id}", status_code=204, summary="删除配比设计")
async def delete_mix_design(
    design_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除配比设计
    """
    query = select(MixDesign).where(MixDesign.id == design_id)
    result = await db.execute(query)
    design = result.scalar_one_or_none()
    
    if design is None:
        raise HTTPException(status_code=404, detail=f"配比设计 ID: {design_id} 不存在")
    
    await db.delete(design)
    await db.commit()


@router.post("/{design_id}/activate", response_model=MixDesignResponse, summary="启用配比设计")
async def activate_mix_design(
    design_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    启用配比设计
    """
    query = select(MixDesign).where(MixDesign.id == design_id)
    result = await db.execute(query)
    design = result.scalar_one_or_none()
    
    if design is None:
        raise HTTPException(status_code=404, detail=f"配比设计 ID: {design_id} 不存在")
    
    design.is_active = True
    design.status = "已启用"
    
    await db.commit()
    await db.refresh(design)
    
    return design


@router.post("/{design_id}/deactivate", response_model=MixDesignResponse, summary="停用配比设计")
async def deactivate_mix_design(
    design_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    停用配比设计
    """
    query = select(MixDesign).where(MixDesign.id == design_id)
    result = await db.execute(query)
    design = result.scalar_one_or_none()
    
    if design is None:
        raise HTTPException(status_code=404, detail=f"配比设计 ID: {design_id} 不存在")
    
    design.is_active = False
    
    await db.commit()
    await db.refresh(design)
    
    return design

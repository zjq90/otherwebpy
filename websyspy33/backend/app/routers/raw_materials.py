# -*- coding: utf-8 -*-
"""
原材料管理API路由
==================
提供原材料的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import RawMaterial, Supplier
from app.schemas import RawMaterialCreate, RawMaterialUpdate, RawMaterialResponse

router = APIRouter()


@router.get("/", response_model=List[RawMaterialResponse], summary="获取原材料列表")
async def get_raw_materials(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    material_type: Optional[str] = Query(None, description="材料类型筛选"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    status: Optional[bool] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料列表，支持分页和筛选
    """
    query = select(RawMaterial)
    
    if keyword:
        query = query.where(
            (RawMaterial.name.like(f"%{keyword}%")) |
            (RawMaterial.code.like(f"%{keyword}%"))
        )
    
    if material_type:
        query = query.where(RawMaterial.material_type == material_type)
    
    if supplier_id:
        query = query.where(RawMaterial.supplier_id == supplier_id)
    
    if status is not None:
        query = query.where(RawMaterial.status == status)
    
    query = query.order_by(RawMaterial.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    materials = result.scalars().all()
    
    return materials


@router.get("/count", response_model=int, summary="获取原材料总数")
async def get_raw_materials_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    material_type: Optional[str] = Query(None, description="材料类型筛选"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    status: Optional[bool] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料总数
    """
    query = select(func.count(RawMaterial.id))
    
    if keyword:
        query = query.where(
            (RawMaterial.name.like(f"%{keyword}%")) |
            (RawMaterial.code.like(f"%{keyword}%"))
        )
    
    if material_type:
        query = query.where(RawMaterial.material_type == material_type)
    
    if supplier_id:
        query = query.where(RawMaterial.supplier_id == supplier_id)
    
    if status is not None:
        query = query.where(RawMaterial.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/types", response_model=List[str], summary="获取所有材料类型")
async def get_material_types(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有材料类型，用于下拉选择
    """
    query = select(RawMaterial.material_type).distinct()
    result = await db.execute(query)
    types = result.scalars().all()
    
    return list(types)


@router.get("/{material_id}", response_model=RawMaterialResponse, summary="获取单个原材料")
async def get_raw_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取原材料详情
    """
    query = select(RawMaterial).where(RawMaterial.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(status_code=404, detail=f"原材料 ID: {material_id} 不存在")
    
    return material


@router.post("/", response_model=RawMaterialResponse, status_code=201, summary="创建原材料")
async def create_raw_material(
    material: RawMaterialCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新原材料
    """
    # 检查编码是否已存在
    query = select(RawMaterial).where(RawMaterial.code == material.code)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"原材料编码 {material.code} 已存在")
    
    # 如果指定了供应商，检查供应商是否存在
    if material.supplier_id:
        supplier_query = select(Supplier).where(Supplier.id == material.supplier_id)
        supplier_result = await db.execute(supplier_query)
        supplier = supplier_result.scalar_one_or_none()
        if supplier is None:
            raise HTTPException(status_code=400, detail=f"供应商 ID: {material.supplier_id} 不存在")
    
    new_material = RawMaterial(**material.model_dump())
    db.add(new_material)
    await db.commit()
    await db.refresh(new_material)
    
    return new_material


@router.put("/{material_id}", response_model=RawMaterialResponse, summary="更新原材料")
async def update_raw_material(
    material_id: int,
    material: RawMaterialUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新原材料信息
    """
    query = select(RawMaterial).where(RawMaterial.id == material_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"原材料 ID: {material_id} 不存在")
    
    update_data = material.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{material_id}", status_code=204, summary="删除原材料")
async def delete_raw_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除原材料（软删除）
    """
    query = select(RawMaterial).where(RawMaterial.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(status_code=404, detail=f"原材料 ID: {material_id} 不存在")
    
    material.status = False
    await db.commit()

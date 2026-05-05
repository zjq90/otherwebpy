# -*- coding: utf-8 -*-
"""
供应商管理API路由
==================
提供供应商的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Supplier
from app.schemas import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter()


@router.get("/", response_model=List[SupplierResponse], summary="获取供应商列表")
async def get_suppliers(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[bool] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商列表，支持分页和筛选
    
    - **skip**: 跳过的记录数，用于分页
    - **limit**: 返回的最大记录数
    - **keyword**: 搜索关键词，支持名称和编码
    - **status**: 按状态筛选
    """
    query = select(Supplier)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            (Supplier.name.like(f"%{keyword}%")) |
            (Supplier.code.like(f"%{keyword}%"))
        )
    
    # 状态筛选
    if status is not None:
        query = query.where(Supplier.status == status)
    
    # 排序和分页
    query = query.order_by(Supplier.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    suppliers = result.scalars().all()
    
    return suppliers


@router.get("/count", response_model=int, summary="获取供应商总数")
async def get_suppliers_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[bool] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取供应商总数，用于分页
    """
    query = select(func.count(Supplier.id))
    
    if keyword:
        query = query.where(
            (Supplier.name.like(f"%{keyword}%")) |
            (Supplier.code.like(f"%{keyword}%"))
        )
    
    if status is not None:
        query = query.where(Supplier.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/{supplier_id}", response_model=SupplierResponse, summary="获取单个供应商")
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取供应商详情
    
    - **supplier_id**: 供应商ID
    """
    query = select(Supplier).where(Supplier.id == supplier_id)
    result = await db.execute(query)
    supplier = result.scalar_one_or_none()
    
    if supplier is None:
        raise HTTPException(status_code=404, detail=f"供应商 ID: {supplier_id} 不存在")
    
    return supplier


@router.post("/", response_model=SupplierResponse, status_code=201, summary="创建供应商")
async def create_supplier(
    supplier: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新供应商
    
    - **supplier**: 供应商信息
    """
    # 检查编码是否已存在
    query = select(Supplier).where(Supplier.code == supplier.code)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"供应商编码 {supplier.code} 已存在")
    
    # 创建供应商
    new_supplier = Supplier(**supplier.model_dump())
    db.add(new_supplier)
    await db.commit()
    await db.refresh(new_supplier)
    
    return new_supplier


@router.put("/{supplier_id}", response_model=SupplierResponse, summary="更新供应商")
async def update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新供应商信息
    
    - **supplier_id**: 供应商ID
    - **supplier**: 更新的供应商信息
    """
    query = select(Supplier).where(Supplier.id == supplier_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"供应商 ID: {supplier_id} 不存在")
    
    # 更新字段
    update_data = supplier.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{supplier_id}", status_code=204, summary="删除供应商")
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除供应商（软删除，实际设置status为False）
    
    - **supplier_id**: 供应商ID
    """
    query = select(Supplier).where(Supplier.id == supplier_id)
    result = await db.execute(query)
    supplier = result.scalar_one_or_none()
    
    if supplier is None:
        raise HTTPException(status_code=404, detail=f"供应商 ID: {supplier_id} 不存在")
    
    # 软删除：设置状态为禁用
    supplier.status = False
    await db.commit()

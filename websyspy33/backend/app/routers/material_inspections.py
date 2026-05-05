# -*- coding: utf-8 -*-
"""
原材料检验API路由
==================
提供原材料检验的增删改查接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import MaterialInspection, RawMaterial, Supplier
from app.schemas import MaterialInspectionCreate, MaterialInspectionUpdate, MaterialInspectionResponse

router = APIRouter()


@router.get("/", response_model=List[MaterialInspectionResponse], summary="获取原材料检验列表")
async def get_material_inspections(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    material_id: Optional[int] = Query(None, description="原材料ID筛选"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    result: Optional[str] = Query(None, description="检验结果筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料检验列表，支持分页和筛选
    """
    query = select(MaterialInspection)
    
    if keyword:
        query = query.where(
            (MaterialInspection.inspection_no.like(f"%{keyword}%")) |
            (MaterialInspection.batch_no.like(f"%{keyword}%"))
        )
    
    if material_id:
        query = query.where(MaterialInspection.material_id == material_id)
    
    if supplier_id:
        query = query.where(MaterialInspection.supplier_id == supplier_id)
    
    if result:
        query = query.where(MaterialInspection.result == result)
    
    if status:
        query = query.where(MaterialInspection.status == status)
    
    query = query.order_by(MaterialInspection.created_at.desc()).offset(skip).limit(limit)
    
    result_set = await db.execute(query)
    inspections = result_set.scalars().all()
    
    return inspections


@router.get("/count", response_model=int, summary="获取原材料检验总数")
async def get_material_inspections_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    material_id: Optional[int] = Query(None, description="原材料ID筛选"),
    supplier_id: Optional[int] = Query(None, description="供应商ID筛选"),
    result: Optional[str] = Query(None, description="检验结果筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料检验总数
    """
    query = select(func.count(MaterialInspection.id))
    
    if keyword:
        query = query.where(
            (MaterialInspection.inspection_no.like(f"%{keyword}%")) |
            (MaterialInspection.batch_no.like(f"%{keyword}%"))
        )
    
    if material_id:
        query = query.where(MaterialInspection.material_id == material_id)
    
    if supplier_id:
        query = query.where(MaterialInspection.supplier_id == supplier_id)
    
    if result:
        query = query.where(MaterialInspection.result == result)
    
    if status:
        query = query.where(MaterialInspection.status == status)
    
    result_set = await db.execute(query)
    count = result_set.scalar_one()
    
    return count


@router.get("/{inspection_id}", response_model=MaterialInspectionResponse, summary="获取单个原材料检验")
async def get_material_inspection(
    inspection_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取原材料检验详情
    """
    query = select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    result = await db.execute(query)
    inspection = result.scalar_one_or_none()
    
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"检验记录 ID: {inspection_id} 不存在")
    
    return inspection


@router.post("/", response_model=MaterialInspectionResponse, status_code=201, summary="创建原材料检验")
async def create_material_inspection(
    inspection: MaterialInspectionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的原材料检验记录
    """
    # 检查检验单号是否已存在
    query = select(MaterialInspection).where(MaterialInspection.inspection_no == inspection.inspection_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"检验单号 {inspection.inspection_no} 已存在")
    
    # 检查原材料是否存在
    material_query = select(RawMaterial).where(RawMaterial.id == inspection.material_id)
    material_result = await db.execute(material_query)
    material = material_result.scalar_one_or_none()
    if material is None:
        raise HTTPException(status_code=400, detail=f"原材料 ID: {inspection.material_id} 不存在")
    
    # 如果指定了供应商，检查供应商是否存在
    if inspection.supplier_id:
        supplier_query = select(Supplier).where(Supplier.id == inspection.supplier_id)
        supplier_result = await db.execute(supplier_query)
        supplier = supplier_result.scalar_one_or_none()
        if supplier is None:
            raise HTTPException(status_code=400, detail=f"供应商 ID: {inspection.supplier_id} 不存在")
    
    new_inspection = MaterialInspection(**inspection.model_dump())
    db.add(new_inspection)
    await db.commit()
    await db.refresh(new_inspection)
    
    return new_inspection


@router.put("/{inspection_id}", response_model=MaterialInspectionResponse, summary="更新原材料检验")
async def update_material_inspection(
    inspection_id: int,
    inspection: MaterialInspectionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新原材料检验记录
    """
    query = select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"检验记录 ID: {inspection_id} 不存在")
    
    update_data = inspection.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{inspection_id}", status_code=204, summary="删除原材料检验")
async def delete_material_inspection(
    inspection_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除原材料检验记录
    """
    query = select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    result = await db.execute(query)
    inspection = result.scalar_one_or_none()
    
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"检验记录 ID: {inspection_id} 不存在")
    
    await db.delete(inspection)
    await db.commit()


@router.post("/{inspection_id}/submit", response_model=MaterialInspectionResponse, summary="提交检验")
async def submit_material_inspection(
    inspection_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    提交检验记录，状态从草稿变为已提交
    """
    query = select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    result = await db.execute(query)
    inspection = result.scalar_one_or_none()
    
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"检验记录 ID: {inspection_id} 不存在")
    
    if inspection.status != "草稿":
        raise HTTPException(status_code=400, detail="只能提交草稿状态的检验记录")
    
    inspection.status = "已提交"
    await db.commit()
    await db.refresh(inspection)
    
    return inspection


@router.post("/{inspection_id}/review", response_model=MaterialInspectionResponse, summary="审核检验")
async def review_material_inspection(
    inspection_id: int,
    reviewer: str,
    db: AsyncSession = Depends(get_db)
):
    """
    审核检验记录
    """
    from datetime import date
    
    query = select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    result = await db.execute(query)
    inspection = result.scalar_one_or_none()
    
    if inspection is None:
        raise HTTPException(status_code=404, detail=f"检验记录 ID: {inspection_id} 不存在")
    
    if inspection.status != "已提交":
        raise HTTPException(status_code=400, detail="只能审核已提交的检验记录")
    
    inspection.status = "已审核"
    inspection.reviewed_by = reviewer
    inspection.review_date = date.today()
    
    await db.commit()
    await db.refresh(inspection)
    
    return inspection

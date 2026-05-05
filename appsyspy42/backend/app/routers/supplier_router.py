"""
供应商管理路由
处理供应商信息、供货记录、评价等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplyRecordCreate, SupplyRecordResponse,
    SupplierEvaluationCreate, SupplierEvaluationResponse
)
from app.services.supplier_service import SupplierService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/supplier", tags=["供应商管理"])


@router.get("/list", summary="获取供应商列表")
def get_supplier_list(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    is_active: Optional[int] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取供应商列表，支持关键词搜索和状态筛选"""
    service = SupplierService(db)
    result = service.get_supplier_list(
        keyword=keyword,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    return result


@router.get("/list/{supplier_id}", response_model=SupplierResponse, summary="获取供应商详情")
def get_supplier_detail(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定供应商的详细信息"""
    service = SupplierService(db)
    supplier = service.get_supplier_by_id(supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    return supplier


@router.post("/list", response_model=SupplierResponse, summary="创建供应商")
def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的供应商"""
    service = SupplierService(db)
    supplier = service.create_supplier(supplier_data)
    
    return supplier


@router.put("/list/{supplier_id}", response_model=SupplierResponse, summary="更新供应商")
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新供应商信息"""
    service = SupplierService(db)
    supplier = service.update_supplier(supplier_id, supplier_data)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    return supplier


@router.delete("/list/{supplier_id}", summary="删除供应商（软删除）")
def delete_supplier(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除供应商（软删除，设置为禁用状态）"""
    service = SupplierService(db)
    success = service.delete_supplier(supplier_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    return {"success": True, "message": "供应商已删除"}


@router.get("/supply-records", summary="获取供货记录列表")
def get_supply_records(
    supplier_id: Optional[int] = Query(None, description="供应商ID"),
    material_id: Optional[int] = Query(None, description="原材料ID"),
    quality_status: Optional[str] = Query(None, description="质量状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取供货记录列表，支持多种筛选条件"""
    service = SupplierService(db)
    result = service.get_supply_records(
        supplier_id=supplier_id,
        material_id=material_id,
        quality_status=quality_status,
        page=page,
        page_size=page_size
    )
    
    return result


@router.post("/supply-records", summary="创建供货记录")
def create_supply_record(
    record_data: SupplyRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的供货记录"""
    service = SupplierService(db)
    record = service.create_supply_record(record_data)
    
    return {
        "success": True, 
        "message": "供货记录创建成功", 
        "data": {"id": record.id}
    }


@router.get("/evaluations", summary="获取供应商评价列表")
def get_evaluations(
    supplier_id: Optional[int] = Query(None, description="供应商ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取供应商评价列表"""
    service = SupplierService(db)
    result = service.get_evaluations(
        supplier_id=supplier_id,
        page=page,
        page_size=page_size
    )
    
    return result


@router.post("/evaluations", summary="创建供应商评价")
def create_evaluation(
    eval_data: SupplierEvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """对供应商进行评价打分"""
    service = SupplierService(db)
    evaluation = service.create_evaluation(eval_data, current_user.id)
    
    return {
        "success": True, 
        "message": "评价创建成功", 
        "data": {"id": evaluation.id, "total_score": evaluation.total_score}
    }


@router.get("/statistics", summary="获取供应商统计数据")
def get_supplier_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取供应商相关的统计数据"""
    service = SupplierService(db)
    stats = service.get_statistics()
    
    return stats

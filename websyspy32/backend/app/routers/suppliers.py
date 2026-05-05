from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplierRatingCreate, SupplierRatingResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse
)
from app.crud import supplier_crud, supplier_rating_crud, purchase_order_crud

router = APIRouter(
    prefix="/api/suppliers",
    tags=["供应商评级与结算管理"],
    responses={404: {"description": "未找到"}}
)

@router.post("/", response_model=SupplierResponse, summary="创建供应商")
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    """
    创建新供应商
    - **supplier: 供应商信息
    """
    return supplier_crud.create(db, supplier)

@router.get("/", response_model=List[SupplierResponse], summary="获取供应商列表")
def read_suppliers(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取所有供应商列表
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    suppliers = supplier_crud.get_multi(db, skip=skip, limit=limit)
    return suppliers

@router.get("/by-material", response_model=List[SupplierResponse], summary="按供应物料类型获取供应商")
def read_suppliers_by_material(material_type: str, db: Session = Depends(get_db)):
    """
    按供应物料类型获取合作中的供应商
    - **material_type**: 物料类型
    """
    suppliers = supplier_crud.get_by_material_type(db, material_type)
    return suppliers

@router.get("/{supplier_id}", response_model=SupplierResponse, summary="获取单个供应商信息")
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取供应商信息
    - **supplier_id**: 供应商ID
    """
    supplier = supplier_crud.get(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier

@router.put("/{supplier_id}", response_model=SupplierResponse, summary="更新供应商信息")
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    """
    更新供应商信息
    - **supplier_id**: 供应商ID
    - **supplier**: 更新的供应商信息
    """
    db_supplier = supplier_crud.get(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier_crud.update(db, db_supplier, supplier)

@router.delete("/{supplier_id}", summary="删除供应商")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    删除供应商
    - **supplier_id**: 供应商ID
    """
    db_supplier = supplier_crud.get(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    supplier_crud.remove(db, supplier_id)
    return {"message": "删除成功", "id": supplier_id}

@router.post("/ratings/", response_model=SupplierRatingResponse, summary="创建供应商评级")
def create_supplier_rating(rating: SupplierRatingCreate, db: Session = Depends(get_db)):
    """
    创建新的供应商评级
    - **rating: 评级信息
    """
    supplier = supplier_crud.get(db, rating.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    db_rating = supplier_rating_crud.create(db, rating)
    supplier_crud.update_overall_rating(db, rating.supplier_id)
    
    return db_rating

@router.get("/ratings/by-supplier/{supplier_id}", response_model=List[SupplierRatingResponse], summary="获取供应商的评级记录")
def read_supplier_ratings(
    supplier_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取指定供应商的评级记录
    - **supplier_id**: 供应商ID
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    supplier = supplier_crud.get(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    ratings = supplier_rating_crud.get_by_supplier(db, supplier_id, skip=skip, limit=limit)
    return ratings

@router.get("/ratings/{rating_id}", response_model=SupplierRatingResponse, summary="获取单个评级记录")
def read_supplier_rating(rating_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取评级记录
    - **rating_id**: 评级记录ID
    """
    rating = supplier_rating_crud.get(db, rating_id)
    if rating is None:
        raise HTTPException(status_code=404, detail="评级记录不存在")
    return rating

@router.post("/orders/", response_model=PurchaseOrderResponse, summary="创建采购订单")
def create_purchase_order(order: PurchaseOrderCreate, db: Session = Depends(get_db)):
    """
    创建新的采购订单
    - **order: 采购订单信息
    """
    supplier = supplier_crud.get(db, order.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    return purchase_order_crud.create(db, order)

@router.get("/orders/", response_model=List[PurchaseOrderResponse], summary="获取采购订单列表")
def read_purchase_orders(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取所有采购订单列表
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    orders = purchase_order_crud.get_multi(db, skip=skip, limit=limit)
    return orders

@router.get("/orders/pending", response_model=List[PurchaseOrderResponse], summary="获取待处理的采购订单")
def read_pending_orders(db: Session = Depends(get_db)):
    """
    获取所有待处理的采购订单（待发货、已发货、部分收货）
    """
    orders = purchase_order_crud.get_pending_orders(db)
    return orders

@router.get("/orders/by-supplier/{supplier_id}", response_model=List[PurchaseOrderResponse], summary="获取供应商的采购订单")
def read_orders_by_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    获取指定供应商的所有采购订单
    - **supplier_id**: 供应商ID
    """
    supplier = supplier_crud.get(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    orders = purchase_order_crud.get_by_supplier(db, supplier_id)
    return orders

@router.get("/orders/by-status", response_model=List[PurchaseOrderResponse], summary="按状态获取采购订单")
def read_orders_by_status(status: str, db: Session = Depends(get_db)):
    """
    按状态获取采购订单
    - **status**: 订单状态
    """
    orders = purchase_order_crud.get_by_status(db, status)
    return orders

@router.get("/orders/{order_id}", response_model=PurchaseOrderResponse, summary="获取单个采购订单")
def read_purchase_order(order_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取采购订单
    - **order_id**: 采购订单ID
    """
    order = purchase_order_crud.get(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    return order

@router.put("/orders/{order_id}", response_model=PurchaseOrderResponse, summary="更新采购订单")
def update_purchase_order(order_id: int, order: PurchaseOrderUpdate, db: Session = Depends(get_db)):
    """
    更新采购订单
    - **order_id**: 采购订单ID
    - **order**: 更新的采购订单信息
    """
    db_order = purchase_order_crud.get(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    return purchase_order_crud.update(db, db_order, order)

@router.delete("/orders/{order_id}", summary="删除采购订单")
def delete_purchase_order(order_id: int, db: Session = Depends(get_db)):
    """
    删除采购订单
    - **order_id**: 采购订单ID
    """
    db_order = purchase_order_crud.get(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    purchase_order_crud.remove(db, order_id)
    return {"message": "删除成功", "id": order_id}

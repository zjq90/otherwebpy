from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.database import get_db
from app.schemas import (
    SiloCreate, SiloUpdate, SiloResponse,
    InventoryRecordCreate, InventoryRecordResponse,
    LowInventoryAlert
)
from app.crud import silo_crud, inventory_record_crud

router = APIRouter(
    prefix="/api/silos",
    tags=["料仓与库存管理"],
    responses={404: {"description": "未找到"}}
)

@router.post("/", response_model=SiloResponse, summary="创建料仓")
def create_silo(silo: SiloCreate, db: Session = Depends(get_db)):
    """
    创建新料仓
    - **silo: 料仓信息
    """
    return silo_crud.create(db, silo)

@router.get("/", response_model=List[SiloResponse], summary="获取所有料仓列表")
def read_silos(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """
    获取所有料仓列表
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    silos = silo_crud.get_multi(db, skip=skip, limit=limit)
    return silos

@router.get("/{silo_id}", response_model=SiloResponse, summary="获取单个料仓信息")
def read_silo(silo_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取料仓信息
    - **silo_id**: 料仓ID
    """
    silo = silo_crud.get(db, silo_id)
    if silo is None:
        raise HTTPException(status_code=404, detail="料仓不存在")
    return silo

@router.put("/{silo_id}", response_model=SiloResponse, summary="更新料仓信息")
def update_silo(silo_id: int, silo: SiloUpdate, db: Session = Depends(get_db)):
    """
    更新料仓信息
    - **silo_id**: 料仓ID
    - **silo**: 更新的料仓信息
    """
    db_silo = silo_crud.get(db, silo_id)
    if db_silo is None:
        raise HTTPException(status_code=404, detail="料仓不存在")
    return silo_crud.update(db, db_silo, silo)

@router.delete("/{silo_id}", summary="删除料仓")
def delete_silo(silo_id: int, db: Session = Depends(get_db)):
    """
    删除料仓
    - **silo_id**: 料仓ID
    """
    db_silo = silo_crud.get(db, silo_id)
    if db_silo is None:
        raise HTTPException(status_code=404, detail="料仓不存在")
    silo_crud.remove(db, silo_id)
    return {"message": "删除成功", "id": silo_id}

@router.post("/{silo_id}/adjust", response_model=SiloResponse, summary="调整料仓库存")
def adjust_inventory(
    silo_id: int, 
    record: InventoryRecordCreate,
    db: Session = Depends(get_db)
):
    """
    调整料仓库存（入库、出库或调整）
    - **silo_id**: 料仓ID
    - **record**: 库存变更记录信息
    """
    if record.change_type not in ["入库", "出库", "调整"]:
        raise HTTPException(status_code=400, detail="变更类型必须是：入库、出库、调整")
    
    if record.change_type == "调整":
        if record.quantity < 0:
            raise HTTPException(status_code=400, detail="调整数量不能为负数")
    
    silo = silo_crud.update_current_level(
        db, 
        silo_id=record.silo_id,
        quantity=record.quantity,
        change_type=record.change_type,
        reason=record.reason,
        operator=record.operator
    )
    
    if silo is None:
        raise HTTPException(status_code=404, detail="料仓不存在")
    
    return silo

@router.get("/inventory/records", response_model=List[InventoryRecordResponse], summary="获取库存记录列表")
def get_inventory_records(
    silo_id: Optional[int] = Query(None, description="料仓ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    获取库存记录列表
    - **silo_id**: 料仓ID（可选，不传则返回所有料仓记录）
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    if silo_id:
        return inventory_record_crud.get_by_silo(db, silo_id, skip=skip, limit=limit)
    return inventory_record_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/inventory/low-alert", response_model=List[LowInventoryAlert], summary="获取低库存预警列表")
def get_low_inventory_alert(db: Session = Depends(get_db)):
    """
    获取所有低库存预警的料仓列表
    """
    silos = silo_crud.get_low_inventory(db)
    alerts = []
    for silo in silos:
        percentage = (silo.current_level / silo.capacity) * 100 if silo.capacity > 0 else 0
        alerts.append(LowInventoryAlert(
            silo_id=silo.id,
            silo_name=silo.name,
            material_type=silo.material_type,
            current_level=silo.current_level,
            capacity=silo.capacity,
            min_threshold=silo.min_threshold,
            percentage=round(percentage, 2)
        ))
    return alerts

@router.get("/inventory/by-material", response_model=List[SiloResponse], summary="按物料类型获取料仓")
def get_silos_by_material(material_type: str, db: Session = Depends(get_db)):
    """
    按物料类型获取料仓列表
    - **material_type**: 物料类型，如：水泥、砂石、粉煤灰、外加剂等
    """
    return silo_crud.get_by_material_type(db, material_type)

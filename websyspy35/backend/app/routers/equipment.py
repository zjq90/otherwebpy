from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.equipment import Equipment, Sensor
from app.schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    SensorCreate, SensorUpdate, SensorResponse
)

router = APIRouter(
    prefix="/api/equipment",
    tags=["设备档案管理"]
)


@router.get("/", response_model=List[EquipmentResponse], summary="获取设备列表")
def get_equipment_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最大记录数"),
    equipment_type: Optional[str] = Query(None, description="设备类型筛选"),
    status: Optional[str] = Query(None, description="设备状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（设备编号、名称）"),
    db: Session = Depends(get_db)
):
    """
    分页获取设备列表，支持筛选和搜索
    """
    query = db.query(Equipment)
    
    # 设备类型筛选
    if equipment_type:
        query = query.filter(Equipment.equipment_type == equipment_type)
    
    # 状态筛选
    if status:
        query = query.filter(Equipment.status == status)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Equipment.equipment_code.contains(keyword)) |
            (Equipment.name.contains(keyword))
        )
    
    # 按创建时间倒序排列
    query = query.order_by(Equipment.created_at.desc())
    
    # 分页
    equipments = query.offset(skip).limit(limit).all()
    
    return equipments


@router.get("/{equipment_id}", response_model=EquipmentResponse, summary="获取设备详情")
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取设备详情
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail=f"设备ID {equipment_id} 不存在")
    
    return equipment


@router.post("/", response_model=EquipmentResponse, summary="创建设备")
def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db)
):
    """
    创建新设备档案
    """
    # 检查设备编号是否已存在
    existing = db.query(Equipment).filter(
        Equipment.equipment_code == equipment.equipment_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"设备编号 {equipment.equipment_code} 已存在"
        )
    
    # 创建设备
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    
    return db_equipment


@router.put("/{equipment_id}", response_model=EquipmentResponse, summary="更新设备")
def update_equipment(
    equipment_id: int,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    """
    更新设备信息
    """
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    
    if not db_equipment:
        raise HTTPException(status_code=404, detail=f"设备ID {equipment_id} 不存在")
    
    # 检查设备编号是否被其他设备使用
    update_data = equipment.model_dump(exclude_unset=True)
    if "equipment_code" in update_data:
        existing = db.query(Equipment).filter(
            Equipment.equipment_code == update_data["equipment_code"],
            Equipment.id != equipment_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"设备编号 {update_data['equipment_code']} 已被其他设备使用"
            )
    
    # 更新设备信息
    for key, value in update_data.items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    
    return db_equipment


@router.delete("/{equipment_id}", summary="删除设备")
def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """
    删除设备档案
    """
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    
    if not db_equipment:
        raise HTTPException(status_code=404, detail=f"设备ID {equipment_id} 不存在")
    
    db.delete(db_equipment)
    db.commit()
    
    return {"message": f"设备ID {equipment_id} 已删除", "success": True}


@router.get("/types/all", summary="获取所有设备类型")
def get_equipment_types(db: Session = Depends(get_db)):
    """
    获取所有设备类型列表（用于下拉选择）
    """
    types = db.query(Equipment.equipment_type).distinct().all()
    return {"types": [t[0] for t in types]}


# ==================== 传感器相关路由 ====================

@router.get("/sensors/", response_model=List[SensorResponse], summary="获取传感器列表")
def get_sensor_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    equipment_id: Optional[int] = Query(None, description="设备ID筛选"),
    sensor_type: Optional[str] = Query(None, description="传感器类型筛选"),
    db: Session = Depends(get_db)
):
    """
    获取传感器列表
    """
    query = db.query(Sensor)
    
    if equipment_id:
        query = query.filter(Sensor.equipment_id == equipment_id)
    
    if sensor_type:
        query = query.filter(Sensor.sensor_type == sensor_type)
    
    sensors = query.offset(skip).limit(limit).all()
    return sensors


@router.get("/sensors/{sensor_id}", response_model=SensorResponse, summary="获取传感器详情")
def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """
    获取传感器详情
    """
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"传感器ID {sensor_id} 不存在")
    return sensor


@router.post("/sensors/", response_model=SensorResponse, summary="创建传感器")
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """
    创建传感器
    """
    # 检查传感器编号是否已存在
    existing = db.query(Sensor).filter(
        Sensor.sensor_code == sensor.sensor_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"传感器编号 {sensor.sensor_code} 已存在"
        )
    
    # 检查设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == sensor.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=400,
            detail=f"设备ID {sensor.equipment_id} 不存在"
        )
    
    db_sensor = Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor


@router.put("/sensors/{sensor_id}", response_model=SensorResponse, summary="更新传感器")
def update_sensor(
    sensor_id: int,
    sensor: SensorUpdate,
    db: Session = Depends(get_db)
):
    """
    更新传感器信息
    """
    db_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    
    if not db_sensor:
        raise HTTPException(status_code=404, detail=f"传感器ID {sensor_id} 不存在")
    
    update_data = sensor.model_dump(exclude_unset=True)
    
    # 检查设备是否存在（如果更新了设备ID）
    if "equipment_id" in update_data:
        equipment = db.query(Equipment).filter(
            Equipment.id == update_data["equipment_id"]
        ).first()
        if not equipment:
            raise HTTPException(
                status_code=400,
                detail=f"设备ID {update_data['equipment_id']} 不存在"
            )
    
    for key, value in update_data.items():
        setattr(db_sensor, key, value)
    
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor


@router.delete("/sensors/{sensor_id}", summary="删除传感器")
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """
    删除传感器
    """
    db_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    
    if not db_sensor:
        raise HTTPException(status_code=404, detail=f"传感器ID {sensor_id} 不存在")
    
    db.delete(db_sensor)
    db.commit()
    
    return {"message": f"传感器ID {sensor_id} 已删除", "success": True}

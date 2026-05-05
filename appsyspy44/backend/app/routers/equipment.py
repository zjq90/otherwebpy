from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    EquipmentRuntimeCreate, EquipmentRuntimeUpdate, EquipmentRuntimeResponse,
    EquipmentFaultCreate, EquipmentFaultUpdate, EquipmentFaultResponse,
    EquipmentMaintenanceCreate, EquipmentMaintenanceUpdate, EquipmentMaintenanceResponse,
    EquipmentOperatingRateResponse, MaintenanceRateResponse
)
from app.schemas.common import ChartResponse
from app.models.equipment import Equipment, EquipmentRuntime, EquipmentFault, EquipmentMaintenance
from app.crud.equipment_crud import EquipmentCRUD

router = APIRouter()

@router.get("/equipment", response_model=List[EquipmentResponse])
def get_equipment_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return EquipmentCRUD.get_all(db, skip=skip, limit=limit)

@router.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = EquipmentCRUD.get_by_id(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    return equipment

@router.post("/equipment", response_model=EquipmentResponse)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    existing = EquipmentCRUD.get_by_no(db, equipment.equipment_no)
    if existing:
        raise HTTPException(status_code=400, detail="设备编号已存在")
    return EquipmentCRUD.create(db, equipment)

@router.put("/equipment/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(equipment_id: int, equipment: EquipmentUpdate, db: Session = Depends(get_db)):
    db_equipment = EquipmentCRUD.update(db, equipment_id, equipment)
    if not db_equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    return db_equipment

@router.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    success = EquipmentCRUD.delete(db, equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="设备不存在")
    return {"message": "删除成功"}

@router.get("/runtime", response_model=List[EquipmentRuntimeResponse])
def get_runtime_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(EquipmentRuntime).order_by(EquipmentRuntime.record_date.desc()).offset(skip).limit(limit).all()

@router.post("/runtime", response_model=EquipmentRuntimeResponse)
def create_runtime(data: EquipmentRuntimeCreate, db: Session = Depends(get_db)):
    db_data = EquipmentRuntime(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/faults", response_model=List[EquipmentFaultResponse])
def get_faults_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(EquipmentFault).order_by(EquipmentFault.fault_date.desc()).offset(skip).limit(limit).all()

@router.post("/faults", response_model=EquipmentFaultResponse)
def create_fault(data: EquipmentFaultCreate, db: Session = Depends(get_db)):
    db_data = EquipmentFault(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/maintenance", response_model=List[EquipmentMaintenanceResponse])
def get_maintenance_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(EquipmentMaintenance).order_by(EquipmentMaintenance.plan_date.desc()).offset(skip).limit(limit).all()

@router.post("/maintenance", response_model=EquipmentMaintenanceResponse)
def create_maintenance(data: EquipmentMaintenanceCreate, db: Session = Depends(get_db)):
    db_data = EquipmentMaintenance(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/operating-rate-chart", response_model=ChartResponse)
def get_operating_rate_chart(
    chart_type: str = Query("line", description="图表类型：line或bar"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    runtime_data = db.query(EquipmentRuntime, Equipment).join(
        Equipment, Equipment.id == EquipmentRuntime.equipment_id
    ).filter(
        EquipmentRuntime.record_date >= start_date,
        EquipmentRuntime.record_date <= end_date
    ).order_by(EquipmentRuntime.record_date).all()
    
    daily_stats = {}
    for runtime, equipment in runtime_data:
        day_key = runtime.record_date.isoformat()
        if day_key not in daily_stats:
            daily_stats[day_key] = {
                "planned": 0,
                "actual": 0,
                "downtime": 0
            }
        daily_stats[day_key]["planned"] += runtime.planned_runtime
        daily_stats[day_key]["actual"] += runtime.actual_runtime
        daily_stats[day_key]["downtime"] += runtime.downtime
    
    sorted_dates = sorted(daily_stats.keys())
    
    x_axis_data = [d for d in sorted_dates]
    operating_rates = []
    for d in sorted_dates:
        stats = daily_stats[d]
        rate = 0.0
        if stats["planned"] > 0:
            rate = round((stats["actual"] / stats["planned"]) * 100, 2)
        operating_rates.append(rate)
    
    return {
        "chart_type": chart_type,
        "title": "设备开机率趋势",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "开机率(%)", "data": operating_rates, "type": chart_type}
        ]
    }

@router.get("/downtime-chart", response_model=ChartResponse)
def get_downtime_chart(
    chart_type: str = Query("bar", description="图表类型：bar或line"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    faults = db.query(EquipmentFault, Equipment).join(
        Equipment, Equipment.id == EquipmentFault.equipment_id
    ).filter(
        EquipmentFault.fault_date >= start_date,
        EquipmentFault.fault_date <= end_date
    ).order_by(EquipmentFault.fault_date).all()
    
    daily_stats = {}
    for fault, equipment in faults:
        day_key = fault.fault_date.isoformat()
        if day_key not in daily_stats:
            daily_stats[day_key] = 0
        daily_stats[day_key] += fault.downtime_duration
    
    sorted_dates = sorted(daily_stats.keys())
    
    x_axis_data = [d for d in sorted_dates]
    downtime_data = [daily_stats[d] for d in sorted_dates]
    
    return {
        "chart_type": chart_type,
        "title": "设备故障停机时长",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "停机时长(小时)", "data": downtime_data, "type": chart_type}
        ]
    }

@router.get("/maintenance-rate-chart", response_model=ChartResponse)
def get_maintenance_rate_chart(
    chart_type: str = Query("line", description="图表类型：line或bar"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    maintenance = db.query(EquipmentMaintenance).filter(
        EquipmentMaintenance.plan_date >= start_date,
        EquipmentMaintenance.plan_date <= end_date
    ).order_by(EquipmentMaintenance.plan_date).all()
    
    daily_stats = {}
    for m in maintenance:
        day_key = m.plan_date.isoformat()
        if day_key not in daily_stats:
            daily_stats[day_key] = {
                "planned": 0,
                "completed": 0
            }
        daily_stats[day_key]["planned"] += 1
        if m.is_completed:
            daily_stats[day_key]["completed"] += 1
    
    sorted_dates = sorted(daily_stats.keys())
    
    x_axis_data = [d for d in sorted_dates]
    completion_rates = []
    for d in sorted_dates:
        stats = daily_stats[d]
        rate = 0.0
        if stats["planned"] > 0:
            rate = round((stats["completed"] / stats["planned"]) * 100, 2)
        completion_rates.append(rate)
    
    return {
        "chart_type": chart_type,
        "title": "设备保养完成率",
        "x_axis_data": x_axis_data,
        "series": [
            {"name": "完成率(%)", "data": completion_rates, "type": chart_type}
        ]
    }

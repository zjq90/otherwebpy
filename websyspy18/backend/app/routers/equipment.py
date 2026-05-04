"""
工程维保管理模块 - API路由
包含设备台账、巡检计划、保养计划、故障维修记录等API接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    InspectionPlanCreate, InspectionPlanUpdate, InspectionPlanResponse,
    InspectionRecordCreate, InspectionRecordResponse,
    MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlanResponse,
    MaintenanceRecordCreate, MaintenanceRecordResponse,
    FaultRecordCreate, FaultRecordUpdate, FaultRecordResponse,
    CostStatisticsResponse, EquipmentStatusStatistics, FaultTypeStatistics
)
from app.crud import equipment as crud_equipment

router = APIRouter()

# ==================== 设备台账 API ====================

@router.post("/equipment/", response_model=EquipmentResponse, tags=["设备台账"])
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """
    创建设备台账
    
    - **equipment**: 设备信息对象
    
    返回: 创建的设备信息
    """
    db_equipment = crud_equipment.equipment.get_by_code(db, code=equipment.code)
    if db_equipment:
        raise HTTPException(status_code=400, detail="设备编号已存在")
    return crud_equipment.equipment.create(db=db, obj_in=equipment)

@router.get("/equipment/", response_model=List[EquipmentResponse], tags=["设备台账"])
def read_equipment_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备台账列表（支持分页和筛选）
    
    - **skip**: 跳过记录数
    - **limit**: 返回最大记录数
    - **category**: 按设备类别筛选
    - **status**: 按设备状态筛选
    - **keyword**: 关键词搜索（名称或编号）
    
    返回: 设备列表
    """
    if keyword:
        return crud_equipment.equipment.search(db, keyword=keyword, skip=skip, limit=limit)
    if category:
        return crud_equipment.equipment.get_by_category(db, category=category, skip=skip, limit=limit)
    if status:
        return crud_equipment.equipment.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_equipment.equipment.get_multi(db, skip=skip, limit=limit)

@router.get("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["设备台账"])
def read_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个设备信息
    
    - **equipment_id**: 设备ID
    
    返回: 设备详细信息
    """
    db_equipment = crud_equipment.equipment.get(db, id=equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return db_equipment

@router.put("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["设备台账"])
def update_equipment(equipment_id: int, equipment: EquipmentUpdate, db: Session = Depends(get_db)):
    """
    更新设备信息
    
    - **equipment_id**: 设备ID
    - **equipment**: 更新的设备信息
    
    返回: 更新后的设备信息
    """
    db_equipment = crud_equipment.equipment.get(db, id=equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return crud_equipment.equipment.update(db, db_obj=db_equipment, obj_in=equipment)

@router.delete("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["设备台账"])
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """
    删除设备
    
    - **equipment_id**: 设备ID
    
    返回: 被删除的设备信息
    """
    db_equipment = crud_equipment.equipment.get(db, id=equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    return crud_equipment.equipment.remove(db, id=equipment_id)

@router.get("/statistics/equipment/status", response_model=List[EquipmentStatusStatistics], tags=["设备统计"])
def get_equipment_status_statistics(db: Session = Depends(get_db)):
    """
    获取设备状态统计
    
    返回: 各状态设备数量统计
    """
    return crud_equipment.equipment.get_status_statistics(db)

# ==================== 巡检计划 API ====================

@router.post("/inspection-plans/", response_model=InspectionPlanResponse, tags=["巡检计划"])
def create_inspection_plan(plan: InspectionPlanCreate, db: Session = Depends(get_db)):
    """
    创建巡检计划
    """
    return crud_equipment.inspection_plan.create(db=db, obj_in=plan)

@router.get("/inspection-plans/", response_model=List[InspectionPlanResponse], tags=["巡检计划"])
def read_inspection_plans(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取巡检计划列表
    """
    if equipment_id:
        return crud_equipment.inspection_plan.get_by_equipment(db, equipment_id=equipment_id, skip=skip, limit=limit)
    if status:
        return crud_equipment.inspection_plan.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_equipment.inspection_plan.get_multi(db, skip=skip, limit=limit)

@router.get("/inspection-plans/{plan_id}", response_model=InspectionPlanResponse, tags=["巡检计划"])
def read_inspection_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    获取单个巡检计划
    """
    db_plan = crud_equipment.inspection_plan.get(db, id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="巡检计划不存在")
    return db_plan

@router.put("/inspection-plans/{plan_id}", response_model=InspectionPlanResponse, tags=["巡检计划"])
def update_inspection_plan(plan_id: int, plan: InspectionPlanUpdate, db: Session = Depends(get_db)):
    """
    更新巡检计划
    """
    db_plan = crud_equipment.inspection_plan.get(db, id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="巡检计划不存在")
    return crud_equipment.inspection_plan.update(db, db_obj=db_plan, obj_in=plan)

@router.delete("/inspection-plans/{plan_id}", response_model=InspectionPlanResponse, tags=["巡检计划"])
def delete_inspection_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    删除巡检计划
    """
    db_plan = crud_equipment.inspection_plan.get(db, id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="巡检计划不存在")
    return crud_equipment.inspection_plan.remove(db, id=plan_id)

# ==================== 巡检记录 API ====================

@router.post("/inspection-records/", response_model=InspectionRecordResponse, tags=["巡检记录"])
def create_inspection_record(record: InspectionRecordCreate, db: Session = Depends(get_db)):
    """
    创建巡检记录
    """
    from app.models.equipment import InspectionRecord as ModelInspectionRecord
    from fastapi.encoders import jsonable_encoder
    
    obj_in_data = jsonable_encoder(record)
    db_obj = ModelInspectionRecord(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/inspection-records/", response_model=List[InspectionRecordResponse], tags=["巡检记录"])
def read_inspection_records(
    skip: int = 0,
    limit: int = 100,
    plan_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取巡检记录列表
    """
    from app.models.equipment import InspectionRecord as ModelInspectionRecord
    
    if plan_id:
        return db.query(ModelInspectionRecord).filter(ModelInspectionRecord.plan_id == plan_id).offset(skip).limit(limit).all()
    return db.query(ModelInspectionRecord).offset(skip).limit(limit).all()

# ==================== 保养计划 API ====================

@router.post("/maintenance-plans/", response_model=MaintenancePlanResponse, tags=["保养计划"])
def create_maintenance_plan(plan: MaintenancePlanCreate, db: Session = Depends(get_db)):
    """
    创建保养计划
    """
    return crud_equipment.maintenance_plan.create(db=db, obj_in=plan)

@router.get("/maintenance-plans/", response_model=List[MaintenancePlanResponse], tags=["保养计划"])
def read_maintenance_plans(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取保养计划列表
    """
    if equipment_id:
        return crud_equipment.maintenance_plan.get_by_equipment(db, equipment_id=equipment_id, skip=skip, limit=limit)
    if status:
        return crud_equipment.maintenance_plan.get_multi(db, skip=skip, limit=limit)
    return crud_equipment.maintenance_plan.get_multi(db, skip=skip, limit=limit)

@router.get("/maintenance-plans/{plan_id}", response_model=MaintenancePlanResponse, tags=["保养计划"])
def read_maintenance_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    获取单个保养计划
    """
    db_plan = crud_equipment.maintenance_plan.get(db, id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="保养计划不存在")
    return db_plan

@router.put("/maintenance-plans/{plan_id}", response_model=MaintenancePlanResponse, tags=["保养计划"])
def update_maintenance_plan(plan_id: int, plan: MaintenancePlanUpdate, db: Session = Depends(get_db)):
    """
    更新保养计划
    """
    db_plan = crud_equipment.maintenance_plan.get(db, id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="保养计划不存在")
    return crud_equipment.maintenance_plan.update(db, db_obj=db_plan, obj_in=plan)

@router.delete("/maintenance-plans/{plan_id}", response_model=MaintenancePlanResponse, tags=["保养计划"])
def delete_maintenance_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    删除保养计划
    """
    db_plan = crud_equipment.maintenance_plan.get(db, id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="保养计划不存在")
    return crud_equipment.maintenance_plan.remove(db, id=plan_id)

# ==================== 保养记录 API ====================

@router.post("/maintenance-records/", response_model=MaintenanceRecordResponse, tags=["保养记录"])
def create_maintenance_record(record: MaintenanceRecordCreate, db: Session = Depends(get_db)):
    """
    创建保养记录
    """
    from app.models.equipment import MaintenanceRecord as ModelMaintenanceRecord
    from fastapi.encoders import jsonable_encoder
    
    obj_in_data = jsonable_encoder(record)
    db_obj = ModelMaintenanceRecord(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/maintenance-records/", response_model=List[MaintenanceRecordResponse], tags=["保养记录"])
def read_maintenance_records(
    skip: int = 0,
    limit: int = 100,
    plan_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取保养记录列表
    """
    from app.models.equipment import MaintenanceRecord as ModelMaintenanceRecord
    
    if plan_id:
        return db.query(ModelMaintenanceRecord).filter(ModelMaintenanceRecord.plan_id == plan_id).offset(skip).limit(limit).all()
    return db.query(ModelMaintenanceRecord).offset(skip).limit(limit).all()

# ==================== 故障维修记录 API ====================

@router.post("/fault-records/", response_model=FaultRecordResponse, tags=["故障维修"])
def create_fault_record(record: FaultRecordCreate, db: Session = Depends(get_db)):
    """
    创建故障维修记录
    """
    db_record = db.query(crud_equipment.fault_record.model).filter(
        crud_equipment.fault_record.model.fault_code == record.fault_code
    ).first()
    if db_record:
        raise HTTPException(status_code=400, detail="故障编号已存在")
    return crud_equipment.fault_record.create(db=db, obj_in=record)

@router.get("/fault-records/", response_model=List[FaultRecordResponse], tags=["故障维修"])
def read_fault_records(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取故障维修记录列表
    """
    if equipment_id:
        return crud_equipment.fault_record.get_by_equipment(db, equipment_id=equipment_id, skip=skip, limit=limit)
    if status:
        return crud_equipment.fault_record.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_equipment.fault_record.get_multi(db, skip=skip, limit=limit)

@router.get("/fault-records/{record_id}", response_model=FaultRecordResponse, tags=["故障维修"])
def read_fault_record(record_id: int, db: Session = Depends(get_db)):
    """
    获取单个故障维修记录
    """
    db_record = crud_equipment.fault_record.get(db, id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="故障记录不存在")
    return db_record

@router.put("/fault-records/{record_id}", response_model=FaultRecordResponse, tags=["故障维修"])
def update_fault_record(record_id: int, record: FaultRecordUpdate, db: Session = Depends(get_db)):
    """
    更新故障维修记录
    """
    db_record = crud_equipment.fault_record.get(db, id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="故障记录不存在")
    return crud_equipment.fault_record.update(db, db_obj=db_record, obj_in=record)

@router.delete("/fault-records/{record_id}", response_model=FaultRecordResponse, tags=["故障维修"])
def delete_fault_record(record_id: int, db: Session = Depends(get_db)):
    """
    删除故障维修记录
    """
    db_record = crud_equipment.fault_record.get(db, id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="故障记录不存在")
    return crud_equipment.fault_record.remove(db, id=record_id)

# ==================== 费用统计 API ====================

@router.get("/statistics/cost", response_model=CostStatisticsResponse, tags=["费用统计"])
def get_cost_statistics(db: Session = Depends(get_db)):
    """
    获取费用统计信息
    包含故障维修总费用、保养总费用等
    """
    return crud_equipment.fault_record.get_cost_statistics(db)

@router.get("/statistics/fault-type", response_model=List[FaultTypeStatistics], tags=["费用统计"])
def get_fault_type_statistics(db: Session = Depends(get_db)):
    """
    获取故障类型统计
    按故障类型统计数量和费用
    """
    return crud_equipment.fault_record.get_fault_type_statistics(db)

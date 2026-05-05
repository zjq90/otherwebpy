"""
生产数据分析模块的API路由
包含设备管理、生产记录、设备利用率、能耗指标的增删改查和统计分析接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date, datetime, timedelta

from ..database import get_db
from ..models import (
    Equipment, ProductionRecord, EquipmentUtilization, EnergyConsumption
)
from ..schemas import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    ProductionRecordCreate, ProductionRecordUpdate, ProductionRecordResponse,
    EquipmentUtilizationCreate, EquipmentUtilizationUpdate, EquipmentUtilizationResponse,
    EnergyConsumptionCreate, EnergyConsumptionUpdate, EnergyConsumptionResponse,
    DailyProductionStats, MonthlyProductionStats, EquipmentUtilizationStats, EnergyConsumptionStats
)

router = APIRouter(prefix="/api/production", tags=["生产数据分析"])


# ============ 设备管理接口 ============

@router.post("/equipment/", response_model=EquipmentResponse, summary="创建设备")
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """
    创建设备信息
    - **equipment_code**: 设备编号（必填，唯一）
    - **equipment_name**: 设备名称（必填）
    - **equipment_type**: 设备类型
    - **specification**: 规格型号
    - **max_capacity**: 最大产能
    - **manufacturer**: 生产厂家
    - **purchase_date**: 购买日期
    - **status**: 设备状态（正常/维修中/停用）
    """
    # 检查设备编号是否已存在
    existing = db.query(Equipment).filter(Equipment.equipment_code == equipment.equipment_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="设备编号已存在")
    
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.get("/equipment/", response_model=List[EquipmentResponse], summary="获取设备列表")
def get_equipment_list(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    status: Optional[str] = Query(None, description="设备状态筛选"),
    equipment_type: Optional[str] = Query(None, description="设备类型筛选"),
    db: Session = Depends(get_db)
):
    """
    获取设备列表，支持分页和条件筛选
    """
    query = db.query(Equipment)
    if status:
        query = query.filter(Equipment.status == status)
    if equipment_type:
        query = query.filter(Equipment.equipment_type == equipment_type)
    
    equipments = query.order_by(Equipment.id.desc()).offset(skip).limit(limit).all()
    return equipments


@router.get("/equipment/{equipment_id}", response_model=EquipmentResponse, summary="获取单个设备")
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取设备详情
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    return equipment


@router.put("/equipment/{equipment_id}", response_model=EquipmentResponse, summary="更新设备")
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
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新字段
    update_data = equipment.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.delete("/equipment/{equipment_id}", summary="删除设备")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """
    删除设备
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    db.delete(equipment)
    db.commit()
    return {"message": "设备删除成功", "id": equipment_id}


# ============ 生产记录接口 ============

@router.post("/records/", response_model=ProductionRecordResponse, summary="创建生产记录")
def create_production_record(record: ProductionRecordCreate, db: Session = Depends(get_db)):
    """
    创建生产记录
    """
    # 检查日期是否已存在
    existing = db.query(ProductionRecord).filter(ProductionRecord.record_date == record.record_date).first()
    if existing:
        raise HTTPException(status_code=400, detail="该日期的生产记录已存在")
    
    db_record = ProductionRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/records/", response_model=List[ProductionRecordResponse], summary="获取生产记录列表")
def get_production_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取生产记录列表，支持日期范围筛选
    """
    query = db.query(ProductionRecord)
    if start_date:
        query = query.filter(ProductionRecord.record_date >= start_date)
    if end_date:
        query = query.filter(ProductionRecord.record_date <= end_date)
    
    records = query.order_by(ProductionRecord.record_date.desc()).offset(skip).limit(limit).all()
    return records


@router.get("/records/{record_id}", response_model=ProductionRecordResponse, summary="获取单个生产记录")
def get_production_record(record_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产记录详情
    """
    record = db.query(ProductionRecord).filter(ProductionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="生产记录不存在")
    return record


@router.put("/records/{record_id}", response_model=ProductionRecordResponse, summary="更新生产记录")
def update_production_record(
    record_id: int,
    record: ProductionRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新生产记录
    """
    db_record = db.query(ProductionRecord).filter(ProductionRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="生产记录不存在")
    
    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/records/{record_id}", summary="删除生产记录")
def delete_production_record(record_id: int, db: Session = Depends(get_db)):
    """
    删除生产记录
    """
    record = db.query(ProductionRecord).filter(ProductionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="生产记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "生产记录删除成功", "id": record_id}


# ============ 设备利用率接口 ============

@router.post("/utilization/", response_model=EquipmentUtilizationResponse, summary="创建设备利用率记录")
def create_utilization(utilization: EquipmentUtilizationCreate, db: Session = Depends(get_db)):
    """
    创建设备利用率记录
    自动计算设备利用率：actual_working_hours / total_available_hours * 100
    """
    # 检查设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == utilization.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 计算利用率
    data = utilization.model_dump()
    if data.get("total_available_hours", 0) > 0:
        data["utilization_rate"] = (data["actual_working_hours"] / data["total_available_hours"]) * 100
    
    db_utilization = EquipmentUtilization(**data)
    db.add(db_utilization)
    db.commit()
    db.refresh(db_utilization)
    
    # 添加设备名称到响应
    result = EquipmentUtilizationResponse.model_validate(db_utilization)
    result.equipment_name = equipment.equipment_name
    return result


@router.get("/utilization/", response_model=List[EquipmentUtilizationResponse], summary="获取设备利用率列表")
def get_utilization_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    equipment_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取设备利用率记录列表
    """
    query = db.query(EquipmentUtilization).join(Equipment)
    if equipment_id:
        query = query.filter(EquipmentUtilization.equipment_id == equipment_id)
    if start_date:
        query = query.filter(EquipmentUtilization.record_date >= start_date)
    if end_date:
        query = query.filter(EquipmentUtilization.record_date <= end_date)
    
    records = query.order_by(EquipmentUtilization.record_date.desc()).offset(skip).limit(limit).all()
    
    # 添加设备名称
    results = []
    for record in records:
        result = EquipmentUtilizationResponse.model_validate(record)
        result.equipment_name = record.equipment.equipment_name if record.equipment else None
        results.append(result)
    return results


@router.put("/utilization/{utilization_id}", response_model=EquipmentUtilizationResponse, summary="更新设备利用率记录")
def update_utilization(
    utilization_id: int,
    utilization: EquipmentUtilizationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新设备利用率记录
    """
    db_record = db.query(EquipmentUtilization).filter(EquipmentUtilization.id == utilization_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="设备利用率记录不存在")
    
    update_data = utilization.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新计算利用率
    if db_record.total_available_hours > 0:
        db_record.utilization_rate = (db_record.actual_working_hours / db_record.total_available_hours) * 100
    
    db.commit()
    db.refresh(db_record)
    
    result = EquipmentUtilizationResponse.model_validate(db_record)
    result.equipment_name = db_record.equipment.equipment_name if db_record.equipment else None
    return result


@router.delete("/utilization/{utilization_id}", summary="删除设备利用率记录")
def delete_utilization(utilization_id: int, db: Session = Depends(get_db)):
    """
    删除设备利用率记录
    """
    record = db.query(EquipmentUtilization).filter(EquipmentUtilization.id == utilization_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="设备利用率记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "设备利用率记录删除成功", "id": utilization_id}


# ============ 能耗指标接口 ============

@router.post("/energy/", response_model=EnergyConsumptionResponse, summary="创建能耗记录")
def create_energy(energy: EnergyConsumptionCreate, db: Session = Depends(get_db)):
    """
    创建能耗记录
    """
    # 如果有关联设备，检查设备是否存在
    if energy.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == energy.equipment_id).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="设备不存在")
    
    db_energy = EnergyConsumption(**energy.model_dump())
    db.add(db_energy)
    db.commit()
    db.refresh(db_energy)
    
    result = EnergyConsumptionResponse.model_validate(db_energy)
    if db_energy.equipment:
        result.equipment_name = db_energy.equipment.equipment_name
    return result


@router.get("/energy/", response_model=List[EnergyConsumptionResponse], summary="获取能耗记录列表")
def get_energy_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    energy_type: Optional[str] = Query(None),
    equipment_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取能耗记录列表
    """
    query = db.query(EnergyConsumption)
    if energy_type:
        query = query.filter(EnergyConsumption.energy_type == energy_type)
    if equipment_id:
        query = query.filter(EnergyConsumption.equipment_id == equipment_id)
    if start_date:
        query = query.filter(EnergyConsumption.record_date >= start_date)
    if end_date:
        query = query.filter(EnergyConsumption.record_date <= end_date)
    
    records = query.order_by(EnergyConsumption.record_date.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = EnergyConsumptionResponse.model_validate(record)
        if record.equipment:
            result.equipment_name = record.equipment.equipment_name
        results.append(result)
    return results


@router.put("/energy/{energy_id}", response_model=EnergyConsumptionResponse, summary="更新能耗记录")
def update_energy(
    energy_id: int,
    energy: EnergyConsumptionUpdate,
    db: Session = Depends(get_db)
):
    """
    更新能耗记录
    """
    db_record = db.query(EnergyConsumption).filter(EnergyConsumption.id == energy_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="能耗记录不存在")
    
    update_data = energy.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    
    result = EnergyConsumptionResponse.model_validate(db_record)
    if db_record.equipment:
        result.equipment_name = db_record.equipment.equipment_name
    return result


@router.delete("/energy/{energy_id}", summary="删除能耗记录")
def delete_energy(energy_id: int, db: Session = Depends(get_db)):
    """
    删除能耗记录
    """
    record = db.query(EnergyConsumption).filter(EnergyConsumption.id == energy_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="能耗记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "能耗记录删除成功", "id": energy_id}


# ============ 统计分析接口 ============

@router.get("/stats/daily/", response_model=List[DailyProductionStats], summary="日产量统计")
def get_daily_production_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    日产量统计分析
    计算每日的总产量、合格产量、合格率、批次数量、工作时长
    """
    query = db.query(ProductionRecord)
    if start_date:
        query = query.filter(ProductionRecord.record_date >= start_date)
    if end_date:
        query = query.filter(ProductionRecord.record_date <= end_date)
    
    records = query.order_by(ProductionRecord.record_date).all()
    
    stats = []
    for record in records:
        qualified_rate = (record.qualified_production / record.total_production * 100) if record.total_production > 0 else 0
        stats.append(DailyProductionStats(
            record_date=record.record_date,
            total_production=record.total_production,
            qualified_production=record.qualified_production,
            qualified_rate=qualified_rate,
            batch_count=record.batch_count,
            working_hours=record.working_hours
        ))
    return stats


@router.get("/stats/monthly/", response_model=List[MonthlyProductionStats], summary="月产量统计")
def get_monthly_production_stats(
    year: Optional[int] = Query(None, description="年份"),
    db: Session = Depends(get_db)
):
    """
    月产量统计分析
    按月汇总生产数据
    """
    query = db.query(
        extract('year', ProductionRecord.record_date).label('year'),
        extract('month', ProductionRecord.record_date).label('month'),
        func.sum(ProductionRecord.total_production).label('total_production'),
        func.sum(ProductionRecord.qualified_production).label('qualified_production'),
        func.sum(ProductionRecord.batch_count).label('total_batches'),
        func.sum(ProductionRecord.working_hours).label('total_working_hours')
    )
    
    if year:
        query = query.filter(extract('year', ProductionRecord.record_date) == year)
    
    results = query.group_by('year', 'month').order_by('year', 'month').all()
    
    stats = []
    for result in results:
        qualified_rate = (result.qualified_production / result.total_production * 100) if result.total_production > 0 else 0
        stats.append(MonthlyProductionStats(
            year=int(result.year),
            month=int(result.month),
            total_production=result.total_production or 0,
            qualified_production=result.qualified_production or 0,
            qualified_rate=qualified_rate,
            total_batches=int(result.total_batches or 0),
            total_working_hours=result.total_working_hours or 0
        ))
    return stats


@router.get("/stats/equipment-utilization/", response_model=List[EquipmentUtilizationStats], summary="设备利用率统计")
def get_equipment_utilization_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    设备利用率统计
    统计每台设备的总可用时长、实际工作时长、维护时长、闲置时长、平均利用率
    """
    query = db.query(
        Equipment.id.label('equipment_id'),
        Equipment.equipment_name,
        Equipment.equipment_code,
        func.sum(EquipmentUtilization.total_available_hours).label('total_available_hours'),
        func.sum(EquipmentUtilization.actual_working_hours).label('total_working_hours'),
        func.sum(EquipmentUtilization.maintenance_hours).label('total_maintenance_hours'),
        func.sum(EquipmentUtilization.idle_hours).label('total_idle_hours'),
        func.avg(EquipmentUtilization.utilization_rate).label('average_utilization_rate')
    ).join(EquipmentUtilization, Equipment.id == EquipmentUtilization.equipment_id)
    
    if start_date:
        query = query.filter(EquipmentUtilization.record_date >= start_date)
    if end_date:
        query = query.filter(EquipmentUtilization.record_date <= end_date)
    
    results = query.group_by(Equipment.id).all()
    
    stats = []
    for result in results:
        stats.append(EquipmentUtilizationStats(
            equipment_id=result.equipment_id,
            equipment_name=result.equipment_name,
            equipment_code=result.equipment_code,
            total_available_hours=result.total_available_hours or 0,
            total_working_hours=result.total_working_hours or 0,
            total_maintenance_hours=result.total_maintenance_hours or 0,
            total_idle_hours=result.total_idle_hours or 0,
            average_utilization_rate=result.average_utilization_rate or 0
        ))
    return stats


@router.get("/stats/energy/", response_model=List[EnergyConsumptionStats], summary="能耗统计")
def get_energy_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    能耗统计
    按能源类型统计总消耗量和总成本
    """
    query = db.query(
        EnergyConsumption.energy_type,
        func.sum(EnergyConsumption.consumption_amount).label('total_consumption'),
        func.sum(EnergyConsumption.cost).label('total_cost'),
        func.first(EnergyConsumption.unit).label('unit')
    )
    
    if start_date:
        query = query.filter(EnergyConsumption.record_date >= start_date)
    if end_date:
        query = query.filter(EnergyConsumption.record_date <= end_date)
    
    results = query.group_by(EnergyConsumption.energy_type).all()
    
    stats = []
    for result in results:
        stats.append(EnergyConsumptionStats(
            energy_type=result.energy_type,
            total_consumption=result.total_consumption or 0,
            total_cost=result.total_cost or 0,
            unit=result.unit or ""
        ))
    return stats

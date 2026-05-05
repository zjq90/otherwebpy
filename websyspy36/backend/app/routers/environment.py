"""
环保合规监管模块的API路由
包含监测点位管理、粉尘监测、噪音监测、废水监测、报警记录的增删改查和统计分析接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date, datetime

from ..database import get_db
from ..config import settings
from ..models import (
    MonitoringPoint, DustMonitoring, NoiseMonitoring, WastewaterMonitoring, AlarmRecord
)
from ..schemas import (
    MonitoringPointCreate, MonitoringPointUpdate, MonitoringPointResponse,
    DustMonitoringCreate, DustMonitoringUpdate, DustMonitoringResponse,
    NoiseMonitoringCreate, NoiseMonitoringUpdate, NoiseMonitoringResponse,
    WastewaterMonitoringCreate, WastewaterMonitoringUpdate, WastewaterMonitoringResponse,
    AlarmRecordCreate, AlarmRecordUpdate, AlarmRecordResponse,
    DailyDustStats, DailyNoiseStats, DailyWastewaterStats, AlarmStats
)

router = APIRouter(prefix="/api/environment", tags=["环保合规监管"])


# ============ 监测点位管理接口 ============

@router.post("/monitoring-points/", response_model=MonitoringPointResponse, summary="创建监测点位")
def create_monitoring_point(point: MonitoringPointCreate, db: Session = Depends(get_db)):
    """
    创建监测点位
    """
    # 检查点位编号是否已存在
    existing = db.query(MonitoringPoint).filter(MonitoringPoint.point_code == point.point_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="监测点位编号已存在")
    
    db_point = MonitoringPoint(**point.model_dump())
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return db_point


@router.get("/monitoring-points/", response_model=List[MonitoringPointResponse], summary="获取监测点位列表")
def get_monitoring_points(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    monitoring_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取监测点位列表，支持条件筛选
    """
    query = db.query(MonitoringPoint)
    if monitoring_type:
        query = query.filter(MonitoringPoint.monitoring_type == monitoring_type)
    if status:
        query = query.filter(MonitoringPoint.status == status)
    
    points = query.order_by(MonitoringPoint.id.desc()).offset(skip).limit(limit).all()
    return points


@router.get("/monitoring-points/{point_id}", response_model=MonitoringPointResponse, summary="获取单个监测点位")
def get_monitoring_point(point_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取监测点位详情
    """
    point = db.query(MonitoringPoint).filter(MonitoringPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="监测点位不存在")
    return point


@router.put("/monitoring-points/{point_id}", response_model=MonitoringPointResponse, summary="更新监测点位")
def update_monitoring_point(
    point_id: int,
    point: MonitoringPointUpdate,
    db: Session = Depends(get_db)
):
    """
    更新监测点位信息
    """
    db_point = db.query(MonitoringPoint).filter(MonitoringPoint.id == point_id).first()
    if not db_point:
        raise HTTPException(status_code=404, detail="监测点位不存在")
    
    update_data = point.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_point, key, value)
    
    db.commit()
    db.refresh(db_point)
    return db_point


@router.delete("/monitoring-points/{point_id}", summary="删除监测点位")
def delete_monitoring_point(point_id: int, db: Session = Depends(get_db)):
    """
    删除监测点位
    """
    point = db.query(MonitoringPoint).filter(MonitoringPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="监测点位不存在")
    
    db.delete(point)
    db.commit()
    return {"message": "监测点位删除成功", "id": point_id}


# ============ 粉尘监测接口 ============

@router.post("/dust/", response_model=DustMonitoringResponse, summary="创建粉尘监测记录")
def create_dust_monitoring(dust: DustMonitoringCreate, db: Session = Depends(get_db)):
    """
    创建粉尘监测记录
    自动检查是否超标，超标时创建报警记录
    """
    # 检查监测点位是否存在
    point = db.query(MonitoringPoint).filter(MonitoringPoint.id == dust.monitoring_point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="监测点位不存在")
    
    data = dust.model_dump()
    
    # 设置记录时间和日期
    if not data.get("record_time"):
        data["record_time"] = datetime.now()
    if not data.get("record_date"):
        data["record_date"] = data["record_time"].date()
    
    # 设置阈值
    if data.get("threshold_value", 0) <= 0:
        data["threshold_value"] = settings.DUST_THRESHOLD
    
    # 检查是否超标（以TSP浓度为准）
    data["is_over_limit"] = data.get("tsp_concentration", 0) > data["threshold_value"]
    
    db_dust = DustMonitoring(**data)
    db.add(db_dust)
    db.commit()
    db.refresh(db_dust)
    
    # 如果超标，创建报警记录
    if db_dust.is_over_limit:
        alarm_level = "一般"
        if db_dust.tsp_concentration > db_dust.threshold_value * 2:
            alarm_level = "紧急"
        elif db_dust.tsp_concentration > db_dust.threshold_value * 1.5:
            alarm_level = "重要"
        
        alarm = AlarmRecord(
            alarm_time=db_dust.record_time,
            alarm_type="粉尘超标",
            monitoring_point_id=db_dust.monitoring_point_id,
            dust_monitoring_id=db_dust.id,
            alarm_level=alarm_level,
            actual_value=db_dust.tsp_concentration,
            threshold_value=db_dust.threshold_value,
            message=f"监测点位[{point.point_name}]粉尘浓度超标，当前值：{db_dust.tsp_concentration}mg/m³，阈值：{db_dust.threshold_value}mg/m³"
        )
        db.add(alarm)
        db.commit()
    
    result = DustMonitoringResponse.model_validate(db_dust)
    result.point_name = point.point_name
    result.point_location = point.location
    return result


@router.get("/dust/", response_model=List[DustMonitoringResponse], summary="获取粉尘监测列表")
def get_dust_monitorings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    monitoring_point_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_over_limit: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取粉尘监测记录列表
    """
    query = db.query(DustMonitoring).join(MonitoringPoint)
    if monitoring_point_id:
        query = query.filter(DustMonitoring.monitoring_point_id == monitoring_point_id)
    if start_date:
        query = query.filter(DustMonitoring.record_date >= start_date)
    if end_date:
        query = query.filter(DustMonitoring.record_date <= end_date)
    if is_over_limit is not None:
        query = query.filter(DustMonitoring.is_over_limit == is_over_limit)
    
    records = query.order_by(DustMonitoring.record_time.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = DustMonitoringResponse.model_validate(record)
        if record.monitoring_point:
            result.point_name = record.monitoring_point.point_name
            result.point_location = record.monitoring_point.location
        results.append(result)
    return results


@router.put("/dust/{record_id}", response_model=DustMonitoringResponse, summary="更新粉尘监测记录")
def update_dust_monitoring(
    record_id: int,
    dust: DustMonitoringUpdate,
    db: Session = Depends(get_db)
):
    """
    更新粉尘监测记录
    """
    db_record = db.query(DustMonitoring).filter(DustMonitoring.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="粉尘监测记录不存在")
    
    update_data = dust.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新检查是否超标
    db_record.is_over_limit = db_record.tsp_concentration > db_record.threshold_value
    
    db.commit()
    db.refresh(db_record)
    
    result = DustMonitoringResponse.model_validate(db_record)
    if db_record.monitoring_point:
        result.point_name = db_record.monitoring_point.point_name
        result.point_location = db_record.monitoring_point.location
    return result


@router.delete("/dust/{record_id}", summary="删除粉尘监测记录")
def delete_dust_monitoring(record_id: int, db: Session = Depends(get_db)):
    """
    删除粉尘监测记录
    """
    record = db.query(DustMonitoring).filter(DustMonitoring.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="粉尘监测记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "粉尘监测记录删除成功", "id": record_id}


# ============ 噪音监测接口 ============

@router.post("/noise/", response_model=NoiseMonitoringResponse, summary="创建噪音监测记录")
def create_noise_monitoring(noise: NoiseMonitoringCreate, db: Session = Depends(get_db)):
    """
    创建噪音监测记录
    自动检查是否超标，超标时创建报警记录
    """
    # 检查监测点位是否存在
    point = db.query(MonitoringPoint).filter(MonitoringPoint.id == noise.monitoring_point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="监测点位不存在")
    
    data = noise.model_dump()
    
    # 设置记录时间和日期
    if not data.get("record_time"):
        data["record_time"] = datetime.now()
    if not data.get("record_date"):
        data["record_date"] = data["record_time"].date()
    
    # 设置阈值
    if data.get("threshold_value", 0) <= 0:
        data["threshold_value"] = settings.NOISE_THRESHOLD
    
    # 检查是否超标
    data["is_over_limit"] = data.get("db_value", 0) > data["threshold_value"]
    
    db_noise = NoiseMonitoring(**data)
    db.add(db_noise)
    db.commit()
    db.refresh(db_noise)
    
    # 如果超标，创建报警记录
    if db_noise.is_over_limit:
        alarm_level = "一般"
        if db_noise.db_value > db_noise.threshold_value * 1.3:
            alarm_level = "紧急"
        elif db_noise.db_value > db_noise.threshold_value * 1.15:
            alarm_level = "重要"
        
        alarm = AlarmRecord(
            alarm_time=db_noise.record_time,
            alarm_type="噪音超标",
            monitoring_point_id=db_noise.monitoring_point_id,
            noise_monitoring_id=db_noise.id,
            alarm_level=alarm_level,
            actual_value=db_noise.db_value,
            threshold_value=db_noise.threshold_value,
            message=f"监测点位[{point.point_name}]噪音超标，当前值：{db_noise.db_value}dB，阈值：{db_noise.threshold_value}dB"
        )
        db.add(alarm)
        db.commit()
    
    result = NoiseMonitoringResponse.model_validate(db_noise)
    result.point_name = point.point_name
    result.point_location = point.location
    return result


@router.get("/noise/", response_model=List[NoiseMonitoringResponse], summary="获取噪音监测列表")
def get_noise_monitorings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    monitoring_point_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_over_limit: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取噪音监测记录列表
    """
    query = db.query(NoiseMonitoring).join(MonitoringPoint)
    if monitoring_point_id:
        query = query.filter(NoiseMonitoring.monitoring_point_id == monitoring_point_id)
    if start_date:
        query = query.filter(NoiseMonitoring.record_date >= start_date)
    if end_date:
        query = query.filter(NoiseMonitoring.record_date <= end_date)
    if is_over_limit is not None:
        query = query.filter(NoiseMonitoring.is_over_limit == is_over_limit)
    
    records = query.order_by(NoiseMonitoring.record_time.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = NoiseMonitoringResponse.model_validate(record)
        if record.monitoring_point:
            result.point_name = record.monitoring_point.point_name
            result.point_location = record.monitoring_point.location
        results.append(result)
    return results


@router.put("/noise/{record_id}", response_model=NoiseMonitoringResponse, summary="更新噪音监测记录")
def update_noise_monitoring(
    record_id: int,
    noise: NoiseMonitoringUpdate,
    db: Session = Depends(get_db)
):
    """
    更新噪音监测记录
    """
    db_record = db.query(NoiseMonitoring).filter(NoiseMonitoring.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="噪音监测记录不存在")
    
    update_data = noise.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新检查是否超标
    db_record.is_over_limit = db_record.db_value > db_record.threshold_value
    
    db.commit()
    db.refresh(db_record)
    
    result = NoiseMonitoringResponse.model_validate(db_record)
    if db_record.monitoring_point:
        result.point_name = db_record.monitoring_point.point_name
        result.point_location = db_record.monitoring_point.location
    return result


@router.delete("/noise/{record_id}", summary="删除噪音监测记录")
def delete_noise_monitoring(record_id: int, db: Session = Depends(get_db)):
    """
    删除噪音监测记录
    """
    record = db.query(NoiseMonitoring).filter(NoiseMonitoring.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="噪音监测记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "噪音监测记录删除成功", "id": record_id}


# ============ 废水监测接口 ============

@router.post("/wastewater/", response_model=WastewaterMonitoringResponse, summary="创建废水监测记录")
def create_wastewater_monitoring(wastewater: WastewaterMonitoringCreate, db: Session = Depends(get_db)):
    """
    创建废水监测记录
    自动检查是否超标，超标时创建报警记录
    """
    # 检查监测点位是否存在
    point = db.query(MonitoringPoint).filter(MonitoringPoint.id == wastewater.monitoring_point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="监测点位不存在")
    
    data = wastewater.model_dump()
    
    # 设置记录时间和日期
    if not data.get("record_time"):
        data["record_time"] = datetime.now()
    if not data.get("record_date"):
        data["record_date"] = data["record_time"].date()
    
    # 设置PH阈值
    if data.get("ph_threshold_min", 0) <= 0:
        data["ph_threshold_min"] = settings.WASTEWATER_PH_MIN
    if data.get("ph_threshold_max", 0) <= 0:
        data["ph_threshold_max"] = settings.WASTEWATER_PH_MAX
    
    # 检查是否超标（PH值超出范围视为超标）
    ph_value = data.get("ph_value", 7.0)
    ph_over = ph_value < data["ph_threshold_min"] or ph_value > data["ph_threshold_max"]
    data["is_over_limit"] = ph_over
    
    db_wastewater = WastewaterMonitoring(**data)
    db.add(db_wastewater)
    db.commit()
    db.refresh(db_wastewater)
    
    # 如果超标，创建报警记录
    if db_wastewater.is_over_limit:
        alarm_level = "一般"
        ph_deviation = abs(ph_value - (db_wastewater.ph_threshold_min + db_wastewater.ph_threshold_max) / 2)
        if ph_deviation > 3:
            alarm_level = "紧急"
        elif ph_deviation > 1.5:
            alarm_level = "重要"
        
        alarm = AlarmRecord(
            alarm_time=db_wastewater.record_time,
            alarm_type="废水超标",
            monitoring_point_id=db_wastewater.monitoring_point_id,
            wastewater_monitoring_id=db_wastewater.id,
            alarm_level=alarm_level,
            actual_value=ph_value,
            threshold_value=(db_wastewater.ph_threshold_min + db_wastewater.ph_threshold_max) / 2,
            message=f"监测点位[{point.point_name}]废水PH值超标，当前值：{ph_value}，正常范围：{db_wastewater.ph_threshold_min}-{db_wastewater.ph_threshold_max}"
        )
        db.add(alarm)
        db.commit()
    
    result = WastewaterMonitoringResponse.model_validate(db_wastewater)
    result.point_name = point.point_name
    result.point_location = point.location
    return result


@router.get("/wastewater/", response_model=List[WastewaterMonitoringResponse], summary="获取废水监测列表")
def get_wastewater_monitorings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    monitoring_point_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_over_limit: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取废水监测记录列表
    """
    query = db.query(WastewaterMonitoring).join(MonitoringPoint)
    if monitoring_point_id:
        query = query.filter(WastewaterMonitoring.monitoring_point_id == monitoring_point_id)
    if start_date:
        query = query.filter(WastewaterMonitoring.record_date >= start_date)
    if end_date:
        query = query.filter(WastewaterMonitoring.record_date <= end_date)
    if is_over_limit is not None:
        query = query.filter(WastewaterMonitoring.is_over_limit == is_over_limit)
    
    records = query.order_by(WastewaterMonitoring.record_time.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = WastewaterMonitoringResponse.model_validate(record)
        if record.monitoring_point:
            result.point_name = record.monitoring_point.point_name
            result.point_location = record.monitoring_point.location
        results.append(result)
    return results


@router.put("/wastewater/{record_id}", response_model=WastewaterMonitoringResponse, summary="更新废水监测记录")
def update_wastewater_monitoring(
    record_id: int,
    wastewater: WastewaterMonitoringUpdate,
    db: Session = Depends(get_db)
):
    """
    更新废水监测记录
    """
    db_record = db.query(WastewaterMonitoring).filter(WastewaterMonitoring.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="废水监测记录不存在")
    
    update_data = wastewater.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新检查是否超标
    ph_over = db_record.ph_value < db_record.ph_threshold_min or db_record.ph_value > db_record.ph_threshold_max
    db_record.is_over_limit = ph_over
    
    db.commit()
    db.refresh(db_record)
    
    result = WastewaterMonitoringResponse.model_validate(db_record)
    if db_record.monitoring_point:
        result.point_name = db_record.monitoring_point.point_name
        result.point_location = db_record.monitoring_point.location
    return result


@router.delete("/wastewater/{record_id}", summary="删除废水监测记录")
def delete_wastewater_monitoring(record_id: int, db: Session = Depends(get_db)):
    """
    删除废水监测记录
    """
    record = db.query(WastewaterMonitoring).filter(WastewaterMonitoring.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="废水监测记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "废水监测记录删除成功", "id": record_id}


# ============ 报警记录接口 ============

@router.get("/alarms/", response_model=List[AlarmRecordResponse], summary="获取报警记录列表")
def get_alarms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    alarm_type: Optional[str] = Query(None),
    alarm_level: Optional[str] = Query(None),
    is_handled: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取报警记录列表
    """
    query = db.query(AlarmRecord).outerjoin(MonitoringPoint)
    if start_date:
        query = query.filter(func.date(AlarmRecord.alarm_time) >= start_date)
    if end_date:
        query = query.filter(func.date(AlarmRecord.alarm_time) <= end_date)
    if alarm_type:
        query = query.filter(AlarmRecord.alarm_type == alarm_type)
    if alarm_level:
        query = query.filter(AlarmRecord.alarm_level == alarm_level)
    if is_handled is not None:
        query = query.filter(AlarmRecord.is_handled == is_handled)
    
    records = query.order_by(AlarmRecord.alarm_time.desc()).offset(skip).limit(limit).all()
    
    results = []
    for record in records:
        result = AlarmRecordResponse.model_validate(record)
        if record.monitoring_point:
            result.point_name = record.monitoring_point.point_name
            result.point_location = record.monitoring_point.location
        results.append(result)
    return results


@router.get("/alarms/{alarm_id}", response_model=AlarmRecordResponse, summary="获取单个报警记录")
def get_alarm(alarm_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取报警记录详情
    """
    record = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    result = AlarmRecordResponse.model_validate(record)
    if record.monitoring_point:
        result.point_name = record.monitoring_point.point_name
        result.point_location = record.monitoring_point.location
    return result


@router.put("/alarms/{alarm_id}/handle", response_model=AlarmRecordResponse, summary="处理报警")
def handle_alarm(
    alarm_id: int,
    handled_by: str = Query(..., description="处理人"),
    handling_method: str = Query(..., description="处理方式"),
    db: Session = Depends(get_db)
):
    """
    处理报警记录
    标记为已处理，记录处理人、处理时间和处理方式
    """
    record = db.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    record.is_handled = True
    record.handled_by = handled_by
    record.handled_time = datetime.now()
    record.handling_method = handling_method
    
    db.commit()
    db.refresh(record)
    
    result = AlarmRecordResponse.model_validate(record)
    if record.monitoring_point:
        result.point_name = record.monitoring_point.point_name
        result.point_location = record.monitoring_point.location
    return result


# ============ 统计分析接口 ============

@router.get("/stats/dust-daily/", response_model=List[DailyDustStats], summary="日粉尘统计")
def get_daily_dust_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    日粉尘统计
    按日期和监测点位统计粉尘数据
    """
    query = db.query(
        DustMonitoring.record_date,
        DustMonitoring.monitoring_point_id,
        MonitoringPoint.point_name,
        func.avg(DustMonitoring.pm25_concentration).label('avg_pm25'),
        func.avg(DustMonitoring.pm10_concentration).label('avg_pm10'),
        func.avg(DustMonitoring.tsp_concentration).label('avg_tsp'),
        func.max(DustMonitoring.pm25_concentration).label('max_pm25'),
        func.max(DustMonitoring.pm10_concentration).label('max_pm10'),
        func.max(DustMonitoring.tsp_concentration).label('max_tsp'),
        func.sum(func.cast(DustMonitoring.is_over_limit, Integer)).label('over_limit_count'),
        func.count(DustMonitoring.id).label('total_records')
    ).join(MonitoringPoint)
    
    if start_date:
        query = query.filter(DustMonitoring.record_date >= start_date)
    if end_date:
        query = query.filter(DustMonitoring.record_date <= end_date)
    
    from sqlalchemy import Integer
    results = query.group_by(DustMonitoring.record_date, DustMonitoring.monitoring_point_id, MonitoringPoint.point_name).order_by(DustMonitoring.record_date).all()
    
    stats = []
    for result in results:
        stats.append(DailyDustStats(
            record_date=result.record_date,
            monitoring_point_id=result.monitoring_point_id,
            point_name=result.point_name,
            avg_pm25=round(result.avg_pm25 or 0, 2),
            avg_pm10=round(result.avg_pm10 or 0, 2),
            avg_tsp=round(result.avg_tsp or 0, 4),
            max_pm25=round(result.max_pm25 or 0, 2),
            max_pm10=round(result.max_pm10 or 0, 2),
            max_tsp=round(result.max_tsp or 0, 4),
            over_limit_count=result.over_limit_count or 0,
            total_records=result.total_records or 0
        ))
    return stats


@router.get("/stats/noise-daily/", response_model=List[DailyNoiseStats], summary="日噪音统计")
def get_daily_noise_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    日噪音统计
    """
    query = db.query(
        NoiseMonitoring.record_date,
        NoiseMonitoring.monitoring_point_id,
        MonitoringPoint.point_name,
        func.avg(NoiseMonitoring.db_value).label('avg_db'),
        func.max(NoiseMonitoring.db_value).label('max_db'),
        func.min(NoiseMonitoring.db_value).label('min_db'),
        func.sum(func.cast(NoiseMonitoring.is_over_limit, Integer)).label('over_limit_count'),
        func.count(NoiseMonitoring.id).label('total_records')
    ).join(MonitoringPoint)
    
    if start_date:
        query = query.filter(NoiseMonitoring.record_date >= start_date)
    if end_date:
        query = query.filter(NoiseMonitoring.record_date <= end_date)
    
    from sqlalchemy import Integer
    results = query.group_by(NoiseMonitoring.record_date, NoiseMonitoring.monitoring_point_id, MonitoringPoint.point_name).order_by(NoiseMonitoring.record_date).all()
    
    stats = []
    for result in results:
        stats.append(DailyNoiseStats(
            record_date=result.record_date,
            monitoring_point_id=result.monitoring_point_id,
            point_name=result.point_name,
            avg_db=round(result.avg_db or 0, 1),
            max_db=round(result.max_db or 0, 1),
            min_db=round(result.min_db or 0, 1),
            over_limit_count=result.over_limit_count or 0,
            total_records=result.total_records or 0
        ))
    return stats


@router.get("/stats/wastewater-daily/", response_model=List[DailyWastewaterStats], summary="日废水统计")
def get_daily_wastewater_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    日废水统计
    """
    query = db.query(
        WastewaterMonitoring.record_date,
        WastewaterMonitoring.monitoring_point_id,
        MonitoringPoint.point_name,
        func.avg(WastewaterMonitoring.ph_value).label('avg_ph'),
        func.avg(WastewaterMonitoring.cod_value).label('avg_cod'),
        func.avg(WastewaterMonitoring.ss_value).label('avg_ss'),
        func.avg(WastewaterMonitoring.ammonia_nitrogen).label('avg_ammonia_nitrogen'),
        func.sum(WastewaterMonitoring.flow_rate).label('total_flow'),
        func.sum(func.cast(WastewaterMonitoring.is_over_limit, Integer)).label('over_limit_count'),
        func.count(WastewaterMonitoring.id).label('total_records')
    ).join(MonitoringPoint)
    
    if start_date:
        query = query.filter(WastewaterMonitoring.record_date >= start_date)
    if end_date:
        query = query.filter(WastewaterMonitoring.record_date <= end_date)
    
    from sqlalchemy import Integer
    results = query.group_by(WastewaterMonitoring.record_date, WastewaterMonitoring.monitoring_point_id, MonitoringPoint.point_name).order_by(WastewaterMonitoring.record_date).all()
    
    stats = []
    for result in results:
        stats.append(DailyWastewaterStats(
            record_date=result.record_date,
            monitoring_point_id=result.monitoring_point_id,
            point_name=result.point_name,
            avg_ph=round(result.avg_ph or 7.0, 2),
            avg_cod=round(result.avg_cod or 0, 2),
            avg_ss=round(result.avg_ss or 0, 2),
            avg_ammonia_nitrogen=round(result.avg_ammonia_nitrogen or 0, 2),
            total_flow=round(result.total_flow or 0, 2),
            over_limit_count=result.over_limit_count or 0,
            total_records=result.total_records or 0
        ))
    return stats


@router.get("/stats/alarms/", response_model=List[AlarmStats], summary="报警统计")
def get_alarm_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    报警统计
    按日期和报警类型统计报警数据
    """
    query = db.query(
        func.date(AlarmRecord.alarm_time).label('record_date'),
        AlarmRecord.alarm_type,
        func.count(AlarmRecord.id).label('total_alarms'),
        func.sum(func.cast(AlarmRecord.is_handled, Integer)).label('handled_alarms'),
        func.sum(func.cast(~AlarmRecord.is_handled, Integer)).label('pending_alarms'),
        func.sum(func.cast(AlarmRecord.alarm_level == "紧急", Integer)).label('urgent_alarms'),
        func.sum(func.cast(AlarmRecord.alarm_level == "重要", Integer)).label('important_alarms'),
        func.sum(func.cast(AlarmRecord.alarm_level == "一般", Integer)).label('normal_alarms')
    )
    
    if start_date:
        query = query.filter(func.date(AlarmRecord.alarm_time) >= start_date)
    if end_date:
        query = query.filter(func.date(AlarmRecord.alarm_time) <= end_date)
    
    from sqlalchemy import Integer
    results = query.group_by(func.date(AlarmRecord.alarm_time), AlarmRecord.alarm_type).order_by(func.date(AlarmRecord.alarm_time)).all()
    
    stats = []
    for result in results:
        stats.append(AlarmStats(
            record_date=result.record_date,
            alarm_type=result.alarm_type,
            total_alarms=result.total_alarms or 0,
            handled_alarms=result.handled_alarms or 0,
            pending_alarms=result.pending_alarms or 0,
            urgent_alarms=result.urgent_alarms or 0,
            important_alarms=result.important_alarms or 0,
            normal_alarms=result.normal_alarms or 0
        ))
    return stats

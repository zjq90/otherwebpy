from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.monitoring import SensorData, OperationLog, ControlSystemStatus
from app.models.equipment import Sensor, Equipment
from app.schemas.monitoring import (
    SensorDataCreate, SensorDataResponse,
    OperationLogCreate, OperationLogResponse,
    ControlSystemStatusCreate, ControlSystemStatusUpdate, ControlSystemStatusResponse
)

router = APIRouter(
    prefix="/api/monitoring",
    tags=["设备运行状态监测"]
)


# ==================== 传感器数据相关路由 ====================

@router.get("/sensor-data/", response_model=List[SensorDataResponse], summary="获取传感器数据列表")
def get_sensor_data_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sensor_id: Optional[int] = Query(None, description="传感器ID筛选"),
    equipment_id: Optional[int] = Query(None, description="设备ID筛选"),
    status: Optional[str] = Query(None, description="数据状态筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    分页获取传感器数据，支持多条件筛选
    """
    query = db.query(SensorData).join(Sensor)
    
    # 传感器ID筛选
    if sensor_id:
        query = query.filter(SensorData.sensor_id == sensor_id)
    
    # 设备ID筛选
    if equipment_id:
        query = query.filter(Sensor.equipment_id == equipment_id)
    
    # 状态筛选
    if status:
        query = query.filter(SensorData.status == status)
    
    # 时间范围筛选
    if start_time:
        query = query.filter(SensorData.collected_at >= start_time)
    if end_time:
        query = query.filter(SensorData.collected_at <= end_time)
    
    # 按采集时间倒序排列
    query = query.order_by(desc(SensorData.collected_at))
    
    # 分页
    sensor_data_list = query.offset(skip).limit(limit).all()
    
    return sensor_data_list


@router.get("/sensor-data/statistics", summary="获取传感器数据统计")
def get_sensor_data_statistics(
    sensor_id: int = Query(..., description="传感器ID"),
    hours: int = Query(24, ge=1, le=168, description="统计时长（小时）"),
    db: Session = Depends(get_db)
):
    """
    获取指定传感器在指定时间范围内的统计数据
    """
    # 检查传感器是否存在
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"传感器ID {sensor_id} 不存在")
    
    start_time = datetime.now() - timedelta(hours=hours)
    
    # 查询统计数据
    query = db.query(
        func.count(SensorData.id).label("total_count"),
        func.avg(SensorData.value).label("avg_value"),
        func.max(SensorData.value).label("max_value"),
        func.min(SensorData.value).label("min_value"),
        func.count(SensorData.id).filter(SensorData.status == "预警").label("warning_count"),
        func.count(SensorData.id).filter(SensorData.status == "报警").label("alarm_count")
    ).filter(
        SensorData.sensor_id == sensor_id,
        SensorData.collected_at >= start_time
    )
    
    result = query.first()
    
    return {
        "sensor_id": sensor_id,
        "sensor_name": sensor.name,
        "time_range_hours": hours,
        "total_count": result.total_count or 0,
        "avg_value": float(result.avg_value) if result.avg_value else 0,
        "max_value": float(result.max_value) if result.max_value else 0,
        "min_value": float(result.min_value) if result.min_value else 0,
        "warning_count": result.warning_count or 0,
        "alarm_count": result.alarm_count or 0,
        "unit": sensor.unit
    }


@router.get("/sensor-data/{data_id}", response_model=SensorDataResponse, summary="获取传感器数据详情")
def get_sensor_data(data_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取传感器数据详情
    """
    sensor_data = db.query(SensorData).filter(SensorData.id == data_id).first()
    
    if not sensor_data:
        raise HTTPException(status_code=404, detail=f"传感器数据ID {data_id} 不存在")
    
    return sensor_data


@router.post("/sensor-data/", response_model=SensorDataResponse, summary="上传传感器数据")
def create_sensor_data(sensor_data: SensorDataCreate, db: Session = Depends(get_db)):
    """
    上传传感器采集数据（传感器数据上传接口）
    """
    # 检查传感器是否存在
    sensor = db.query(Sensor).filter(Sensor.id == sensor_data.sensor_id).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail=f"传感器ID {sensor_data.sensor_id} 不存在")
    
    # 判断数据状态
    value = sensor_data.value
    status = "正常"
    is_abnormal = False
    
    if sensor.alarm_threshold is not None and value >= sensor.alarm_threshold:
        status = "报警"
        is_abnormal = True
    elif sensor.warning_threshold is not None and value >= sensor.warning_threshold:
        status = "预警"
        is_abnormal = True
    
    # 创建数据记录
    data_dict = sensor_data.model_dump()
    data_dict["status"] = status
    data_dict["is_abnormal"] = is_abnormal
    
    if not data_dict.get("collected_at"):
        data_dict["collected_at"] = datetime.now()
    
    db_sensor_data = SensorData(**data_dict)
    db.add(db_sensor_data)
    
    # 如果是异常数据，创建运行日志
    if is_abnormal:
        equipment = db.query(Equipment).filter(Equipment.id == sensor.equipment_id).first()
        if equipment:
            log = OperationLog(
                equipment_id=equipment.id,
                log_type="故障事件",
                level="警告" if status == "预警" else "错误",
                title=f"传感器{sensor.name}数据异常",
                content=f"传感器{sensor.name}采集值为{value}{sensor.unit}，超出正常范围。正常范围：{sensor.min_value}~{sensor.max_value}",
                from_status=equipment.status,
                to_status=equipment.status,
                related_sensor_data_id=db_sensor_data.id
            )
            db.add(log)
    
    db.commit()
    db.refresh(db_sensor_data)
    
    return db_sensor_data


@router.post("/sensor-data/batch", summary="批量上传传感器数据")
def batch_create_sensor_data(
    sensor_data_list: List[SensorDataCreate],
    db: Session = Depends(get_db)
):
    """
    批量上传传感器数据
    """
    results = []
    errors = []
    
    for i, data in enumerate(sensor_data_list):
        try:
            # 检查传感器是否存在
            sensor = db.query(Sensor).filter(Sensor.id == data.sensor_id).first()
            
            if not sensor:
                errors.append({"index": i, "error": f"传感器ID {data.sensor_id} 不存在"})
                continue
            
            # 判断数据状态
            value = data.value
            status = "正常"
            is_abnormal = False
            
            if sensor.alarm_threshold is not None and value >= sensor.alarm_threshold:
                status = "报警"
                is_abnormal = True
            elif sensor.warning_threshold is not None and value >= sensor.warning_threshold:
                status = "预警"
                is_abnormal = True
            
            # 创建数据记录
            data_dict = data.model_dump()
            data_dict["status"] = status
            data_dict["is_abnormal"] = is_abnormal
            
            if not data_dict.get("collected_at"):
                data_dict["collected_at"] = datetime.now()
            
            db_sensor_data = SensorData(**data_dict)
            db.add(db_sensor_data)
            db.flush()
            
            results.append({
                "index": i,
                "success": True,
                "data_id": db_sensor_data.id
            })
            
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    db.commit()
    
    return {
        "total": len(sensor_data_list),
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors
    }


# ==================== 运行日志相关路由 ====================

@router.get("/operation-logs/", response_model=List[OperationLogResponse], summary="获取运行日志列表")
def get_operation_log_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    equipment_id: Optional[int] = Query(None, description="设备ID筛选"),
    log_type: Optional[str] = Query(None, description="日志类型筛选"),
    level: Optional[str] = Query(None, description="日志级别筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取运行日志列表
    """
    query = db.query(OperationLog)
    
    if equipment_id:
        query = query.filter(OperationLog.equipment_id == equipment_id)
    
    if log_type:
        query = query.filter(OperationLog.log_type == log_type)
    
    if level:
        query = query.filter(OperationLog.level == level)
    
    if start_time:
        query = query.filter(OperationLog.recorded_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.recorded_at <= end_time)
    
    query = query.order_by(desc(OperationLog.recorded_at))
    
    logs = query.offset(skip).limit(limit).all()
    return logs


@router.get("/operation-logs/{log_id}", response_model=OperationLogResponse, summary="获取运行日志详情")
def get_operation_log(log_id: int, db: Session = Depends(get_db)):
    """
    获取运行日志详情
    """
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"运行日志ID {log_id} 不存在")
    return log


@router.post("/operation-logs/", response_model=OperationLogResponse, summary="创建运行日志")
def create_operation_log(log: OperationLogCreate, db: Session = Depends(get_db)):
    """
    创建运行日志
    """
    # 检查设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=400, detail=f"设备ID {log.equipment_id} 不存在")
    
    log_dict = log.model_dump()
    if not log_dict.get("recorded_at"):
        log_dict["recorded_at"] = datetime.now()
    
    db_log = OperationLog(**log_dict)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


# ==================== 控制系统监控相关路由 ====================

@router.get("/control-system/", response_model=List[ControlSystemStatusResponse], summary="获取控制系统监控列表")
def get_control_system_status_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    monitor_type: Optional[str] = Query(None, description="监控类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取控制系统监控状态列表
    """
    query = db.query(ControlSystemStatus)
    
    if monitor_type:
        query = query.filter(ControlSystemStatus.monitor_type == monitor_type)
    
    if status:
        query = query.filter(ControlSystemStatus.status == status)
    
    status_list = query.offset(skip).limit(limit).all()
    return status_list


@router.get("/control-system/{status_id}", response_model=ControlSystemStatusResponse, summary="获取控制系统监控详情")
def get_control_system_status(status_id: int, db: Session = Depends(get_db)):
    """
    获取控制系统监控详情
    """
    status = db.query(ControlSystemStatus).filter(ControlSystemStatus.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail=f"控制系统监控项ID {status_id} 不存在")
    return status


@router.post("/control-system/", response_model=ControlSystemStatusResponse, summary="创建控制系统监控项")
def create_control_system_status(status: ControlSystemStatusCreate, db: Session = Depends(get_db)):
    """
    创建控制系统监控项
    """
    db_status = ControlSystemStatus(**status.model_dump())
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    
    return db_status


@router.put("/control-system/{status_id}", response_model=ControlSystemStatusResponse, summary="更新控制系统监控项")
def update_control_system_status(
    status_id: int,
    status_update: ControlSystemStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    更新控制系统监控项状态
    """
    db_status = db.query(ControlSystemStatus).filter(ControlSystemStatus.id == status_id).first()
    
    if not db_status:
        raise HTTPException(status_code=404, detail=f"控制系统监控项ID {status_id} 不存在")
    
    update_data = status_update.model_dump(exclude_unset=True)
    update_data["last_checked_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_status, key, value)
    
    db.commit()
    db.refresh(db_status)
    
    return db_status


@router.post("/control-system/refresh", summary="刷新所有控制系统状态")
def refresh_control_system_status(db: Session = Depends(get_db)):
    """
    模拟刷新所有控制系统监控项状态（测试用）
    """
    import random
    
    status_list = db.query(ControlSystemStatus).all()
    updated_count = 0
    
    for status in status_list:
        # 模拟随机状态更新（90%概率正常，10%概率异常）
        rand = random.random()
        if rand < 0.9:
            new_status = "正常"
        elif rand < 0.95:
            new_status = "预警"
        else:
            new_status = "异常"
        
        status.status = new_status
        status.last_checked_at = datetime.now()
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"已刷新 {updated_count} 个监控项状态",
        "updated_count": updated_count
    }


@router.delete("/control-system/{status_id}", summary="删除控制系统监控项")
def delete_control_system_status(status_id: int, db: Session = Depends(get_db)):
    """
    删除控制系统监控项
    """
    db_status = db.query(ControlSystemStatus).filter(ControlSystemStatus.id == status_id).first()
    
    if not db_status:
        raise HTTPException(status_code=404, detail=f"控制系统监控项ID {status_id} 不存在")
    
    db.delete(db_status)
    db.commit()
    
    return {"message": f"控制系统监控项ID {status_id} 已删除", "success": True}

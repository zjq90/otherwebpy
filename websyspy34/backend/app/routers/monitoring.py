from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.models.models import (
    ProductionOrder, ProductionLog, ProductionAlert,
    ProductionPlan, Resource,
    ProductionStatus, ProductionStage, AlertLevel, AlertStatus
)
from app.schemas.schemas import (
    ProductionLog as ProductionLogSchema,
    ProductionLogCreate,
    ProductionAlert as ProductionAlertSchema,
    ProductionAlertCreate,
    ProductionAlertUpdate,
    ProductionOrder as ProductionOrderSchema
)

router = APIRouter(prefix="/api/monitoring", tags=["实时生产监控"])


@router.get("/dashboard", summary="获取监控面板数据")
def get_monitoring_dashboard(db: Session = Depends(get_db)):
    """
    获取监控面板汇总数据
    
    返回当前生产状态统计、预警数量、资源状态等
    """
    in_progress_orders = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionStatus.IN_PROGRESS
    ).count()
    
    pending_orders = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionStatus.PENDING
    ).count()
    
    completed_today = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionStatus.COMPLETED,
        func.date(ProductionOrder.actual_end_time) == func.date(datetime.utcnow())
    ).count()
    
    open_alerts = db.query(ProductionAlert).filter(
        ProductionAlert.alert_status == AlertStatus.OPEN
    ).count()
    
    warning_alerts = db.query(ProductionAlert).filter(
        ProductionAlert.alert_status == AlertStatus.OPEN,
        ProductionAlert.alert_level == AlertLevel.WARNING
    ).count()
    
    critical_alerts = db.query(ProductionAlert).filter(
        ProductionAlert.alert_status == AlertStatus.OPEN,
        ProductionAlert.alert_level.in_([AlertLevel.ERROR, AlertLevel.CRITICAL])
    ).count()
    
    available_resources = db.query(Resource).filter(
        Resource.status == "available"
    ).count()
    
    in_use_resources = db.query(Resource).filter(
        Resource.status == "in_use"
    ).count()
    
    in_progress_list = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionStatus.IN_PROGRESS
    ).order_by(ProductionOrder.updated_at.desc()).limit(10).all()
    
    recent_alerts = db.query(ProductionAlert).filter(
        ProductionAlert.alert_status == AlertStatus.OPEN
    ).order_by(ProductionAlert.created_at.desc()).limit(5).all()
    
    return {
        "summary": {
            "in_progress_orders": in_progress_orders,
            "pending_orders": pending_orders,
            "completed_today": completed_today,
            "open_alerts": open_alerts,
            "warning_alerts": warning_alerts,
            "critical_alerts": critical_alerts,
            "available_resources": available_resources,
            "in_use_resources": in_use_resources
        },
        "in_progress_orders": [
            {
                "id": order.id,
                "order_code": order.order_code,
                "current_stage": order.current_stage.value if order.current_stage else None,
                "progress": order.progress,
                "volume": order.volume,
                "updated_at": order.updated_at
            }
            for order in in_progress_list
        ],
        "recent_alerts": [
            {
                "id": alert.id,
                "alert_title": alert.alert_title,
                "alert_level": alert.alert_level.value,
                "created_at": alert.created_at,
                "order_id": alert.order_id
            }
            for alert in recent_alerts
        ]
    }


@router.get("/production-status", summary="获取当前生产状态")
def get_production_status(db: Session = Depends(get_db)):
    """
    获取当前所有进行中生产任务的状态
    
    返回各阶段的生产任务数量和详情
    """
    in_progress_orders = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionStatus.IN_PROGRESS
    ).all()
    
    stage_counts = {
        "batching": 0,
        "mixing": 0,
        "discharging": 0,
        "completed": 0
    }
    
    for order in in_progress_orders:
        stage = order.current_stage.value if order.current_stage else "unknown"
        if stage in stage_counts:
            stage_counts[stage] += 1
    
    return {
        "stage_counts": stage_counts,
        "total_in_progress": len(in_progress_orders),
        "orders": [
            {
                "id": order.id,
                "order_code": order.order_code,
                "batch_number": order.batch_number,
                "current_stage": order.current_stage.value if order.current_stage else None,
                "progress": order.progress,
                "volume": order.volume,
                "formula_id": order.formula_id,
                "actual_start_time": order.actual_start_time,
                "updated_at": order.updated_at
            }
            for order in in_progress_orders
        ]
    }


@router.post("/logs/", response_model=ProductionLogSchema, summary="创建生产日志")
def create_production_log(log: ProductionLogCreate, db: Session = Depends(get_db)):
    """
    创建生产日志记录
    
    - **log**: 生产日志数据
    """
    order = db.query(ProductionOrder).filter(ProductionOrder.id == log.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产任务单不存在")
    
    db_log = ProductionLog(**log.dict())
    db_log.created_at = datetime.utcnow()
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/logs/", response_model=List[ProductionLogSchema], summary="获取生产日志列表")
def get_production_logs(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    order_id: Optional[int] = Query(None, description="任务单ID"),
    stage: Optional[ProductionStage] = Query(None, description="生产阶段"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取生产日志列表，支持筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **order_id**: 按任务单ID筛选
    - **stage**: 按生产阶段筛选
    - **start_time**: 按开始时间筛选
    - **end_time**: 按结束时间筛选
    """
    query = db.query(ProductionLog)
    
    if order_id:
        query = query.filter(ProductionLog.order_id == order_id)
    if stage:
        query = query.filter(ProductionLog.stage == stage)
    if start_time:
        query = query.filter(ProductionLog.created_at >= start_time)
    if end_time:
        query = query.filter(ProductionLog.created_at <= end_time)
    
    logs = query.order_by(ProductionLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/logs/{log_id}", response_model=ProductionLogSchema, summary="获取生产日志详情")
def get_production_log(log_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取生产日志详情
    
    - **log_id**: 日志ID
    """
    log = db.query(ProductionLog).filter(ProductionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="生产日志不存在")
    return log


@router.get("/alerts/", response_model=List[ProductionAlertSchema], summary="获取生产预警列表")
def get_production_alerts(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    order_id: Optional[int] = Query(None, description="任务单ID"),
    alert_level: Optional[AlertLevel] = Query(None, description="预警级别"),
    alert_status: Optional[AlertStatus] = Query(None, description="预警状态"),
    db: Session = Depends(get_db)
):
    """
    获取生产预警列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **order_id**: 按任务单ID筛选
    - **alert_level**: 按预警级别筛选
    - **alert_status**: 按预警状态筛选
    """
    query = db.query(ProductionAlert)
    
    if order_id:
        query = query.filter(ProductionAlert.order_id == order_id)
    if alert_level:
        query = query.filter(ProductionAlert.alert_level == alert_level)
    if alert_status:
        query = query.filter(ProductionAlert.alert_status == alert_status)
    
    alerts = query.order_by(ProductionAlert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/alerts/{alert_id}", response_model=ProductionAlertSchema, summary="获取预警详情")
def get_production_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取预警详情
    
    - **alert_id**: 预警ID
    """
    alert = db.query(ProductionAlert).filter(ProductionAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    return alert


@router.post("/alerts/", response_model=ProductionAlertSchema, summary="创建预警")
def create_production_alert(alert: ProductionAlertCreate, db: Session = Depends(get_db)):
    """
    创建新的生产预警
    
    - **alert**: 预警数据
    """
    if alert.order_id:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == alert.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="生产任务单不存在")
    
    db_alert = ProductionAlert(**alert.dict())
    db_alert.created_at = datetime.utcnow()
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.put("/alerts/{alert_id}", response_model=ProductionAlertSchema, summary="更新预警状态")
def update_production_alert(alert_id: int, alert_update: ProductionAlertUpdate, db: Session = Depends(get_db)):
    """
    更新预警状态（确认、解决等）
    
    - **alert_id**: 预警ID
    - **alert_update**: 更新数据
    """
    alert = db.query(ProductionAlert).filter(ProductionAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    
    update_data = alert_update.dict(exclude_unset=True)
    
    if alert_update.alert_status == AlertStatus.ACKNOWLEDGED and alert.alert_status == AlertStatus.OPEN:
        update_data["acknowledged_at"] = datetime.utcnow()
    
    if alert_update.alert_status == AlertStatus.RESOLVED and alert.alert_status != AlertStatus.RESOLVED:
        update_data["resolved_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(alert, key, value)
    
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/orders/{order_id}/realtime", summary="获取任务单实时数据")
def get_order_realtime_data(order_id: int, db: Session = Depends(get_db)):
    """
    获取指定任务单的实时生产数据
    
    - **order_id**: 任务单ID
    """
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产任务单不存在")
    
    recent_logs = db.query(ProductionLog).filter(
        ProductionLog.order_id == order_id
    ).order_by(ProductionLog.created_at.desc()).limit(10).all()
    
    related_alerts = db.query(ProductionAlert).filter(
        ProductionAlert.order_id == order_id,
        ProductionAlert.alert_status == AlertStatus.OPEN
    ).all()
    
    return {
        "order": {
            "id": order.id,
            "order_code": order.order_code,
            "status": order.status.value if order.status else None,
            "current_stage": order.current_stage.value if order.current_stage else None,
            "progress": order.progress,
            "volume": order.volume,
            "actual_start_time": order.actual_start_time,
            "updated_at": order.updated_at
        },
        "recent_logs": [
            {
                "id": log.id,
                "stage": log.stage.value if log.stage else None,
                "log_message": log.log_message,
                "temperature": log.temperature,
                "humidity": log.humidity,
                "created_at": log.created_at
            }
            for log in recent_logs
        ],
        "active_alerts": [
            {
                "id": alert.id,
                "alert_title": alert.alert_title,
                "alert_message": alert.alert_message,
                "alert_level": alert.alert_level.value,
                "created_at": alert.created_at
            }
            for alert in related_alerts
        ]
    }


@router.get("/statistics/hourly", summary="获取小时生产统计")
def get_hourly_statistics(
    hours: int = Query(24, ge=1, le=168, description="统计小时数"),
    db: Session = Depends(get_db)
):
    """
    获取指定小时内的生产统计数据
    
    - **hours**: 统计的小时数，默认24小时
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    completed_orders = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionStatus.COMPLETED,
        ProductionOrder.actual_end_time >= start_time,
        ProductionOrder.actual_end_time <= end_time
    ).all()
    
    total_volume = sum(order.volume for order in completed_orders)
    order_count = len(completed_orders)
    
    logs = db.query(ProductionLog).filter(
        ProductionLog.created_at >= start_time,
        ProductionLog.created_at <= end_time
    ).all()
    
    avg_temperature = None
    avg_humidity = None
    if logs:
        temperatures = [log.temperature for log in logs if log.temperature is not None]
        humidities = [log.humidity for log in logs if log.humidity is not None]
        if temperatures:
            avg_temperature = sum(temperatures) / len(temperatures)
        if humidities:
            avg_humidity = sum(humidities) / len(humidities)
    
    return {
        "period": {
            "start_time": start_time,
            "end_time": end_time,
            "hours": hours
        },
        "production": {
            "completed_orders": order_count,
            "total_volume": total_volume,
            "avg_temperature": avg_temperature,
            "avg_humidity": avg_humidity
        }
    }

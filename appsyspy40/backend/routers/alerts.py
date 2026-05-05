"""
质量异常预警路由
包含预警创建、查询、处理等功能
"""
from datetime import datetime
from typing import Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user
from models.models import User, ProductionRecord, ProductionFormula, QualityAlert, FeedingRecord
from schemas.schemas import (
    QualityAlertCreate, QualityAlertUpdate, QualityAlertResponse,
    ApiResponse, PaginatedResponse
)


router = APIRouter(prefix="/api/alerts", tags=["质量预警"])


def generate_alert_no() -> str:
    """
    生成预警编号
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    return f"ALT{date_str}{now.microsecond:06d}"


def check_and_create_alerts(production_id: int, db: Session) -> list:
    """
    检查生产记录是否存在异常，并创建预警
    :param production_id: 生产记录ID
    :param db: 数据库会话
    :return: 创建的预警列表
    """
    production = db.query(ProductionRecord).filter(
        ProductionRecord.id == production_id
    ).first()
    if not production:
        return []
    
    formula = db.query(ProductionFormula).filter(
        ProductionFormula.id == production.formula_id
    ).first()
    if not formula:
        return []
    
    alerts = []
    
    # 检查1：搅拌时间不足
    if production.mix_duration < production.target_mix_duration:
        alert_no = generate_alert_no()
        mix_shortage = production.target_mix_duration - production.mix_duration
        
        alert = QualityAlert(
            alert_no=alert_no,
            production_id=production.id,
            alert_type="mix_time_short",
            alert_level="严重" if mix_shortage > 10 else "一般",
            description=f"搅拌时间不足：目标{production.target_mix_duration}秒，实际{production.mix_duration}秒，短缺{mix_shortage}秒",
            deviation_data=json.dumps({
                "target_duration": production.target_mix_duration,
                "actual_duration": production.mix_duration,
                "shortage": mix_shortage
            }),
            status="待处理"
        )
        db.add(alert)
        alerts.append(alert)
    
    # 检查2：配比偏差
    feeding_records = db.query(FeedingRecord).filter(
        FeedingRecord.production_id == production.id
    ).all()
    
    for fr in feeding_records:
        tolerance = 2.0  # 默认允许偏差2%
        
        # 根据材料类型设置不同的允许偏差
        if fr.material_type == "cement":
            tolerance = formula.cement_tolerance
        elif fr.material_type in ["sand", "stone", "aggregate"]:
            tolerance = formula.aggregate_tolerance
        elif fr.material_type == "water":
            tolerance = formula.water_tolerance
        
        if abs(fr.deviation_percent) > tolerance:
            alert_no = generate_alert_no()
            
            alert = QualityAlert(
                alert_no=alert_no,
                production_id=production.id,
                alert_type="mix_ratio_deviation",
                alert_level="严重" if abs(fr.deviation_percent) > tolerance * 2 else "一般",
                description=f"配比偏差：{fr.material_type}目标用量{fr.target_amount}kg，实际{fr.actual_amount}kg，偏差{fr.deviation_percent:.2f}%，允许偏差±{tolerance}%",
                deviation_data=json.dumps({
                    "material_type": fr.material_type,
                    "target_amount": fr.target_amount,
                    "actual_amount": fr.actual_amount,
                    "deviation_percent": fr.deviation_percent,
                    "allowed_tolerance": tolerance
                }),
                status="待处理"
            )
            db.add(alert)
            alerts.append(alert)
    
    if alerts:
        db.commit()
    
    return alerts


@router.post("", response_model=ApiResponse, summary="创建质量预警")
async def create_alert(
    alert_data: QualityAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    手动创建质量预警
    """
    # 检查生产记录是否存在
    production = db.query(ProductionRecord).filter(
        ProductionRecord.id == alert_data.production_id
    ).first()
    if not production:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    alert_no = generate_alert_no()
    
    new_alert = QualityAlert(
        alert_no=alert_no,
        production_id=alert_data.production_id,
        alert_type=alert_data.alert_type,
        alert_level=alert_data.alert_level,
        description=alert_data.description,
        deviation_data=alert_data.deviation_data,
        status="待处理"
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    new_alert.production = production
    
    return ApiResponse(
        code=200,
        message="预警创建成功",
        data={"alert": QualityAlertResponse.model_validate(new_alert).model_dump()}
    )


@router.get("", response_model=PaginatedResponse, summary="获取预警列表")
async def get_alerts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="预警状态"),
    alert_level: Optional[str] = Query(None, description="预警级别"),
    alert_type: Optional[str] = Query(None, description="预警类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分页获取质量预警列表
    支持按状态、级别、类型筛选
    """
    query = db.query(QualityAlert)
    
    if status:
        query = query.filter(QualityAlert.status == status)
    if alert_level:
        query = query.filter(QualityAlert.alert_level == alert_level)
    if alert_type:
        query = query.filter(QualityAlert.alert_type == alert_type)
    
    total = query.count()
    alerts = query.order_by(QualityAlert.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # 关联生产记录信息
    alert_list = []
    for alert in alerts:
        alert.production = db.query(ProductionRecord).filter(
            ProductionRecord.id == alert.production_id
        ).first()
        alert_list.append(QualityAlertResponse.model_validate(alert).model_dump())
    
    return PaginatedResponse(
        code=200,
        message="success",
        data={"items": alert_list},
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{alert_id}", response_model=ApiResponse, summary="获取预警详情")
async def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取预警详情
    """
    alert = db.query(QualityAlert).filter(QualityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预警不存在"
        )
    
    # 关联生产记录
    alert.production = db.query(ProductionRecord).filter(
        ProductionRecord.id == alert.production_id
    ).first()
    
    return ApiResponse(
        code=200,
        message="success",
        data={"alert": QualityAlertResponse.model_validate(alert).model_dump()}
    )


@router.put("/{alert_id}", response_model=ApiResponse, summary="处理预警")
async def handle_alert(
    alert_id: int,
    alert_update: QualityAlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理质量预警
    更新状态、处理人、处理时间和处理结果
    """
    alert = db.query(QualityAlert).filter(QualityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预警不存在"
        )
    
    # 更新字段
    update_data = alert_update.model_dump(exclude_unset=True)
    
    # 如果设置了状态为处理中或已处理，则设置处理人
    if "status" in update_data:
        alert.status = update_data["status"]
        if update_data["status"] in ["处理中", "已处理"]:
            alert.handler_id = current_user.id
            alert.handle_time = datetime.utcnow()
    
    if "handle_result" in update_data:
        alert.handle_result = update_data["handle_result"]
    
    db.commit()
    db.refresh(alert)
    
    return ApiResponse(
        code=200,
        message="预警处理成功",
        data={"alert": QualityAlertResponse.model_validate(alert).model_dump()}
    )


@router.post("/{alert_id}/resolve", response_model=ApiResponse, summary="标记预警为已处理")
async def resolve_alert(
    alert_id: int,
    handle_result: str = Query(..., description="处理结果"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    一键标记预警为已处理
    用于快速处理预警
    """
    alert = db.query(QualityAlert).filter(QualityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预警不存在"
        )
    
    # 更新为已处理状态
    alert.status = "已处理"
    alert.handler_id = current_user.id
    alert.handle_time = datetime.utcnow()
    alert.handle_result = handle_result
    
    db.commit()
    db.refresh(alert)
    
    return ApiResponse(
        code=200,
        message="预警已标记为已处理",
        data={"alert": QualityAlertResponse.model_validate(alert).model_dump()}
    )


@router.get("/statistics/overview", response_model=ApiResponse, summary="预警统计概览")
async def get_alert_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取预警统计信息
    包括待处理数量、各级别预警数量等
    """
    # 总数量
    total = db.query(QualityAlert).count()
    
    # 待处理数量
    pending = db.query(QualityAlert).filter(QualityAlert.status == "待处理").count()
    
    # 处理中数量
    processing = db.query(QualityAlert).filter(QualityAlert.status == "处理中").count()
    
    # 已处理数量
    resolved = db.query(QualityAlert).filter(QualityAlert.status == "已处理").count()
    
    # 按级别统计
    urgent = db.query(QualityAlert).filter(QualityAlert.alert_level == "紧急").count()
    serious = db.query(QualityAlert).filter(QualityAlert.alert_level == "严重").count()
    normal = db.query(QualityAlert).filter(QualityAlert.alert_level == "一般").count()
    
    # 按类型统计
    mix_ratio = db.query(QualityAlert).filter(QualityAlert.alert_type == "mix_ratio_deviation").count()
    mix_time = db.query(QualityAlert).filter(QualityAlert.alert_type == "mix_time_short").count()
    material = db.query(QualityAlert).filter(QualityAlert.alert_type == "material_unqualified").count()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "by_status": {
                "pending": pending,
                "processing": processing,
                "resolved": resolved
            },
            "by_level": {
                "urgent": urgent,
                "serious": serious,
                "normal": normal
            },
            "by_type": {
                "mix_ratio_deviation": mix_ratio,
                "mix_time_short": mix_time,
                "material_unqualified": material
            }
        }
    )

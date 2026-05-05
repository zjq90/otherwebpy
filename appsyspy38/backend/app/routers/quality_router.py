"""
试验检测相关API路由
包含原材料检验、成品质量报告、质量预警等功能
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models.user_models import User
from ..models.business_models import (
    MaterialInspection, QualityReport, QualityAlert
)
from ..schemas.business_schemas import (
    MaterialInspectionCreate, MaterialInspectionResponse,
    QualityReportCreate, QualityReportResponse,
    QualityAlertCreate, QualityAlertUpdate, QualityAlertResponse
)
from ..schemas.user_schemas import ApiResponse, PaginatedResponse
from ..utils.security import (
    get_current_user, require_role, is_admin
)

router = APIRouter(prefix="/quality", tags=["试验检测管理"])


def generate_inspection_no() -> str:
    """生成检验编号"""
    import time
    timestamp = int(time.time())
    return f"MI{timestamp}"


def generate_report_no() -> str:
    """生成报告编号"""
    import time
    timestamp = int(time.time())
    return f"QR{timestamp}"


def generate_alert_no() -> str:
    """生成预警编号"""
    import time
    timestamp = int(time.time())
    return f"QA{timestamp}"


@router.post("/inspections", response_model=MaterialInspectionResponse)
async def create_material_inspection(
    inspection_data: MaterialInspectionCreate,
    current_user: User = Depends(require_role("quality_inspector")),
    db: AsyncSession = Depends(get_db)
):
    """
    录入原材料检验数据（试验检测员权限）
    """
    inspection = MaterialInspection(
        **inspection_data.model_dump(),
        inspection_no=generate_inspection_no(),
        inspector_id=current_user.id
    )
    db.add(inspection)
    await db.commit()
    await db.refresh(inspection)
    
    return MaterialInspectionResponse.model_validate(inspection)


@router.get("/inspections", response_model=PaginatedResponse)
async def get_material_inspections(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    material_type: Optional[str] = Query(None, description="材料类型"),
    inspection_result: Optional[str] = Query(None, description="检验结果"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料检验记录列表
    - 管理员：可以查看所有记录
    - 试验检测员：可以查看所有检验记录
    """
    # 构建查询条件
    query = select(MaterialInspection)
    
    if material_type:
        query = query.where(MaterialInspection.material_type == material_type)
    
    if inspection_result:
        query = query.where(MaterialInspection.inspection_result == inspection_result)
    
    if start_date:
        query = query.where(MaterialInspection.inspection_date >= start_date)
    
    if end_date:
        query = query.where(MaterialInspection.inspection_date <= end_date)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(MaterialInspection.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    inspections = result.scalars().all()
    
    inspection_responses = [MaterialInspectionResponse.model_validate(i) for i in inspections]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=inspection_responses
    )


@router.get("/inspections/{inspection_id}", response_model=MaterialInspectionResponse)
async def get_material_inspection(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取原材料检验详情
    """
    result = await db.execute(
        select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    )
    inspection = result.scalar_one_or_none()
    
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检验记录不存在"
        )
    
    return MaterialInspectionResponse.model_validate(inspection)


@router.put("/inspections/{inspection_id}", response_model=MaterialInspectionResponse)
async def update_material_inspection(
    inspection_id: int,
    inspection_data: MaterialInspectionCreate,
    current_user: User = Depends(require_role("quality_inspector")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新原材料检验记录（试验检测员权限）
    """
    result = await db.execute(
        select(MaterialInspection).where(MaterialInspection.id == inspection_id)
    )
    inspection = result.scalar_one_or_none()
    
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检验记录不存在"
        )
    
    # 只能修改自己录入的记录
    if inspection.inspector_id != current_user.id and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己录入的记录"
        )
    
    # 更新字段
    update_data = inspection_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inspection, key, value)
    
    inspection.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(inspection)
    
    return MaterialInspectionResponse.model_validate(inspection)


@router.post("/reports", response_model=QualityReportResponse)
async def create_quality_report(
    report_data: QualityReportCreate,
    current_user: User = Depends(require_role("quality_inspector")),
    db: AsyncSession = Depends(get_db)
):
    """
    录入成品质量报告（试验检测员权限）
    """
    report = QualityReport(
        **report_data.model_dump(),
        report_no=generate_report_no(),
        inspector_id=current_user.id
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return QualityReportResponse.model_validate(report)


@router.get("/reports", response_model=PaginatedResponse)
async def get_quality_reports(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    project_name: Optional[str] = Query(None, description="项目名称"),
    concrete_type: Optional[str] = Query(None, description="混凝土类型"),
    conclusion: Optional[str] = Query(None, description="结论"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取成品质量报告列表
    """
    # 构建查询条件
    query = select(QualityReport)
    
    if project_name:
        query = query.where(QualityReport.project_name.contains(project_name))
    
    if concrete_type:
        query = query.where(QualityReport.concrete_type == concrete_type)
    
    if conclusion:
        query = query.where(QualityReport.conclusion == conclusion)
    
    if start_date:
        query = query.where(QualityReport.report_date >= start_date)
    
    if end_date:
        query = query.where(QualityReport.report_date <= end_date)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(QualityReport.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    report_responses = [QualityReportResponse.model_validate(r) for r in reports]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=report_responses
    )


@router.get("/reports/{report_id}", response_model=QualityReportResponse)
async def get_quality_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取成品质量报告详情
    """
    result = await db.execute(
        select(QualityReport).where(QualityReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="质量报告不存在"
        )
    
    return QualityReportResponse.model_validate(report)


@router.post("/alerts", response_model=QualityAlertResponse)
async def create_quality_alert(
    alert_data: QualityAlertCreate,
    current_user: User = Depends(require_role("quality_inspector")),
    db: AsyncSession = Depends(get_db)
):
    """
    发起质量异常预警（试验检测员权限）
    """
    alert = QualityAlert(
        **alert_data.model_dump(),
        alert_no=generate_alert_no(),
        initiator_id=current_user.id,
        status="pending"
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return QualityAlertResponse.model_validate(alert)


@router.get("/alerts", response_model=PaginatedResponse)
async def get_quality_alerts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态"),
    alert_level: Optional[str] = Query(None, description="预警级别"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取质量预警列表
    """
    # 构建查询条件
    query = select(QualityAlert)
    
    if status:
        query = query.where(QualityAlert.status == status)
    
    if alert_level:
        query = query.where(QualityAlert.alert_level == alert_level)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(QualityAlert.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    alert_responses = [QualityAlertResponse.model_validate(a) for a in alerts]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=alert_responses
    )


@router.get("/alerts/{alert_id}", response_model=QualityAlertResponse)
async def get_quality_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取质量预警详情
    """
    result = await db.execute(
        select(QualityAlert).where(QualityAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="质量预警不存在"
        )
    
    return QualityAlertResponse.model_validate(alert)


@router.put("/alerts/{alert_id}", response_model=QualityAlertResponse)
async def handle_quality_alert(
    alert_id: int,
    alert_data: QualityAlertUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    处理质量预警
    - 管理员：可以处理所有预警
    - 试验检测员：可以处理自己发起的预警
    """
    result = await db.execute(
        select(QualityAlert).where(QualityAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="质量预警不存在"
        )
    
    # 权限检查
    if not is_admin(current_user) and alert.initiator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权处理此预警"
        )
    
    # 更新字段
    update_data = alert_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alert, key, value)
    
    if alert_data.status:
        alert.handler_id = current_user.id
    
    alert.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(alert)
    
    return QualityAlertResponse.model_validate(alert)

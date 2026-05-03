"""
病虫害防治管理API路由
提供病虫害防治记录的增删改查、高毒农药预警等功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models import PestDiseaseControl
from backend.app.models.pest_disease_control import (
    PestDiseaseTypeEnum,
    ControlMethodEnum,
    SeverityLevelEnum,
    TreatmentStatusEnum
)
from backend.app.schemas.pest_disease_control import (
    PestDiseaseControlCreate,
    PestDiseaseControlUpdate,
    PestDiseaseControlResponse,
    PestDiseaseControlListResponse,
    WarningResponse,
)

# 创建路由
router = APIRouter(
    prefix="/pest-disease-controls",
    tags=["病虫害防治管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=PestDiseaseControlResponse, status_code=status.HTTP_201_CREATED)
def create_pest_disease_control(
    record_data: PestDiseaseControlCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的病虫害防治记录
    包含高毒农药自动预警功能
    
    参数:
        record_data: 记录创建数据
        db: 数据库会话
    
    返回:
        创建的记录详情
    
    异常:
        HTTPException: 记录编号已存在时抛出400错误
    """
    # 检查记录编号是否已存在
    existing = db.query(PestDiseaseControl).filter(
        PestDiseaseControl.record_code == record_data.record_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"记录编号 {record_data.record_code} 已存在"
        )
    
    # 创建记录
    db_record = PestDiseaseControl(**record_data.model_dump())
    
    # 更新预警状态（检查高毒农药）
    db_record.update_warning_status()
    
    # 计算允许使用日期
    db_record.calculate_allowed_use_date()
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.get("/", response_model=PestDiseaseControlListResponse)
def get_pest_disease_controls(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    pest_disease_type: Optional[str] = Query(None, description="筛选病虫害类型"),
    crop_type: Optional[str] = Query(None, description="筛选作物种类"),
    plot_location: Optional[str] = Query(None, description="筛选发生地块"),
    severity: Optional[str] = Query(None, description="筛选严重程度"),
    treatment_status: Optional[str] = Query(None, description="筛选防治状态"),
    has_warning: Optional[bool] = Query(None, description="筛选是否有预警"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    分页查询病虫害防治记录列表
    
    参数:
        page: 页码，从1开始
        page_size: 每页数量，最大100
        pest_disease_type: 按病虫害类型筛选
        crop_type: 按作物种类筛选
        plot_location: 按发生地块筛选
        severity: 按严重程度筛选
        treatment_status: 按防治状态筛选
        has_warning: 按是否有预警筛选
        start_date: 开始日期
        end_date: 结束日期
        keyword: 关键词搜索
        db: 数据库会话
    
    返回:
        包含分页信息的记录列表
    """
    # 构建查询
    query = db.query(PestDiseaseControl)
    
    # 应用筛选条件
    if pest_disease_type:
        try:
            pd_type_enum = PestDiseaseTypeEnum(pest_disease_type)
            query = query.filter(PestDiseaseControl.pest_disease_type == pd_type_enum)
        except ValueError:
            pass
    
    if crop_type:
        query = query.filter(PestDiseaseControl.crop_type.contains(crop_type))
    
    if plot_location:
        query = query.filter(PestDiseaseControl.plot_location.contains(plot_location))
    
    if severity:
        try:
            severity_enum = SeverityLevelEnum(severity)
            query = query.filter(PestDiseaseControl.severity == severity_enum)
        except ValueError:
            pass
    
    if treatment_status:
        try:
            status_enum = TreatmentStatusEnum(treatment_status)
            query = query.filter(PestDiseaseControl.treatment_status == status_enum)
        except ValueError:
            pass
    
    if has_warning is not None:
        query = query.filter(PestDiseaseControl.has_warning == has_warning)
    
    if start_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(PestDiseaseControl.discovery_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(PestDiseaseControl.discovery_date <= end_dt)
        except ValueError:
            pass
    
    if keyword:
        query = query.filter(
            or_(
                PestDiseaseControl.record_code.contains(keyword),
                PestDiseaseControl.pest_disease_name.contains(keyword),
                PestDiseaseControl.pesticide_name.contains(keyword),
                PestDiseaseControl.crop_type.contains(keyword),
                PestDiseaseControl.plot_location.contains(keyword)
            )
        )
    
    # 获取总记录数
    total = query.count()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 执行分页查询
    items = query.order_by(PestDiseaseControl.discovery_date.desc(), PestDiseaseControl.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{record_id}", response_model=PestDiseaseControlResponse)
def get_pest_disease_control(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取病虫害防治记录详情
    
    参数:
        record_id: 记录ID
        db: 数据库会话
    
    返回:
        记录详情
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    record = db.query(PestDiseaseControl).filter(PestDiseaseControl.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"病虫害防治记录 ID {record_id} 不存在"
        )
    
    return record


@router.put("/{record_id}", response_model=PestDiseaseControlResponse)
def update_pest_disease_control(
    record_id: int,
    record_data: PestDiseaseControlUpdate,
    db: Session = Depends(get_db)
):
    """
    更新病虫害防治记录
    更新时会自动检查高毒农药预警
    
    参数:
        record_id: 记录ID
        record_data: 更新数据
        db: 数据库会话
    
    返回:
        更新后的记录详情
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    db_record = db.query(PestDiseaseControl).filter(PestDiseaseControl.id == record_id).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"病虫害防治记录 ID {record_id} 不存在"
        )
    
    # 更新字段
    update_data = record_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新检查高毒农药预警
    db_record.update_warning_status()
    
    # 重新计算允许使用日期
    db_record.calculate_allowed_use_date()
    
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pest_disease_control(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    删除病虫害防治记录
    
    参数:
        record_id: 记录ID
        db: 数据库会话
    
    异常:
        HTTPException: 记录不存在时抛出404错误
    """
    db_record = db.query(PestDiseaseControl).filter(PestDiseaseControl.id == record_id).first()
    
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"病虫害防治记录 ID {record_id} 不存在"
        )
    
    db.delete(db_record)
    db.commit()


@router.get("/warnings/check", response_model=WarningResponse)
def check_pesticide_warnings(
    db: Session = Depends(get_db)
):
    """
    检查高毒农药使用预警
    查询所有存在高毒农药预警的记录
    
    参数:
        db: 数据库会话
    
    返回:
        预警响应，包含所有预警记录
    """
    # 查询所有有预警的记录
    warning_records = db.query(PestDiseaseControl).filter(
        PestDiseaseControl.has_warning == True
    ).order_by(PestDiseaseControl.discovery_date.desc()).all()
    
    # 构建预警详情列表
    warnings = []
    for record in warning_records:
        warnings.append({
            "id": record.id,
            "record_code": record.record_code,
            "pest_disease_name": record.pest_disease_name,
            "pesticide_name": record.pesticide_name,
            "discovery_date": record.discovery_date.isoformat() if record.discovery_date else None,
            "treatment_date": record.treatment_date.isoformat() if record.treatment_date else None,
            "warning_message": record.warning_message,
            "affected_area": float(record.affected_area) if record.affected_area else 0
        })
    
    return {
        "has_warning": len(warnings) > 0,
        "warning_count": len(warnings),
        "warnings": warnings
    }


@router.get("/statistics/summary")
def get_pest_disease_statistics(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    crop_type: Optional[str] = Query(None, description="作物种类筛选"),
    db: Session = Depends(get_db)
):
    """
    获取病虫害防治统计数据
    
    参数:
        start_date: 开始日期
        end_date: 结束日期
        crop_type: 作物种类筛选
        db: 数据库会话
    
    返回:
        统计数据，包括：
        - 按病虫害类型统计
        - 按严重程度统计
        - 按防治状态统计
        - 高毒农药预警数量
    """
    query = db.query(PestDiseaseControl)
    
    # 应用筛选条件
    if crop_type:
        query = query.filter(PestDiseaseControl.crop_type.contains(crop_type))
    
    if start_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(PestDiseaseControl.discovery_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(PestDiseaseControl.discovery_date <= end_dt)
        except ValueError:
            pass
    
    records = query.all()
    
    # 统计数据
    type_stats = {}
    severity_stats = {}
    status_stats = {}
    method_stats = {}
    total_warnings = 0
    total_records = len(records)
    
    for record in records:
        # 按病虫害类型统计
        type_val = record.pest_disease_type.value if record.pest_disease_type else "未知"
        if type_val not in type_stats:
            type_stats[type_val] = {
                "count": 0,
                "affected_area": 0
            }
        type_stats[type_val]["count"] += 1
        type_stats[type_val]["affected_area"] += float(record.affected_area) if record.affected_area else 0
        
        # 按严重程度统计
        severity_val = record.severity.value if record.severity else "未知"
        if severity_val not in severity_stats:
            severity_stats[severity_val] = 0
        severity_stats[severity_val] += 1
        
        # 按防治状态统计
        status_val = record.treatment_status.value if record.treatment_status else "未知"
        if status_val not in status_stats:
            status_stats[status_val] = 0
        status_stats[status_val] += 1
        
        # 按防治方法统计
        if record.control_method:
            method_val = record.control_method.value
            if method_val not in method_stats:
                method_stats[method_val] = 0
            method_stats[method_val] += 1
        
        # 预警统计
        if record.has_warning:
            total_warnings += 1
    
    return {
        "total_records": total_records,
        "total_warnings": total_warnings,
        "type_statistics": type_stats,
        "severity_statistics": severity_stats,
        "status_statistics": status_stats,
        "method_statistics": method_stats
    }


@router.get("/stats")
def get_pest_disease_stats(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    crop_type: Optional[str] = Query(None, description="作物种类筛选"),
    db: Session = Depends(get_db)
):
    """
    获取病虫害防治统计数据（前端调用别名）
    与 /statistics/summary 功能相同，方便前端调用
    """
    return get_pest_disease_statistics(start_date=start_date, end_date=end_date, crop_type=crop_type, db=db)

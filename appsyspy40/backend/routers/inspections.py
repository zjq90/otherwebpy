"""
原材料检验路由
包含原材料检验录入、查询、判断等功能
"""
from datetime import datetime
from typing import Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user
from models.models import User, Material, MaterialInspection
from schemas.schemas import (
    MaterialInspectionCreate, MaterialInspectionResponse,
    MaterialResponse, ApiResponse, PaginatedResponse
)


router = APIRouter(prefix="/api/inspections", tags=["原材料检验"])


def generate_inspection_no() -> str:
    """
    生成检验单号
    格式：INS + 年月日 + 6位序号
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    return f"INS{date_str}{now.microsecond:06d}"


def check_qualified(inspection_data: MaterialInspectionCreate, material: Material) -> bool:
    """
    根据原材料类型自动判断检验是否合格
    :param inspection_data: 检验数据
    :param material: 原材料信息
    :return: 是否合格
    """
    # 根据材料类型设置不同的合格标准
    if material.material_type == "cement":  # 水泥
        # 检查3天强度（最低要求：20MPa）
        if inspection_data.cement_strength_3d is not None:
            if inspection_data.cement_strength_3d < 20:
                return False
        # 检查28天强度（最低要求：42.5MPa）
        if inspection_data.cement_strength_28d is not None:
            if inspection_data.cement_strength_28d < 42.5:
                return False
        # 检查细度（筛余不超过10%）
        if inspection_data.cement_fineness is not None:
            if inspection_data.cement_fineness > 10:
                return False
    
    elif material.material_type == "aggregate":  # 骨料
        # 检查级配数据
        if inspection_data.aggregate_gradation:
            try:
                gradation = json.loads(inspection_data.aggregate_gradation)
                # 简单检查：级配数据必须存在
                if not gradation:
                    return False
            except json.JSONDecodeError:
                return False
        # 检查杂质含量（不超过1%）
        if inspection_data.impurity_content is not None:
            if inspection_data.impurity_content > 1:
                return False
    
    elif material.material_type == "admixture":  # 外加剂
        # 检查性能数据
        if inspection_data.admixture_performance:
            try:
                performance = json.loads(inspection_data.admixture_performance)
                if not performance:
                    return False
            except json.JSONDecodeError:
                return False
    
    # 通用检查：含水量（不超过5%）
    if inspection_data.water_content is not None:
        if inspection_data.water_content > 5:
            return False
    
    return True


@router.post("", response_model=ApiResponse, summary="录入原材料检验")
async def create_inspection(
    inspection_data: MaterialInspectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    录入原材料进场检验数据
    系统自动判断是否合格
    """
    # 检查原材料是否存在
    material = db.query(Material).filter(Material.id == inspection_data.material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    
    # 生成检验单号
    inspection_no = generate_inspection_no()
    
    # 自动判断是否合格
    is_qualified = check_qualified(inspection_data, material)
    
    # 创建检验记录
    new_inspection = MaterialInspection(
        inspection_no=inspection_no,
        material_id=inspection_data.material_id,
        batch_no=inspection_data.batch_no,
        arrival_date=inspection_data.arrival_date,
        inspector_id=current_user.id,
        cement_strength_3d=inspection_data.cement_strength_3d,
        cement_strength_28d=inspection_data.cement_strength_28d,
        cement_fineness=inspection_data.cement_fineness,
        aggregate_gradation=inspection_data.aggregate_gradation,
        admixture_performance=inspection_data.admixture_performance,
        water_content=inspection_data.water_content,
        impurity_content=inspection_data.impurity_content,
        inspection_report=inspection_data.inspection_report,
        remarks=inspection_data.remarks,
        is_qualified=is_qualified,
        status="合格" if is_qualified else "禁用"
    )
    
    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)
    
    # 关联材料信息
    new_inspection.material = material
    
    return ApiResponse(
        code=200,
        message="检验录入成功" if is_qualified else "检验录入成功，该批次材料不合格，已标记为禁用状态",
        data={"inspection": MaterialInspectionResponse.model_validate(new_inspection).model_dump()}
    )


@router.get("", response_model=PaginatedResponse, summary="获取检验记录列表")
async def get_inspections(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    material_id: Optional[int] = Query(None, description="原材料ID"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分页获取原材料检验记录列表
    支持多种筛选条件
    """
    query = db.query(MaterialInspection)
    
    # 按原材料筛选
    if material_id:
        query = query.filter(MaterialInspection.material_id == material_id)
    
    # 按状态筛选
    if status:
        query = query.filter(MaterialInspection.status == status)
    
    # 按日期范围筛选
    if start_date:
        query = query.filter(MaterialInspection.inspection_date >= start_date)
    if end_date:
        query = query.filter(MaterialInspection.inspection_date <= end_date)
    
    # 计算总数
    total = query.count()
    
    # 分页
    inspections = query.order_by(MaterialInspection.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # 关联材料信息
    inspection_list = []
    for ins in inspections:
        ins.material = db.query(Material).filter(Material.id == ins.material_id).first()
        inspection_list.append(MaterialInspectionResponse.model_validate(ins).model_dump())
    
    return PaginatedResponse(
        code=200,
        message="success",
        data={"items": inspection_list},
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{inspection_id}", response_model=ApiResponse, summary="获取检验详情")
async def get_inspection(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取检验记录详情
    """
    inspection = db.query(MaterialInspection).filter(
        MaterialInspection.id == inspection_id
    ).first()
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检验记录不存在"
        )
    
    # 关联材料信息
    inspection.material = db.query(Material).filter(Material.id == inspection.material_id).first()
    
    return ApiResponse(
        code=200,
        message="success",
        data={"inspection": MaterialInspectionResponse.model_validate(inspection).model_dump()}
    )


@router.get("/batch/{batch_no}", response_model=ApiResponse, summary="按批次号查询检验")
async def get_inspection_by_batch(
    batch_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据批次号查询检验记录
    """
    inspections = db.query(MaterialInspection).filter(
        MaterialInspection.batch_no == batch_no
    ).all()
    
    inspection_list = []
    for ins in inspections:
        ins.material = db.query(Material).filter(Material.id == ins.material_id).first()
        inspection_list.append(MaterialInspectionResponse.model_validate(ins).model_dump())
    
    return ApiResponse(
        code=200,
        message="success",
        data={"inspections": inspection_list}
    )


@router.post("/{inspection_id}/recheck", response_model=ApiResponse, summary="复检检验记录")
async def recheck_inspection(
    inspection_id: int,
    inspection_data: MaterialInspectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    对不合格的检验记录进行复检
    """
    inspection = db.query(MaterialInspection).filter(
        MaterialInspection.id == inspection_id
    ).first()
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检验记录不存在"
        )
    
    # 检查原材料
    material = db.query(Material).filter(Material.id == inspection_data.material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    
    # 重新判断是否合格
    is_qualified = check_qualified(inspection_data, material)
    
    # 更新检验记录
    inspection.cement_strength_3d = inspection_data.cement_strength_3d
    inspection.cement_strength_28d = inspection_data.cement_strength_28d
    inspection.cement_fineness = inspection_data.cement_fineness
    inspection.aggregate_gradation = inspection_data.aggregate_gradation
    inspection.admixture_performance = inspection_data.admixture_performance
    inspection.water_content = inspection_data.water_content
    inspection.impurity_content = inspection_data.impurity_content
    inspection.inspection_report = inspection_data.inspection_report
    inspection.remarks = inspection_data.remarks
    inspection.is_qualified = is_qualified
    inspection.status = "合格" if is_qualified else "禁用"
    
    db.commit()
    db.refresh(inspection)
    
    inspection.material = material
    
    return ApiResponse(
        code=200,
        message="复检完成，结果为：" + ("合格" if is_qualified else "不合格"),
        data={"inspection": MaterialInspectionResponse.model_validate(inspection).model_dump()}
    )

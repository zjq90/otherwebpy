"""
质量追溯路由
包含通过二维码查询生产全链条数据的功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user
from models.models import (
    User, ProductionRecord, ProductionFormula, FeedingRecord,
    QualityAlert, InspectionReport
)
from schemas.schemas import (
    QualityTraceResponse, ProductionRecordResponse, ProductionFormulaResponse,
    FeedingRecordResponse, InspectionReportResponse, QualityAlertResponse,
    ApiResponse
)


router = APIRouter(prefix="/api/trace", tags=["质量追溯"])


@router.get("/qr/{qr_code}", response_model=ApiResponse, summary="通过二维码追溯质量")
async def trace_by_qr(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    通过二维码标识追溯混凝土生产全链条数据
    包括：生产配方、投料记录、搅拌参数、检验报告、质量预警等
    """
    # 查询生产记录
    production = db.query(ProductionRecord).filter(
        ProductionRecord.qr_code == qr_code
    ).first()
    if not production:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对应的生产记录"
        )
    
    # 查询生产配方
    formula = db.query(ProductionFormula).filter(
        ProductionFormula.id == production.formula_id
    ).first()
    
    # 查询投料记录
    feeding_records = db.query(FeedingRecord).filter(
        FeedingRecord.production_id == production.id
    ).all()
    
    # 查询检验报告
    inspection_reports = db.query(InspectionReport).filter(
        InspectionReport.production_id == production.id
    ).all()
    
    # 查询关联的质量预警
    alerts = db.query(QualityAlert).filter(
        QualityAlert.production_id == production.id
    ).all()
    
    # 构建响应数据
    production.formula = formula
    
    trace_data = {
        "production": ProductionRecordResponse.model_validate(production).model_dump(),
        "formula": ProductionFormulaResponse.model_validate(formula).model_dump() if formula else None,
        "feeding_records": [FeedingRecordResponse.model_validate(fr).model_dump() for fr in feeding_records],
        "inspection_reports": [InspectionReportResponse.model_validate(ir).model_dump() for ir in inspection_reports],
        "alerts": [QualityAlertResponse.model_validate(a).model_dump() for a in alerts]
    }
    
    return ApiResponse(
        code=200,
        message="success",
        data=trace_data
    )


@router.get("/production/{production_id}", response_model=ApiResponse, summary="通过生产记录ID追溯质量")
async def trace_by_production_id(
    production_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    通过生产记录ID追溯混凝土生产全链条数据
    """
    # 查询生产记录
    production = db.query(ProductionRecord).filter(
        ProductionRecord.id == production_id
    ).first()
    if not production:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    # 查询生产配方
    formula = db.query(ProductionFormula).filter(
        ProductionFormula.id == production.formula_id
    ).first()
    
    # 查询投料记录
    feeding_records = db.query(FeedingRecord).filter(
        FeedingRecord.production_id == production.id
    ).all()
    
    # 查询检验报告
    inspection_reports = db.query(InspectionReport).filter(
        InspectionReport.production_id == production.id
    ).all()
    
    # 查询关联的质量预警
    alerts = db.query(QualityAlert).filter(
        QualityAlert.production_id == production.id
    ).all()
    
    # 构建响应数据
    production.formula = formula
    
    trace_data = {
        "production": ProductionRecordResponse.model_validate(production).model_dump(),
        "formula": ProductionFormulaResponse.model_validate(formula).model_dump() if formula else None,
        "feeding_records": [FeedingRecordResponse.model_validate(fr).model_dump() for fr in feeding_records],
        "inspection_reports": [InspectionReportResponse.model_validate(ir).model_dump() for ir in inspection_reports],
        "alerts": [QualityAlertResponse.model_validate(a).model_dump() for a in alerts]
    }
    
    return ApiResponse(
        code=200,
        message="success",
        data=trace_data
    )


@router.get("/batch/{batch_no}", response_model=ApiResponse, summary="按批次号追溯原材料")
async def trace_material_by_batch(
    batch_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据原材料批次号追溯相关的检验记录
    用于原材料质量追溯
    """
    from models.models import MaterialInspection, Material
    
    # 查询原材料检验记录
    inspections = db.query(MaterialInspection).filter(
        MaterialInspection.batch_no == batch_no
    ).all()
    
    if not inspections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该批次的检验记录"
        )
    
    inspection_list = []
    for ins in inspections:
        material = db.query(Material).filter(Material.id == ins.material_id).first()
        ins.material = material
        inspection_list.append({
            "inspection": {
                "id": ins.id,
                "inspection_no": ins.inspection_no,
                "batch_no": ins.batch_no,
                "arrival_date": ins.arrival_date.isoformat() if ins.arrival_date else None,
                "inspection_date": ins.inspection_date.isoformat() if ins.inspection_date else None,
                "is_qualified": ins.is_qualified,
                "status": ins.status,
                "cement_strength_3d": ins.cement_strength_3d,
                "cement_strength_28d": ins.cement_strength_28d,
                "cement_fineness": ins.cement_fineness,
                "water_content": ins.water_content,
                "impurity_content": ins.impurity_content,
                "remarks": ins.remarks
            },
            "material": {
                "id": material.id,
                "material_code": material.material_code,
                "material_name": material.material_name,
                "material_type": material.material_type,
                "supplier": material.supplier,
                "specification": material.specification
            } if material else None
        })
    
    return ApiResponse(
        code=200,
        message="success",
        data={"inspections": inspection_list}
    )


@router.get("/truck/{truck_no}", response_model=ApiResponse, summary="按罐车编号查询生产记录")
async def trace_by_truck(
    truck_no: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据罐车编号查询所有生产记录
    用于罐车运输质量追溯
    """
    # 查询该罐车的生产记录
    query = db.query(ProductionRecord).filter(
        ProductionRecord.truck_no == truck_no
    )
    
    total = query.count()
    productions = query.order_by(ProductionRecord.production_date.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    production_list = []
    for prod in productions:
        formula = db.query(ProductionFormula).filter(
            ProductionFormula.id == prod.formula_id
        ).first()
        prod.formula = formula
        production_list.append(ProductionRecordResponse.model_validate(prod).model_dump())
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "productions": production_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )

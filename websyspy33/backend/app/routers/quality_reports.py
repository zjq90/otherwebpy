# -*- coding: utf-8 -*-
"""
质量报告API路由
================
提供质量报告的增删改查接口
生成可追溯的质量报告
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import QualityReport, ProductionBatch, MaterialInspection, ProductionRecord, StrengthTest
from app.schemas import QualityReportCreate, QualityReportUpdate, QualityReportResponse

router = APIRouter()


@router.get("/", response_model=List[QualityReportResponse], summary="获取质量报告列表")
async def get_quality_reports(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    batch_id: Optional[int] = Query(None, description="生产批次ID筛选"),
    report_type: Optional[str] = Query(None, description="报告类型筛选"),
    overall_result: Optional[str] = Query(None, description="综合评定结果筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取质量报告列表，支持分页和筛选
    """
    query = select(QualityReport)
    
    if keyword:
        query = query.where(
            (QualityReport.report_no.like(f"%{keyword}%"))
        )
    
    if batch_id:
        query = query.where(QualityReport.batch_id == batch_id)
    
    if report_type:
        query = query.where(QualityReport.report_type == report_type)
    
    if overall_result:
        query = query.where(QualityReport.overall_result == overall_result)
    
    if status:
        query = query.where(QualityReport.status == status)
    
    query = query.order_by(QualityReport.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return reports


@router.get("/count", response_model=int, summary="获取质量报告总数")
async def get_quality_reports_count(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    batch_id: Optional[int] = Query(None, description="生产批次ID筛选"),
    report_type: Optional[str] = Query(None, description="报告类型筛选"),
    overall_result: Optional[str] = Query(None, description="综合评定结果筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取质量报告总数
    """
    query = select(func.count(QualityReport.id))
    
    if keyword:
        query = query.where(
            (QualityReport.report_no.like(f"%{keyword}%"))
        )
    
    if batch_id:
        query = query.where(QualityReport.batch_id == batch_id)
    
    if report_type:
        query = query.where(QualityReport.report_type == report_type)
    
    if overall_result:
        query = query.where(QualityReport.overall_result == overall_result)
    
    if status:
        query = query.where(QualityReport.status == status)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


@router.get("/{report_id}", response_model=QualityReportResponse, summary="获取单个质量报告")
async def get_quality_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取质量报告详情
    """
    query = select(QualityReport).where(QualityReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if report is None:
        raise HTTPException(status_code=404, detail=f"质量报告 ID: {report_id} 不存在")
    
    return report


@router.post("/", response_model=QualityReportResponse, status_code=201, summary="创建质量报告")
async def create_quality_report(
    report: QualityReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的质量报告
    """
    # 检查报告编号是否已存在
    query = select(QualityReport).where(QualityReport.report_no == report.report_no)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"报告编号 {report.report_no} 已存在")
    
    # 检查生产批次是否存在
    batch_query = select(ProductionBatch).where(ProductionBatch.id == report.batch_id)
    batch_result = await db.execute(batch_query)
    batch = batch_result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=400, detail=f"生产批次 ID: {report.batch_id} 不存在")
    
    new_report = QualityReport(**report.model_dump())
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    
    return new_report


@router.put("/{report_id}", response_model=QualityReportResponse, summary="更新质量报告")
async def update_quality_report(
    report_id: int,
    report: QualityReportUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新质量报告
    """
    query = select(QualityReport).where(QualityReport.id == report_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        raise HTTPException(status_code=404, detail=f"质量报告 ID: {report_id} 不存在")
    
    update_data = report.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return existing


@router.delete("/{report_id}", status_code=204, summary="删除质量报告")
async def delete_quality_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除质量报告
    """
    query = select(QualityReport).where(QualityReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if report is None:
        raise HTTPException(status_code=404, detail=f"质量报告 ID: {report_id} 不存在")
    
    await db.delete(report)
    await db.commit()


@router.post("/{report_id}/approve", response_model=QualityReportResponse, summary="批准发布报告")
async def approve_quality_report(
    report_id: int,
    approver: str,
    db: AsyncSession = Depends(get_db)
):
    """
    批准发布质量报告
    """
    from datetime import date
    
    query = select(QualityReport).where(QualityReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if report is None:
        raise HTTPException(status_code=404, detail=f"质量报告 ID: {report_id} 不存在")
    
    if report.status != "草稿":
        raise HTTPException(status_code=400, detail="只能批准草稿状态的报告")
    
    report.status = "已发布"
    report.approved_by = approver
    report.approval_date = date.today()
    
    await db.commit()
    await db.refresh(report)
    
    return report


@router.post("/{report_id}/void", response_model=QualityReportResponse, summary="作废报告")
async def void_quality_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    作废质量报告
    """
    query = select(QualityReport).where(QualityReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if report is None:
        raise HTTPException(status_code=404, detail=f"质量报告 ID: {report_id} 不存在")
    
    report.status = "已作废"
    
    await db.commit()
    await db.refresh(report)
    
    return report


@router.post("/generate/{batch_id}", response_model=QualityReportResponse, summary="生成质量报告")
async def generate_quality_report(
    batch_id: int,
    report_type: str = "出厂合格证",
    db: AsyncSession = Depends(get_db)
):
    """
    根据生产批次自动生成质量报告
    关联原材料检验、生产记录、强度检测结果
    """
    from datetime import date, datetime
    import json
    
    # 检查生产批次是否存在
    batch_query = select(ProductionBatch).where(ProductionBatch.id == batch_id)
    batch_result = await db.execute(batch_query)
    batch = batch_result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"生产批次 ID: {batch_id} 不存在")
    
    # 生成报告编号
    report_no = f"QR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 收集关联数据
    material_inspections = []
    production_records = []
    strength_tests = []
    
    # 获取该批次的原材料检验记录（简化逻辑）
    # 实际应用中应该根据生产批次关联的材料来获取
    
    # 获取该批次的生产记录
    record_query = select(ProductionRecord).where(ProductionRecord.batch_id == batch_id)
    record_result = await db.execute(record_query)
    records = record_result.scalars().all()
    production_record_ids = [str(r.id) for r in records]
    
    # 获取该批次的强度检测
    test_query = select(StrengthTest).where(
        StrengthTest.block_id.in_(
            select(TestBlock.id).where(TestBlock.batch_id == batch_id)
        )
    )
    test_result = await db.execute(test_query)
    tests = test_result.scalars().all()
    strength_test_ids = [str(t.id) for t in tests]
    
    # 计算综合评定
    # 简化逻辑：检查是否有不合格的记录
    has_anomaly = any(not r.is_normal for r in records) if records else False
    has_failed_test = any(not t.is_qualified for t in tests) if tests else False
    
    overall_result = "合格" if not has_anomaly and not has_failed_test else "不合格"
    is_qualified = not has_anomaly and not has_failed_test
    
    # 生成报告摘要
    summary = f"生产批次 {batch.batch_no} 质量报告\n"
    summary += f"强度等级: {batch.strength_grade}\n"
    summary += f"生产记录数: {len(records)}\n"
    summary += f"强度检测数: {len(tests)}\n"
    summary += f"综合评定: {overall_result}"
    
    # 创建报告
    new_report = QualityReport(
        report_no=report_no,
        batch_id=batch_id,
        report_type=report_type,
        report_date=date.today(),
        generated_by="系统自动生成",
        material_inspection_ids=",".join(material_inspections) if material_inspections else None,
        production_record_ids=",".join(production_record_ids) if production_record_ids else None,
        strength_test_ids=",".join(strength_test_ids) if strength_test_ids else None,
        summary=summary,
        conclusion=f"本批次混凝土{overall_result}",
        overall_result=overall_result,
        is_qualified=is_qualified,
        status="草稿"
    )
    
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    
    return new_report

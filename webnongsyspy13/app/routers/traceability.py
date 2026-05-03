"""
溯源API路由
提供农产品溯源查询功能，消费者扫码后可查看完整溯源信息
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db

# 创建路由实例
router = APIRouter(
    prefix="/traceability",
    tags=["溯源查询"],
    responses={404: {"description": "未找到"}},
)


@router.get("/batch/{batch_number}", response_model=schemas.TraceabilityInfo)
def get_traceability_by_batch_number(
    batch_number: str,
    db: Session = Depends(get_db)
):
    """
    根据批次编号获取完整溯源信息
    消费者扫码后调用此接口查看完整溯源信息
    
    Args:
        batch_number: 批次编号
        db: 数据库会话
        
    Returns:
        完整溯源信息
    """
    # 获取批次信息
    batch = crud.batch.get_by_batch_number(db, batch_number=batch_number)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    # 获取产品信息
    product = crud.product.get(db, id=batch.product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联的产品不存在"
        )
    
    # 获取种植记录
    planting_records = crud.planting_record.get_by_batch_id(
        db, batch_id=batch.id, limit=100
    )
    
    # 获取农资使用记录
    agrochemical_usages = crud.agrochemical_usage.get_by_batch_id(
        db, batch_id=batch.id, limit=100
    )
    
    # 获取检测结果
    test_results = crud.test_result.get_by_batch_id(
        db, batch_id=batch.id, limit=100
    )
    
    # 构建溯源信息
    traceability_info = schemas.TraceabilityInfo(
        batch=schemas.Batch.model_validate(batch),
        product=schemas.Product.model_validate(product),
        planting_records=[schemas.PlantingRecord.model_validate(r) for r in planting_records],
        agrochemical_usages=[schemas.AgrochemicalUsage.model_validate(u) for u in agrochemical_usages],
        test_results=[schemas.TestResult.model_validate(t) for t in test_results]
    )
    
    return traceability_info


@router.get("/batch-id/{batch_id}", response_model=schemas.TraceabilityInfo)
def get_traceability_by_batch_id(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    根据批次ID获取完整溯源信息
    
    Args:
        batch_id: 批次ID
        db: 数据库会话
        
    Returns:
        完整溯源信息
    """
    # 获取批次信息
    batch = crud.batch.get(db, id=batch_id)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    return get_traceability_by_batch_number(batch_number=batch.batch_number, db=db)


@router.get("/summary/{batch_number}")
def get_traceability_summary(
    batch_number: str,
    db: Session = Depends(get_db)
):
    """
    获取溯源信息摘要（简化版）
    用于快速显示关键信息
    
    Args:
        batch_number: 批次编号
        db: 数据库会话
        
    Returns:
        溯源信息摘要
    """
    # 获取批次信息
    batch = crud.batch.get_by_batch_number(db, batch_number=batch_number)
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    # 获取产品信息
    product = crud.product.get(db, id=batch.product_id)
    
    # 获取种植记录数量
    planting_count = db.query(models.PlantingRecord).filter(
        models.PlantingRecord.batch_id == batch.id
    ).count()
    
    # 获取农资使用记录数量
    usage_count = db.query(models.AgrochemicalUsage).filter(
        models.AgrochemicalUsage.batch_id == batch.id
    ).count()
    
    # 获取检测结果
    test_results = crud.test_result.get_by_batch_id(
        db, batch_id=batch.id, limit=10
    )
    
    # 统计检测结果
    passed_count = sum(1 for t in test_results if t.result == "合格")
    failed_count = sum(1 for t in test_results if t.result == "不合格")
    
    # 构建摘要信息
    summary = {
        "batch_number": batch.batch_number,
        "product_name": product.name if product else "未知产品",
        "product_category": product.category if product else None,
        "origin": product.origin if product else None,
        "supplier": product.supplier if product else None,
        "quantity": batch.quantity,
        "unit": batch.unit,
        "planting_date": batch.planting_date,
        "harvest_date": batch.harvest_date,
        "planting_records_count": planting_count,
        "agrochemical_usages_count": usage_count,
        "test_results_summary": {
            "total": len(test_results),
            "passed": passed_count,
            "failed": failed_count
        }
    }
    
    return summary

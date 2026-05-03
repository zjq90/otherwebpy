"""
统计API路由
提供系统统计数据查询功能
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app import crud

# 创建路由实例
router = APIRouter(
    prefix="/statistics",
    tags=["系统统计"],
    responses={404: {"description": "未找到"}},
)


@router.get("/")
def get_statistics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取系统统计数据
    
    Args:
        db: 数据库会话
        
    Returns:
        包含各类数据统计的字典
    """
    # 更新证书状态
    crud.certificate.update_certificate_status(db)
    
    # 获取即将过期的证书
    expiring_certificates = crud.certificate.get_expiring_soon(db)
    
    return {
        "products": crud.product.get_count(db),
        "batches": crud.batch.get_count(db),
        "planting_records": crud.planting_record.get_count(db),
        "agrochemical_usages": crud.agrochemical_usage.get_count(db),
        "test_results": crud.test_result.get_count(db),
        "certificates": crud.certificate.get_count(db),
        "expiring_certificates": len(expiring_certificates)
    }


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取系统摘要信息（用于首页展示）
    
    Args:
        db: 数据库会话
        
    Returns:
        包含系统摘要信息的字典
    """
    stats = get_statistics(db)
    
    return {
        "message": "系统运行正常",
        "statistics": stats,
        "has_data": (
            stats["products"] > 0 or 
            stats["batches"] > 0 or 
            stats["certificates"] > 0
        )
    }

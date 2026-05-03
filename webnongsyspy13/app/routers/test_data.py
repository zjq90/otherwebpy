"""
测试数据生成API路由
提供生成测试数据的接口，用于系统功能测试
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.test_data_generator import (
    generate_all_test_data,
    generate_test_products,
    generate_test_batches,
    generate_test_planting_records,
    generate_test_agrochemical_usages,
    generate_test_results,
    generate_test_certificates
)

# 创建路由实例
router = APIRouter(
    prefix="/test-data",
    tags=["测试数据"],
    responses={404: {"description": "未找到"}},
)


@router.post("/generate/")
def generate_all_data(
    db: Session = Depends(get_db)
):
    """
    生成所有测试数据
    包括产品、批次、种植记录、农资使用记录、检测结果、认证证书
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果统计信息
    """
    try:
        result = generate_all_test_data(db)
        return {
            "success": True,
            "message": result["message"],
            "total_created": result["total_created"],
            "details": {
                "products": result["products"]["created_count"],
                "batches": result["batches"]["created_count"],
                "planting_records": result["planting_records"]["created_count"],
                "agrochemical_usages": result["agrochemical_usages"]["created_count"],
                "test_results": result["test_results"]["created_count"],
                "certificates": result["certificates"]["created_count"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试数据失败: {str(e)}"
        )


@router.post("/generate/products/")
def generate_products(
    db: Session = Depends(get_db)
):
    """
    仅生成产品测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果
    """
    try:
        result = generate_test_products(db)
        return {
            "success": True,
            "message": f"成功生成 {result['created_count']} 个产品",
            "created_count": result["created_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成产品数据失败: {str(e)}"
        )


@router.post("/generate/batches/")
def generate_batches(
    db: Session = Depends(get_db)
):
    """
    仅生成批次测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果
    """
    try:
        result = generate_test_batches(db)
        return {
            "success": True,
            "message": f"成功生成 {result['created_count']} 个批次",
            "created_count": result["created_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成批次数据失败: {str(e)}"
        )


@router.post("/generate/planting-records/")
def generate_planting_records(
    db: Session = Depends(get_db)
):
    """
    仅生成种植记录测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果
    """
    try:
        result = generate_test_planting_records(db)
        return {
            "success": True,
            "message": f"成功生成 {result['created_count']} 条种植记录",
            "created_count": result["created_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成种植记录数据失败: {str(e)}"
        )


@router.post("/generate/agrochemical-usages/")
def generate_agrochemical_usages(
    db: Session = Depends(get_db)
):
    """
    仅生成农资使用记录测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果
    """
    try:
        result = generate_test_agrochemical_usages(db)
        return {
            "success": True,
            "message": f"成功生成 {result['created_count']} 条农资使用记录",
            "created_count": result["created_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成农资使用记录数据失败: {str(e)}"
        )


@router.post("/generate/test-results/")
def generate_test_results_api(
    db: Session = Depends(get_db)
):
    """
    仅生成检测结果测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果
    """
    try:
        result = generate_test_results(db)
        return {
            "success": True,
            "message": f"成功生成 {result['created_count']} 条检测结果",
            "created_count": result["created_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成检测结果数据失败: {str(e)}"
        )


@router.post("/generate/certificates/")
def generate_certificates(
    db: Session = Depends(get_db)
):
    """
    仅生成认证证书测试数据
    
    Args:
        db: 数据库会话
        
    Returns:
        生成结果
    """
    try:
        result = generate_test_certificates(db)
        return {
            "success": True,
            "message": f"成功生成 {result['created_count']} 个认证证书",
            "created_count": result["created_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成认证证书数据失败: {str(e)}"
        )


@router.get("/status/")
def get_test_data_status(
    db: Session = Depends(get_db)
):
    """
    获取测试数据状态
    统计数据库中各类数据的数量
    
    Args:
        db: 数据库会话
        
    Returns:
        数据统计信息
    """
    from app import crud
    
    try:
        return {
            "success": True,
            "statistics": {
                "products": crud.product.get_count(db),
                "batches": crud.batch.get_count(db),
                "planting_records": crud.planting_record.get_count(db),
                "agrochemical_usages": crud.agrochemical_usage.get_count(db),
                "test_results": crud.test_result.get_count(db),
                "certificates": crud.certificate.get_count(db)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据状态失败: {str(e)}"
        )

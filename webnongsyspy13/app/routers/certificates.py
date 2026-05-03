"""
认证证书API路由
提供认证证书的增删改查功能，包括到期提醒
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

# 创建路由实例
router = APIRouter(
    prefix="/certificates",
    tags=["认证证书管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/", response_model=schemas.Certificate, status_code=status.HTTP_201_CREATED)
def create_certificate(
    cert_in: schemas.CertificateCreate,
    db: Session = Depends(get_db)
):
    """
    创建新认证证书
    
    Args:
        cert_in: 认证证书创建数据
        db: 数据库会话
        
    Returns:
        创建的认证证书对象
    """
    # 检查证书编号是否已存在
    existing_cert = crud.certificate.get_by_certificate_number(
        db, certificate_number=cert_in.certificate_number
    )
    if existing_cert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="证书编号已存在"
        )
    
    # 如果指定了产品ID，检查产品是否存在
    if cert_in.product_id:
        product = crud.product.get(db, id=cert_in.product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的产品不存在"
            )
    
    # 创建认证证书
    cert = crud.certificate.create(db, obj_in=cert_in.model_dump())
    return cert


@router.get("/", response_model=List[schemas.Certificate])
def read_certificates(
    skip: int = 0,
    limit: int = 100,
    certificate_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取认证证书列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        certificate_type: 可选，按认证类型筛选
        db: 数据库会话
        
    Returns:
        认证证书列表
    """
    if certificate_type:
        certs = crud.certificate.get_by_type(
            db, certificate_type=certificate_type, skip=skip, limit=limit
        )
    else:
        certs = crud.certificate.get_multi(db, skip=skip, limit=limit)
    return certs


@router.get("/{cert_id}", response_model=schemas.Certificate)
def read_certificate(
    cert_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个认证证书
    
    Args:
        cert_id: 认证证书ID
        db: 数据库会话
        
    Returns:
        认证证书对象
    """
    cert = crud.certificate.get(db, id=cert_id)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="认证证书不存在"
        )
    return cert


@router.get("/number/{certificate_number}", response_model=schemas.Certificate)
def read_certificate_by_number(
    certificate_number: str,
    db: Session = Depends(get_db)
):
    """
    根据证书编号获取认证证书
    
    Args:
        certificate_number: 证书编号
        db: 数据库会话
        
    Returns:
        认证证书对象
    """
    cert = crud.certificate.get_by_certificate_number(db, certificate_number=certificate_number)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="认证证书不存在"
        )
    return cert


@router.get("/expiring-soon/", response_model=List[schemas.Certificate])
def read_expiring_soon_certificates(
    days: int = None,
    db: Session = Depends(get_db)
):
    """
    获取即将过期的认证证书
    
    Args:
        days: 提前提醒天数，默认使用配置中的值
        db: 数据库会话
        
    Returns:
        即将过期的认证证书列表
    """
    certs = crud.certificate.get_expiring_soon(db, days=days)
    return certs


@router.get("/expired/", response_model=List[schemas.Certificate])
def read_expired_certificates(
    db: Session = Depends(get_db)
):
    """
    获取已过期的认证证书
    
    Args:
        db: 数据库会话
        
    Returns:
        已过期的认证证书列表
    """
    certs = crud.certificate.get_expired(db)
    return certs


@router.put("/{cert_id}", response_model=schemas.Certificate)
def update_certificate(
    cert_id: int,
    cert_in: schemas.CertificateUpdate,
    db: Session = Depends(get_db)
):
    """
    更新认证证书
    
    Args:
        cert_id: 认证证书ID
        cert_in: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的认证证书对象
    """
    cert = crud.certificate.get(db, id=cert_id)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="认证证书不存在"
        )
    
    # 如果更新了证书编号，检查新编号是否已存在
    update_data = cert_in.model_dump(exclude_unset=True)
    if "certificate_number" in update_data:
        existing_cert = crud.certificate.get_by_certificate_number(
            db, certificate_number=update_data["certificate_number"]
        )
        if existing_cert and existing_cert.id != cert_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="证书编号已存在"
            )
    
    # 如果更新了产品ID，检查新产品是否存在
    if "product_id" in update_data and update_data["product_id"]:
        product = crud.product.get(db, id=update_data["product_id"])
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的产品不存在"
            )
    
    # 更新认证证书
    cert = crud.certificate.update(db, db_obj=cert, obj_in=update_data)
    return cert


@router.delete("/{cert_id}", response_model=schemas.Certificate)
def delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db)
):
    """
    删除认证证书
    
    Args:
        cert_id: 认证证书ID
        db: 数据库会话
        
    Returns:
        被删除的认证证书对象
    """
    cert = crud.certificate.get(db, id=cert_id)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="认证证书不存在"
        )
    
    # 删除认证证书
    cert = crud.certificate.remove(db, id=cert_id)
    return cert


@router.post("/update-status/", response_model=Dict[str, Any])
def update_certificates_status(
    db: Session = Depends(get_db)
):
    """
    更新所有认证证书的状态
    
    Args:
        db: 数据库会话
        
    Returns:
        更新结果
    """
    count = crud.certificate.update_certificate_status(db)
    return {"message": f"成功更新 {count} 个证书状态", "updated_count": count}

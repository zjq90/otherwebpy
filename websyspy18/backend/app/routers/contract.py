"""
合同与供应商管理模块 - API路由
包含供应商管理、合同管理、付款记录、服务质量评估等API接口
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.contract import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    ContractCreate, ContractUpdate, ContractResponse,
    ContractPaymentCreate, ContractPaymentUpdate, ContractPaymentResponse,
    ServiceEvaluationCreate, ServiceEvaluationUpdate, ServiceEvaluationResponse
)
from app.crud import contract as crud_contract

router = APIRouter()

# ==================== 供应商 API ====================

@router.post("/suppliers/", response_model=SupplierResponse, tags=["供应商管理"])
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    """
    创建供应商
    """
    if supplier.code:
        db_supplier = crud_contract.supplier.get_by_code(db, code=supplier.code)
        if db_supplier:
            raise HTTPException(status_code=400, detail="供应商编号已存在")
    return crud_contract.supplier.create(db=db, obj_in=supplier)

@router.get("/suppliers/", response_model=List[SupplierResponse], tags=["供应商管理"])
def read_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取供应商列表
    """
    if keyword:
        return crud_contract.supplier.search(db, keyword=keyword, skip=skip, limit=limit)
    if category:
        return crud_contract.supplier.get_by_category(db, category=category, skip=skip, limit=limit)
    if status:
        return crud_contract.supplier.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_contract.supplier.get_multi(db, skip=skip, limit=limit)

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["供应商管理"])
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    获取单个供应商
    """
    db_supplier = crud_contract.supplier.get(db, id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return db_supplier

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["供应商管理"])
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    """
    更新供应商
    """
    db_supplier = crud_contract.supplier.get(db, id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return crud_contract.supplier.update(db, db_obj=db_supplier, obj_in=supplier)

@router.delete("/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["供应商管理"])
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    删除供应商
    """
    db_supplier = crud_contract.supplier.get(db, id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return crud_contract.supplier.remove(db, id=supplier_id)

@router.get("/suppliers/{supplier_id}/statistics", tags=["供应商管理"])
def get_supplier_statistics(supplier_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取供应商评估统计
    """
    db_supplier = crud_contract.supplier.get(db, id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return crud_contract.service_evaluation.get_supplier_statistics(db, supplier_id=supplier_id)

# ==================== 合同 API ====================

@router.post("/contracts/", response_model=ContractResponse, tags=["合同管理"])
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    """
    创建合同
    """
    if contract.contract_no:
        db_contract = crud_contract.contract.get_by_contract_no(db, contract_no=contract.contract_no)
        if db_contract:
            raise HTTPException(status_code=400, detail="合同编号已存在")
    return crud_contract.contract.create(db=db, obj_in=contract)

@router.get("/contracts/", response_model=List[ContractResponse], tags=["合同管理"])
def read_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取合同列表
    """
    if keyword:
        return crud_contract.contract.search(db, keyword=keyword, skip=skip, limit=limit)
    if supplier_id:
        return crud_contract.contract.get_by_supplier(db, supplier_id=supplier_id, skip=skip, limit=limit)
    if status:
        return crud_contract.contract.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_contract.contract.get_multi(db, skip=skip, limit=limit)

@router.get("/contracts/{contract_id}", response_model=ContractResponse, tags=["合同管理"])
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    """
    获取单个合同
    """
    db_contract = crud_contract.contract.get(db, id=contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    return db_contract

@router.put("/contracts/{contract_id}", response_model=ContractResponse, tags=["合同管理"])
def update_contract(contract_id: int, contract: ContractUpdate, db: Session = Depends(get_db)):
    """
    更新合同
    """
    db_contract = crud_contract.contract.get(db, id=contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    return crud_contract.contract.update(db, db_obj=db_contract, obj_in=contract)

@router.delete("/contracts/{contract_id}", response_model=ContractResponse, tags=["合同管理"])
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    """
    删除合同
    """
    db_contract = crud_contract.contract.get(db, id=contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    return crud_contract.contract.remove(db, id=contract_id)

# ==================== 合同付款 API ====================

@router.post("/payments/", response_model=ContractPaymentResponse, tags=["合同付款"])
def create_payment(payment: ContractPaymentCreate, db: Session = Depends(get_db)):
    """
    创建合同付款记录
    """
    return crud_contract.contract_payment.create(db=db, obj_in=payment)

@router.get("/payments/", response_model=List[ContractPaymentResponse], tags=["合同付款"])
def read_payments(
    skip: int = 0,
    limit: int = 100,
    contract_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取合同付款列表
    """
    if contract_id:
        return crud_contract.contract_payment.get_by_contract(db, contract_id=contract_id, skip=skip, limit=limit)
    if status:
        return crud_contract.contract_payment.get_by_status(db, status=status, skip=skip, limit=limit)
    return crud_contract.contract_payment.get_multi(db, skip=skip, limit=limit)

@router.get("/payments/{payment_id}", response_model=ContractPaymentResponse, tags=["合同付款"])
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    """
    获取单个合同付款记录
    """
    db_payment = crud_contract.contract_payment.get(db, id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="付款记录不存在")
    return db_payment

@router.put("/payments/{payment_id}", response_model=ContractPaymentResponse, tags=["合同付款"])
def update_payment(payment_id: int, payment: ContractPaymentUpdate, db: Session = Depends(get_db)):
    """
    更新合同付款记录
    """
    db_payment = crud_contract.contract_payment.get(db, id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="付款记录不存在")
    return crud_contract.contract_payment.update(db, db_obj=db_payment, obj_in=payment)

@router.delete("/payments/{payment_id}", response_model=ContractPaymentResponse, tags=["合同付款"])
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """
    删除合同付款记录
    """
    db_payment = crud_contract.contract_payment.get(db, id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="付款记录不存在")
    return crud_contract.contract_payment.remove(db, id=payment_id)

# ==================== 服务质量评估 API ====================

@router.post("/evaluations/", response_model=ServiceEvaluationResponse, tags=["服务质量评估"])
def create_evaluation(evaluation: ServiceEvaluationCreate, db: Session = Depends(get_db)):
    """
    创建服务质量评估
    """
    return crud_contract.service_evaluation.create(db=db, obj_in=evaluation)

@router.get("/evaluations/", response_model=List[ServiceEvaluationResponse], tags=["服务质量评估"])
def read_evaluations(
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[int] = None,
    period: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取服务质量评估列表
    """
    if supplier_id:
        return crud_contract.service_evaluation.get_by_supplier(db, supplier_id=supplier_id, skip=skip, limit=limit)
    if period:
        return crud_contract.service_evaluation.get_by_period(db, period=period, skip=skip, limit=limit)
    return crud_contract.service_evaluation.get_multi(db, skip=skip, limit=limit)

@router.get("/evaluations/{evaluation_id}", response_model=ServiceEvaluationResponse, tags=["服务质量评估"])
def read_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """
    获取单个服务质量评估
    """
    db_evaluation = crud_contract.service_evaluation.get(db, id=evaluation_id)
    if db_evaluation is None:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    return db_evaluation

@router.put("/evaluations/{evaluation_id}", response_model=ServiceEvaluationResponse, tags=["服务质量评估"])
def update_evaluation(evaluation_id: int, evaluation: ServiceEvaluationUpdate, db: Session = Depends(get_db)):
    """
    更新服务质量评估
    """
    db_evaluation = crud_contract.service_evaluation.get(db, id=evaluation_id)
    if db_evaluation is None:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    return crud_contract.service_evaluation.update(db, db_obj=db_evaluation, obj_in=evaluation)

@router.delete("/evaluations/{evaluation_id}", response_model=ServiceEvaluationResponse, tags=["服务质量评估"])
def delete_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """
    删除服务质量评估
    """
    db_evaluation = crud_contract.service_evaluation.get(db, id=evaluation_id)
    if db_evaluation is None:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    return crud_contract.service_evaluation.remove(db, id=evaluation_id)

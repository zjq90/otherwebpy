from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.crud import contract_crud

router = APIRouter(prefix="/api/contracts", tags=["合同管理"])

@router.get("/", response_model=schemas.ContractList)
def read_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from app.models import Contract, Order
    from sqlalchemy import or_
    
    skip = (page - 1) * limit
    query = db.query(Contract)
    
    if keyword:
        query = query.join(Order, Contract.order_id == Order.id).filter(
            or_(
                Contract.contract_number.contains(keyword),
                Contract.party_b.contains(keyword),
                Order.id == int(keyword) if keyword.isdigit() else False
            )
        )
    
    if status:
        query = query.filter(Contract.status == status)
    
    total = query.count()
    contracts = query.order_by(Contract.contract_date.desc()).offset(skip).limit(limit).all()
    
    return {"contracts": contracts, "total": total}

@router.get("/{contract_id}", response_model=schemas.Contract)
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_crud.get(db, id=contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract

@router.get("/order/{order_id}", response_model=schemas.Contract)
def get_contract_by_order(order_id: int, db: Session = Depends(get_db)):
    contract = contract_crud.get_by_order(db, order_id=order_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="该订单暂无合同")
    return contract

@router.get("/number/{contract_number}", response_model=schemas.Contract)
def get_contract_by_number(contract_number: str, db: Session = Depends(get_db)):
    contract = contract_crud.get_by_number(db, contract_number=contract_number)
    if contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract

@router.post("/", response_model=schemas.Contract)
def create_contract(contract: schemas.ContractCreate, db: Session = Depends(get_db)):
    existing = contract_crud.get_by_order(db, order_id=contract.order_id)
    if existing:
        raise HTTPException(status_code=400, detail="该订单已存在合同")
    contract_data = contract.model_dump()
    return contract_crud.create(db, obj_in=contract_data)

@router.put("/{contract_id}", response_model=schemas.Contract)
def update_contract(
    contract_id: int,
    contract: schemas.ContractUpdate,
    db: Session = Depends(get_db)
):
    db_contract = contract_crud.get(db, id=contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    update_data = contract.model_dump(exclude_unset=True)
    return contract_crud.update(db, db_obj=db_contract, obj_in=update_data)

@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = contract_crud.get(db, id=contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    contract_crud.remove(db, id=contract_id)
    return {"message": "删除成功"}

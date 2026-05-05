from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from app.database import get_db
from app.schemas import (
    SettlementCreate, SettlementUpdate, SettlementResponse
)
from app.crud import settlement_crud, purchase_order_crud

router = APIRouter(
    prefix="/api/settlements",
    tags=["结算管理"],
    responses={404: {"description": "未找到"}}
)

@router.post("/", response_model=SettlementResponse, summary="创建结算单")
def create_settlement(settlement: SettlementCreate, db: Session = Depends(get_db)):
    """
    创建新的结算单
    - **settlement: 结算单信息
    """
    purchase_order = purchase_order_crud.get(db, settlement.purchase_order_id)
    if purchase_order is None:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    
    existing_settlement = settlement_crud.get_by_purchase_order(db, settlement.purchase_order_id)
    if existing_settlement:
        raise HTTPException(status_code=400, detail="该采购订单已存在结算单")
    
    db_settlement = settlement_crud.create(db, settlement)
    if db_settlement is None:
        raise HTTPException(status_code=500, detail="创建结算单失败")
    
    return db_settlement

@router.get("/", response_model=List[SettlementResponse], summary="获取结算单列表")
def read_settlements(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取所有结算单列表
    - **skip**: 跳过数量
    - **limit**: 返回数量限制
    """
    settlements = settlement_crud.get_multi(db, skip=skip, limit=limit)
    return settlements

@router.get("/pending-payments", response_model=List[SettlementResponse], summary="获取待付款结算单")
def read_pending_payments(db: Session = Depends(get_db)):
    """
    获取所有待付款或部分付款的结算单
    """
    settlements = settlement_crud.get_pending_payments(db)
    return settlements

@router.get("/by-purchase-order/{purchase_order_id}", response_model=SettlementResponse, summary="根据采购订单获取结算单")
def read_settlement_by_purchase_order(purchase_order_id: int, db: Session = Depends(get_db)):
    """
    根据采购订单ID获取对应的结算单
    - **purchase_order_id**: 采购订单ID
    """
    settlement = settlement_crud.get_by_purchase_order(db, purchase_order_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="该采购订单暂无结算单")
    return settlement

@router.get("/{settlement_id}", response_model=SettlementResponse, summary="获取单个结算单")
def read_settlement(settlement_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取结算单
    - **settlement_id**: 结算单ID
    """
    settlement = settlement_crud.get(db, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="结算单不存在")
    return settlement

@router.put("/{settlement_id}", response_model=SettlementResponse, summary="更新结算单")
def update_settlement(settlement_id: int, settlement: SettlementUpdate, db: Session = Depends(get_db)):
    """
    更新结算单（主要用于更新付款状态和已付金额）
    - **settlement_id**: 结算单ID
    - **settlement**: 更新的结算单信息
    """
    db_settlement = settlement_crud.get(db, settlement_id)
    if db_settlement is None:
        raise HTTPException(status_code=404, detail="结算单不存在")
    
    if settlement.paid_amount is not None:
        if settlement.paid_amount < 0:
            raise HTTPException(status_code=400, detail="已付金额不能为负数")
        
        if settlement.paid_amount >= db_settlement.total_payable:
            db_settlement.paid_amount = settlement.paid_amount
            db_settlement.payment_status = "已付款"
        elif settlement.paid_amount > 0:
            db_settlement.paid_amount = settlement.paid_amount
            db_settlement.payment_status = "部分付款"
        else:
            db_settlement.paid_amount = settlement.paid_amount
        
        if settlement.remark is not None:
            db_settlement.remark = settlement.remark
        
        db.commit()
        db.refresh(db_settlement)
    else:
        db_settlement = settlement_crud.update(db, db_settlement, settlement)
    
    return db_settlement

@router.delete("/{settlement_id}", summary="删除结算单")
def delete_settlement(settlement_id: int, db: Session = Depends(get_db)):
    """
    删除结算单
    - **settlement_id**: 结算单ID
    """
    db_settlement = settlement_crud.get(db, settlement_id)
    if db_settlement is None:
        raise HTTPException(status_code=404, detail="结算单不存在")
    settlement_crud.remove(db, settlement_id)
    return {"message": "删除成功", "id": settlement_id}

class PaymentRequest(BaseModel):
    amount: float

@router.post("/{settlement_id}/pay", response_model=SettlementResponse, summary="支付结算单")
def pay_settlement(
    settlement_id: int, 
    payment: PaymentRequest,
    db: Session = Depends(get_db)
):
    """
    支付结算单
    - **settlement_id**: 结算单ID
    - **payment**: 支付信息（包含金额）
    """
    amount = payment.amount
    if amount <= 0:
        raise HTTPException(status_code=400, detail="支付金额必须大于0")
    
    db_settlement = settlement_crud.get(db, settlement_id)
    if db_settlement is None:
        raise HTTPException(status_code=404, detail="结算单不存在")
    
    if db_settlement.payment_status == "已付款":
        raise HTTPException(status_code=400, detail="该结算单已全额付款")
    
    new_paid_amount = db_settlement.paid_amount + amount
    
    if new_paid_amount > db_settlement.total_payable:
        raise HTTPException(status_code=400, detail="支付金额不能超过应付总额")
    
    db_settlement.paid_amount = new_paid_amount
    
    if new_paid_amount >= db_settlement.total_payable:
        db_settlement.payment_status = "已付款"
    else:
        db_settlement.payment_status = "部分付款"
    
    db.commit()
    db.refresh(db_settlement)
    
    return db_settlement

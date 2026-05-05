from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Order, Withdrawal
from schemas import (
    UserResponse, UserUpdate, UserStats,
    WithdrawalCreate, WithdrawalResponse
)
from utils import get_current_user

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("/profile", response_model=UserResponse, summary="获取个人信息")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户的个人信息
    """
    return current_user


@router.put("/profile", response_model=UserResponse, summary="更新个人信息")
async def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户的个人信息
    """
    update_data = user_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/stats", response_model=UserStats, summary="获取业绩统计")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取回收人员的业绩统计
    - 总订单数、总重量、总收益
    - 今日订单数、今日重量、今日收益
    """
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    today_orders = db.query(func.count(Order.id)).filter(
        Order.collector_id == current_user.id,
        Order.status == "completed",
        Order.completed_at >= today_start
    ).scalar() or 0
    
    today_weight = db.query(func.sum(Order.actual_weight)).filter(
        Order.collector_id == current_user.id,
        Order.status == "completed",
        Order.completed_at >= today_start
    ).scalar() or 0.0
    
    today_income = db.query(func.sum(Order.total_amount)).filter(
        Order.collector_id == current_user.id,
        Order.status == "completed",
        Order.completed_at >= today_start
    ).scalar() or 0.0
    
    return UserStats(
        total_orders=current_user.total_orders,
        total_weight=current_user.total_weight,
        total_income=current_user.total_income,
        today_orders=today_orders,
        today_weight=today_weight,
        today_income=today_income
    )


@router.post("/withdrawal", response_model=WithdrawalResponse, summary="申请提现")
async def create_withdrawal(
    withdrawal_data: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    回收人员申请提现
    - 检查余额是否足够
    - 创建提现记录
    """
    if withdrawal_data.amount > current_user.total_income:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足"
        )
    
    if withdrawal_data.amount < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="最低提现金额为10元"
        )
    
    new_withdrawal = Withdrawal(
        user_id=current_user.id,
        amount=withdrawal_data.amount,
        bank_card=withdrawal_data.bank_card,
        bank_name=withdrawal_data.bank_name,
        account_name=withdrawal_data.account_name,
        status="pending"
    )
    
    db.add(new_withdrawal)
    db.commit()
    db.refresh(new_withdrawal)
    
    return new_withdrawal


@router.get("/withdrawals", response_model=List[WithdrawalResponse], summary="获取提现记录")
async def get_withdrawals(
    status: Optional[str] = Query(None, description="提现状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的提现记录
    """
    query = db.query(Withdrawal).filter(Withdrawal.user_id == current_user.id)
    
    if status:
        query = query.filter(Withdrawal.status == status)
    
    withdrawals = query.order_by(Withdrawal.created_at.desc()).all()
    
    return withdrawals


@router.get("/withdrawals/{withdrawal_id}", response_model=WithdrawalResponse, summary="获取提现详情")
async def get_withdrawal_detail(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取提现记录详情
    """
    withdrawal = db.query(Withdrawal).filter(
        Withdrawal.id == withdrawal_id,
        Withdrawal.user_id == current_user.id
    ).first()
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提现记录不存在"
        )
    
    return withdrawal

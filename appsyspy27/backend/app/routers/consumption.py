"""
消费记录路由模块
包含消费记录查询、月度账单导出等接口
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.order import ConsumptionRecord
from app.schemas.order import (
    ConsumptionRecordResponse, MonthlyBillResponse
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/consumptions", tags=["消费记录管理"])


@router.get("/my", response_model=List[ConsumptionRecordResponse], summary="获取我的消费记录")
def get_my_consumptions(
    record_type: Optional[str] = Query(None, description="消费类型筛选"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的消费记录列表
    
    - **record_type**: 消费类型（PURCHASE购卡, RENEWAL续费, LESSON课程扣费, GOODS商品消费, RECHARGE充值, REFUND退款）
    - **start_date**: 开始日期（格式：YYYY-MM-DD）
    - **end_date**: 结束日期（格式：YYYY-MM-DD）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    query = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_id == current_user.id
    )
    
    # 按类型筛选
    if record_type:
        query = query.filter(ConsumptionRecord.record_type == record_type)
    
    # 按日期范围筛选
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(ConsumptionRecord.created_at >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(ConsumptionRecord.created_at <= end_dt)
        except ValueError:
            pass
    
    # 按时间倒序排列
    query = query.order_by(ConsumptionRecord.created_at.desc())
    
    # 分页
    records = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return [ConsumptionRecordResponse.model_validate(r) for r in records]


@router.get("/my/{record_id}", response_model=ConsumptionRecordResponse, summary="获取消费记录详情")
def get_consumption_detail(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定消费记录的详细信息
    
    - **record_id**: 消费记录ID
    """
    from fastapi import HTTPException, status
    
    record = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.id == record_id,
        ConsumptionRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消费记录不存在或不属于当前用户"
        )
    
    return ConsumptionRecordResponse.model_validate(record)


@router.get("/monthly-bill", response_model=MonthlyBillResponse, summary="获取月度账单")
def get_monthly_bill(
    year: int = Query(..., ge=2000, le=2100, description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定月份的消费账单
    
    - **year**: 年份（如：2024）
    - **month**: 月份（1-12）
    """
    # 计算月份的开始和结束时间
    if month == 12:
        next_month_year = year + 1
        next_month = 1
    else:
        next_month_year = year
        next_month = month + 1
    
    start_dt = datetime(year, month, 1, 0, 0, 0)
    end_dt = datetime(next_month_year, next_month, 1, 0, 0, 0)
    
    # 查询该月的消费记录
    records = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_id == current_user.id,
        ConsumptionRecord.created_at >= start_dt,
        ConsumptionRecord.created_at < end_dt
    ).order_by(ConsumptionRecord.created_at.desc()).all()
    
    # 计算总金额
    total_amount = Decimal("0")
    total_count = len(records)
    
    for record in records:
        if record.amount > 0:  # 只计算支出
            total_amount += record.amount
    
    return MonthlyBillResponse(
        year=year,
        month=month,
        total_amount=total_amount,
        total_count=total_count,
        records=[ConsumptionRecordResponse.model_validate(r) for r in records]
    )


@router.get("/statistics", summary="获取消费统计")
def get_consumption_statistics(
    period: str = Query("month", description="统计周期：day/week/month/year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取消费统计数据
    
    - **period**: 统计周期（day日, week周, month月, year年）
    """
    now = datetime.now()
    
    # 根据周期确定时间范围
    if period == "day":
        start_dt = datetime(now.year, now.month, now.day)
        group_format = "%H"
    elif period == "week":
        start_dt = now - (now.weekday() * 24 * 60 * 60)
        group_format = "%w"
    elif period == "year":
        start_dt = datetime(now.year, 1, 1)
        group_format = "%m"
    else:  # month
        start_dt = datetime(now.year, now.month, 1)
        group_format = "%d"
    
    # 统计
    records = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_id == current_user.id,
        ConsumptionRecord.created_at >= start_dt
    ).all()
    
    total_amount = sum(r.amount for r in records if r.amount > 0)
    total_count = len(records)
    
    # 按类型统计
    type_stats = {}
    for r in records:
        if r.record_type not in type_stats:
            type_stats[r.record_type] = {"count": 0, "amount": Decimal("0")}
        type_stats[r.record_type]["count"] += 1
        if r.amount > 0:
            type_stats[r.record_type]["amount"] += r.amount
    
    return {
        "period": period,
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": now.strftime("%Y-%m-%d"),
        "total_amount": total_amount,
        "total_count": total_count,
        "type_statistics": {
            k: {
                "count": v["count"],
                "amount": float(v["amount"])
            } for k, v in type_stats.items()
        }
    }

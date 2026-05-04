"""
催缴管理API路由
实现催缴记录管理和催缴功能
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import (
    Reminder as ReminderModel,
    Bill as BillModel,
    Property as PropertyModel,
)
from app.schemas import (
    Reminder as ReminderSchema,
    ReminderCreate as ReminderCreateSchema,
    BillStatus,
)

router = APIRouter(
    prefix="/api/reminders",
    tags=["催缴管理"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", response_model=List[ReminderSchema], summary="获取催缴记录列表")
def get_reminders(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    bill_id: Optional[int] = Query(None, description="账单ID筛选"),
    method: Optional[str] = Query(None, description="催缴方式筛选"),
    db: Session = Depends(get_db)
):
    """
    获取所有催缴记录列表，支持分页和筛选
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **bill_id**: 按账单ID筛选
    - **method**: 按催缴方式筛选
    """
    query = db.query(ReminderModel)
    
    if bill_id:
        query = query.filter(ReminderModel.bill_id == bill_id)
    if method:
        query = query.filter(ReminderModel.method == method)
    
    reminders = query.order_by(ReminderModel.created_at.desc()).offset(skip).limit(limit).all()
    return reminders


@router.get("/{reminder_id}", response_model=ReminderSchema, summary="获取单个催缴记录详情")
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个催缴记录详情
    
    - **reminder_id**: 催缴记录ID
    """
    reminder = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
    if reminder is None:
        raise HTTPException(status_code=404, detail="催缴记录不存在")
    return reminder


@router.post("/", response_model=ReminderSchema, summary="创建催缴记录")
def create_reminder(
    reminder_data: ReminderCreateSchema,
    db: Session = Depends(get_db)
):
    """
    创建新的催缴记录
    
    - **reminder_data**: 催缴记录信息
    """
    # 验证账单是否存在
    bill = db.query(BillModel).filter(BillModel.id == reminder_data.bill_id).first()
    if bill is None:
        raise HTTPException(status_code=400, detail="账单不存在")
    
    # 查询该账单已有的催缴次数
    existing_count = db.query(func.count(ReminderModel.id)).filter(
        ReminderModel.bill_id == reminder_data.bill_id
    ).scalar()
    
    db_reminder = ReminderModel(
        **reminder_data.dict(),
        reminder_count=existing_count + 1
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


@router.post("/bill/{bill_id}", response_model=ReminderSchema, summary="对账单发送催缴")
def send_reminder(
    bill_id: int,
    method: str = Query("notice", description="催缴方式: sms/phone/notice/wechat"),
    operator: Optional[str] = Query(None, description="执行人"),
    db: Session = Depends(get_db)
):
    """
    对指定账单发送催缴通知
    
    - **bill_id**: 账单ID
    - **method**: 催缴方式
    - **operator**: 执行人
    """
    # 验证账单是否存在
    bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    # 检查账单状态
    if bill.status not in [BillStatus.PENDING.value, BillStatus.PARTIAL.value, BillStatus.OVERDUE.value]:
        raise HTTPException(status_code=400, detail="该账单无需催缴")
    
    # 查询该账单已有的催缴次数
    existing_count = db.query(func.count(ReminderModel.id)).filter(
        ReminderModel.bill_id == bill_id
    ).scalar()
    
    # 生成催缴内容
    property_obj = bill.property
    fee_item = bill.fee_item
    content = (
        f"催缴通知单\n"
        f"业主: {property_obj.owner_name if property_obj else '未知'}\n"
        f"房产: {property_obj.property_number if property_obj else '未知'}\n"
        f"费用项目: {fee_item.name if fee_item else '未知'}\n"
        f"计费周期: {bill.billing_year}年{bill.billing_month}月\n"
        f"应缴金额: {bill.amount}元\n"
        f"已缴金额: {bill.paid_amount}元\n"
        f"待缴金额: {bill.amount - bill.paid_amount}元\n"
        f"缴费截止日期: {bill.due_date}\n\n"
        f"请尽快缴费，感谢您的配合！"
    )
    
    db_reminder = ReminderModel(
        bill_id=bill_id,
        method=method,
        reminder_count=existing_count + 1,
        content=content,
        operator=operator
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


@router.post("/batch-overdue", summary="批量对逾期账单发送催缴")
def batch_remind_overdue(
    method: str = Query("notice", description="催缴方式: sms/phone/notice/wechat"),
    operator: Optional[str] = Query(None, description="执行人"),
    db: Session = Depends(get_db)
):
    """
    批量对所有逾期账单发送催缴通知
    
    - **method**: 催缴方式
    - **operator**: 执行人
    """
    # 查询所有逾期账单
    overdue_bills = db.query(BillModel).filter(
        BillModel.status == BillStatus.OVERDUE.value
    ).all()
    
    if not overdue_bills:
        return {"message": "没有逾期账单需要催缴", "count": 0}
    
    reminded_count = 0
    
    for bill in overdue_bills:
        # 查询该账单已有的催缴次数
        existing_count = db.query(func.count(ReminderModel.id)).filter(
            ReminderModel.bill_id == bill.id
        ).scalar()
        
        # 生成催缴内容
        property_obj = bill.property
        fee_item = bill.fee_item
        content = (
            f"催缴通知单\n"
            f"【逾期提醒】\n"
            f"业主: {property_obj.owner_name if property_obj else '未知'}\n"
            f"房产: {property_obj.property_number if property_obj else '未知'}\n"
            f"费用项目: {fee_item.name if fee_item else '未知'}\n"
            f"计费周期: {bill.billing_year}年{bill.billing_month}月\n"
            f"应缴金额: {bill.amount}元\n"
            f"已缴金额: {bill.paid_amount}元\n"
            f"待缴金额: {bill.amount - bill.paid_amount}元\n"
            f"缴费截止日期: {bill.due_date}\n\n"
            f"您的账单已逾期，请尽快缴费，感谢您的配合！"
        )
        
        db_reminder = ReminderModel(
            bill_id=bill.id,
            method=method,
            reminder_count=existing_count + 1,
            content=content,
            operator=operator
        )
        db.add(db_reminder)
        reminded_count += 1
    
    db.commit()
    
    return {
        "message": f"已对 {reminded_count} 个逾期账单发送催缴",
        "count": reminded_count
    }


@router.get("/bill/{bill_id}/history", response_model=List[ReminderSchema], summary="获取账单催缴历史")
def get_bill_reminder_history(
    bill_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定账单的催缴历史记录
    
    - **bill_id**: 账单ID
    """
    # 验证账单是否存在
    bill = db.query(BillModel).filter(BillModel.id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    reminders = db.query(ReminderModel).filter(
        ReminderModel.bill_id == bill_id
    ).order_by(ReminderModel.reminder_count.desc()).all()
    
    return reminders


@router.get("/stats/summary", summary="获取催缴统计信息")
def get_reminder_stats(
    db: Session = Depends(get_db)
):
    """
    获取催缴统计信息
    """
    # 总催缴次数
    total_reminders = db.query(func.count(ReminderModel.id)).scalar() or 0
    
    # 按催缴方式统计
    method_stats = db.query(
        ReminderModel.method,
        func.count(ReminderModel.id).label("count")
    ).group_by(ReminderModel.method).all()
    
    # 逾期账单数量
    overdue_count = db.query(func.count(BillModel.id)).filter(
        BillModel.status == BillStatus.OVERDUE.value
    ).scalar() or 0
    
    return {
        "total_reminders": total_reminders,
        "overdue_bills_count": overdue_count,
        "method_statistics": [
            {"method": stat.method, "count": stat.count}
            for stat in method_stats
        ]
    }

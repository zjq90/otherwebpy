"""
续费提醒相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from config.database import get_db
from schemas.reminder import (
    RenewalReminder, RenewalReminderCreate, RenewalReminderUpdate, RenewalReminderListResponse
)
from crud.reminder import reminder_crud
from crud.member import member_crud, member_card_crud
from models.reminder import ReminderType, ReminderStatus

router = APIRouter(prefix="/api/reminders", tags=["续费提醒管理"])


@router.get("/", response_model=RenewalReminderListResponse, summary="获取提醒记录列表")
def get_reminders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    reminder_type: Optional[str] = Query(None, description="提醒类型"),
    status: Optional[str] = Query(None, description="提醒状态"),
    db: Session = Depends(get_db)
):
    """
    获取续费提醒记录列表
    """
    skip = (page - 1) * page_size
    reminders, total = reminder_crud.get_list(
        db, skip=skip, limit=page_size,
        member_id=member_id, reminder_type=reminder_type, status=status
    )
    return RenewalReminderListResponse(
        total=total,
        items=reminders,
        page=page,
        page_size=page_size
    )


@router.get("/pending", response_model=List[RenewalReminder], summary="获取待发送的提醒")
def get_pending_reminders(db: Session = Depends(get_db)):
    """
    获取所有待发送的续费提醒
    """
    return reminder_crud.get_pending_reminders(db)


@router.get("/{reminder_id}", response_model=RenewalReminder, summary="获取提醒详情")
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取提醒详情
    """
    db_reminder = reminder_crud.get_by_id(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="提醒记录不存在")
    return db_reminder


@router.post("/", response_model=RenewalReminder, summary="创建提醒记录")
def create_reminder(reminder_in: RenewalReminderCreate, db: Session = Depends(get_db)):
    """
    创建新的续费提醒记录
    """
    # 检查会员是否存在
    db_member = member_crud.get_by_id(db, member_id=reminder_in.member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 检查会员卡是否存在
    db_card = member_card_crud.get_by_id(db, card_id=reminder_in.member_card_id)
    if db_card is None:
        raise HTTPException(status_code=404, detail="会员卡不存在")
    
    return reminder_crud.create(db, reminder_in=reminder_in)


@router.put("/{reminder_id}", response_model=RenewalReminder, summary="更新提醒记录")
def update_reminder(
    reminder_id: int,
    reminder_in: RenewalReminderUpdate,
    db: Session = Depends(get_db)
):
    """
    更新提醒记录信息
    """
    db_reminder = reminder_crud.get_by_id(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="提醒记录不存在")
    
    return reminder_crud.update(db, db_reminder=db_reminder, reminder_in=reminder_in)


@router.post("/{reminder_id}/send", response_model=RenewalReminder, summary="标记为已发送")
def mark_reminder_as_sent(reminder_id: int, db: Session = Depends(get_db)):
    """
    标记提醒为已发送
    """
    db_reminder = reminder_crud.get_by_id(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="提醒记录不存在")
    
    return reminder_crud.mark_as_sent(db, db_reminder=db_reminder)


@router.post("/{reminder_id}/fail", response_model=RenewalReminder, summary="标记为发送失败")
def mark_reminder_as_failed(
    reminder_id: int,
    error_message: str = Query(..., description="错误信息"),
    db: Session = Depends(get_db)
):
    """
    标记提醒为发送失败
    """
    db_reminder = reminder_crud.get_by_id(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="提醒记录不存在")
    
    return reminder_crud.mark_as_failed(
        db, db_reminder=db_reminder, error_message=error_message
    )


@router.post("/{reminder_id}/renewed", response_model=RenewalReminder, summary="标记为已续费")
def mark_reminder_as_renewed(
    reminder_id: int,
    renewal_method: str = Query("offline", description="续费方式（offline/online）"),
    db: Session = Depends(get_db)
):
    """
    标记提醒为已续费
    """
    db_reminder = reminder_crud.get_by_id(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="提醒记录不存在")
    
    return reminder_crud.mark_as_renewed(
        db, db_reminder=db_reminder, renewal_method=renewal_method
    )


@router.post("/generate-for-expiring", summary="为即将到期的会员卡生成提醒")
def generate_reminders_for_expiring(db: Session = Depends(get_db)):
    """
    为即将到期的会员卡自动生成续费提醒
    - 到期前7天：生成7天提醒
    - 到期前3天：生成3天提醒
    """
    today = datetime.now().date()
    seven_days_later = today + timedelta(days=7)
    three_days_later = today + timedelta(days=3)
    
    # 获取7天后到期的会员卡
    cards_7days = member_card_crud.get_expiring_soon(db, days=7)
    # 获取3天后到期的会员卡
    cards_3days = member_card_crud.get_expiring_soon(db, days=3)
    
    generated_count = 0
    
    # 处理7天到期提醒
    for card in cards_7days:
        member = member_crud.get_by_id(db, member_id=card.member_id)
        if member:
            reminder = reminder_crud.create_reminder_for_card(
                db,
                member_id=member.id,
                member_card_id=card.id,
                reminder_type=ReminderType.SEVEN_DAYS.value,
                valid_to=card.valid_to,
                member_name=member.name,
                card_type=card.card_type
            )
            if reminder:
                generated_count += 1
    
    # 处理3天到期提醒
    for card in cards_3days:
        member = member_crud.get_by_id(db, member_id=card.member_id)
        if member:
            reminder = reminder_crud.create_reminder_for_card(
                db,
                member_id=member.id,
                member_card_id=card.id,
                reminder_type=ReminderType.THREE_DAYS.value,
                valid_to=card.valid_to,
                member_name=member.name,
                card_type=card.card_type
            )
            if reminder:
                generated_count += 1
    
    return {
        "message": f"成功生成 {generated_count} 条续费提醒",
        "generated_count": generated_count,
        "cards_7days": len(cards_7days),
        "cards_3days": len(cards_3days)
    }


@router.post("/send-pending", summary="发送所有待发送的提醒")
def send_pending_reminders(db: Session = Depends(get_db)):
    """
    模拟发送所有待发送的提醒
    实际应用中应该集成短信/微信/邮件发送服务
    """
    pending_reminders = reminder_crud.get_pending_reminders(db)
    
    sent_count = 0
    failed_count = 0
    
    for reminder in pending_reminders:
        # 模拟发送（实际项目中应调用真实的发送服务）
        try:
            # 这里可以添加真实的发送逻辑
            # 例如：短信服务、微信模板消息、邮件服务等
            print(f"发送提醒: {reminder.message_content}")
            
            # 标记为已发送
            reminder_crud.mark_as_sent(db, db_reminder=reminder)
            sent_count += 1
        except Exception as e:
            # 标记为发送失败
            reminder_crud.mark_as_failed(
                db, db_reminder=reminder, error_message=str(e)
            )
            failed_count += 1
    
    return {
        "message": f"发送完成：成功 {sent_count} 条，失败 {failed_count} 条",
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total": len(pending_reminders)
    }

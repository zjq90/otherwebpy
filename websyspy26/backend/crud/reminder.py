"""
续费提醒相关CRUD操作
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from models.reminder import RenewalReminder, ReminderType, ReminderStatus, ReminderChannel
from schemas.reminder import RenewalReminderCreate, RenewalReminderUpdate


class ReminderCRUD:
    """续费提醒CRUD操作类"""

    def get_by_id(self, db: Session, reminder_id: int) -> Optional[RenewalReminder]:
        """根据ID获取提醒记录"""
        return db.query(RenewalReminder).filter(RenewalReminder.id == reminder_id).first()

    def get_list(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        member_id: Optional[int] = None,
        reminder_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[RenewalReminder], int]:
        """
        获取提醒记录列表
        返回：(提醒列表, 总数)
        """
        query = db.query(RenewalReminder)
        
        if member_id:
            query = query.filter(RenewalReminder.member_id == member_id)
        
        if reminder_type:
            query = query.filter(RenewalReminder.reminder_type == reminder_type)
        
        if status:
            query = query.filter(RenewalReminder.status == status)
        
        total = query.count()
        reminders = query.order_by(RenewalReminder.created_at.desc()).offset(skip).limit(limit).all()
        
        return reminders, total

    def get_pending_reminders(self, db: Session) -> List[RenewalReminder]:
        """获取待发送的提醒"""
        now = datetime.now()
        return db.query(RenewalReminder).filter(
            RenewalReminder.status == ReminderStatus.PENDING.value,
            RenewalReminder.scheduled_time <= now
        ).all()

    def get_by_member_card_id(self, db: Session, member_card_id: int) -> List[RenewalReminder]:
        """获取会员卡的所有提醒记录"""
        return db.query(RenewalReminder).filter(
            RenewalReminder.member_card_id == member_card_id
        ).order_by(RenewalReminder.created_at.desc()).all()

    def check_reminder_exists(
        self, 
        db: Session, 
        member_card_id: int, 
        reminder_type: str
    ) -> bool:
        """
        检查会员卡是否已存在指定类型的提醒
        """
        return db.query(RenewalReminder).filter(
            RenewalReminder.member_card_id == member_card_id,
            RenewalReminder.reminder_type == reminder_type
        ).first() is not None

    def create(self, db: Session, reminder_in: RenewalReminderCreate) -> RenewalReminder:
        """创建提醒记录"""
        db_reminder = RenewalReminder(**reminder_in.model_dump())
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    def create_reminder_for_card(
        self,
        db: Session,
        member_id: int,
        member_card_id: int,
        reminder_type: str,
        valid_to: datetime.date,
        member_name: str,
        card_type: str
    ) -> Optional[RenewalReminder]:
        """
        为会员卡创建提醒记录
        参数：
            member_id: 会员ID
            member_card_id: 会员卡ID
            reminder_type: 提醒类型（seven_days或three_days）
            valid_to: 会员卡到期日期
            member_name: 会员姓名
            card_type: 卡类型
        """
        # 检查是否已存在该类型的提醒
        if self.check_reminder_exists(db, member_card_id, reminder_type):
            return None

        # 计算发送时间
        if reminder_type == ReminderType.SEVEN_DAYS.value:
            days_before = 7
        elif reminder_type == ReminderType.THREE_DAYS.value:
            days_before = 3
        else:
            return None

        scheduled_time = datetime.combine(
            valid_to - timedelta(days=days_before),
            datetime.min.time().replace(hour=10)  # 上午10点发送
        )

        # 生成消息内容
        message_content = self._generate_message_content(
            member_name, card_type, valid_to, days_before
        )

        reminder_in = RenewalReminderCreate(
            member_id=member_id,
            member_card_id=member_card_id,
            reminder_type=reminder_type,
            channel=ReminderChannel.SMS.value,
            message_content=message_content,
            scheduled_time=scheduled_time,
            status=ReminderStatus.PENDING.value
        )

        return self.create(db, reminder_in)

    def _generate_message_content(
        self,
        member_name: str,
        card_type: str,
        valid_to: datetime.date,
        days_before: int
    ) -> str:
        """
        生成提醒消息内容
        """
        return (
            f"尊敬的{member_name}先生/女士，您的{card_type}将于{valid_to.strftime('%Y-%m-%d')}到期，"
            f"距到期还有{days_before}天。请及时办理续费手续，可选择到店续费或线上续费。"
            f"感谢您的支持！"
        )

    def update(self, db: Session, db_reminder: RenewalReminder, reminder_in: RenewalReminderUpdate) -> RenewalReminder:
        """更新提醒记录"""
        update_data = reminder_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_reminder, key, value)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    def mark_as_sent(self, db: Session, db_reminder: RenewalReminder) -> RenewalReminder:
        """标记为已发送"""
        db_reminder.status = ReminderStatus.SENT.value
        db_reminder.sent_time = datetime.now()
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    def mark_as_failed(self, db: Session, db_reminder: RenewalReminder, error_message: str) -> RenewalReminder:
        """标记为发送失败"""
        db_reminder.status = ReminderStatus.FAILED.value
        db_reminder.sent_time = datetime.now()
        db_reminder.error_message = error_message
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    def mark_as_renewed(self, db: Session, db_reminder: RenewalReminder, renewal_method: str = "offline") -> RenewalReminder:
        """
        标记为已续费
        参数：
            renewal_method: 续费方式（offline到店, online线上）
        """
        db_reminder.status = ReminderStatus.RENEWED.value
        db_reminder.renewed_at = datetime.now()
        db_reminder.renewal_method = renewal_method
        db.commit()
        db.refresh(db_reminder)
        return db_reminder


# 创建全局CRUD实例
reminder_crud = ReminderCRUD()

"""
提醒服务模块
处理租借到期/逾期提醒的核心逻辑，包括：
1. 平台提醒（系统生成催还订单）
2. 短信提醒（发送给租借人员和工作人员）
3. 押金自动扣除（逾期3天后）
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Rental, Reminder, CollectionOrder, User, Item
from sms_service import SMSService
from utils import (
    calculate_overdue_days, 
    generate_reminder_content, 
    get_reminder_level,
    generate_collection_order_no
)
from config import (
    REMINDER_DAYS_BEFORE_DUE,
    MAX_REMINDER_DAYS,
    DEPOSIT_DEDUCT_DAYS_AFTER_OVERDUE
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderService:
    """
    提醒服务类
    处理所有与提醒相关的业务逻辑
    """
    
    def __init__(self, db: Session):
        """
        初始化提醒服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.sms_service = SMSService(db)
        self.today = date.today()
    
    def check_and_generate_reminders(self) -> Dict:
        """
        检查所有租借记录并生成提醒
        这是定时任务的入口函数
        
        Returns:
            Dict: 统计结果，包含各类提醒的数量
        """
        stats = {
            'total_rentals_checked': 0,
            'platform_reminders_created': 0,
            'sms_reminders_sent': 0,
            'collection_orders_created': 0,
            'deposits_deducted': 0,
            'errors': []
        }
        
        try:
            # 查询所有活跃的租借记录（租借中或逾期）
            active_rentals = self.db.query(Rental).filter(
                or_(Rental.status == 'active', Rental.status == 'overdue')
            ).all()
            
            stats['total_rentals_checked'] = len(active_rentals)
            logger.info(f"开始检查 {len(active_rentals)} 条活跃租借记录")
            
            for rental in active_rentals:
                try:
                    result = self._process_single_rental(rental)
                    
                    # 更新统计
                    stats['platform_reminders_created'] += result.get('platform_reminders', 0)
                    stats['sms_reminders_sent'] += result.get('sms_reminders', 0)
                    stats['collection_orders_created'] += result.get('collection_orders', 0)
                    stats['deposits_deducted'] += result.get('deposits_deducted', 0)
                    
                except Exception as e:
                    error_msg = f"处理租借记录 {rental.rental_no} 时出错: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            self.db.commit()
            logger.info(f"提醒检查完成: {stats}")
            
        except Exception as e:
            error_msg = f"提醒检查过程中发生错误: {str(e)}"
            logger.error(error_msg)
            stats['errors'].append(error_msg)
            self.db.rollback()
        
        return stats
    
    def _process_single_rental(self, rental: Rental) -> Dict:
        """
        处理单条租借记录的提醒逻辑
        
        Args:
            rental: 租借记录对象
            
        Returns:
            Dict: 处理结果统计
        """
        result = {
            'platform_reminders': 0,
            'sms_reminders': 0,
            'collection_orders': 0,
            'deposits_deducted': 0
        }
        
        # 计算逾期天数
        overdue_days = calculate_overdue_days(rental.due_date, self.today)
        
        # 获取该租借记录已发送的提醒次数
        existing_reminders = self.db.query(Reminder).filter(
            Reminder.rental_id == rental.id,
            Reminder.reminder_type == 'sms'
        ).order_by(Reminder.reminder_day.desc()).all()
        
        # 确定今天是第几次提醒
        last_reminder_day = max([r.reminder_day or 0 for r in existing_reminders], default=0)
        
        # 判断是否需要提醒
        should_remind, reminder_day = self._should_remind_today(
            rental.due_date, 
            overdue_days, 
            last_reminder_day
        )
        
        if not should_remind:
            return result
        
        # 获取关联信息
        renter = self.db.query(User).filter(User.id == rental.user_id).first()
        item = self.db.query(Item).filter(Item.id == rental.item_id).first()
        
        if not renter or not item:
            logger.warning(f"租借记录 {rental.rental_no} 缺少关联的用户或物品信息")
            return result
        
        # 准备提醒信息
        rental_info = {
            'rental_no': rental.rental_no,
            'item_name': item.name,
            'due_date': rental.due_date.strftime('%Y-%m-%d'),
            'deposit': rental.deposit_amount,
            'overdue_days': overdue_days
        }
        
        # 更新租借记录状态（如果已逾期）
        if overdue_days > 0 and rental.status == 'active':
            rental.status = 'overdue'
        
        # 1. 创建平台提醒（生成催还订单）
        if overdue_days > 0:
            collection_created = self._create_collection_order(rental, renter, item, overdue_days)
            if collection_created:
                result['collection_orders'] += 1
        
        # 2. 创建平台提醒记录
        platform_created = self._create_platform_reminder(
            rental, renter, rental_info, reminder_day, overdue_days
        )
        if platform_created:
            result['platform_reminders'] += 1
        
        # 3. 发送短信提醒（给租借人员）
        if renter.phone:
            sms_sent = self._send_sms_reminder(
                rental, renter, item, reminder_day, overdue_days
            )
            if sms_sent:
                result['sms_reminders'] += 1
        
        # 4. 发送短信提醒（给工作人员/管理者）
        staff_members = self.db.query(User).filter(
            or_(User.role == 'admin', User.role == 'staff'),
            User.status == 'active'
        ).all()
        
        for staff in staff_members:
            if staff.phone:
                self._send_staff_notification(rental, renter, item, staff, overdue_days, reminder_day)
        
        # 5. 检查是否需要扣除押金（逾期3天后）
        if overdue_days >= DEPOSIT_DEDUCT_DAYS_AFTER_OVERDUE and rental.deposit_status == 'paid':
            deducted = self._deduct_deposit(rental, renter, item)
            if deducted:
                result['deposits_deducted'] += 1
        
        return result
    
    def _should_remind_today(self, due_date: date, overdue_days: int, 
                              last_reminder_day: int) -> tuple:
        """
        判断今天是否需要发送提醒
        
        Args:
            due_date: 应归还日期
            overdue_days: 逾期天数
            last_reminder_day: 上次提醒是第几次
            
        Returns:
            tuple: (是否需要提醒, 第几次提醒)
        """
        # 情况1：到期前1天（第一次提醒）
        days_before_due = (due_date - self.today).days
        if days_before_due == REMINDER_DAYS_BEFORE_DUE and last_reminder_day == 0:
            return True, 1
        
        # 情况2：已逾期，最多提醒3次
        if overdue_days > 0:
            # 逾期第1天：第2次提醒
            if overdue_days == 1 and last_reminder_day < 2:
                return True, 2
            # 逾期第2天：第3次提醒
            elif overdue_days == 2 and last_reminder_day < 3:
                return True, 3
            # 逾期超过2天但还没提醒完3次
            elif overdue_days > 2 and last_reminder_day < MAX_REMINDER_DAYS:
                return True, last_reminder_day + 1
        
        return False, 0
    
    def _create_platform_reminder(self, rental: Rental, renter: User, 
                                   rental_info: dict, reminder_day: int, 
                                   overdue_days: int) -> bool:
        """
        创建平台提醒记录
        
        Args:
            rental: 租借记录
            renter: 租借人
            rental_info: 租借信息
            reminder_day: 第几次提醒
            overdue_days: 逾期天数
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 生成提醒标题和内容
            title, content = generate_reminder_content(rental_info, reminder_day, overdue_days)
            
            # 获取提醒级别
            reminder_level = get_reminder_level(overdue_days)
            
            # 创建提醒记录
            reminder = Reminder(
                rental_id=rental.id,
                user_id=renter.id,
                reminder_type='platform',
                reminder_level=reminder_level,
                title=title,
                content=content,
                is_read=False,
                reminder_day=reminder_day
            )
            
            self.db.add(reminder)
            logger.info(f"创建平台提醒: {rental.rental_no} - 第{reminder_day}次提醒")
            return True
            
        except Exception as e:
            logger.error(f"创建平台提醒失败: {str(e)}")
            return False
    
    def _send_sms_reminder(self, rental: Rental, renter: User, item: Item,
                            reminder_day: int, overdue_days: int) -> bool:
        """
        发送短信提醒给租借人员
        
        Args:
            rental: 租借记录
            renter: 租借人
            item: 租借物品
            reminder_day: 第几次提醒
            overdue_days: 逾期天数
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 先创建短信提醒记录
            reminder_level = get_reminder_level(overdue_days)
            title = f"短信提醒-第{reminder_day}次-{item.name}"
            
            reminder = Reminder(
                rental_id=rental.id,
                user_id=renter.id,
                reminder_type='sms',
                reminder_level=reminder_level,
                title=title,
                content=f"发送短信至 {renter.phone}",
                is_read=True,
                is_sent=False,
                reminder_day=reminder_day
            )
            
            self.db.add(reminder)
            self.db.flush()
            
            # 发送短信
            result = self.sms_service.send_rental_reminder(
                phone=renter.phone,
                renter_name=renter.real_name or renter.username,
                item_name=item.name,
                due_date=rental.due_date.strftime('%Y-%m-%d'),
                reminder_day=reminder_day
            )
            
            # 更新提醒记录状态
            reminder.is_sent = result['success']
            if result['success']:
                reminder.sent_at = datetime.now()
                logger.info(f"短信发送成功: {renter.phone} - 第{reminder_day}次提醒")
            else:
                logger.warning(f"短信发送失败: {renter.phone} - {result['message']}")
            
            return result['success']
            
        except Exception as e:
            logger.error(f"发送短信提醒失败: {str(e)}")
            return False
    
    def _send_staff_notification(self, rental: Rental, renter: User, item: Item,
                                   staff: User, overdue_days: int, reminder_day: int) -> bool:
        """
        发送通知给工作人员/管理者
        
        Args:
            rental: 租借记录
            renter: 租借人
            item: 租借物品
            staff: 工作人员
            overdue_days: 逾期天数
            reminder_day: 第几次提醒
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 只有逾期时才通知工作人员
            if overdue_days <= 0:
                return False
            
            content = (
                f"【租借系统-工作人员通知】\n"
                f"租借人: {renter.real_name or renter.username}\n"
                f"联系电话: {renter.phone}\n"
                f"租借物品: {item.name}\n"
                f"租借单号: {rental.rental_no}\n"
                f"应归还日期: {rental.due_date.strftime('%Y-%m-%d')}\n"
                f"已逾期: {overdue_days}天\n"
                f"提醒次数: 第{reminder_day}次\n"
                f"押金金额: {rental.deposit_amount}元\n\n"
                f"请及时跟进处理！"
            )
            
            result = self.sms_service.send_sms(
                phone=staff.phone,
                template_code='STAFF_NOTIFY',
                content=content
            )
            
            if result['success']:
                logger.info(f"工作人员通知发送成功: {staff.real_name or staff.username}")
            else:
                logger.warning(f"工作人员通知发送失败: {result['message']}")
            
            return result['success']
            
        except Exception as e:
            logger.error(f"发送工作人员通知失败: {str(e)}")
            return False
    
    def _create_collection_order(self, rental: Rental, renter: User, 
                                  item: Item, overdue_days: int) -> bool:
        """
        创建催还订单（平台提醒的一种形式）
        
        Args:
            rental: 租借记录
            renter: 租借人
            item: 租借物品
            overdue_days: 逾期天数
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 检查是否已存在未处理的催还订单
            existing_order = self.db.query(CollectionOrder).filter(
                CollectionOrder.rental_id == rental.id,
                CollectionOrder.status == 'pending'
            ).first()
            
            if existing_order:
                # 更新逾期天数
                existing_order.overdue_days = overdue_days
                existing_order.is_urgent = overdue_days >= 2
                return False
            
            # 计算应缴金额（租金 + 可能的逾期罚款）
            # 这里简化处理，实际可根据业务规则计算
            total_rent = rental.total_rent or (
                (rental.due_date - rental.start_date).days + 1
            ) * rental.daily_rent * rental.quantity
            
            # 创建催还订单
            order = CollectionOrder(
                order_no=generate_collection_order_no(),
                rental_id=rental.id,
                user_id=renter.id,
                overdue_days=overdue_days,
                total_amount=total_rent,
                status='pending',
                is_urgent=overdue_days >= 2
            )
            
            self.db.add(order)
            logger.info(f"创建催还订单: {order.order_no} - 逾期{overdue_days}天")
            return True
            
        except Exception as e:
            logger.error(f"创建催还订单失败: {str(e)}")
            return False
    
    def _deduct_deposit(self, rental: Rental, renter: User, item: Item) -> bool:
        """
        扣除押金（逾期3天后自动执行）
        
        Args:
            rental: 租借记录
            renter: 租借人
            item: 租借物品
            
        Returns:
            bool: 是否扣除成功
        """
        try:
            # 更新租借记录的押金状态
            rental.deposit_status = 'deducted'
            
            # 创建提醒记录
            reminder = Reminder(
                rental_id=rental.id,
                user_id=renter.id,
                reminder_type='platform',
                reminder_level='critical',
                title=f"【重要】押金已扣除 - {item.name}",
                content=(
                    f"由于您租借的{item.name}逾期未还，系统已自动扣除您的押金{rental.deposit_amount}元。\n"
                    f"租借单号: {rental.rental_no}\n"
                    f"请尽快联系工作人员处理。"
                ),
                is_read=False
            )
            self.db.add(reminder)
            
            # 发送押金扣除通知短信
            if renter.phone:
                self.sms_service.send_deposit_deduction_notice(
                    phone=renter.phone,
                    renter_name=renter.real_name or renter.username,
                    item_name=item.name,
                    deposit_amount=rental.deposit_amount
                )
            
            # 更新相关催还订单状态
            orders = self.db.query(CollectionOrder).filter(
                CollectionOrder.rental_id == rental.id,
                CollectionOrder.status == 'pending'
            ).all()
            
            for order in orders:
                order.status = 'deducted'
            
            logger.info(f"押金已扣除: 租借记录 {rental.rental_no}, 金额 {rental.deposit_amount}元")
            return True
            
        except Exception as e:
            logger.error(f"扣除押金失败: {str(e)}")
            return False
    
    def get_reminder_statistics(self) -> Dict:
        """
        获取提醒统计数据
        
        Returns:
            Dict: 统计信息
        """
        today = self.today
        
        # 今日待提醒数量
        today_reminders = self.db.query(Reminder).filter(
            Reminder.created_at >= datetime(today.year, today.month, today.day)
        ).count()
        
        # 未读平台提醒
        unread_platform = self.db.query(Reminder).filter(
            Reminder.reminder_type == 'platform',
            Reminder.is_read == False
        ).count()
        
        # 待处理催还订单
        pending_orders = self.db.query(CollectionOrder).filter(
            CollectionOrder.status == 'pending'
        ).count()
        
        # 紧急催还订单
        urgent_orders = self.db.query(CollectionOrder).filter(
            CollectionOrder.status == 'pending',
            CollectionOrder.is_urgent == True
        ).count()
        
        return {
            'today_reminders': today_reminders,
            'unread_platform_reminders': unread_platform,
            'pending_collection_orders': pending_orders,
            'urgent_collection_orders': urgent_orders
        }

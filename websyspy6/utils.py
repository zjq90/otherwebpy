"""
工具函数模块
包含系统通用的工具函数
"""
import hashlib
import random
import string
from datetime import datetime, date
from typing import Optional
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 验证是否通过
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def generate_rental_no() -> str:
    """
    生成租借单号
    格式：ZL + 年月日时分秒 + 6位随机数
    
    Returns:
        str: 租借单号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"ZL{timestamp}{random_str}"


def generate_collection_order_no() -> str:
    """
    生成催还单号
    格式：CH + 年月日时分秒 + 6位随机数
    
    Returns:
        str: 催还单号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"CH{timestamp}{random_str}"


def calculate_overdue_days(due_date: date, actual_date: Optional[date] = None) -> int:
    """
    计算逾期天数
    
    Args:
        due_date: 应归还日期
        actual_date: 实际日期，默认为今天
        
    Returns:
        int: 逾期天数，正数表示逾期，0或负数表示未逾期
    """
    if actual_date is None:
        actual_date = date.today()
    
    delta = actual_date - due_date
    return max(0, delta.days)


def calculate_rental_total(start_date: date, end_date: date, daily_rent: float, quantity: int = 1) -> float:
    """
    计算租借总费用
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        daily_rent: 日租金
        quantity: 数量
        
    Returns:
        float: 总租金
    """
    days = (end_date - start_date).days + 1  # 包含开始和结束日期
    return round(days * daily_rent * quantity, 2)


def get_reminder_level(overdue_days: int) -> str:
    """
    根据逾期天数获取提醒级别
    
    Args:
        overdue_days: 逾期天数
        
    Returns:
        str: 提醒级别
    """
    if overdue_days <= 0:
        return "normal"
    elif overdue_days <= 1:
        return "urgent"
    else:
        return "critical"


def generate_reminder_content(rental_info: dict, reminder_day: int, overdue_days: int) -> tuple:
    """
    生成提醒内容
    
    Args:
        rental_info: 租借信息字典
        reminder_day: 第几次提醒（1-3）
        overdue_days: 逾期天数
        
    Returns:
        tuple: (标题, 内容)
    """
    item_name = rental_info.get('item_name', '物品')
    due_date = rental_info.get('due_date', '')
    deposit = rental_info.get('deposit', 0)
    rental_no = rental_info.get('rental_no', '')
    
    if overdue_days <= 0:
        title = f"【提醒】您租借的{item_name}即将到期"
        content = (
            f"尊敬的用户，您好！\n"
            f"您的租借单号：{rental_no}\n"
            f"租借物品：{item_name}\n"
            f"应归还日期：{due_date}\n\n"
            f"请按时归还物品，以免产生逾期费用。\n"
            f"如有疑问，请联系客服。"
        )
    else:
        title = f"【警告第{reminder_day}次】您租借的{item_name}已逾期{overdue_days}天"
        if reminder_day < 3:
            content = (
                f"尊敬的用户，您好！\n"
                f"这是第{reminder_day}次提醒。\n"
                f"您的租借单号：{rental_no}\n"
                f"租借物品：{item_name}\n"
                f"应归还日期：{due_date}\n"
                f"已逾期：{overdue_days}天\n\n"
                f"请尽快归还物品，否则我们将在提醒3次后扣除您的押金{deposit}元。\n"
                f"如有疑问，请联系客服。"
            )
        else:
            content = (
                f"尊敬的用户，您好！\n"
                f"这是最后一次提醒（第{reminder_day}次）。\n"
                f"您的租借单号：{rental_no}\n"
                f"租借物品：{item_name}\n"
                f"应归还日期：{due_date}\n"
                f"已逾期：{overdue_days}天\n\n"
                f"由于您未按时归还物品，系统将自动扣除您的押金{deposit}元。\n"
                f"请尽快联系工作人员处理。"
            )
    
    return title, content


def md5_hash(text: str) -> str:
    """
    MD5哈希加密
    
    Args:
        text: 待加密文本
        
    Returns:
        str: 加密后的字符串
    """
    return hashlib.md5(text.encode()).hexdigest()


def format_datetime(dt: datetime) -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        
    Returns:
        str: 格式化后的字符串
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(d: date) -> str:
    """
    格式化日期
    
    Args:
        d: date对象
        
    Returns:
        str: 格式化后的字符串
    """
    return d.strftime("%Y-%m-%d")

"""
通用工具函数
包含日期处理、生成唯一编号等功能
"""

from datetime import datetime, date
from typing import Optional
import random
import string


def generate_reservation_no() -> str:
    """
    生成预约单号
    格式：RES + 时间戳(YYYYMMDDHHMMSS) + 4位随机数字
    例如：RES202405031430221234
    
    Returns:
        str: 预约单号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"RES{timestamp}{random_num}"


def calculate_rental_days(start_date: date, end_date: date) -> int:
    """
    计算租借天数
    结束日期 - 开始日期 + 1（包含开始和结束日）
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        int: 租借天数
    """
    delta = end_date - start_date
    return delta.days + 1


def calculate_total_rent(daily_rent: float, rental_days: int, quantity: int = 1) -> float:
    """
    计算总租金
    公式：日租金 × 租借天数 × 数量
    
    Args:
        daily_rent: 日租金
        rental_days: 租借天数
        quantity: 数量
        
    Returns:
        float: 总租金
    """
    return daily_rent * rental_days * quantity


def calculate_total_deposit(deposit_per_item: float, quantity: int = 1) -> float:
    """
    计算总押金
    公式：单价押金 × 数量
    
    Args:
        deposit_per_item: 单件产品押金
        quantity: 数量
        
    Returns:
        float: 总押金
    """
    return deposit_per_item * quantity


def format_date(date_obj: Optional[date]) -> str:
    """
    格式化日期对象为字符串
    
    Args:
        date_obj: 日期对象
        
    Returns:
        str: 格式化后的日期字符串，格式为YYYY-MM-DD
    """
    if date_obj is None:
        return ""
    return date_obj.strftime("%Y-%m-%d")


def format_datetime(datetime_obj: Optional[datetime]) -> str:
    """
    格式化日期时间对象为字符串
    
    Args:
        datetime_obj: 日期时间对象
        
    Returns:
        str: 格式化后的日期时间字符串，格式为YYYY-MM-DD HH:MM:SS
    """
    if datetime_obj is None:
        return ""
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

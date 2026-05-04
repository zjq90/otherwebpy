"""
通用工具函数模块
包含订单号生成、卡号生成等通用功能
"""

import uuid
import random
import string
from datetime import datetime
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP


def generate_order_no() -> str:
    """
    生成订单号
    格式：年月日时分秒 + 6位随机数，共20位
    
    Returns:
        str: 订单号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"ORD{timestamp}{random_str}"


def generate_card_number() -> str:
    """
    生成会员卡号
    格式：前缀 + 时间戳后8位 + 4位随机数，共16位
    
    Returns:
        str: 会员卡号
    """
    prefix = "MC"
    timestamp = datetime.now().strftime("%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"


def generate_uuid() -> str:
    """
    生成UUID
    
    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4()).replace("-", "")


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    四舍五入Decimal值
    
    Args:
        value: 要四舍五入的值
        places: 小数位数
        
    Returns:
        Decimal: 四舍五入后的值
    """
    return value.quantize(Decimal(f'0.{"0" * places}'), rounding=ROUND_HALF_UP)


def calculate_discount(original_amount: Decimal, discount_config: dict) -> tuple[Decimal, str]:
    """
    根据优惠配置计算优惠金额
    
    支持的优惠类型：
    - discount: 折扣率（如 0.85 表示85折）
    - full_reduction: 满减（如满100减20）
    - buy_gift: 买赠（如买10次送2次）
    
    Args:
        original_amount: 原价
        discount_config: 优惠配置字典
        
    Returns:
        tuple[Decimal, str]: (优惠金额, 优惠描述)
    """
    promotion_type = discount_config.get("type", "discount")
    discount_amount = Decimal("0")
    description = ""
    
    if promotion_type == "discount":
        rate = discount_config.get("rate", 1.0)
        discount_amount = original_amount * (Decimal("1") - Decimal(str(rate)))
        description = f"{int(rate * 10)}折优惠"
    
    elif promotion_type == "full_reduction":
        thresholds = discount_config.get("thresholds", [])
        for threshold in sorted(thresholds, key=lambda x: x["full"], reverse=True):
            full_amount = Decimal(str(threshold["full"]))
            if original_amount >= full_amount:
                discount_amount = Decimal(str(threshold["reduction"]))
                description = f"满{full_amount}减{discount_amount}"
                break
    
    elif promotion_type == "buy_gift":
        description = "买赠活动"
    
    return round_decimal(discount_amount), description


def mask_phone(phone: str) -> str:
    """
    脱敏手机号
    中间4位替换为*
    
    Args:
        phone: 手机号
        
    Returns:
        str: 脱敏后的手机号
    """
    if not phone or len(phone) < 11:
        return phone
    return phone[:3] + "****" + phone[-4:]


def format_duration(minutes: int) -> str:
    """
    格式化时长（分钟转小时分钟）
    
    Args:
        minutes: 分钟数
        
    Returns:
        str: 格式化后的时长字符串
    """
    if minutes < 60:
        return f"{minutes}分钟"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}小时"
    return f"{hours}小时{mins}分钟"

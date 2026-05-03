"""
系统配置文件
包含所有系统相关的配置参数
"""
import os
from datetime import timedelta

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'rental_system.db')}"

# 安全配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 提醒配置
REMINDER_DAYS_BEFORE_DUE = 1  # 到期前1天开始提醒
MAX_REMINDER_DAYS = 3  # 最多提醒3天
DAILY_REMINDER_TIME = "09:00"  # 每天提醒时间

# 押金扣除配置
DEPOSIT_DEDUCT_DAYS_AFTER_OVERDUE = 3  # 逾期3天后扣除押金

# 短信服务配置（示例，需要替换为实际短信提供商配置）
SMS_CONFIG = {
    "provider": "aliyun",  # 可选: aliyun, tencent, huawei等
    "access_key": "your-access-key",
    "secret_key": "your-secret-key",
    "sign_name": "租借系统",
    "template_code": "SMS_123456789"
}

# 分页配置
PAGE_SIZE = 10

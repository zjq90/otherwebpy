"""
短信服务模块
提供短信发送功能，测试环境使用模拟发送
"""
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import settings
from app.models.notification import SmsNotification
from app.models.member import MemberStatus
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """
    短信服务类
    负责发送短信通知和验证码
    """
    
    def __init__(self):
        self._verification_codes: Dict[str, dict] = {}  # 内存存储验证码，生产环境应使用Redis
    
    def generate_verification_code(self, length: int = 6) -> str:
        """
        生成随机验证码
        Args:
            length: 验证码长度，默认6位
        Returns:
            验证码字符串
        """
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_code(self, phone: str, purpose: str = "verification") -> dict:
        """
        发送短信验证码
        Args:
            phone: 手机号
            purpose: 验证码用途: verification-实名认证, login-登录
        Returns:
            包含发送状态的字典
        """
        code = self.generate_verification_code()
        expires_at = datetime.now() + timedelta(minutes=5)
        
        # 存储验证码
        self._verification_codes[phone] = {
            "code": code,
            "purpose": purpose,
            "expires_at": expires_at,
            "attempts": 0
        }
        
        # 测试环境：模拟发送，直接返回验证码
        if not settings.SMS_ENABLED:
            logger.info(f"[模拟短信发送] 手机号: {phone}, 验证码: {code}, 用途: {purpose}")
            return {
                "success": True,
                "message": "验证码已发送（测试环境）",
                "phone": phone,
                "test_code": code  # 测试环境返回验证码方便测试
            }
        
        # 生产环境：调用实际短信API
        return self._send_sms_via_provider(phone, f"您的验证码是：{code}，5分钟内有效。")
    
    def verify_code(self, phone: str, code: str, purpose: str = "verification") -> bool:
        """
        验证短信验证码
        Args:
            phone: 手机号
            code: 验证码
            purpose: 验证码用途
        Returns:
            验证是否通过
        """
        stored = self._verification_codes.get(phone)
        
        if not stored:
            return False
        
        # 检查用途
        if stored.get("purpose") != purpose:
            return False
        
        # 检查是否过期
        if stored.get("expires_at") < datetime.now():
            del self._verification_codes[phone]
            return False
        
        # 检查尝试次数（防止暴力破解）
        if stored.get("attempts", 0) >= 3:
            del self._verification_codes[phone]
            return False
        
        # 验证验证码
        if stored.get("code") == code:
            # 验证成功，删除验证码
            del self._verification_codes[phone]
            return True
        
        # 验证失败，增加尝试次数
        stored["attempts"] = stored.get("attempts", 0) + 1
        self._verification_codes[phone] = stored
        return False
    
    def send_status_change_notification(
        self, 
        db: Session,
        phone: str, 
        member_id: Optional[int],
        old_status: Optional[MemberStatus], 
        new_status: MemberStatus,
        reason: Optional[str] = None
    ) -> dict:
        """
        发送账户状态变更通知
        Args:
            db: 数据库会话
            phone: 手机号
            member_id: 会员ID
            old_status: 变更前状态
            new_status: 变更后状态
            reason: 变更原因
        Returns:
            包含发送状态的字典
        """
        status_messages = {
            MemberStatus.ACTIVE: "您的账户已恢复正常状态",
            MemberStatus.FROZEN: "您的账户已被冻结",
            MemberStatus.CANCELLED: "您的账户已注销"
        }
        
        message = status_messages.get(new_status, f"您的账户状态已变更")
        if reason:
            message += f"，原因：{reason}"
        message += "。如有疑问，请联系客服。"
        
        # 记录通知
        notification = SmsNotification(
            member_id=member_id,
            phone=phone,
            notification_type="status_change",
            title=f"账户状态变更通知",
            content=message,
            status="pending"
        )
        db.add(notification)
        db.flush()
        
        # 测试环境：模拟发送
        if not settings.SMS_ENABLED:
            logger.info(f"[模拟短信发送] 手机号: {phone}, 内容: {message}")
            notification.status = "sent"
            notification.sent_time = datetime.now()
            db.commit()
            return {
                "success": True,
                "message": "状态变更通知已发送（测试环境）",
                "content": message
            }
        
        # 生产环境：调用实际短信API
        result = self._send_sms_via_provider(phone, message)
        if result.get("success"):
            notification.status = "sent"
            notification.sent_time = datetime.now()
        else:
            notification.status = "failed"
            notification.error_message = result.get("message")
        
        db.commit()
        return result
    
    def send_consumption_notification(
        self,
        db: Session,
        phone: str,
        member_id: Optional[int],
        item_name: str,
        amount: int,  # 分
        actual_amount: int  # 分
    ) -> dict:
        """
        发送消费通知
        Args:
            db: 数据库会话
            phone: 手机号
            member_id: 会员ID
            item_name: 消费项目
            amount: 消费金额（分）
            actual_amount: 实付金额（分）
        Returns:
            包含发送状态的字典
        """
        amount_yuan = amount / 100
        actual_yuan = actual_amount / 100
        
        message = f"尊敬的会员，您已成功消费{item_name}，消费金额{amount_yuan:.2f}元"
        if actual_amount < amount:
            discount_yuan = (amount - actual_amount) / 100
            message += f"，优惠{discount_yuan:.2f}元，实付{actual_yuan:.2f}元"
        message += "。感谢您的光临！"
        
        # 记录通知
        notification = SmsNotification(
            member_id=member_id,
            phone=phone,
            notification_type="consumption",
            title=f"消费通知",
            content=message,
            status="pending"
        )
        db.add(notification)
        db.flush()
        
        # 测试环境：模拟发送
        if not settings.SMS_ENABLED:
            logger.info(f"[模拟短信发送] 手机号: {phone}, 内容: {message}")
            notification.status = "sent"
            notification.sent_time = datetime.now()
            db.commit()
            return {
                "success": True,
                "message": "消费通知已发送（测试环境）",
                "content": message
            }
        
        return self._send_sms_via_provider(phone, message)
    
    def _send_sms_via_provider(self, phone: str, content: str) -> dict:
        """
        通过短信服务商发送短信（生产环境）
        Args:
            phone: 手机号
            content: 短信内容
        Returns:
            包含发送状态的字典
        """
        # TODO: 集成实际的短信服务商（如阿里云短信、腾讯云短信等）
        # 这里是占位实现，实际项目中需要替换为真实的API调用
        try:
            # 示例：调用第三方短信API
            # response = httpx.post(
            #     "https://sms-api.example.com/send",
            #     json={
            #         "phone": phone,
            #         "content": content,
            #         "api_key": settings.SMS_API_KEY
            #     }
            # )
            # if response.status_code == 200:
            #     return {"success": True, "message": "发送成功"}
            
            return {"success": True, "message": "发送成功"}
        except Exception as e:
            logger.error(f"短信发送失败: {str(e)}")
            return {"success": False, "message": f"发送失败: {str(e)}"}


# 创建全局服务实例
sms_service = SMSService()

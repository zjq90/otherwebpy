"""
短信服务模块
提供短信发送接口，支持多种短信服务商（阿里云、腾讯云等）
目前实现为模拟模式，可根据实际需求接入真实短信服务商
"""
from datetime import datetime
from typing import Dict, Optional
import logging
import json
from sqlalchemy.orm import Session

from models import SMSLog, Reminder
from config import SMS_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSService:
    """
    短信服务类
    提供短信发送功能，支持多种短信提供商
    """
    
    def __init__(self, db: Session):
        """
        初始化短信服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.config = SMS_CONFIG
        self._mock_mode = True  # 模拟模式（测试用）
        
        # 根据配置选择短信提供商
        self.provider = self._get_provider()
    
    def _get_provider(self) -> str:
        """
        获取短信提供商
        
        Returns:
            str: 提供商名称
        """
        return self.config.get('provider', 'aliyun')
    
    def send_sms(self, phone: str, template_code: str, 
                  template_param: Dict = None, content: str = None,
                  reminder_id: int = None) -> Dict:
        """
        发送短信
        
        Args:
            phone: 手机号码
            template_code: 短信模板代码
            template_param: 模板参数
            content: 短信内容（纯文本，用于模拟模式）
            reminder_id: 关联的提醒记录ID
            
        Returns:
            Dict: 发送结果，包含 success, message, data
        """
        # 创建短信日志记录
        sms_log = SMSLog(
            phone=phone,
            template_code=template_code,
            template_param=json.dumps(template_param, ensure_ascii=False) if template_param else None,
            content=content or f"短信发送至 {phone}",
            status='pending',
            reminder_id=reminder_id
        )
        self.db.add(sms_log)
        self.db.flush()
        
        try:
            if self._mock_mode:
                # 模拟发送模式（用于测试）
                result = self._mock_send(phone, template_code, template_param, content)
            else:
                # 真实发送模式
                result = self._send_to_provider(phone, template_code, template_param)
            
            # 更新短信日志状态
            if result['success']:
                sms_log.status = 'success'
                # 将data字典转换为JSON字符串存储
                response_data = result.get('data')
                sms_log.provider_response = json.dumps(response_data, ensure_ascii=False) if response_data else ''
                sms_log.sent_at = datetime.now()
                logger.info(f"短信发送成功: {phone} - {content[:30] if content else ''}")
            else:
                sms_log.status = 'failed'
                # message已经是字符串，直接存储
                sms_log.provider_response = result.get('message', '')
                logger.warning(f"短信发送失败: {phone} - {result['message']}")
            
            self.db.commit()
            return result
            
        except Exception as e:
            error_msg = f"短信发送异常: {str(e)}"
            logger.error(error_msg)
            sms_log.status = 'failed'
            sms_log.provider_response = error_msg
            self.db.commit()
            return {'success': False, 'message': error_msg, 'data': None}
    
    def _mock_send(self, phone: str, template_code: str, 
                   template_param: Dict = None, content: str = None) -> Dict:
        """
        模拟发送短信（测试用）
        
        Args:
            phone: 手机号码
            template_code: 模板代码
            template_param: 模板参数
            content: 短信内容
            
        Returns:
            Dict: 发送结果
        """
        # 构建实际短信内容（模拟）
        if content:
            actual_content = content
        else:
            actual_content = self._build_content_from_template(template_code, template_param)
        
        # 记录模拟发送日志
        logger.info(f"[模拟模式] 发送短信到 {phone}: {actual_content[:50]}...")
        
        # 模拟95%成功率
        import random
        if random.random() < 0.95:
            return {
                'success': True,
                'message': '模拟发送成功',
                'data': {
                    'provider': 'mock',
                    'phone': phone,
                    'content': actual_content,
                    'timestamp': datetime.now().isoformat()
                }
            }
        else:
            return {
                'success': False,
                'message': '模拟发送失败（随机模拟）',
                'data': None
            }
    
    def _send_to_provider(self, phone: str, template_code: str, 
                          template_param: Dict = None) -> Dict:
        """
        发送到真实短信提供商
        
        Args:
            phone: 手机号码
            template_code: 模板代码
            template_param: 模板参数
            
        Returns:
            Dict: 发送结果
        """
        provider = self.provider.lower()
        
        if provider == 'aliyun':
            return self._send_aliyun(phone, template_code, template_param)
        elif provider == 'tencent':
            return self._send_tencent(phone, template_code, template_param)
        elif provider == 'huawei':
            return self._send_huawei(phone, template_code, template_param)
        else:
            return {
                'success': False,
                'message': f'不支持的短信提供商: {provider}',
                'data': None
            }
    
    def _send_aliyun(self, phone: str, template_code: str, 
                      template_param: Dict = None) -> Dict:
        """
        发送阿里云短信
        
        注意：需要安装 alibabacloud_dysmsapi20170525
        pip install alibabacloud_dysmsapi20170525
        
        Args:
            phone: 手机号码
            template_code: 模板代码
            template_param: 模板参数
            
        Returns:
            Dict: 发送结果
        """
        try:
            # 这里是阿里云短信的示例代码，需要根据实际情况配置
            # from alibabacloud_dysmsapi20170525.client import Client
            # from alibabacloud_dysmsapi20170525.models import SendSmsRequest
            # from alibabacloud_tea_openapi.models import Config
            
            # config = Config(
            #     access_key_id=self.config.get('access_key'),
            #     access_key_secret=self.config.get('secret_key'),
            #     endpoint='dysmsapi.aliyuncs.com'
            # )
            # client = Client(config)
            
            # request = SendSmsRequest(
            #     phone_numbers=phone,
            #     sign_name=self.config.get('sign_name'),
            #     template_code=template_code,
            #     template_param=json.dumps(template_param, ensure_ascii=False) if template_param else None
            # )
            # response = client.send_sms(request)
            
            # 目前返回模拟结果，实际使用时请接入真实SDK
            return {
                'success': False,
                'message': '阿里云短信SDK未配置，请在代码中接入真实SDK',
                'data': None
            }
        except Exception as e:
            return {'success': False, 'message': str(e), 'data': None}
    
    def _send_tencent(self, phone: str, template_code: str, 
                       template_param: Dict = None) -> Dict:
        """
        发送腾讯云短信
        """
        # 腾讯云短信实现示例
        return {
            'success': False,
            'message': '腾讯云短信SDK未配置',
            'data': None
        }
    
    def _send_huawei(self, phone: str, template_code: str, 
                      template_param: Dict = None) -> Dict:
        """
        发送华为云短信
        """
        # 华为云短信实现示例
        return {
            'success': False,
            'message': '华为云短信SDK未配置',
            'data': None
        }
    
    def _build_content_from_template(self, template_code: str, 
                                       template_param: Dict = None) -> str:
        """
        根据模板代码构建短信内容
        
        Args:
            template_code: 模板代码
            template_param: 模板参数
            
        Returns:
            str: 短信内容
        """
        params = template_param or {}
        
        # 预定义的模板内容映射
        templates = {
            'RENTAL_REMINDER': '【租借系统】尊敬的{name}，您租借的{item}将于{due_date}到期，请及时归还。',
            'OVERDUE_REMINDER': '【租借系统】尊敬的{name}，您租借的{item}已逾期{days}天，押金{deposit}元将在3天后扣除。',
            'DEPOSIT_DEDUCTION': '【租借系统】尊敬的{name}，由于您租借的{item}逾期未还，已扣除您的押金{deposit}元。',
            'RETURN_CONFIRM': '【租借系统】尊敬的{name}，您租借的{item}已成功归还，感谢您的使用。'
        }
        
        template = templates.get(template_code, '【租借系统】您有一条新消息。')
        
        # 替换模板变量
        for key, value in params.items():
            template = template.replace(f'{{{key}}}', str(value))
        
        return template
    
    # 快捷方法：发送租借提醒
    def send_rental_reminder(self, phone: str, renter_name: str, 
                               item_name: str, due_date: str, 
                               reminder_day: int) -> Dict:
        """
        发送租借到期/逾期提醒短信
        
        Args:
            phone: 手机号
            renter_name: 租借人姓名
            item_name: 物品名称
            due_date: 应归还日期
            reminder_day: 第几次提醒（1-3）
            
        Returns:
            Dict: 发送结果
        """
        if reminder_day <= 1:
            # 到期提醒
            template_code = 'RENTAL_REMINDER'
            content = (
                f"【租借系统】尊敬的{renter_name}，您租借的{item_name}将于{due_date}到期，"
                f"请及时归还。这是第{reminder_day}次提醒。"
            )
        else:
            # 逾期提醒
            template_code = 'OVERDUE_REMINDER'
            content = (
                f"【租借系统】尊敬的{renter_name}，您租借的{item_name}已逾期，"
                f"这是第{reminder_day}次提醒。如3天后仍未归还，系统将自动扣除您的押金。"
            )
        
        return self.send_sms(
            phone=phone,
            template_code=template_code,
            template_param={
                'name': renter_name,
                'item': item_name,
                'due_date': due_date,
                'reminder_day': reminder_day
            },
            content=content
        )
    
    # 快捷方法：发送押金扣除通知
    def send_deposit_deduction_notice(self, phone: str, renter_name: str,
                                         item_name: str, deposit_amount: float) -> Dict:
        """
        发送押金扣除通知短信
        
        Args:
            phone: 手机号
            renter_name: 租借人姓名
            item_name: 物品名称
            deposit_amount: 扣除的押金金额
            
        Returns:
            Dict: 发送结果
        """
        content = (
            f"【租借系统】尊敬的{renter_name}，由于您租借的{item_name}逾期未还，"
            f"系统已自动扣除您的押金{deposit_amount}元。请尽快联系工作人员处理。"
        )
        
        return self.send_sms(
            phone=phone,
            template_code='DEPOSIT_DEDUCTION',
            template_param={
                'name': renter_name,
                'item': item_name,
                'deposit': deposit_amount
            },
            content=content
        )
    
    # 快捷方法：发送归还确认短信
    def send_return_confirm(self, phone: str, renter_name: str,
                              item_name: str, return_date: str) -> Dict:
        """
        发送物品归还确认短信
        
        Args:
            phone: 手机号
            renter_name: 租借人姓名
            item_name: 物品名称
            return_date: 归还日期
            
        Returns:
            Dict: 发送结果
        """
        content = (
            f"【租借系统】尊敬的{renter_name}，您租借的{item_name}已于{return_date}成功归还。"
            f"押金将在确认无误后退还。感谢您的使用！"
        )
        
        return self.send_sms(
            phone=phone,
            template_code='RETURN_CONFIRM',
            template_param={
                'name': renter_name,
                'item': item_name,
                'return_date': return_date
            },
            content=content
        )

"""
通用验证工具模块
提供常用的格式验证函数和正则表达式
"""
import re
from typing import Optional
from pydantic import field_validator, ValidationInfo

# ==================== 正则表达式常量 ====================

# 中国大陆手机号正则（11位数字，以1开头）
PHONE_REGEX = r'^1[3-9]\d{9}$'

# 邮箱正则（RFC 5322简化版）
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# 身份证号正则（18位或15位）
ID_CARD_REGEX = r'(^\d{18}$)|(^\d{15}$)|(^\d{17}(\d|X|x)$)'

# 中国大陆固定电话正则
TEL_REGEX = r'^0\d{2,3}-?\d{7,8}$'

# 邮政编码正则
POSTAL_CODE_REGEX = r'^[1-9]\d{5}$'

# 密码强度正则（至少8位，包含大小写字母和数字）
PASSWORD_STRONG_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

# 密码中等正则（至少6位，包含字母和数字）
PASSWORD_MEDIUM_REGEX = r'^(?=.*[a-zA-Z])(?=.*\d).{6,}$'

# 金额正则（最多两位小数）
AMOUNT_REGEX = r'^\d+(\.\d{1,2})?$'

# 正整数正则
POSITIVE_INT_REGEX = r'^[1-9]\d*$'

# 非负整数正则
NON_NEGATIVE_INT_REGEX = r'^[0-9]\d*$'

# ==================== 验证函数 ====================

def is_valid_phone(phone: str) -> bool:
    """
    验证手机号格式
    :param phone: 手机号字符串
    :return: True/False
    """
    if not phone:
        return False
    phone = str(phone).strip().replace('-', '').replace(' ', '')
    return bool(re.match(PHONE_REGEX, phone))


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式
    :param email: 邮箱字符串
    :return: True/False
    """
    if not email:
        return False
    email = str(email).strip()
    if len(email) > 254:
        return False
    return bool(re.match(EMAIL_REGEX, email))


def is_valid_id_card(id_card: str) -> bool:
    """
    验证身份证号格式
    :param id_card: 身份证号字符串
    :return: True/False
    """
    if not id_card:
        return False
    id_card = str(id_card).strip().upper()
    
    if not re.match(ID_CARD_REGEX, id_card):
        return False
    
    if len(id_card) == 15:
        return True
    
    if len(id_card) == 18:
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        sum_val = sum(int(id_card[i]) * weights[i] for i in range(17))
        check_code = check_codes[sum_val % 11]
        
        return id_card[17] == check_code
    
    return False


def is_valid_tel(tel: str) -> bool:
    """
    验证固定电话格式
    :param tel: 固定电话字符串
    :return: True/False
    """
    if not tel:
        return False
    tel = str(tel).strip().replace(' ', '')
    return bool(re.match(TEL_REGEX, tel))


def is_valid_postal_code(postal_code: str) -> bool:
    """
    验证邮政编码格式
    :param postal_code: 邮政编码字符串
    :return: True/False
    """
    if not postal_code:
        return False
    postal_code = str(postal_code).strip()
    return bool(re.match(POSTAL_CODE_REGEX, postal_code))


def is_valid_amount(amount: float) -> bool:
    """
    验证金额格式（最多两位小数，非负）
    :param amount: 金额数值
    :return: True/False
    """
    if amount is None:
        return False
    if amount < 0:
        return False
    amount_str = str(amount)
    return bool(re.match(AMOUNT_REGEX, amount_str))


def is_valid_positive_int(value: int) -> bool:
    """
    验证正整数
    :param value: 整数值
    :return: True/False
    """
    if value is None:
        return False
    return isinstance(value, int) and value > 0


def is_valid_non_negative_int(value: int) -> bool:
    """
    验证非负整数
    :param value: 整数值
    :return: True/False
    """
    if value is None:
        return False
    return isinstance(value, int) and value >= 0


def validate_password_strength(password: str, min_length: int = 6, require_letter: bool = True, require_digit: bool = True) -> dict:
    """
    验证密码强度
    :param password: 密码字符串
    :param min_length: 最小长度
    :param require_letter: 是否要求包含字母
    :param require_digit: 是否要求包含数字
    :return: {'valid': bool, 'message': str, 'level': str}
    """
    if not password:
        return {'valid': False, 'message': '密码不能为空', 'level': 'empty'}
    
    password = str(password)
    
    if len(password) < min_length:
        return {'valid': False, 'message': f'密码长度不能少于{min_length}位', 'level': 'short'}
    
    issues = []
    
    if require_letter and not re.search(r'[a-zA-Z]', password):
        issues.append('需要包含字母')
    
    if require_digit and not re.search(r'\d', password):
        issues.append('需要包含数字')
    
    if issues:
        return {'valid': False, 'message': '密码' + '、'.join(issues), 'level': 'weak'}
    
    level = 'medium'
    if re.match(PASSWORD_STRONG_REGEX, password):
        level = 'strong'
    
    return {'valid': True, 'message': '密码强度符合要求', 'level': level}


# ==================== Pydantic 验证器装饰器 ====================

def phone_validator(field_name: str = 'phone'):
    """
    手机号验证器装饰器（用于Pydantic）
    """
    @field_validator(field_name)
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v
    return validate_phone


def email_validator(field_name: str = 'email'):
    """
    邮箱验证器装饰器（用于Pydantic）
    """
    @field_validator(field_name)
    @classmethod
    def validate_email(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        if not is_valid_email(v):
            raise ValueError('邮箱格式不正确')
        return v
    return validate_email


def id_card_validator(field_name: str = 'id_card'):
    """
    身份证号验证器装饰器（用于Pydantic）
    """
    @field_validator(field_name)
    @classmethod
    def validate_id_card(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        if not is_valid_id_card(v):
            raise ValueError('身份证号格式不正确')
        return v
    return validate_id_card


def amount_validator(field_name: str = 'amount', min_value: float = 0, max_value: float = None):
    """
    金额验证器装饰器（用于Pydantic）
    """
    @field_validator(field_name)
    @classmethod
    def validate_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('金额不能为空')
        if v < min_value:
            raise ValueError(f'金额不能小于{min_value}')
        if max_value is not None and v > max_value:
            raise ValueError(f'金额不能大于{max_value}')
        return round(v, 2)
    return validate_amount


def positive_int_validator(field_name: str = 'quantity'):
    """
    正整数验证器装饰器（用于Pydantic）
    """
    @field_validator(field_name)
    @classmethod
    def validate_positive_int(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('数值不能为空')
        if not is_valid_positive_int(v):
            raise ValueError('必须为正整数')
        return v
    return validate_positive_int


def string_length_validator(field_name: str, min_length: int = 0, max_length: int = 255):
    """
    字符串长度验证器装饰器（用于Pydantic）
    """
    @field_validator(field_name)
    @classmethod
    def validate_string_length(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = str(v).strip()
        if len(v) < min_length:
            raise ValueError(f'长度不能少于{min_length}个字符')
        if len(v) > max_length:
            raise ValueError(f'长度不能超过{max_length}个字符')
        return v
    return validate_string_length

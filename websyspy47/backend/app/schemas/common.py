from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Generic, List, Optional, TypeVar, Any
from datetime import datetime
from decimal import Decimal
import re

T = TypeVar('T')

PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
ID_CARD_PATTERN = re.compile(r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$')
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 20

def validate_phone(phone: Optional[str]) -> Optional[str]:
    if phone is None or phone == '':
        return None
    if not PHONE_PATTERN.match(phone):
        raise ValueError('手机号码格式不正确，必须为11位中国大陆手机号')
    return phone

def validate_id_card(id_card: Optional[str]) -> Optional[str]:
    if id_card is None or id_card == '':
        return None
    if not ID_CARD_PATTERN.match(id_card):
        raise ValueError('身份证号格式不正确，必须为18位有效身份证号')
    id_card = id_card.upper()
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    total = sum(int(id_card[i]) * factors[i] for i in range(17))
    if check_codes[total % 11] != id_card[17]:
        raise ValueError('身份证号校验失败，请检查是否正确')
    return id_card

def validate_password(password: str, is_new: bool = True) -> str:
    if not password:
        if is_new:
            raise ValueError('密码不能为空')
        return password
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f'密码长度不能少于{PASSWORD_MIN_LENGTH}位')
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(f'密码长度不能超过{PASSWORD_MAX_LENGTH}位')
    if not re.search(r'[a-zA-Z]', password):
        raise ValueError('密码必须包含至少一个字母')
    if not re.search(r'[0-9]', password):
        raise ValueError('密码必须包含至少一个数字')
    return password

class PageParams(BaseModel):
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")

class PageResult(BaseModel, Generic[T]):
    list: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0

class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: Optional[T] = None

class IdListRequest(BaseModel):
    ids: List[int] = Field(..., description="ID列表")

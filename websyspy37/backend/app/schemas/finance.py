"""
财务模块Pydantic schemas
用于API的数据验证和序列化
"""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime, date


# 账户相关schemas
class AccountBase(BaseModel):
    """
    账户基础schema
    """
    account_no: str
    name: str
    type: str = "银行账户"
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    balance: float = 0.0
    description: Optional[str] = None

    @field_validator('account_no')
    @classmethod
    def validate_account_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('账户编码不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('账户编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('账户名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('账户名称长度不能超过100个字符')
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str, info: ValidationInfo) -> str:
        if v is None or v == '':
            return "银行账户"
        v = v.strip()
        valid_types = ["银行账户", "现金账户", "支付宝", "微信", "其他"]
        if v not in valid_types:
            raise ValueError(f'账户类型必须是以下之一：{", ".join(valid_types)}')
        return v

    @field_validator('bank_name')
    @classmethod
    def validate_bank_name(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 100:
            raise ValueError('银行名称长度不能超过100个字符')
        return v

    @field_validator('bank_account')
    @classmethod
    def validate_bank_account(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace(' ', '')
        if len(v) > 50:
            raise ValueError('银行账号长度不能超过50个字符')
        if not v.isdigit():
            raise ValueError('银行账号只能包含数字')
        return v

    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('余额不能为负数')
        if v > 100000000000:
            raise ValueError('余额不能超过100000000000')
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class AccountCreate(AccountBase):
    """
    账户创建schema
    """
    pass


class AccountUpdate(BaseModel):
    """
    账户更新schema
    """
    account_no: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    balance: Optional[float] = None
    description: Optional[str] = None

    @field_validator('bank_account')
    @classmethod
    def validate_bank_account_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace(' ', '')
        if len(v) > 50:
            raise ValueError('银行账号长度不能超过50个字符')
        if not v.isdigit():
            raise ValueError('银行账号只能包含数字')
        return v

    @field_validator('balance')
    @classmethod
    def validate_balance_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('余额不能为负数')
        if v > 100000000000:
            raise ValueError('余额不能超过100000000000')
        return round(v, 2)


class AccountResponse(AccountBase):
    """
    账户响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 收入相关schemas
class IncomeBase(BaseModel):
    """
    收入基础schema
    """
    account_id: int
    income_date: date = date.today()
    amount: float
    category: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('收入金额不能为空')
        if v <= 0:
            raise ValueError('收入金额必须大于0')
        if v > 100000000000:
            raise ValueError('收入金额不能超过100000000000')
        return round(v, 2)

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError('分类名称长度不能超过50个字符')
        return v

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('来源名称长度不能超过200个字符')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class IncomeCreate(IncomeBase):
    """
    收入创建schema
    """
    pass


class IncomeUpdate(BaseModel):
    """
    收入更新schema
    """
    account_id: Optional[int] = None
    income_date: Optional[date] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError('收入金额必须大于0')
        if v > 100000000000:
            raise ValueError('收入金额不能超过100000000000')
        return round(v, 2)


class IncomeResponse(IncomeBase):
    """
    收入响应schema
    """
    id: int
    income_no: str
    created_at: datetime
    updated_at: datetime
    account: Optional[AccountResponse] = None

    class Config:
        from_attributes = True


# 支出相关schemas
class ExpenseBase(BaseModel):
    """
    支出基础schema
    """
    account_id: int
    expense_date: date = date.today()
    amount: float
    category: Optional[str] = None
    recipient: Optional[str] = None
    description: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('支出金额不能为空')
        if v <= 0:
            raise ValueError('支出金额必须大于0')
        if v > 100000000000:
            raise ValueError('支出金额不能超过100000000000')
        return round(v, 2)

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError('分类名称长度不能超过50个字符')
        return v

    @field_validator('recipient')
    @classmethod
    def validate_recipient(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('收款方名称长度不能超过200个字符')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class ExpenseCreate(ExpenseBase):
    """
    支出创建schema
    """
    pass


class ExpenseUpdate(BaseModel):
    """
    支出更新schema
    """
    account_id: Optional[int] = None
    expense_date: Optional[date] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    recipient: Optional[str] = None
    description: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError('支出金额必须大于0')
        if v > 100000000000:
            raise ValueError('支出金额不能超过100000000000')
        return round(v, 2)


class ExpenseResponse(ExpenseBase):
    """
    支出响应schema
    """
    id: int
    expense_no: str
    created_at: datetime
    updated_at: datetime
    account: Optional[AccountResponse] = None

    class Config:
        from_attributes = True


# 发票相关schemas
class InvoiceBase(BaseModel):
    """
    发票基础schema
    """
    type: str = "销售发票"
    invoice_date: date = date.today()
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    party_name: Optional[str] = None
    party_tax_no: Optional[str] = None
    status: str = "待开票"
    remark: Optional[str] = None

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str, info: ValidationInfo) -> str:
        if v is None or v == '':
            return "销售发票"
        v = v.strip()
        valid_types = ["销售发票", "采购发票", "其他发票"]
        if v not in valid_types:
            raise ValueError(f'发票类型必须是以下之一：{", ".join(valid_types)}')
        return v

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('开票金额不能为空')
        if v < 0:
            raise ValueError('开票金额不能为负数')
        if v > 100000000000:
            raise ValueError('开票金额不能超过100000000000')
        return round(v, 2)

    @field_validator('tax_amount')
    @classmethod
    def validate_tax_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('税额不能为负数')
        if v > 100000000000:
            raise ValueError('税额不能超过100000000000')
        return round(v, 2)

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('价税合计不能为空')
        if v < 0:
            raise ValueError('价税合计不能为负数')
        if v > 100000000000:
            raise ValueError('价税合计不能超过100000000000')
        return round(v, 2)

    @field_validator('party_name')
    @classmethod
    def validate_party_name(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('对方名称长度不能超过200个字符')
        return v

    @field_validator('party_tax_no')
    @classmethod
    def validate_party_tax_no(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) != 15 and len(v) != 17 and len(v) != 18:
            raise ValueError('税号长度必须为15、17或18位')
        if not v.replace('-', '').isalnum():
            raise ValueError('税号格式不正确')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待开票"
        v = v.strip()
        valid_statuses = ["待开票", "已开票", "已作废"]
        if v not in valid_statuses:
            raise ValueError(f'发票状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('remark')
    @classmethod
    def validate_remark(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('备注长度不能超过500个字符')
        return v


class InvoiceCreate(InvoiceBase):
    """
    发票创建schema
    """
    pass


class InvoiceUpdate(BaseModel):
    """
    发票更新schema
    """
    type: Optional[str] = None
    invoice_date: Optional[date] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    party_name: Optional[str] = None
    party_tax_no: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('开票金额不能为负数')
        if v > 100000000000:
            raise ValueError('开票金额不能超过100000000000')
        return round(v, 2)

    @field_validator('tax_amount')
    @classmethod
    def validate_tax_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('税额不能为负数')
        if v > 100000000000:
            raise ValueError('税额不能超过100000000000')
        return round(v, 2)

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('价税合计不能为负数')
        if v > 100000000000:
            raise ValueError('价税合计不能超过100000000000')
        return round(v, 2)

    @field_validator('party_tax_no')
    @classmethod
    def validate_party_tax_no_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) != 15 and len(v) != 17 and len(v) != 18:
            raise ValueError('税号长度必须为15、17或18位')
        if not v.replace('-', '').isalnum():
            raise ValueError('税号格式不正确')
        return v

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待开票", "已开票", "已作废"]
        if v not in valid_statuses:
            raise ValueError(f'发票状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class InvoiceResponse(InvoiceBase):
    """
    发票响应schema
    """
    id: int
    invoice_no: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

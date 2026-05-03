"""
Pydantic数据模型定义文件
用于数据验证、序列化和反序列化
包含完整的字段校验逻辑：正则表达式、格式验证、自定义验证器
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    model_validator
)


# ==================== 正则表达式常量 ====================

# 用户名：只能包含字母、数字、下划线，首字母必须是字母，长度2-50
USERNAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]{1,49}$'
USERNAME_PATTERN_COMPILED = re.compile(USERNAME_PATTERN)

# 手机号：中国大陆手机号格式，11位数字，以1开头
PHONE_PATTERN = r'^1[3-9]\d{9}$'
PHONE_PATTERN_COMPILED = re.compile(PHONE_PATTERN)

# 邮箱：标准邮箱格式
EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
EMAIL_PATTERN_COMPILED = re.compile(EMAIL_PATTERN)

# 产品编码：字母、数字、横线、下划线，首字符必须是字母或数字，长度1-50
PRODUCT_CODE_PATTERN = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,49}$'
PRODUCT_CODE_PATTERN_COMPILED = re.compile(PRODUCT_CODE_PATTERN)

# 密码：至少包含大小写字母、数字、特殊字符中的两种，长度6-20
# 特殊字符：!@#$%^&*()_+-=[]{}|;':",.<>?/~`
PASSWORD_SPECIAL_CHARS = r'!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?/~`'


# ==================== 验证工具函数 ====================

def validate_username(username: str) -> str:
    """
    验证用户名格式
    规则：
    - 首字母必须是英文字母
    - 只能包含字母、数字、下划线
    - 长度：2-50个字符
    """
    if not username:
        raise ValueError('用户名不能为空')
    
    username = username.strip()
    
    if len(username) < 2:
        raise ValueError('用户名长度至少为2个字符')
    
    if len(username) > 50:
        raise ValueError('用户名长度不能超过50个字符')
    
    if not USERNAME_PATTERN_COMPILED.match(username):
        raise ValueError(
            '用户名格式错误：首字母必须是英文字母，'
            '只能包含字母、数字、下划线，长度2-50个字符'
        )
    
    return username


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """
    验证手机号格式（可选字段，如果提供则必须符合格式）
    规则：
    - 11位数字
    - 以1开头，第二位是3-9
    """
    if phone is None:
        return None
    
    phone = phone.strip()
    
    if not phone:
        return None
    
    # 移除可能的空格和横线
    phone = re.sub(r'[\s\-]', '', phone)
    
    if not PHONE_PATTERN_COMPILED.match(phone):
        raise ValueError(
            '手机号格式错误：请输入11位有效的中国大陆手机号，'
            '如：13800138000'
        )
    
    return phone


def validate_email(email: Optional[str]) -> Optional[str]:
    """
    验证邮箱格式（可选字段，如果提供则必须符合格式）
    规则：
    - 符合标准邮箱格式：local@domain.tld
    """
    if email is None:
        return None
    
    email = email.strip()
    
    if not email:
        return None
    
    # 转换为小写
    email = email.lower()
    
    if len(email) > 100:
        raise ValueError('邮箱长度不能超过100个字符')
    
    if not EMAIL_PATTERN_COMPILED.match(email):
        raise ValueError(
            '邮箱格式错误：请输入有效的邮箱地址，'
            '如：user@example.com'
        )
    
    return email


def validate_password(password: str) -> str:
    """
    验证密码强度
    规则：
    - 长度：6-20个字符
    - 至少包含两种类型：大小写字母、数字、特殊字符
    - 不能包含空格
    """
    if not password:
        raise ValueError('密码不能为空')
    
    if ' ' in password:
        raise ValueError('密码不能包含空格')
    
    if len(password) < 6:
        raise ValueError('密码长度至少为6个字符')
    
    if len(password) > 20:
        raise ValueError('密码长度不能超过20个字符')
    
    # 检查密码复杂度
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?/~`]', password))
    
    # 统计包含的类型数量
    type_count = sum([
        has_uppercase or has_lowercase,  # 字母算一种
        has_digit,
        has_special
    ])
    
    if type_count < 2:
        raise ValueError(
            '密码强度不足：密码必须至少包含两种类型，'
            '如：字母+数字、字母+特殊字符、数字+特殊字符'
        )
    
    return password


def validate_product_code(code: str) -> str:
    """
    验证产品编码格式
    规则：
    - 首字符必须是字母或数字
    - 只能包含字母、数字、横线、下划线
    - 长度：1-50个字符
    """
    if not code:
        raise ValueError('产品编码不能为空')
    
    code = code.strip().upper()  # 统一转换为大写
    
    if len(code) < 1:
        raise ValueError('产品编码不能为空')
    
    if len(code) > 50:
        raise ValueError('产品编码长度不能超过50个字符')
    
    if not PRODUCT_CODE_PATTERN_COMPILED.match(code):
        raise ValueError(
            '产品编码格式错误：首字符必须是字母或数字，'
            '只能包含字母、数字、横线、下划线，长度1-50个字符'
        )
    
    return code


def validate_price(price: Decimal, field_name: str = '价格') -> Decimal:
    """
    验证价格
    规则：
    - 必须大于等于0
    - 最多保留2位小数
    - 最大值：999999999.99（约10亿）
    """
    if price < 0:
        raise ValueError(f'{field_name}不能为负数')
    
    max_price = Decimal('999999999.99')
    if price > max_price:
        raise ValueError(f'{field_name}不能超过999,999,999.99')
    
    # 检查小数位数
    decimal_str = str(price)
    if '.' in decimal_str:
        decimal_part = decimal_str.split('.')[1]
        if len(decimal_part) > 2:
            raise ValueError(f'{field_name}最多只能保留2位小数')
    
    return price


def validate_stock_quantity(quantity: int, field_name: str = '库存数量') -> int:
    """
    验证库存数量
    规则：
    - 必须大于等于0
    - 最大值：999999
    """
    if quantity < 0:
        raise ValueError(f'{field_name}不能为负数')
    
    max_quantity = 999999
    if quantity > max_quantity:
        raise ValueError(f'{field_name}不能超过{max_quantity}')
    
    return quantity


def validate_min_max_stock(min_stock: int, max_stock: int) -> tuple:
    """
    验证最低库存和最高库存的关系
    规则：
    - 最低库存必须 >= 0
    - 最高库存必须 > 最低库存
    - 最高库存必须 >= 1
    """
    if min_stock < 0:
        raise ValueError('最低库存不能为负数')
    
    if max_stock < 1:
        raise ValueError('最高库存必须至少为1')
    
    if max_stock <= min_stock:
        raise ValueError('最高库存必须大于最低库存')
    
    return min_stock, max_stock


# ==================== 用户相关的Schema ====================

class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        description="用户名：首字母必须是英文字母，只能包含字母、数字、下划线"
    )
    real_name: Optional[str] = Field(
        None, 
        max_length=50, 
        description="真实姓名：最多50个字符"
    )
    email: Optional[str] = Field(
        None, 
        max_length=100, 
        description="电子邮箱：标准邮箱格式"
    )
    phone: Optional[str] = Field(
        None, 
        max_length=20, 
        description="联系电话：11位中国大陆手机号"
    )
    role: str = Field(
        default="user", 
        description="角色：admin-管理员，user-普通用户"
    )

    @field_validator('username')
    @classmethod
    def validate_username_field(cls, v: str) -> str:
        return validate_username(v)

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('email')
    @classmethod
    def validate_email_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_email(v)

    @field_validator('real_name')
    @classmethod
    def validate_real_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and len(v) > 50:
                raise ValueError('真实姓名长度不能超过50个字符')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = ['admin', 'user']
        if v not in valid_roles:
            raise ValueError(f'角色值无效，必须是：{valid_roles}')
        return v


class UserCreate(UserBase):
    """
    创建用户时的模型
    """
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=20, 
        description="密码：6-20个字符，至少包含两种类型（字母、数字、特殊字符）"
    )

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v)


class UserUpdate(BaseModel):
    """
    更新用户时的模型
    """
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    email: Optional[str] = Field(None, max_length=100, description="电子邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    role: Optional[str] = Field(None, description="角色")
    is_active: Optional[bool] = Field(None, description="是否激活")
    password: Optional[str] = Field(
        None, 
        min_length=6, 
        max_length=20, 
        description="新密码（可选）"
    )

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('email')
    @classmethod
    def validate_email_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_email(v)

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_password(v)
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_roles = ['admin', 'user']
            if v not in valid_roles:
                raise ValueError(f'角色值无效，必须是：{valid_roles}')
        return v

    @field_validator('real_name')
    @classmethod
    def validate_real_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and len(v) > 50:
                raise ValueError('真实姓名长度不能超过50个字符')
        return v


class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 分类相关的Schema ====================

class CategoryBase(BaseModel):
    """
    分类基础模型
    """
    name: str = Field(..., max_length=100, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: int = Field(default=0, description="排序")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('分类名称不能为空')
        if len(v) > 100:
            raise ValueError('分类名称长度不能超过100个字符')
        return v

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: int) -> int:
        if v < 0:
            raise ValueError('排序值不能为负数')
        if v > 99999:
            raise ValueError('排序值不能超过99999')
        return v


class CategoryCreate(CategoryBase):
    """
    创建分类时的模型
    """
    pass


class CategoryUpdate(BaseModel):
    """
    更新分类时的模型
    """
    name: Optional[str] = Field(None, max_length=100, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否启用")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('分类名称不能为空')
            if len(v) > 100:
                raise ValueError('分类名称长度不能超过100个字符')
        return v

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 0:
                raise ValueError('排序值不能为负数')
            if v > 99999:
                raise ValueError('排序值不能超过99999')
        return v


class CategoryResponse(CategoryBase):
    """
    分类响应模型
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryWithChildren(CategoryResponse):
    """
    带子分类的分类模型
    """
    children: List["CategoryWithChildren"] = []

    class Config:
        from_attributes = True


# ==================== 产品相关的Schema ====================

class ProductBase(BaseModel):
    """
    产品基础模型
    """
    name: str = Field(..., max_length=200, description="产品名称")
    code: str = Field(
        ..., 
        max_length=50, 
        description="产品编码：首字符必须是字母或数字，只能包含字母、数字、横线、下划线"
    )
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, description="产品描述")
    specification: Optional[str] = Field(None, max_length=200, description="产品规格")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    cost_price: Decimal = Field(default=Decimal("0.00"), description="成本价：>=0，最多2位小数")
    selling_price: Decimal = Field(default=Decimal("0.00"), description="销售价：>=0，最多2位小数")
    stock_quantity: int = Field(default=0, description="库存数量：>=0，最大999999")
    min_stock: int = Field(default=0, description="最低库存预警：>=0")
    max_stock: int = Field(default=99999, description="最高库存：>最低库存")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('产品名称不能为空')
        if len(v) > 200:
            raise ValueError('产品名称长度不能超过200个字符')
        return v

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_product_code(v)

    @field_validator('cost_price')
    @classmethod
    def validate_cost_price(cls, v: Decimal) -> Decimal:
        return validate_price(v, '成本价')

    @field_validator('selling_price')
    @classmethod
    def validate_selling_price(cls, v: Decimal) -> Decimal:
        return validate_price(v, '销售价')

    @field_validator('stock_quantity')
    @classmethod
    def validate_stock_quantity(cls, v: int) -> int:
        return validate_stock_quantity(v, '库存数量')

    @field_validator('min_stock')
    @classmethod
    def validate_min_stock(cls, v: int) -> int:
        if v < 0:
            raise ValueError('最低库存不能为负数')
        if v > 999999:
            raise ValueError('最低库存不能超过999999')
        return v

    @field_validator('max_stock')
    @classmethod
    def validate_max_stock(cls, v: int) -> int:
        if v < 1:
            raise ValueError('最高库存必须至少为1')
        if v > 9999999:
            raise ValueError('最高库存不能超过9999999')
        return v

    @field_validator('specification')
    @classmethod
    def validate_specification(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError('产品规格长度不能超过200个字符')
        return v

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 20:
                raise ValueError('计量单位长度不能超过20个字符')
        return v

    @model_validator(mode='after')
    def check_min_max_stock(self) -> 'ProductBase':
        """
        验证最低库存和最高库存的关系
        """
        min_stock = self.min_stock
        max_stock = self.max_stock
        
        if max_stock <= min_stock:
            raise ValueError('最高库存必须大于最低库存')
        
        return self


class ProductCreate(ProductBase):
    """
    创建产品时的模型
    """
    pass


class ProductUpdate(BaseModel):
    """
    更新产品时的模型
    """
    name: Optional[str] = Field(None, max_length=200, description="产品名称")
    code: Optional[str] = Field(
        None, 
        max_length=50, 
        description="产品编码：首字符必须是字母或数字，只能包含字母、数字、横线、下划线"
    )
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, description="产品描述")
    specification: Optional[str] = Field(None, max_length=200, description="产品规格")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    cost_price: Optional[Decimal] = Field(None, description="成本价")
    selling_price: Optional[Decimal] = Field(None, description="销售价")
    min_stock: Optional[int] = Field(None, description="最低库存预警")
    max_stock: Optional[int] = Field(None, description="最高库存")
    status: Optional[int] = Field(None, description="状态：1-上架，0-下架")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_product_code(v)
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('产品名称不能为空')
            if len(v) > 200:
                raise ValueError('产品名称长度不能超过200个字符')
        return v

    @field_validator('cost_price')
    @classmethod
    def validate_cost_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            return validate_price(v, '成本价')
        return v

    @field_validator('selling_price')
    @classmethod
    def validate_selling_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            return validate_price(v, '销售价')
        return v

    @field_validator('min_stock')
    @classmethod
    def validate_min_stock(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 0:
                raise ValueError('最低库存不能为负数')
            if v > 999999:
                raise ValueError('最低库存不能超过999999')
        return v

    @field_validator('max_stock')
    @classmethod
    def validate_max_stock(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 1:
                raise ValueError('最高库存必须至少为1')
            if v > 9999999:
                raise ValueError('最高库存不能超过9999999')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [0, 1]:
            raise ValueError('状态值无效，必须是0（下架）或1（上架）')
        return v

    @field_validator('specification')
    @classmethod
    def validate_specification(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError('产品规格长度不能超过200个字符')
        return v

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 20:
                raise ValueError('计量单位长度不能超过20个字符')
        return v


class ProductResponse(ProductBase):
    """
    产品响应模型
    """
    id: int
    image: Optional[str] = Field(None, description="产品图片路径")
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductWithCategory(ProductResponse):
    """
    带分类信息的产品模型
    """
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True


# ==================== 进销存记录相关的Schema ====================

class InventoryRecordBase(BaseModel):
    """
    进销存记录基础模型
    """
    product_id: int = Field(..., description="产品ID")
    record_type: str = Field(..., description="类型：in-入库，out-出库")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: Decimal = Field(default=Decimal("0.00"), description="单价")
    remark: Optional[str] = Field(None, description="备注")
    reference_no: Optional[str] = Field(None, max_length=50, description="参考单号")

    @field_validator('record_type')
    @classmethod
    def validate_record_type(cls, v: str) -> str:
        valid_types = ['in', 'out']
        if v not in valid_types:
            raise ValueError(f'记录类型无效，必须是：{valid_types}')
        return v

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('数量必须大于0')
        if v > 999999:
            raise ValueError('数量不能超过999999')
        return v

    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v: Decimal) -> Decimal:
        return validate_price(v, '单价')

    @field_validator('reference_no')
    @classmethod
    def validate_reference_no(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 50:
                raise ValueError('参考单号长度不能超过50个字符')
        return v


class InventoryRecordCreate(InventoryRecordBase):
    """
    创建进销存记录时的模型
    """
    operator_id: Optional[int] = Field(None, description="操作人ID")


class InventoryRecordResponse(InventoryRecordBase):
    """
    进销存记录响应模型
    """
    id: int
    total_amount: Decimal
    operator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryRecordWithDetail(InventoryRecordResponse):
    """
    带产品和操作人信息的进销存记录模型
    """
    product: Optional[ProductResponse] = None
    operator: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# ==================== 数据看板相关的Schema ====================

class DashboardStats(BaseModel):
    """
    数据看板统计模型
    """
    total_products: int = Field(description="产品总数")
    total_categories: int = Field(description="分类总数")
    total_users: int = Field(description="用户总数")
    total_stock_value: Decimal = Field(description="库存总价值")
    low_stock_count: int = Field(description="低库存产品数")
    today_in_count: int = Field(description="今日入库数量")
    today_out_count: int = Field(description="今日出库数量")
    today_in_amount: Decimal = Field(description="今日入库金额")
    today_out_amount: Decimal = Field(description="今日出库金额")


# ==================== 通用响应Schema ====================

class ApiResponse(BaseModel):
    """
    通用API响应模型
    """
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="消息")
    data: Optional[dict] = Field(None, description="数据")


class PaginatedResponse(BaseModel):
    """
    分页响应模型
    """
    items: List = Field(description="数据列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")

"""
数据模型定义模块
使用Pydantic定义请求和响应的数据结构
确保数据验证和类型安全
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator


# ==================== 通用响应模型 ====================

class ApiResponse(BaseModel):
    """
    通用API响应模型
    
    所有API响应都应该使用此格式，确保前端统一处理
    """
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="操作成功", description="消息描述")
    data: Optional[Any] = Field(default=None, description="响应数据")

    class Config:
        from_attributes = True


class PageResponse(ApiResponse):
    """
    分页响应模型
    
    用于需要分页查询的接口
    """
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页数量")


# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserCreate(UserBase):
    """用户注册模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """密码验证"""
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模型(不含敏感信息)"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    is_active: bool = Field(description="是否激活")
    created_at: datetime = Field(description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")
    user: UserResponse = Field(description="用户信息")


# ==================== 商品相关模型 ====================

class ProductBase(BaseModel):
    """商品基础模型"""
    product_name: str = Field(..., max_length=200, description="商品名称")
    product_code: str = Field(..., max_length=50, description="商品编码")
    description: Optional[str] = Field(None, description="商品描述")
    original_price: float = Field(..., gt=0, description="原价")
    seckill_price: float = Field(..., gt=0, description="秒杀价")
    stock_quantity: int = Field(..., ge=0, description="库存数量")
    category: Optional[str] = Field(None, max_length=100, description="商品分类")
    image_url: Optional[str] = Field(None, max_length=500, description="商品图片URL")


class ProductCreate(ProductBase):
    """商品创建模型"""
    pass


class ProductResponse(ProductBase):
    """商品响应模型"""
    id: int = Field(description="商品ID")
    sold_quantity: int = Field(description="已售数量")
    is_active: bool = Field(description="是否上架")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class ProductSeckillResponse(ProductResponse):
    """秒杀商品响应模型"""
    available_stock: int = Field(description="可用库存(Redis)")
    seckill_status: int = Field(description="秒杀状态(0:未开始,1:进行中,2:已结束)")


# ==================== 库存相关模型 ====================

class InventoryResponse(BaseModel):
    """库存响应模型"""
    product_id: int = Field(description="商品ID")
    total_stock: int = Field(description="总库存")
    available_stock: int = Field(description="可用库存")
    frozen_stock: int = Field(description="冻结库存")
    sold_stock: int = Field(description="已售库存")
    version: int = Field(description="乐观锁版本")

    class Config:
        from_attributes = True


# ==================== 订单相关模型 ====================

class OrderCreate(BaseModel):
    """创建订单请求模型"""
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(default=1, ge=1, le=10, description="购买数量")
    receiver_name: Optional[str] = Field(None, max_length=100, description="收货人姓名")
    receiver_phone: Optional[str] = Field(None, max_length=20, description="收货人电话")
    receiver_address: Optional[str] = Field(None, max_length=500, description="收货地址")
    remark: Optional[str] = Field(None, description="备注")


class OrderResponse(BaseModel):
    """订单响应模型"""
    id: int = Field(description="订单ID")
    order_no: str = Field(description="订单编号")
    user_id: int = Field(description="用户ID")
    product_id: int = Field(description="商品ID")
    product_name: str = Field(description="商品名称")
    product_code: str = Field(description="商品编码")
    quantity: int = Field(description="购买数量")
    unit_price: float = Field(description="商品单价")
    total_amount: float = Field(description="订单总金额")
    status: int = Field(description="订单状态")
    status_message: Optional[str] = Field(None, description="状态描述")
    receiver_name: Optional[str] = Field(None, description="收货人姓名")
    receiver_phone: Optional[str] = Field(None, description="收货人电话")
    receiver_address: Optional[str] = Field(None, description="收货地址")
    pay_time: Optional[datetime] = Field(None, description="支付时间")
    pay_method: Optional[str] = Field(None, description="支付方式")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class OrderListQuery(BaseModel):
    """订单列表查询模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    status: Optional[int] = Field(None, description="订单状态筛选")


# ==================== 抢单相关模型 ====================

class SeckillRequest(BaseModel):
    """抢单请求模型"""
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(default=1, ge=1, le=10, description="购买数量")


class SeckillResponse(BaseModel):
    """抢单响应模型"""
    success: bool = Field(description="是否抢单成功")
    order_no: Optional[str] = Field(None, description="订单编号(成功时返回)")
    message: str = Field(description="消息描述")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class SeckillStatusResponse(BaseModel):
    """抢单活动状态响应"""
    product_id: int = Field(description="商品ID")
    activity_status: int = Field(description="活动状态(0:未开始,1:进行中,2:已结束)")
    available_stock: int = Field(description="可用库存")
    sold_count: int = Field(description="已售数量")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")


# ==================== 活动配置模型 ====================

class SeckillConfigBase(BaseModel):
    """抢单活动配置基础模型"""
    config_name: str = Field(..., max_length=200, description="活动配置名称")
    product_id: int = Field(..., gt=0, description="关联商品ID")
    seckill_stock: int = Field(..., gt=0, description="秒杀库存数量")
    start_time: datetime = Field(..., description="活动开始时间")
    end_time: datetime = Field(..., description="活动结束时间")
    max_purchase_per_user: int = Field(default=1, ge=1, description="每人限购数量")
    ip_rate_limit: int = Field(default=10, ge=1, description="IP每秒限流数")
    user_rate_limit: int = Field(default=5, ge=1, description="用户每秒限流数")
    global_rate_limit: int = Field(default=10000, ge=1, description="全局每秒限流数")
    is_active: bool = Field(default=True, description="是否启用")


class SeckillConfigCreate(SeckillConfigBase):
    """创建抢单活动配置模型"""
    pass


class SeckillConfigResponse(SeckillConfigBase):
    """抢单活动配置响应模型"""
    id: int = Field(description="活动配置ID")
    activity_status: int = Field(description="活动状态")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


# ==================== 黑名单模型 ====================

class BlacklistCreate(BaseModel):
    """添加黑名单模型"""
    target_type: str = Field(..., description="目标类型(ip或user_id)")
    target_value: str = Field(..., description="目标值")
    reason: Optional[str] = Field(None, max_length=500, description="拉黑原因")
    expire_hours: Optional[int] = Field(None, ge=1, description="过期时间(小时)")


class BlacklistResponse(BaseModel):
    """黑名单响应模型"""
    id: int = Field(description="黑名单ID")
    target_type: str = Field(description="目标类型")
    target_value: str = Field(description="目标值")
    is_active: bool = Field(description="是否有效")
    reason: Optional[str] = Field(None, description="拉黑原因")
    expire_at: Optional[datetime] = Field(None, description="过期时间")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True


# ==================== 统计模型 ====================

class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_users: int = Field(description="总用户数")
    total_products: int = Field(description="总商品数")
    total_orders: int = Field(description="总订单数")
    total_sales: float = Field(description="总销售额")
    today_orders: int = Field(description="今日订单数")
    today_sales: float = Field(description="今日销售额")
    active_seckills: int = Field(description="进行中的秒杀活动数")

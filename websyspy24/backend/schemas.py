"""
Pydantic模型定义模块
用于API请求和响应的数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==================== 枚举定义 ====================
class CheckInType(str, Enum):
    """签到方式枚举"""
    CARD = "card"        # 刷卡
    QR = "qr"            # 扫码
    FACE = "face"        # 人脸识别


class LockerStatus(str, Enum):
    """储物柜状态枚举"""
    AVAILABLE = "available"      # 空闲
    OCCUPIED = "occupied"        # 占用
    MAINTENANCE = "maintenance"  # 故障维修


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"            # 已支付
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"    # 已退款


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    CASH = "cash"        # 现金
    WECHAT = "wechat"    # 微信
    ALIPAY = "alipay"    # 支付宝
    CARD = "card"        # 会员卡


# ==================== 会员相关模型 ====================
class MemberBase(BaseModel):
    """会员基础模型"""
    member_no: str = Field(..., description="会员编号")
    name: str = Field(..., description="会员姓名")
    id_card: Optional[str] = Field(None, description="身份证号")
    phone: Optional[str] = Field(None, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    card_no: Optional[str] = Field(None, description="卡号")
    qr_code: Optional[str] = Field(None, description="二维码内容")
    face_data: Optional[str] = Field(None, description="人脸特征数据")
    membership_type: str = Field(default="月卡", description="会籍类型")
    membership_start: date = Field(default=date.today, description="会籍开始日期")
    membership_end: date = Field(..., description="会籍到期日期")
    balance: float = Field(default=0.0, description="账户余额")
    status: str = Field(default="active", description="会员状态")
    remarks: Optional[str] = Field(None, description="备注信息")


class MemberCreate(MemberBase):
    """创建会员模型"""
    pass


class MemberUpdate(BaseModel):
    """更新会员模型"""
    name: Optional[str] = Field(None, description="会员姓名")
    id_card: Optional[str] = Field(None, description="身份证号")
    phone: Optional[str] = Field(None, description="手机号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    card_no: Optional[str] = Field(None, description="卡号")
    qr_code: Optional[str] = Field(None, description="二维码内容")
    face_data: Optional[str] = Field(None, description="人脸特征数据")
    membership_type: Optional[str] = Field(None, description="会籍类型")
    membership_end: Optional[date] = Field(None, description="会籍到期日期")
    status: Optional[str] = Field(None, description="会员状态")
    remarks: Optional[str] = Field(None, description="备注信息")


class MemberResponse(MemberBase):
    """会员响应模型"""
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# ==================== 签到相关模型 ====================
class CheckInBase(BaseModel):
    """签到基础模型"""
    member_id: int = Field(..., description="会员ID")
    check_in_type: CheckInType = Field(..., description="签到方式")
    device_no: Optional[str] = Field(None, description="签到设备编号")
    remarks: Optional[str] = Field(None, description="备注信息")


class CheckInCreate(CheckInBase):
    """创建签到记录模型"""
    pass


class CheckInResponse(CheckInBase):
    """签到响应模型"""
    id: int = Field(..., description="主键ID")
    check_in_time: datetime = Field(..., description="签到时间")
    status: str = Field(..., description="签到状态")
    fail_reason: Optional[str] = Field(None, description="失败原因")
    verification_details: Optional[str] = Field(None, description="验证详情")
    
    class Config:
        from_attributes = True


class CheckInVerifyRequest(BaseModel):
    """签到验证请求模型"""
    check_in_type: CheckInType = Field(..., description="签到方式")
    identifier: str = Field(..., description="识别信息（卡号、二维码内容、人脸数据等）")
    device_no: Optional[str] = Field(None, description="签到设备编号")


# ==================== 储物柜相关模型 ====================
class LockerBase(BaseModel):
    """储物柜基础模型"""
    locker_no: str = Field(..., description="储物柜编号")
    location: Optional[str] = Field(None, description="位置描述")
    locker_type: str = Field(default="medium", description="储物柜类型")
    status: LockerStatus = Field(default=LockerStatus.AVAILABLE, description="储物柜状态")
    remarks: Optional[str] = Field(None, description="备注信息")


class LockerCreate(LockerBase):
    """创建储物柜模型"""
    pass


class LockerUpdate(BaseModel):
    """更新储物柜模型"""
    location: Optional[str] = Field(None, description="位置描述")
    locker_type: Optional[str] = Field(None, description="储物柜类型")
    status: Optional[LockerStatus] = Field(None, description="储物柜状态")
    remarks: Optional[str] = Field(None, description="备注信息")


class LockerResponse(LockerBase):
    """储物柜响应模型"""
    id: int = Field(..., description="主键ID")
    status_updated_at: datetime = Field(..., description="状态更新时间")
    
    class Config:
        from_attributes = True


class LockerAssignRequest(BaseModel):
    """储物柜分配请求模型"""
    member_id: int = Field(..., description="会员ID")
    locker_id: Optional[int] = Field(None, description="储物柜ID（可选，不传则自动分配）")
    assign_type: str = Field(default="auto", description="分配方式")
    password: Optional[str] = Field(None, description="密码")


class LockerReturnRequest(BaseModel):
    """储物柜归还请求模型"""
    member_id: int = Field(..., description="会员ID")
    locker_id: int = Field(..., description="储物柜ID")


class LockerUsageResponse(BaseModel):
    """储物柜使用记录响应模型"""
    id: int
    member_id: int
    locker_id: int
    assign_type: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    password: Optional[str]
    remarks: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== 商品相关模型 ====================
class ProductBase(BaseModel):
    """商品基础模型"""
    product_code: str = Field(..., description="商品编码")
    name: str = Field(..., description="商品名称")
    category: Optional[str] = Field(None, description="商品分类")
    price: float = Field(default=0.0, description="销售价格")
    cost_price: Optional[float] = Field(default=0.0, description="成本价格")
    stock_quantity: int = Field(default=0, description="库存数量")
    warning_quantity: int = Field(default=10, description="库存预警数量")
    status: str = Field(default="active", description="商品状态")
    description: Optional[str] = Field(None, description="商品描述")


class ProductCreate(ProductBase):
    """创建商品模型"""
    pass


class ProductUpdate(BaseModel):
    """更新商品模型"""
    name: Optional[str] = Field(None, description="商品名称")
    category: Optional[str] = Field(None, description="商品分类")
    price: Optional[float] = Field(None, description="销售价格")
    cost_price: Optional[float] = Field(None, description="成本价格")
    stock_quantity: Optional[int] = Field(None, description="库存数量")
    warning_quantity: Optional[int] = Field(None, description="库存预警数量")
    status: Optional[str] = Field(None, description="商品状态")
    description: Optional[str] = Field(None, description="商品描述")


class ProductResponse(ProductBase):
    """商品响应模型"""
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# ==================== 优惠券相关模型 ====================
class CouponBase(BaseModel):
    """优惠券基础模型"""
    coupon_code: str = Field(..., description="优惠券码")
    name: str = Field(..., description="优惠券名称")
    coupon_type: str = Field(default="discount", description="优惠券类型")
    value: float = Field(default=0.0, description="折扣值")
    min_amount: float = Field(default=0.0, description="最低消费金额")
    expire_time: datetime = Field(..., description="过期时间")
    member_id: Optional[int] = Field(None, description="关联会员ID")
    remarks: Optional[str] = Field(None, description="备注信息")


class CouponCreate(CouponBase):
    """创建优惠券模型"""
    pass


class CouponResponse(CouponBase):
    """优惠券响应模型"""
    id: int = Field(..., description="主键ID")
    issue_time: datetime = Field(..., description="发放时间")
    status: str = Field(..., description="优惠券状态")
    used_time: Optional[datetime] = Field(None, description="使用时间")
    used_order_id: Optional[int] = Field(None, description="使用订单ID")
    
    class Config:
        from_attributes = True


# ==================== 订单相关模型 ====================
class OrderItemCreate(BaseModel):
    """订单明细创建模型"""
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(default=1, description="购买数量")
    remarks: Optional[str] = Field(None, description="备注信息")


class OrderCreate(BaseModel):
    """创建订单模型"""
    member_id: Optional[int] = Field(None, description="会员ID")
    order_type: str = Field(default="product", description="订单类型")
    items: List[OrderItemCreate] = Field(default=[], description="订单明细")
    coupon_code: Optional[str] = Field(None, description="使用的优惠券码")
    payment_method: Optional[PaymentMethod] = Field(None, description="支付方式")
    cashier: Optional[str] = Field(None, description="收银员")
    remarks: Optional[str] = Field(None, description="备注信息")


class OrderItemResponse(BaseModel):
    """订单明细响应模型"""
    id: int
    order_id: int
    product_id: int
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float
    remarks: Optional[str]
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """订单响应模型"""
    id: int
    order_no: str
    member_id: Optional[int]
    order_type: str
    total_amount: float
    discount_amount: float
    actual_amount: float
    payment_method: Optional[str]
    coupon_code: Optional[str]
    status: str
    order_time: datetime
    pay_time: Optional[datetime]
    cashier: Optional[str]
    remarks: Optional[str]
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """支付请求模型"""
    order_id: int = Field(..., description="订单ID")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    amount: Optional[float] = Field(None, description="支付金额（可选，默认订单金额）")
    transaction_no: Optional[str] = Field(None, description="支付流水号")


# ==================== 通用响应模型 ====================
class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="消息")
    data: Optional[dict] = Field(None, description="数据")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[dict] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页数量")

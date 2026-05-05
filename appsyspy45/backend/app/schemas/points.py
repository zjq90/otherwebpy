"""
积分和兑换相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 积分相关模型 ====================

class PointsTransactionResponse(BaseModel):
    """
    积分交易记录响应
    """
    id: int
    user_id: int
    transaction_type: str
    transaction_type_text: Optional[str]
    points: int
    balance_after: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    description: Optional[str]
    create_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class PointsSummaryResponse(BaseModel):
    """
    积分统计响应
    """
    current_points: int
    total_points: int
    total_earned: int
    total_spent: int
    total_expired: int


class InviteInfoResponse(BaseModel):
    """
    邀请信息响应
    """
    invite_code: str
    invite_url: str
    total_invited_count: int
    total_earned_points: int


class CreateExchangeOrderRequest(BaseModel):
    """
    创建兑换订单请求
    """
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(default=1, ge=1, description="数量")
    
    # 收货地址
    receiver_name: Optional[str] = Field(None, description="收货人姓名")
    receiver_phone: Optional[str] = Field(None, description="收货人电话")
    receiver_province: Optional[str] = Field(None, description="省")
    receiver_city: Optional[str] = Field(None, description="市")
    receiver_district: Optional[str] = Field(None, description="区")
    receiver_address: Optional[str] = Field(None, description="详细地址")
    
    address_id: Optional[int] = Field(None, description="使用的地址ID")
    remark: Optional[str] = Field(None, description="备注")


# ==================== 商品相关模型 ====================

class ProductCategoryResponse(BaseModel):
    """
    商品分类响应
    """
    id: int
    name: str
    code: str
    icon: Optional[str]
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """
    商品响应
    """
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    image: Optional[str]
    images: Optional[str]
    category_id: Optional[int]
    price: float
    points_price: int
    exchange_type: str
    required_clothing_quantity: int
    stock: int
    sales: int
    is_hot: int
    is_new: int
    
    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """
    商品详情响应
    """
    pass


# ==================== 兑换订单相关模型 ====================

class ExchangeOrderResponse(BaseModel):
    """
    兑换订单响应
    """
    id: int
    order_no: str
    user_id: int
    product_id: int
    product_name: Optional[str]
    product_image: Optional[str]
    quantity: int
    exchange_type: Optional[str]
    points_spent: int
    cash_spent: float
    clothing_spent: int
    
    # 收货地址
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    receiver_province: Optional[str]
    receiver_city: Optional[str]
    receiver_district: Optional[str]
    receiver_address: Optional[str]
    
    # 物流
    express_company: Optional[str]
    express_no: Optional[str]
    
    status: int
    status_text: str
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    
    class Config:
        from_attributes = True

"""
订单路由模块
包含订单创建、支付、查询等接口
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from decimal import Decimal
import json

from app.database import get_db
from app.models.user import User
from app.models.card import CardType, UserCard
from app.models.order import Order, ConsumptionRecord, Promotion
from app.schemas.order import (
    OrderCreate, OrderResponse, PaymentRequest, PaymentResponse,
    ConsumptionRecordResponse, PromotionResponse, MonthlyBillResponse
)
from app.utils.security import get_current_user
from app.utils.helpers import (
    generate_order_no, generate_card_number, calculate_discount
)

router = APIRouter(prefix="/orders", tags=["订单管理"])


@router.get("/promotions", response_model=List[PromotionResponse], summary="获取优惠活动列表")
def get_promotions(
    is_active: bool = Query(True, description="是否仅显示有效活动"),
    db: Session = Depends(get_db)
):
    """
    获取所有优惠活动列表
    
    - **is_active**: 是否仅显示有效活动
    """
    query = db.query(Promotion)
    
    if is_active:
        now = datetime.now()
        query = query.filter(
            Promotion.is_active == True,
            (Promotion.start_time == None) | (Promotion.start_time <= now),
            (Promotion.end_time == None) | (Promotion.end_time >= now)
        )
    
    promotions = query.order_by(Promotion.sort_order.desc(), Promotion.id).all()
    
    return [PromotionResponse.model_validate(p) for p in promotions]


@router.post("/create", response_model=OrderResponse, summary="创建订单")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新订单（购卡、续费等）
    
    - **order_type**: 订单类型（PURCHASE购卡, RENEWAL续费, GOODS商品）
    - **card_type_id**: 卡类型ID（购卡/续费时必需）
    - **quantity**: 购买数量
    - **promotion_id**: 优惠活动ID（可选）
    """
    # 验证卡类型
    if order_data.order_type in ["PURCHASE", "RENEWAL"]:
        if not order_data.card_type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="购卡/续费订单必须指定卡类型"
            )
        
        card_type = db.query(CardType).filter(
            CardType.id == order_data.card_type_id,
            CardType.is_on_sale == True
        ).first()
        
        if not card_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="卡类型不存在或已下架"
            )
        
        unit_price = card_type.current_price
        original_amount = unit_price * Decimal(order_data.quantity)
        title = f"{card_type.name} x {order_data.quantity}"
        description = card_type.description
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的订单类型"
        )
    
    # 计算优惠
    discount_amount = Decimal("0")
    promotion = None
    
    if order_data.promotion_id:
        promotion = db.query(Promotion).filter(
            Promotion.id == order_data.promotion_id,
            Promotion.is_active == True
        ).first()
        
        if promotion:
            try:
                discount_config = json.loads(promotion.discount_config)
                discount_amount, _ = calculate_discount(original_amount, discount_config)
            except json.JSONDecodeError:
                pass
    
    # 实付金额
    pay_amount = original_amount - discount_amount
    if pay_amount < 0:
        pay_amount = Decimal("0")
    
    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        user_id=current_user.id,
        order_type=order_data.order_type,
        card_type_id=order_data.card_type_id,
        goods_id=order_data.goods_id,
        title=title,
        description=description,
        quantity=order_data.quantity,
        unit_price=unit_price,
        original_amount=original_amount,
        discount_amount=discount_amount,
        pay_amount=pay_amount,
        status="PENDING",
        promotion_id=promotion.id if promotion else None
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.post("/pay", response_model=PaymentResponse, summary="支付订单")
def pay_order(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    支付订单
    
    - **order_id**: 订单ID
    - **pay_method**: 支付方式（WECHAT微信, ALIPAY支付宝）
    """
    # 查询订单
    order = db.query(Order).filter(
        Order.id == payment_data.order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.status == "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已支付"
        )
    
    if order.status in ["CANCELLED", "REFUNDED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已取消或已退款"
        )
    
    # 模拟支付（实际生产环境需要调用支付接口）
    # 这里直接假设支付成功
    now = datetime.now()
    order.pay_method = payment_data.pay_method
    order.third_pay_no = f"MOCK_{generate_order_no()}"
    order.status = "PAID"
    order.pay_time = now
    
    # 如果是购卡/续费订单，创建用户会员卡
    if order.order_type in ["PURCHASE", "RENEWAL"] and order.card_type_id:
        card_type = db.query(CardType).filter(CardType.id == order.card_type_id).first()
        
        if card_type:
            # 计算过期时间
            expire_time = None
            if card_type.valid_days:
                expire_time = now.date() + timedelta(days=card_type.valid_days)
            
            # 创建用户会员卡
            user_card = UserCard(
                user_id=current_user.id,
                card_type_id=card_type.id,
                card_number=generate_card_number(),
                purchase_time=now,
                activate_time=now,
                expire_time=expire_time,
                remaining_count=card_type.total_count,
                total_count=card_type.total_count,
                remaining_duration=card_type.total_duration,
                total_duration=card_type.total_duration,
                status="ACTIVE",
                order_id=order.id
            )
            db.add(user_card)
            
            # 创建消费记录
            consumption = ConsumptionRecord(
                user_id=current_user.id,
                record_type="PURCHASE" if order.order_type == "PURCHASE" else "RENEWAL",
                order_id=order.id,
                user_card_id=user_card.id,
                title=order.title,
                description=order.description,
                amount=order.pay_amount,
                created_at=now
            )
            db.add(consumption)
    
    db.commit()
    db.refresh(order)
    
    # 返回支付参数（模拟）
    return PaymentResponse(
        order_id=order.id,
        order_no=order.order_no,
        pay_amount=order.pay_amount,
        pay_method=payment_data.pay_method,
        pay_params={
            "mock": True,
            "message": "测试环境支付已完成",
            "third_pay_no": order.third_pay_no
        },
        status="SUCCESS"
    )


@router.get("/my", response_model=List[OrderResponse], summary="获取我的订单列表")
def get_my_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    order_type: Optional[str] = Query(None, description="订单类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的订单列表
    
    - **status**: 订单状态（PENDING待支付, PAID已支付, CANCELLED已取消, REFUNDED已退款）
    - **order_type**: 订单类型（PURCHASE购卡, RENEWAL续费, GOODS商品）
    - **page**: 页码
    - **page_size**: 每页数量
    """
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    if order_type:
        query = query.filter(Order.order_type == order_type)
    
    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/my/{order_id}", response_model=OrderResponse, summary="获取订单详情")
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定订单的详细信息
    
    - **order_id**: 订单ID
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或不属于当前用户"
        )
    
    return OrderResponse.model_validate(order)


@router.post("/my/{order_id}/cancel", response_model=OrderResponse, summary="取消订单")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消待支付的订单
    
    - **order_id**: 订单ID
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或不属于当前用户"
        )
    
    if order.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能取消待支付的订单"
        )
    
    order.status = "CANCELLED"
    order.cancel_time = datetime.now()
    db.commit()
    db.refresh(order)
    
    return OrderResponse.model_validate(order)

"""
收银管理API路由模块
提供商品管理、优惠券管理、订单管理、支付功能和流水对账
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import date, datetime, timedelta
import uuid

from database import get_db
from models import Product, Coupon, Order, OrderItem, PaymentRecord, Member, RechargeRecord
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CouponCreate, CouponResponse,
    OrderCreate, OrderResponse, OrderItemResponse,
    PaymentRequest, PaymentMethod, OrderStatus,
    ApiResponse, PaginatedResponse
)

# 创建路由实例
router = APIRouter(
    prefix="/api/cashier",
    tags=["收银管理"]
)


def generate_order_no() -> str:
    """
    生成订单号
    格式：ORD + 时间戳 + 随机字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"ORD{timestamp}{random_str}"


def generate_transaction_no() -> str:
    """
    生成支付流水号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    return f"TXN{timestamp}"


# ==================== 商品管理 ====================
@router.get("/products", response_model=PaginatedResponse, summary="获取商品列表")
def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（商品编码、名称）"),
    category: Optional[str] = Query(None, description="商品分类"),
    status: Optional[str] = Query(None, description="商品状态"),
    db: Session = Depends(get_db)
):
    """
    分页获取商品列表，支持搜索和筛选
    """
    query = db.query(Product)
    
    if keyword:
        query = query.filter(
            or_(
                Product.product_code.contains(keyword),
                Product.name.contains(keyword)
            )
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    if status:
        query = query.filter(Product.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(page_size).all()
    
    items = [ProductResponse.model_validate(p).model_dump() for p in products]
    
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/products", response_model=ProductResponse, summary="创建商品")
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    创建新商品
    """
    existing = db.query(Product).filter(Product.product_code == product_data.product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"商品编码 {product_data.product_code} 已存在")
    
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/products/{product_id}", response_model=ProductResponse, summary="更新商品")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    更新商品信息
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"商品ID {product_id} 不存在")
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/products/{product_id}", response_model=ApiResponse, summary="删除商品")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    逻辑删除商品（设置为下架状态）
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"商品ID {product_id} 不存在")
    
    product.status = "inactive"
    db.commit()
    
    return ApiResponse(
        success=True,
        message=f"商品 {product.name} 已下架",
        data={"product_id": product_id}
    )


# ==================== 优惠券管理 ====================
@router.get("/coupons", response_model=PaginatedResponse, summary="获取优惠券列表")
def get_coupons(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    coupon_code: Optional[str] = Query(None, description="优惠券码"),
    status: Optional[str] = Query(None, description="状态"),
    coupon_type: Optional[str] = Query(None, description="类型"),
    db: Session = Depends(get_db)
):
    """
    分页获取优惠券列表
    """
    query = db.query(Coupon)
    
    if coupon_code:
        query = query.filter(Coupon.coupon_code == coupon_code)
    
    if status:
        query = query.filter(Coupon.status == status)
    
    if coupon_type:
        query = query.filter(Coupon.coupon_type == coupon_type)
    
    total = query.count()
    offset = (page - 1) * page_size
    coupons = query.order_by(Coupon.issue_time.desc()).offset(offset).limit(page_size).all()
    
    items = [CouponResponse.model_validate(c).model_dump() for c in coupons]
    
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/coupons", response_model=CouponResponse, summary="创建优惠券")
def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db)
):
    """
    创建新优惠券
    """
    existing = db.query(Coupon).filter(Coupon.coupon_code == coupon_data.coupon_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"优惠券码 {coupon_data.coupon_code} 已存在")
    
    new_coupon = Coupon(**coupon_data.model_dump())
    db.add(new_coupon)
    db.commit()
    db.refresh(new_coupon)
    
    return new_coupon


@router.get("/coupons/validate/{coupon_code}", response_model=ApiResponse, summary="验证优惠券")
def validate_coupon(
    coupon_code: str,
    order_amount: float = Query(..., gt=0, description="订单金额"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    db: Session = Depends(get_db)
):
    """
    验证优惠券是否可用，并计算优惠金额
    """
    coupon = db.query(Coupon).filter(Coupon.coupon_code == coupon_code).first()
    
    if not coupon:
        return ApiResponse(success=False, message="优惠券不存在", data={"valid": False})
    
    # 检查状态
    if coupon.status != "available":
        return ApiResponse(success=False, message=f"优惠券状态异常: {coupon.status}", data={"valid": False})
    
    # 检查是否过期
    now = datetime.now()
    if coupon.expire_time < now:
        return ApiResponse(success=False, message="优惠券已过期", data={"valid": False})
    
    # 检查最低消费金额
    if order_amount < coupon.min_amount:
        return ApiResponse(
            success=False, 
            message=f"最低消费金额不足，需要满 {coupon.min_amount} 元", 
            data={"valid": False, "min_amount": coupon.min_amount}
        )
    
    # 检查是否是会员专属券
    if coupon.member_id and (not member_id or coupon.member_id != member_id):
        return ApiResponse(success=False, message="该优惠券仅限指定会员使用", data={"valid": False})
    
    # 计算优惠金额
    discount_amount = 0.0
    if coupon.coupon_type == "discount":
        # 折扣券：金额 * 折扣值
        discount_amount = order_amount * (1 - coupon.value)
    elif coupon.coupon_type == "cash":
        # 代金券：直接抵扣
        discount_amount = min(coupon.value, order_amount)
    elif coupon.coupon_type == "gift":
        # 赠品券：不计算金额
        discount_amount = 0.0
    
    return ApiResponse(
        success=True,
        message="优惠券有效",
        data={
            "valid": True,
            "coupon_id": coupon.id,
            "coupon_code": coupon.coupon_code,
            "coupon_name": coupon.name,
            "coupon_type": coupon.coupon_type,
            "discount_amount": round(discount_amount, 2)
        }
    )


# ==================== 订单管理 ====================
@router.post("/orders/create", response_model=ApiResponse, summary="创建订单")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    创建订单，支持快速下单、价格计算、优惠券核销
    
    流程：
    1. 验证商品库存
    2. 计算订单金额
    3. 验证并应用优惠券
    4. 创建订单和订单明细
    """
    # 生成订单号
    order_no = generate_order_no()
    
    # 验证会员
    member = None
    if order_data.member_id:
        member = db.query(Member).filter(Member.id == order_data.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail=f"会员ID {order_data.member_id} 不存在")
    
    # 验证商品并计算金额
    total_amount = 0.0
    order_items_data = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"商品ID {item.product_id} 不存在")
        
        if product.status != "active":
            raise HTTPException(status_code=400, detail=f"商品 {product.name} 已下架")
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"商品 {product.name} 库存不足")
        
        # 计算小计
        subtotal = product.price * item.quantity
        total_amount += subtotal
        
        order_items_data.append({
            "product_id": item.product_id,
            "product_name": product.name,
            "unit_price": product.price,
            "quantity": item.quantity,
            "subtotal": subtotal,
            "remarks": item.remarks
        })
    
    # 处理优惠券
    discount_amount = 0.0
    used_coupon = None
    
    if order_data.coupon_code and total_amount > 0:
        coupon = db.query(Coupon).filter(Coupon.coupon_code == order_data.coupon_code).first()
        if coupon:
            # 验证优惠券
            coupon_valid = True
            now = datetime.now()
            
            if coupon.status != "available":
                coupon_valid = False
            elif coupon.expire_time < now:
                coupon_valid = False
            elif total_amount < coupon.min_amount:
                coupon_valid = False
            elif coupon.member_id and (not order_data.member_id or coupon.member_id != order_data.member_id):
                coupon_valid = False
            
            if coupon_valid:
                used_coupon = coupon
                # 计算优惠金额
                if coupon.coupon_type == "discount":
                    discount_amount = total_amount * (1 - coupon.value)
                elif coupon.coupon_type == "cash":
                    discount_amount = min(coupon.value, total_amount)
                
                # 优惠金额不能超过订单金额
                discount_amount = min(discount_amount, total_amount)
    
    # 计算实际支付金额
    actual_amount = total_amount - discount_amount
    actual_amount = max(actual_amount, 0.0)
    
    # 创建订单
    new_order = Order(
        order_no=order_no,
        member_id=order_data.member_id,
        order_type=order_data.order_type,
        total_amount=round(total_amount, 2),
        discount_amount=round(discount_amount, 2),
        actual_amount=round(actual_amount, 2),
        payment_method=order_data.payment_method.value if order_data.payment_method else None,
        coupon_code=order_data.coupon_code,
        status=OrderStatus.PENDING.value,
        cashier=order_data.cashier,
        remarks=order_data.remarks
    )
    
    db.add(new_order)
    db.flush()  # 获取order_id
    
    # 创建订单明细
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            **item_data
        )
        db.add(order_item)
        
        # 扣减库存
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if product:
            product.stock_quantity -= item_data["quantity"]
    
    # 如果有支付方式，直接支付
    if order_data.payment_method:
        # 更新优惠券状态
        if used_coupon:
            used_coupon.status = "used"
            used_coupon.used_time = datetime.now()
            used_coupon.used_order_id = new_order.id
        
        # 更新订单状态
        new_order.status = OrderStatus.PAID.value
        new_order.pay_time = datetime.now()
        
        # 创建支付记录
        payment = PaymentRecord(
            order_id=new_order.id,
            order_no=order_no,
            transaction_no=generate_transaction_no(),
            payment_method=order_data.payment_method.value,
            amount=actual_amount,
            status="success",
            pay_time=datetime.now()
        )
        db.add(payment)
        
        # 如果是会员卡支付，扣减余额
        if order_data.payment_method == PaymentMethod.CARD and member:
            if member.balance < actual_amount:
                db.rollback()
                raise HTTPException(status_code=400, detail="会员卡余额不足")
            member.balance -= actual_amount
    
    db.commit()
    db.refresh(new_order)
    
    # 构建响应数据
    order_response = OrderResponse.model_validate(new_order).model_dump()
    order_response["order_items"] = [
        OrderItemResponse.model_validate(item).model_dump() 
        for item in new_order.order_items
    ]
    
    return ApiResponse(
        success=True,
        message="订单创建成功",
        data=order_response
    )


@router.post("/orders/pay", response_model=ApiResponse, summary="订单支付")
def pay_order(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db)
):
    """
    订单支付
    支持现金、微信、支付宝、会员卡等多种支付方式
    """
    # 查询订单
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"订单ID {payment_data.order_id} 不存在")
    
    if order.status != OrderStatus.PENDING.value:
        return ApiResponse(
            success=False,
            message=f"订单状态异常: {order.status}",
            data={"order_id": payment_data.order_id}
        )
    
    # 确定支付金额
    amount = payment_data.amount if payment_data.amount else order.actual_amount
    
    # 验证会员（如果是会员卡支付）
    member = None
    if payment_data.payment_method == PaymentMethod.CARD and order.member_id:
        member = db.query(Member).filter(Member.id == order.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail=f"会员ID {order.member_id} 不存在")
        
        if member.balance < amount:
            raise HTTPException(status_code=400, detail="会员卡余额不足")
    
    # 更新订单状态
    order.status = OrderStatus.PAID.value
    order.payment_method = payment_data.payment_method.value
    order.pay_time = datetime.now()
    
    # 如果使用了优惠券，更新优惠券状态
    if order.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.coupon_code == order.coupon_code).first()
        if coupon and coupon.status == "available":
            coupon.status = "used"
            coupon.used_time = datetime.now()
            coupon.used_order_id = order.id
    
    # 创建支付记录
    payment = PaymentRecord(
        order_id=order.id,
        order_no=order.order_no,
        transaction_no=payment_data.transaction_no or generate_transaction_no(),
        payment_method=payment_data.payment_method.value,
        amount=amount,
        status="success",
        pay_time=datetime.now()
    )
    db.add(payment)
    
    # 会员卡支付：扣减余额
    if payment_data.payment_method == PaymentMethod.CARD and member:
        member.balance -= amount
    
    db.commit()
    db.refresh(order)
    db.refresh(payment)
    
    return ApiResponse(
        success=True,
        message="支付成功",
        data={
            "order_id": order.id,
            "order_no": order.order_no,
            "payment_method": payment.payment_method,
            "amount": payment.amount,
            "transaction_no": payment.transaction_no,
            "pay_time": payment.pay_time.isoformat() if payment.pay_time else None
        }
    )


@router.get("/orders", response_model=PaginatedResponse, summary="获取订单列表")
def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    order_no: Optional[str] = Query(None, description="订单号"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    status: Optional[str] = Query(None, description="订单状态"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    分页获取订单列表
    """
    query = db.query(Order)
    
    if order_no:
        query = query.filter(Order.order_no.contains(order_no))
    
    if member_id:
        query = query.filter(Order.member_id == member_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    if start_date:
        query = query.filter(Order.order_time >= start_date)
    if end_date:
        query = query.filter(Order.order_time < end_date + timedelta(days=1))
    
    total = query.count()
    offset = (page - 1) * page_size
    orders = query.order_by(Order.order_time.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for order in orders:
        order_dict = OrderResponse.model_validate(order).model_dump()
        order_dict["order_items"] = [
            OrderItemResponse.model_validate(item).model_dump()
            for item in order.order_items
        ]
        items.append(order_dict)
    
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/orders/{order_id}", response_model=ApiResponse, summary="获取订单详情")
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    获取订单详情
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"订单ID {order_id} 不存在")
    
    order_dict = OrderResponse.model_validate(order).model_dump()
    order_dict["order_items"] = [
        OrderItemResponse.model_validate(item).model_dump()
        for item in order.order_items
    ]
    
    # 获取支付记录
    payments = db.query(PaymentRecord).filter(PaymentRecord.order_id == order_id).all()
    order_dict["payments"] = [
        {
            "id": p.id,
            "transaction_no": p.transaction_no,
            "payment_method": p.payment_method,
            "amount": p.amount,
            "status": p.status,
            "pay_time": p.pay_time.isoformat() if p.pay_time else None
        }
        for p in payments
    ]
    
    return ApiResponse(success=True, message="获取成功", data=order_dict)


# ==================== 流水对账 ====================
@router.get("/reconcile/daily", response_model=ApiResponse, summary="获取日对账数据")
def get_daily_reconcile(
    date_str: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认今天"),
    db: Session = Depends(get_db)
):
    """
    获取指定日期的对账数据
    """
    # 确定日期
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    else:
        target_date = date.today()
    
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    # 查询当日支付记录
    payments = db.query(PaymentRecord).filter(
        PaymentRecord.pay_time >= start_of_day,
        PaymentRecord.pay_time <= end_of_day,
        PaymentRecord.status == "success"
    ).all()
    
    # 按支付方式统计
    by_method = {
        "cash": 0.0,
        "wechat": 0.0,
        "alipay": 0.0,
        "card": 0.0
    }
    
    total_amount = 0.0
    total_count = 0
    
    for p in payments:
        method = p.payment_method
        if method in by_method:
            by_method[method] += p.amount
        total_amount += p.amount
        total_count += 1
    
    # 查询当日订单统计
    orders = db.query(Order).filter(
        Order.order_time >= start_of_day,
        Order.order_time <= end_of_day
    ).all()
    
    order_stats = {
        "total": len(orders),
        "paid": sum(1 for o in orders if o.status == OrderStatus.PAID.value),
        "pending": sum(1 for o in orders if o.status == OrderStatus.PENDING.value),
        "cancelled": sum(1 for o in orders if o.status == OrderStatus.CANCELLED.value),
        "total_amount": sum(o.total_amount for o in orders if o.status == OrderStatus.PAID.value),
        "discount_amount": sum(o.discount_amount for o in orders if o.status == OrderStatus.PAID.value),
        "actual_amount": sum(o.actual_amount for o in orders if o.status == OrderStatus.PAID.value)
    }
    
    return ApiResponse(
        success=True,
        message="获取对账数据成功",
        data={
            "date": target_date.isoformat(),
            "payment_stats": {
                "total_count": total_count,
                "total_amount": round(total_amount, 2),
                "by_method": {k: round(v, 2) for k, v in by_method.items()}
            },
            "order_stats": order_stats
        }
    )


# ==================== 会员充值 ====================
@router.post("/recharge", response_model=ApiResponse, summary="会员充值")
def member_recharge(
    member_id: int = Query(..., description="会员ID"),
    amount: float = Query(..., gt=0, description="充值金额"),
    gift_amount: float = Query(0.0, ge=0, description="赠送金额"),
    payment_method: PaymentMethod = Query(default=PaymentMethod.CASH, description="支付方式"),
    operator: Optional[str] = Query(None, description="操作人"),
    db: Session = Depends(get_db)
):
    """
    会员充值，支持赠送金额
    """
    # 查询会员
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    if member.status != "active":
        raise HTTPException(status_code=400, detail="会员状态异常，无法充值")
    
    # 记录充值前余额
    balance_before = member.balance
    
    # 更新余额
    total_add = amount + gift_amount
    member.balance += total_add
    
    # 生成订单号
    order_no = generate_order_no()
    
    # 创建充值订单
    order = Order(
        order_no=order_no,
        member_id=member_id,
        order_type="recharge",
        total_amount=amount,
        discount_amount=0.0,
        actual_amount=amount,
        payment_method=payment_method.value,
        status=OrderStatus.PAID.value,
        order_time=datetime.now(),
        pay_time=datetime.now(),
        cashier=operator,
        remarks=f"充值 {amount} 元，赠送 {gift_amount} 元"
    )
    db.add(order)
    db.flush()
    
    # 创建支付记录
    payment = PaymentRecord(
        order_id=order.id,
        order_no=order_no,
        transaction_no=generate_transaction_no(),
        payment_method=payment_method.value,
        amount=amount,
        status="success",
        pay_time=datetime.now()
    )
    db.add(payment)
    
    # 创建充值记录
    recharge = RechargeRecord(
        member_id=member_id,
        order_id=order.id,
        recharge_amount=amount,
        gift_amount=gift_amount,
        payment_method=payment_method.value,
        balance_before=balance_before,
        balance_after=member.balance,
        status="success",
        recharge_time=datetime.now(),
        operator=operator
    )
    db.add(recharge)
    
    db.commit()
    db.refresh(member)
    db.refresh(recharge)
    
    return ApiResponse(
        success=True,
        message="充值成功",
        data={
            "member_id": member_id,
            "member_name": member.name,
            "recharge_amount": amount,
            "gift_amount": gift_amount,
            "balance_before": balance_before,
            "balance_after": member.balance,
            "order_no": order_no,
            "recharge_time": recharge.recharge_time.isoformat()
        }
    )

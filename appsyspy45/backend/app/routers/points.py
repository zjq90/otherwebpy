"""
积分和兑换路由模块
包含积分查询、积分交易记录、邀请奖励、商品兑换等功能
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from datetime import datetime
from typing import Optional, List
import logging

from app.database import get_db
from app.models import (
    User, PointsTransaction, Invite, PointsConfig,
    Product, ProductCategory, ExchangeOrder, UserAddress, RecycleOrder
)
from app.schemas.points import (
    PointsTransactionResponse, PointsSummaryResponse,
    InviteInfoResponse, CreateExchangeOrderRequest,
    ProductCategoryResponse, ProductResponse, ExchangeOrderResponse
)
from app.schemas.common import success, success_page, error, ERROR_CODES
from app.config import get_settings, EXCHANGE_ORDER_STATUS, POINTS_TRANSACTION_TYPES
from app.utils.security import generate_order_no
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/points", tags=["积分与兑换"])


# ==================== 积分相关 ====================

@router.get("/summary")
async def get_points_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取积分统计信息
    """
    # 计算总收入
    earned_result = await db.execute(
        select(func.sum(PointsTransaction.points)).where(
            PointsTransaction.user_id == current_user.id,
            PointsTransaction.points > 0
        )
    )
    total_earned = earned_result.scalar() or 0
    
    # 计算总支出
    spent_result = await db.execute(
        select(func.sum(PointsTransaction.points)).where(
            PointsTransaction.user_id == current_user.id,
            PointsTransaction.points < 0
        )
    )
    total_spent = abs(spent_result.scalar() or 0)
    
    summary = {
        "current_points": current_user.points,
        "total_points": current_user.total_points,
        "total_earned": total_earned,
        "total_spent": total_spent,
        "total_expired": 0  # 暂不支持过期积分
    }
    
    return success(data=summary)


@router.get("/transactions")
async def get_points_transactions(
    transaction_type: Optional[str] = Query(None, description="交易类型筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取积分交易记录列表
    """
    # 构建查询条件
    conditions = [PointsTransaction.user_id == current_user.id]
    
    if transaction_type:
        conditions.append(PointsTransaction.transaction_type == transaction_type)
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(PointsTransaction.id)).where(*conditions)
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(PointsTransaction)
        .where(*conditions)
        .order_by(PointsTransaction.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    transactions = result.scalars().all()
    
    # 转换为字典并添加类型描述
    transaction_list = []
    for t in transactions:
        t_dict = t.to_dict()
        # 添加交易类型描述
        if t.transaction_type in POINTS_TRANSACTION_TYPES:
            t_dict["type_info"] = POINTS_TRANSACTION_TYPES[t.transaction_type]
        transaction_list.append(t_dict)
    
    return success_page(
        items=transaction_list,
        total=total,
        page=page,
        page_size=page_size
    )


# ==================== 邀请相关 ====================

@router.get("/invite/info")
async def get_invite_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取邀请信息
    """
    # 统计邀请人数
    count_result = await db.execute(
        select(func.count(Invite.id)).where(Invite.inviter_id == current_user.id)
    )
    total_invited = count_result.scalar() or 0
    
    # 统计邀请获得的积分
    points_result = await db.execute(
        select(func.sum(Invite.inviter_points_earned)).where(
            Invite.inviter_id == current_user.id
        )
    )
    total_earned = points_result.scalar() or 0
    
    # 生成邀请链接
    invite_url = f"/pages/register/register?invite_code={current_user.invite_code}"
    
    # 获取邀请奖励配置
    result = await db.execute(
        select(PointsConfig).where(PointsConfig.config_key == "invite_inviter_bonus")
    )
    inviter_bonus = result.scalar_one_or_none()
    
    result = await db.execute(
        select(PointsConfig).where(PointsConfig.config_key == "invite_invitee_bonus")
    )
    invitee_bonus = result.scalar_one_or_none()
    
    info = {
        "invite_code": current_user.invite_code,
        "invite_url": invite_url,
        "total_invited_count": total_invited,
        "total_earned_points": total_earned,
        "inviter_bonus": int(inviter_bonus.config_value) if inviter_bonus else 100,
        "invitee_bonus": int(invitee_bonus.config_value) if invitee_bonus else 50,
        "rules": [
            "成功邀请好友注册，双方均可获得积分奖励",
            "邀请人获得100积分，被邀请人获得50积分",
            "邀请人数越多，积分奖励越多"
        ]
    }
    
    return success(data=info)


@router.get("/invite/list")
async def get_invite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取邀请记录列表
    """
    # 统计总数
    count_result = await db.execute(
        select(func.count(Invite.id)).where(Invite.inviter_id == current_user.id)
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Invite, User)
        .join(User, Invite.invitee_id == User.id)
        .where(Invite.inviter_id == current_user.id)
        .order_by(Invite.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = result.all()
    
    invite_list = []
    for invite, user in rows:
        invite_list.append({
            "id": invite.id,
            "invitee_id": invite.invitee_id,
            "invitee_nickname": user.nickname,
            "invitee_phone": user.phone[:3] + "****" + user.phone[-4:] if user.phone else "",
            "inviter_points_earned": invite.inviter_points_earned,
            "invitee_points_earned": invite.invitee_points_earned,
            "status": invite.status,
            "create_time": invite.create_time.isoformat() if invite.create_time else None
        })
    
    return success_page(
        items=invite_list,
        total=total,
        page=page,
        page_size=page_size
    )


# ==================== 商品相关 ====================

@router.get("/categories")
async def get_product_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品分类列表
    """
    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.status == 1
        ).order_by(ProductCategory.sort_order)
    )
    categories = result.scalars().all()
    
    # 添加全部分类
    category_list = [{
        "id": 0,
        "name": "全部",
        "code": "all",
        "icon": None
    }]
    category_list.extend([c.to_dict() for c in categories])
    
    return success(data=category_list)


@router.get("/products")
async def get_products(
    category_id: Optional[int] = Query(None, description="分类ID，0或不传表示全部"),
    exchange_type: Optional[str] = Query(None, description="兑换类型: points, points_cash, clothing"),
    is_hot: Optional[bool] = Query(None, description="是否热门"),
    is_new: Optional[bool] = Query(None, description="是否新品"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品列表
    """
    # 构建查询条件
    conditions = [Product.status == 1]
    
    if category_id and category_id > 0:
        conditions.append(Product.category_id == category_id)
    
    if exchange_type:
        conditions.append(Product.exchange_type == exchange_type)
    
    if is_hot is not None:
        conditions.append(Product.is_hot == 1 if is_hot else 0)
    
    if is_new is not None:
        conditions.append(Product.is_new == 1 if is_new else 0)
    
    if keyword:
        conditions.append(Product.name.contains(keyword))
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(Product.id)).where(*conditions)
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Product)
        .where(*conditions)
        .order_by(Product.sort_order, Product.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    products = result.scalars().all()
    
    return success_page(
        items=[p.to_dict() for p in products],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/products/{product_id}")
async def get_product_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品详情
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.status == 1
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        return error(code=404, message="商品不存在")
    
    return success(data=product.to_dict())


# ==================== 兑换订单相关 ====================

@router.post("/exchange/create")
async def create_exchange_order(
    request: CreateExchangeOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建兑换订单
    """
    # 1. 验证商品
    result = await db.execute(
        select(Product).where(
            Product.id == request.product_id,
            Product.status == 1
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        return error(code=404, message="商品不存在")
    
    # 2. 验证库存
    if product.stock < request.quantity:
        return error(code=3002, message=ERROR_CODES[3002])
    
    # 3. 计算需要的积分和其他资源
    total_points = product.points_price * request.quantity
    total_cash = product.price * request.quantity
    total_clothing = product.required_clothing_quantity * request.quantity
    
    # 4. 验证积分是否足够（如果需要积分）
    if product.exchange_type in ["points", "points_cash"] and current_user.points < total_points:
        return error(code=3001, message=ERROR_CODES[3001])
    
    # 5. 处理地址
    address_data = {}
    if request.address_id:
        # 使用已有地址
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.id == request.address_id,
                UserAddress.user_id == current_user.id,
                UserAddress.status == 1
            )
        )
        address = result.scalar_one_or_none()
        if address:
            address_data = {
                "receiver_name": address.name,
                "receiver_phone": address.phone,
                "receiver_province": address.province,
                "receiver_city": address.city,
                "receiver_district": address.district,
                "receiver_address": address.address
            }
    else:
        # 使用请求中的地址
        address_data = {
            "receiver_name": request.receiver_name,
            "receiver_phone": request.receiver_phone,
            "receiver_province": request.receiver_province,
            "receiver_city": request.receiver_city,
            "receiver_district": request.receiver_district,
            "receiver_address": request.receiver_address
        }
    
    # 验证地址完整性
    if not address_data.get("receiver_name") or not address_data.get("receiver_phone"):
        return error(code=400, message="请填写完整的收货信息")
    
    # 6. 生成订单号
    order_no = generate_order_no("EX")
    
    # 7. 创建订单
    order = ExchangeOrder(
        order_no=order_no,
        user_id=current_user.id,
        product_id=product.id,
        product_name=product.name,
        product_image=product.image,
        quantity=request.quantity,
        exchange_type=product.exchange_type,
        points_spent=total_points,
        cash_spent=total_cash,
        clothing_spent=total_clothing,
        **address_data,
        status=1,
        status_text=EXCHANGE_ORDER_STATUS[1]["text"],
        remark=request.remark
    )
    
    db.add(order)
    
    # 8. 扣减积分（如果需要）
    if product.exchange_type in ["points", "points_cash"] and total_points > 0:
        current_user.points -= total_points
        
        # 记录积分交易
        transaction = PointsTransaction(
            user_id=current_user.id,
            transaction_type="exchange",
            transaction_type_text="积分兑换",
            points=-total_points,
            balance_after=current_user.points,
            reference_type="exchange_order",
            reference_id=order.id,
            description=f"兑换商品: {product.name}"
        )
        db.add(transaction)
    
    # 9. 扣减库存
    product.stock -= request.quantity
    product.sales += request.quantity
    
    await db.commit()
    await db.refresh(order)
    
    return success(
        data={
            "order_id": order.id,
            "order_no": order.order_no,
            "status": order.status,
            "status_text": order.status_text,
            "points_spent": order.points_spent,
            "cash_spent": order.cash_spent
        },
        message="兑换成功"
    )


@router.get("/exchange/orders")
async def get_exchange_orders(
    status: Optional[int] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取兑换订单列表
    """
    # 构建查询条件
    conditions = [ExchangeOrder.user_id == current_user.id]
    
    if status is not None:
        conditions.append(ExchangeOrder.status == status)
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(ExchangeOrder.id)).where(*conditions)
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(ExchangeOrder)
        .where(*conditions)
        .order_by(ExchangeOrder.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = result.scalars().all()
    
    # 转换为字典
    order_list = []
    for order in orders:
        order_dict = order.to_dict()
        # 添加状态颜色信息
        if order.status in EXCHANGE_ORDER_STATUS:
            order_dict["status_color"] = EXCHANGE_ORDER_STATUS[order.status]["color"]
        order_list.append(order_dict)
    
    return success_page(
        items=order_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/exchange/orders/{order_id}")
async def get_exchange_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取兑换订单详情
    """
    result = await db.execute(
        select(ExchangeOrder).where(
            ExchangeOrder.id == order_id,
            ExchangeOrder.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=3003, message=ERROR_CODES[3003])
    
    order_dict = order.to_dict()
    if order.status in EXCHANGE_ORDER_STATUS:
        order_dict["status_color"] = EXCHANGE_ORDER_STATUS[order.status]["color"]
    
    return success(data=order_dict)


@router.post("/exchange/orders/{order_id}/cancel")
async def cancel_exchange_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消兑换订单
    只有待发货状态的订单可以取消
    """
    result = await db.execute(
        select(ExchangeOrder).where(
            ExchangeOrder.id == order_id,
            ExchangeOrder.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=3003, message=ERROR_CODES[3003])
    
    # 检查订单状态
    if order.status != 1:  # 只有待发货可以取消
        return error(code=2002, message="当前订单状态不支持取消")
    
    # 更新订单状态
    order.status = 4
    order.status_text = EXCHANGE_ORDER_STATUS[4]["text"]
    
    # 退还积分
    if order.points_spent > 0:
        current_user.points += order.points_spent
        
        # 记录积分交易
        transaction = PointsTransaction(
            user_id=current_user.id,
            transaction_type="refund",
            transaction_type_text="积分退还",
            points=order.points_spent,
            balance_after=current_user.points,
            reference_type="exchange_order",
            reference_id=order.id,
            description=f"取消兑换订单退还积分: {order.product_name}"
        )
        db.add(transaction)
    
    # 恢复库存
    result = await db.execute(
        select(Product).where(Product.id == order.product_id)
    )
    product = result.scalar_one_or_none()
    if product:
        product.stock += order.quantity
        product.sales -= order.quantity
    
    await db.commit()
    
    return success(message="订单已取消，积分已退还")


@router.post("/exchange/orders/{order_id}/confirm")
async def confirm_exchange_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    确认收货
    """
    result = await db.execute(
        select(ExchangeOrder).where(
            ExchangeOrder.id == order_id,
            ExchangeOrder.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=3003, message=ERROR_CODES[3003])
    
    # 检查订单状态
    if order.status != 2:  # 只有已发货可以确认收货
        return error(code=2002, message="当前订单状态不支持确认收货")
    
    # 更新订单状态
    order.status = 3
    order.status_text = EXCHANGE_ORDER_STATUS[3]["text"]
    
    await db.commit()
    
    return success(message="确认收货成功")

"""
测试功能路由模块
用于测试API功能和生成测试数据
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from datetime import datetime, timedelta
from typing import Optional, List
import random
import logging

from app.database import get_db
from app.models import (
    User, UserAddress, RecycleOrder, OrderStatusHistory,
    Collector, ClothingType, Product, PointsTransaction,
    EcoArticle, ChatSession, ChatMessage
)
from app.schemas.common import success, error
from app.utils.security import get_password_hash, generate_invite_code, generate_order_no
from app.config import ORDER_STATUS, EXCHANGE_ORDER_STATUS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/test", tags=["测试功能"])


@router.post("/generate-users")
async def generate_test_users(
    count: int = Query(10, ge=1, le=100, description="生成用户数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    生成测试用户数据
    """
    created_users = []
    
    for i in range(count):
        phone = f"138{random.randint(10000000, 99999999)}"
        
        # 检查手机号是否已存在
        result = await db.execute(select(User).where(User.phone == phone))
        if result.scalar_one_or_none():
            continue
        
        # 生成唯一邀请码
        invite_code = generate_invite_code()
        while True:
            result = await db.execute(select(User).where(User.invite_code == invite_code))
            if not result.scalar_one_or_none():
                break
            invite_code = generate_invite_code()
        
        user = User(
            phone=phone,
            password=get_password_hash("123456"),
            nickname=f"测试用户{i+1}",
            avatar=f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=头像%20卡通%20用户{i+1}&image_size=square",
            gender=random.choice([0, 1, 2]),
            points=random.randint(0, 5000),
            total_points=random.randint(100, 10000),
            recycle_count=random.randint(0, 20),
            carbon_reduction=round(random.uniform(0, 50), 2),
            invite_code=invite_code,
            register_time=datetime.now() - timedelta(days=random.randint(0, 180))
        )
        
        db.add(user)
        await db.flush()
        
        # 添加收货地址
        provinces = ["北京市", "上海市", "广东省", "江苏省", "浙江省"]
        cities = ["东城区", "浦东新区", "广州市", "南京市", "杭州市"]
        districts = ["某某区", "某某街道"]
        
        for j in range(random.randint(1, 3)):
            address = UserAddress(
                user_id=user.id,
                name=f"收货人{j+1}",
                phone=phone,
                province=random.choice(provinces),
                city=random.choice(cities),
                district=random.choice(districts),
                address=f"某某路{random.randint(1, 1000)}号某某小区{random.randint(1, 20)}号楼{random.randint(101, 999)}室",
                is_default=1 if j == 0 else 0
            )
            db.add(address)
        
        created_users.append({
            "id": user.id,
            "phone": phone,
            "nickname": user.nickname,
            "password": "123456",
            "invite_code": invite_code
        })
    
    await db.commit()
    
    return success(
        data={
            "created_count": len(created_users),
            "users": created_users
        },
        message=f"成功生成 {len(created_users)} 个测试用户"
    )


@router.post("/generate-orders")
async def generate_test_orders(
    user_id: Optional[int] = Query(None, description="指定用户ID，不指定则随机选择用户"),
    count: int = Query(5, ge=1, le=50, description="生成订单数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    生成测试订单数据
    """
    # 获取所有衣物类型
    result = await db.execute(select(ClothingType).where(ClothingType.status == 1))
    clothing_types = result.scalars().all()
    
    if not clothing_types:
        return error(code=404, message="没有衣物类型数据")
    
    # 获取用户
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        users = [result.scalar_one_or_none()]
    else:
        result = await db.execute(select(User).order_by(func.random()).limit(10))
        users = result.scalars().all()
    
    if not users or not users[0]:
        return error(code=404, message="没有用户数据，请先生成用户")
    
    # 获取回收人员
    result = await db.execute(select(Collector).where(Collector.status == 1))
    collectors = result.scalars().all()
    
    created_orders = []
    
    for i in range(count):
        user = random.choice(users)
        clothing_type = random.choice(clothing_types)
        collector = random.choice(collectors) if collectors else None
        
        # 随机生成订单状态
        status = random.choice([1, 2, 3, 4, 5])
        status_info = ORDER_STATUS.get(status, ORDER_STATUS[1])
        
        # 随机生成日期
        days_ago = random.randint(0, 30)
        scheduled_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # 计算积分和减碳量
        quantity = random.randint(1, 10)
        quality = random.choice(["优质", "普通", "较差"])
        quality_multiplier = {"优质": 1.5, "普通": 1.0, "较差": 0.8}.get(quality, 1.0)
        points_earned = int(clothing_type.points_per_unit * quantity * quality_multiplier)
        carbon_earned = round(clothing_type.carbon_per_unit * quantity, 2)
        
        # 获取用户地址
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.user_id == user.id,
                UserAddress.status == 1
            ).limit(1)
        )
        address = result.scalar_one_or_none()
        
        if not address:
            continue
        
        time_slots = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00", "19:00-21:00"]
        
        order = RecycleOrder(
            order_no=generate_order_no("RC"),
            user_id=user.id,
            collector_id=collector.id if collector else None,
            clothing_type_id=clothing_type.id,
            clothing_name=clothing_type.name,
            quantity=quantity,
            quality=quality,
            province=address.province,
            city=address.city,
            district=address.district,
            address=address.address,
            contact_name=address.name,
            contact_phone=address.phone,
            scheduled_date=scheduled_date,
            scheduled_time_slot=random.choice(time_slots),
            estimated_arrival=random.choice(time_slots) if collector else None,
            status=status,
            status_text=status_info["text"],
            points_earned=points_earned if status == 4 else 0,
            carbon_earned=carbon_earned if status == 4 else 0,
            create_time=datetime.now() - timedelta(days=days_ago, hours=random.randint(1, 23))
        )
        
        db.add(order)
        await db.flush()
        
        # 添加订单状态历史
        status_history = OrderStatusHistory(
            order_id=order.id,
            order_no=order.order_no,
            status=status,
            status_text=status_info["text"],
            operator_type="system",
            remark="测试数据"
        )
        db.add(status_history)
        
        # 如果订单已完成，更新用户积分和回收次数
        if status == 4:
            user.points += points_earned
            user.total_points += points_earned
            user.recycle_count += 1
            user.carbon_reduction += carbon_earned
            
            # 添加积分交易记录
            transaction = PointsTransaction(
                user_id=user.id,
                transaction_type="recycle",
                transaction_type_text="回收奖励",
                points=points_earned,
                balance_after=user.points,
                reference_type="order",
                reference_id=order.id,
                description=f"回收{clothing_type.name} {quantity}件"
            )
            db.add(transaction)
        
        created_orders.append({
            "id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "clothing_name": order.clothing_name,
            "quantity": order.quantity,
            "status": order.status,
            "status_text": order.status_text
        })
    
    await db.commit()
    
    return success(
        data={
            "created_count": len(created_orders),
            "orders": created_orders
        },
        message=f"成功生成 {len(created_orders)} 个测试订单"
    )


@router.get("/statistics")
async def get_test_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取测试数据统计
    """
    # 用户统计
    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar() or 0
    
    # 订单统计
    result = await db.execute(select(func.count(RecycleOrder.id)))
    order_count = result.scalar() or 0
    
    # 各状态订单数
    result = await db.execute(
        select(RecycleOrder.status, func.count(RecycleOrder.id))
        .group_by(RecycleOrder.status)
    )
    status_counts = dict(result.all())
    
    # 商品统计
    result = await db.execute(select(func.count(Product.id)))
    product_count = result.scalar() or 0
    
    # 资讯统计
    result = await db.execute(select(func.count(EcoArticle.id)))
    article_count = result.scalar() or 0
    
    return success(data={
        "user_count": user_count,
        "order_count": order_count,
        "order_status_counts": {
            str(k): v for k, v in status_counts.items()
        },
        "product_count": product_count,
        "article_count": article_count
    })


@router.get("/quick-test")
async def quick_test(
    db: AsyncSession = Depends(get_db)
):
    """
    快速测试数据
    返回一些测试用的用户和数据信息
    """
    # 获取一些用户
    result = await db.execute(
        select(User).order_by(User.id.desc()).limit(5)
    )
    users = result.scalars().all()
    
    # 获取一些订单
    result = await db.execute(
        select(RecycleOrder).order_by(RecycleOrder.id.desc()).limit(5)
    )
    orders = result.scalars().all()
    
    # 获取衣物类型
    result = await db.execute(select(ClothingType).where(ClothingType.status == 1))
    clothing_types = result.scalars().all()
    
    return success(data={
        "test_users": [
            {
                "id": u.id,
                "phone": u.phone,
                "nickname": u.nickname,
                "password": "123456",
                "points": u.points,
                "invite_code": u.invite_code
            }
            for u in users
        ],
        "test_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "status": o.status,
                "status_text": o.status_text
            }
            for o in orders
        ],
        "clothing_types": [
            {
                "id": ct.id,
                "name": ct.name,
                "points_per_unit": ct.points_per_unit
            }
            for ct in clothing_types
        ],
        "test_info": {
            "默认密码": "123456",
            "万能验证码": "123456",
            "测试说明": "用于开发和测试环境，生产环境请禁用此接口"
        }
    })


@router.post("/clear-test-data")
async def clear_test_data(
    confirm: bool = Query(False, description="确认删除"),
    db: AsyncSession = Depends(get_db)
):
    """
    清除测试数据
    警告：这将删除所有用户、订单等数据，仅用于测试环境
    """
    if not confirm:
        return error(code=400, message="请确认删除操作，设置 confirm=true")
    
    try:
        # 注意：这里只是示例，实际需要根据外键关系顺序删除
        # 这里使用简单的方式，实际项目应该更谨慎
        
        await db.execute(delete(ChatMessage))
        await db.execute(delete(ChatSession))
        await db.execute(delete(OrderStatusHistory))
        await db.execute(delete(RecycleOrder))
        await db.execute(delete(PointsTransaction))
        await db.execute(delete(UserAddress))
        await db.execute(delete(User))
        
        await db.commit()
        
        return success(message="测试数据已清除")
    except Exception as e:
        await db.rollback()
        return error(code=500, message=f"清除失败: {str(e)}")


@router.post("/simulate-order-complete")
async def simulate_order_complete(
    order_id: int = Query(..., description="订单ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    模拟订单完成
    用于测试订单完成后的积分发放等功能
    """
    # 获取订单
    result = await db.execute(
        select(RecycleOrder).where(RecycleOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=2001, message=ERROR_CODES[2001])
    
    # 检查订单状态
    if order.status == 4:
        return error(code=2002, message="订单已完成")
    
    # 获取用户
    result = await db.execute(select(User).where(User.id == order.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return error(code=1001, message=ERROR_CODES[1001])
    
    # 更新订单状态
    order.status = 4
    order.status_text = ORDER_STATUS[4]["text"]
    order.complete_time = datetime.now()
    
    # 发放积分
    user.points += order.points_earned
    user.total_points += order.points_earned
    user.recycle_count += 1
    user.carbon_reduction += order.carbon_earned
    
    # 记录积分交易
    transaction = PointsTransaction(
        user_id=user.id,
        transaction_type="recycle",
        transaction_type_text="回收奖励",
        points=order.points_earned,
        balance_after=user.points,
        reference_type="order",
        reference_id=order.id,
        description=f"回收{order.clothing_name} {order.quantity}件，订单完成"
    )
    db.add(transaction)
    
    # 记录订单状态历史
    status_history = OrderStatusHistory(
        order_id=order.id,
        order_no=order.order_no,
        status=4,
        status_text=ORDER_STATUS[4]["text"],
        operator_type="system",
        remark="模拟订单完成"
    )
    db.add(status_history)
    
    await db.commit()
    
    return success(data={
        "order_id": order.id,
        "order_no": order.order_no,
        "points_earned": order.points_earned,
        "carbon_earned": order.carbon_earned,
        "user_points_after": user.points
    }, message="订单已完成，积分已发放")

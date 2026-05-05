"""
订单路由模块
包含衣物类型查询、预约订单创建、订单跟踪等功能
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from datetime import datetime, date, timedelta
from typing import Optional, List
import logging

from app.database import get_db
from app.models import (
    User, ClothingType, RecycleOrder, OrderStatusHistory,
    Collector, RecycleProcess, PointsTransaction, Invite, PointsConfig
)
from app.schemas.order import (
    ClothingTypeResponse, CreateOrderRequest, OrderResponse,
    OrderDetailResponse, CancelOrderRequest, UpdateTimeSlotRequest,
    RecycleProcessResponse, CollectorResponse
)
from app.schemas.common import success, success_page, error, ERROR_CODES
from app.config import get_settings, ORDER_STATUS, DEFAULT_TIME_SLOTS
from app.utils.security import generate_order_no
from app.utils.dependencies import get_current_user, get_pagination_params

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/order", tags=["订单管理"])


# ==================== 衣物类型相关 ====================

@router.get("/clothing-types")
async def get_clothing_types(
    db: AsyncSession = Depends(get_db)
):
    """
    获取衣物类型列表
    """
    result = await db.execute(
        select(ClothingType).where(
            ClothingType.status == 1
        ).order_by(ClothingType.sort_order)
    )
    types = result.scalars().all()
    
    return success(data=[t.to_dict() for t in types])


@router.get("/clothing-types/{type_id}")
async def get_clothing_type(
    type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个衣物类型详情
    """
    result = await db.execute(
        select(ClothingType).where(
            ClothingType.id == type_id,
            ClothingType.status == 1
        )
    )
    clothing_type = result.scalar_one_or_none()
    
    if not clothing_type:
        return error(code=404, message="衣物类型不存在")
    
    return success(data=clothing_type.to_dict())


# ==================== 可预约时间相关 ====================

@router.get("/available-dates")
async def get_available_dates():
    """
    获取可预约日期列表
    16:00前可预约当天
    """
    now = datetime.now()
    current_hour = now.hour
    
    dates = []
    today = date.today()
    
    # 今天是否可预约
    if current_hour < 16:
        dates.append({
            "date": today.isoformat(),
            "label": "今天",
            "available": True
        })
    else:
        dates.append({
            "date": today.isoformat(),
            "label": "今天",
            "available": False,
            "reason": "已过当天预约截止时间"
        })
    
    # 未来6天
    for i in range(1, 7):
        d = today + timedelta(days=i)
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]
        dates.append({
            "date": d.isoformat(),
            "label": f"{'明天' if i == 1 else weekday}",
            "available": True
        })
    
    return success(data=dates)


@router.get("/time-slots")
async def get_time_slots():
    """
    获取可预约时间段
    """
    return success(data=DEFAULT_TIME_SLOTS)


# ==================== 回收流程 ====================

@router.get("/recycle-process")
async def get_recycle_process(
    db: AsyncSession = Depends(get_db)
):
    """
    获取回收流程说明
    """
    result = await db.execute(
        select(RecycleProcess).where(
            RecycleProcess.status == 1
        ).order_by(RecycleProcess.step, RecycleProcess.sort_order)
    )
    processes = result.scalars().all()
    
    return success(data=[p.to_dict() for p in processes])


# ==================== 回收人员相关 ====================

@router.get("/collectors")
async def get_available_collectors(
    db: AsyncSession = Depends(get_db)
):
    """
    获取可用的回收人员列表
    """
    result = await db.execute(
        select(Collector).where(
            Collector.status == 1,
            Collector.work_status == 1  # 工作中
        ).order_by(Collector.rating.desc())
    )
    collectors = result.scalars().all()
    
    return success(data=[c.to_dict() for c in collectors])


# ==================== 订单相关 ====================

@router.post("/create")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建旧衣回收预约订单
    """
    # 1. 验证衣物类型
    result = await db.execute(
        select(ClothingType).where(ClothingType.id == request.clothing_type_id)
    )
    clothing_type = result.scalar_one_or_none()
    
    if not clothing_type:
        return error(code=404, message="衣物类型不存在")
    
    # 2. 验证预约时间
    now = datetime.now()
    scheduled_date = datetime.strptime(request.scheduled_date, "%Y-%m-%d").date()
    today = now.date()
    
    if scheduled_date == today and now.hour >= 16:
        return error(code=2003, message=ERROR_CODES[2003])
    
    # 3. 生成订单号
    order_no = generate_order_no("RC")
    
    # 4. 计算积分和减碳量
    quality_multiplier = {
        "优质": 1.5,
        "普通": 1.0,
        "较差": 0.8
    }.get(request.quality, 1.0)
    
    base_points = clothing_type.points_per_unit * request.quantity
    points_earned = int(base_points * quality_multiplier)
    carbon_earned = clothing_type.carbon_per_unit * request.quantity
    
    # 5. 自动分配回收人员（简单策略：找评分最高的空闲回收员）
    collector_id = None
    result = await db.execute(
        select(Collector).where(
            Collector.status == 1,
            Collector.work_status == 1
        ).order_by(Collector.rating.desc())
    )
    collectors = result.scalars().all()
    if collectors:
        collector_id = collectors[0].id
    
    # 6. 创建订单
    order = RecycleOrder(
        order_no=order_no,
        user_id=current_user.id,
        collector_id=collector_id,
        clothing_type_id=clothing_type.id,
        clothing_name=clothing_type.name,
        quantity=request.quantity,
        quality=request.quality,
        province=request.province,
        city=request.city,
        district=request.district,
        address=request.address,
        contact_name=request.contact_name,
        contact_phone=request.contact_phone,
        scheduled_date=request.scheduled_date,
        scheduled_time_slot=request.scheduled_time_slot,
        estimated_arrival=request.scheduled_time_slot if collector_id else None,
        status=1,
        status_text=ORDER_STATUS[1]["text"],
        points_earned=points_earned,
        carbon_earned=carbon_earned,
        remark=request.remark
    )
    
    db.add(order)
    await db.flush()
    
    # 7. 记录订单状态历史
    status_history = OrderStatusHistory(
        order_id=order.id,
        order_no=order_no,
        status=1,
        status_text=ORDER_STATUS[1]["text"],
        operator_type="user",
        operator_id=current_user.id,
        remark="用户创建订单"
    )
    db.add(status_history)
    
    await db.commit()
    await db.refresh(order)
    
    return success(
        data={
            "order_id": order.id,
            "order_no": order.order_no,
            "status": order.status,
            "status_text": order.status_text,
            "estimated_arrival": order.estimated_arrival,
            "collector_id": order.collector_id
        },
        message="预约成功"
    )


@router.get("/list")
async def get_order_list(
    status: Optional[int] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单列表
    支持按状态筛选
    """
    # 构建查询条件
    conditions = [RecycleOrder.user_id == current_user.id]
    
    if status is not None:
        conditions.append(RecycleOrder.status == status)
    
    # 统计总数
    count_result = await db.execute(
        select(func.count(RecycleOrder.id)).where(*conditions)
    )
    total = count_result.scalar() or 0
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(RecycleOrder)
        .where(*conditions)
        .order_by(RecycleOrder.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = result.scalars().all()
    
    # 转换为字典
    order_list = []
    for order in orders:
        order_dict = order.to_dict()
        # 添加状态颜色信息
        if order.status in ORDER_STATUS:
            order_dict["status_color"] = ORDER_STATUS[order.status]["color"]
        order_list.append(order_dict)
    
    return success_page(
        items=order_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{order_id}")
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单详情
    """
    # 查询订单
    result = await db.execute(
        select(RecycleOrder).where(
            RecycleOrder.id == order_id,
            RecycleOrder.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=2001, message=ERROR_CODES[2001])
    
    # 查询订单状态历史
    history_result = await db.execute(
        select(OrderStatusHistory).where(
            OrderStatusHistory.order_id == order_id
        ).order_by(OrderStatusHistory.create_time)
    )
    histories = history_result.scalars().all()
    
    # 查询回收人员信息
    collector = None
    if order.collector_id:
        collector_result = await db.execute(
            select(Collector).where(Collector.id == order.collector_id)
        )
        collector = collector_result.scalar_one_or_none()
    
    # 构建响应
    order_dict = order.to_dict()
    if order.status in ORDER_STATUS:
        order_dict["status_color"] = ORDER_STATUS[order.status]["color"]
    
    if collector:
        order_dict["collector"] = collector.to_dict()
    
    order_dict["status_histories"] = [h.to_dict() for h in histories]
    
    return success(data=order_dict)


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    request: CancelOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消订单
    只有待接单、待上门状态的订单可以取消
    """
    result = await db.execute(
        select(RecycleOrder).where(
            RecycleOrder.id == order_id,
            RecycleOrder.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=2001, message=ERROR_CODES[2001])
    
    # 检查订单状态
    if order.status not in [1, 2]:  # 待接单、待上门
        return error(code=2002, message="当前订单状态不支持取消")
    
    # 更新订单状态
    order.status = 5
    order.status_text = ORDER_STATUS[5]["text"]
    order.cancel_time = datetime.now()
    order.cancel_reason = request.cancel_reason
    
    # 记录状态历史
    status_history = OrderStatusHistory(
        order_id=order.id,
        order_no=order.order_no,
        status=5,
        status_text=ORDER_STATUS[5]["text"],
        operator_type="user",
        operator_id=current_user.id,
        remark=f"用户取消订单: {request.cancel_reason}"
    )
    db.add(status_history)
    
    await db.commit()
    
    return success(message="订单已取消")


@router.put("/{order_id}/time-slot")
async def update_time_slot(
    order_id: int,
    request: UpdateTimeSlotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    调整预约时间
    只有待接单、待上门状态的订单可以调整时间
    """
    result = await db.execute(
        select(RecycleOrder).where(
            RecycleOrder.id == order_id,
            RecycleOrder.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error(code=2001, message=ERROR_CODES[2001])
    
    # 检查订单状态
    if order.status not in [1, 2]:
        return error(code=2002, message="当前订单状态不支持调整时间")
    
    # 验证新的预约时间
    now = datetime.now()
    scheduled_date = datetime.strptime(request.scheduled_date, "%Y-%m-%d").date()
    today = now.date()
    
    if scheduled_date == today and now.hour >= 16:
        return error(code=2003, message=ERROR_CODES[2003])
    
    # 更新订单时间
    old_date = order.scheduled_date
    old_slot = order.scheduled_time_slot
    
    order.scheduled_date = request.scheduled_date
    order.scheduled_time_slot = request.scheduled_time_slot
    
    # 记录状态历史
    status_history = OrderStatusHistory(
        order_id=order.id,
        order_no=order.order_no,
        status=order.status,
        status_text=order.status_text,
        operator_type="user",
        operator_id=current_user.id,
        remark=f"用户调整预约时间: 从 {old_date} {old_slot} 改为 {request.scheduled_date} {request.scheduled_time_slot}"
    )
    db.add(status_history)
    
    await db.commit()
    
    return success(message="预约时间已调整")


@router.get("/statistics/summary")
async def get_order_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单统计信息
    """
    # 各状态订单数
    result = await db.execute(
        select(RecycleOrder.status, func.count(RecycleOrder.id))
        .where(RecycleOrder.user_id == current_user.id)
        .group_by(RecycleOrder.status)
    )
    status_counts = dict(result.all())
    
    # 统计信息
    statistics = {
        "total_orders": 0,
        "pending_orders": status_counts.get(1, 0) + status_counts.get(2, 0) + status_counts.get(3, 0),
        "completed_orders": status_counts.get(4, 0),
        "cancelled_orders": status_counts.get(5, 0),
        "total_points": current_user.total_points,
        "current_points": current_user.points,
        "total_carbon": current_user.carbon_reduction,
        "total_recycles": current_user.recycle_count
    }
    
    return success(data=statistics)

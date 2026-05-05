from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Order
from schemas import RoutePlanResponse, RoutePoint, OrderStatus
from utils import get_current_user, optimize_route

router = APIRouter(prefix="/api/route", tags=["路线规划"])


@router.get("/plan", response_model=RoutePlanResponse, summary="规划上门路线")
async def plan_route(
    start_lat: Optional[float] = Query(None, description="起点纬度"),
    start_lon: Optional[float] = Query(None, description="起点经度"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据已接订单规划最优上门路线
    - 使用最近邻算法优化路线
    - 计算总距离和预计时间
    """
    orders = db.query(Order).filter(
        Order.collector_id == current_user.id,
        Order.status.in_([OrderStatus.ACCEPTED.value, OrderStatus.PROCESSING.value])
    ).all()
    
    if not orders:
        return RoutePlanResponse(
            total_distance=0.0,
            total_duration=0.0,
            points=[],
            optimized_order=[]
        )
    
    points = []
    for order in orders:
        if order.latitude and order.longitude:
            points.append({
                "order_id": order.id,
                "latitude": order.latitude,
                "longitude": order.longitude
            })
    
    optimized_order, total_distance, total_duration = optimize_route(
        points, start_lat, start_lon
    )
    
    order_map = {order.id: order for order in orders}
    
    route_points = []
    for order_id in optimized_order:
        order = order_map.get(order_id)
        if order:
            route_points.append(RoutePoint(
                order_id=order.id,
                order_no=order.order_no,
                user_name=order.user_name,
                address=order.address,
                latitude=order.latitude,
                longitude=order.longitude,
                estimated_weight=order.estimated_weight
            ))
    
    return RoutePlanResponse(
        total_distance=round(total_distance, 2),
        total_duration=round(total_duration, 1),
        points=route_points,
        optimized_order=optimized_order
    )


@router.get("/orders", response_model=List[RoutePoint], summary="获取待上门订单列表")
async def get_pending_route_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前回收人员已接单但未完成的订单列表
    用于路线规划展示
    """
    orders = db.query(Order).filter(
        Order.collector_id == current_user.id,
        Order.status.in_([OrderStatus.ACCEPTED.value, OrderStatus.PROCESSING.value])
    ).order_by(Order.created_at.asc()).all()
    
    route_points = []
    for order in orders:
        route_points.append(RoutePoint(
            order_id=order.id,
            order_no=order.order_no,
            user_name=order.user_name,
            address=order.address,
            latitude=order.latitude,
            longitude=order.longitude,
            estimated_weight=order.estimated_weight
        ))
    
    return route_points

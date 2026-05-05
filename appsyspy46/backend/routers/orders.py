from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Order, OrderLog
from schemas import (
    OrderCreate, OrderAccept, OrderReject, OrderComplete,
    OrderResponse, OrderListResponse, OrderLogResponse, OrderStatus
)
from utils import get_current_user, generate_order_no

router = APIRouter(prefix="/api/orders", tags=["订单管理"])


@router.get("/pending", response_model=OrderListResponse, summary="获取待接单列表")
async def get_pending_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取待接单订单列表
    - 状态为 pending 的订单
    - 支持分页
    """
    query = db.query(Order).filter(Order.status == OrderStatus.PENDING.value)
    
    total = query.count()
    
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return OrderListResponse(total=total, orders=orders)


@router.get("/accepted", response_model=OrderListResponse, summary="获取已接单列表")
async def get_accepted_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取已接单订单列表
    - 状态为 accepted 或 processing 的订单
    - 仅显示当前回收人员的订单
    """
    query = db.query(Order).filter(
        Order.collector_id == current_user.id,
        Order.status.in_([OrderStatus.ACCEPTED.value, OrderStatus.PROCESSING.value])
    )
    
    total = query.count()
    
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return OrderListResponse(total=total, orders=orders)


@router.get("/completed", response_model=OrderListResponse, summary="获取已完成列表")
async def get_completed_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取已完成订单列表
    - 状态为 completed 的订单
    - 仅显示当前回收人员的订单
    """
    query = db.query(Order).filter(
        Order.collector_id == current_user.id,
        Order.status == OrderStatus.COMPLETED.value
    )
    
    total = query.count()
    
    orders = query.order_by(Order.completed_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return OrderListResponse(total=total, orders=orders)


@router.get("/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单详情
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.collector_id and order.collector_id != current_user.id:
        if order.status != OrderStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此订单"
            )
    
    return order


@router.post("/create", response_model=OrderResponse, summary="创建订单")
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    创建回收订单(供用户端或测试使用)
    """
    new_order = Order(
        order_no=generate_order_no(),
        user_name=order_data.user_name,
        user_phone=order_data.user_phone,
        address=order_data.address,
        province=order_data.province,
        city=order_data.city,
        district=order_data.district,
        latitude=order_data.latitude,
        longitude=order_data.longitude,
        clothing_types=order_data.clothing_types,
        estimated_weight=order_data.estimated_weight,
        estimated_quantity=order_data.estimated_quantity,
        description=order_data.description,
        appointment_time=order_data.appointment_time,
        status=OrderStatus.PENDING.value
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    log = OrderLog(
        order_id=new_order.id,
        operator_type="user",
        action="create_order",
        description="用户创建回收订单"
    )
    db.add(log)
    db.commit()
    
    return new_order


@router.post("/accept", response_model=OrderResponse, summary="接单")
async def accept_order(
    accept_data: OrderAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    回收人员接单
    """
    order = db.query(Order).filter(Order.id == accept_data.order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许接单"
        )
    
    order.status = OrderStatus.ACCEPTED.value
    order.collector_id = current_user.id
    order.accepted_at = datetime.now()
    
    log = OrderLog(
        order_id=order.id,
        operator_type="collector",
        operator_id=current_user.id,
        action="accept_order",
        description=f"回收人员 {current_user.real_name or current_user.username} 接单"
    )
    db.add(log)
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/reject", response_model=OrderResponse, summary="拒绝订单")
async def reject_order(
    reject_data: OrderReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    回收人员拒绝订单
    """
    order = db.query(Order).filter(Order.id == reject_data.order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许拒绝"
        )
    
    order.status = OrderStatus.REJECTED.value
    order.collector_id = current_user.id
    order.reject_reason = reject_data.reject_reason
    
    log = OrderLog(
        order_id=order.id,
        operator_type="collector",
        operator_id=current_user.id,
        action="reject_order",
        description=f"回收人员拒绝订单，原因: {reject_data.reject_reason}"
    )
    db.add(log)
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/complete", response_model=OrderResponse, summary="完成订单")
async def complete_order(
    complete_data: OrderComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    回收人员完成订单
    - 上传实际重量、数量、照片
    - 计算总金额
    - 更新用户统计数据
    """
    order = db.query(Order).filter(Order.id == complete_data.order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.collector_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此订单"
        )
    
    if order.status not in [OrderStatus.ACCEPTED.value, OrderStatus.PROCESSING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许完成"
        )
    
    total_amount = complete_data.actual_weight * complete_data.unit_price
    
    order.status = OrderStatus.COMPLETED.value
    order.actual_weight = complete_data.actual_weight
    order.actual_quantity = complete_data.actual_quantity
    order.recycle_photos = complete_data.recycle_photos
    order.unit_price = complete_data.unit_price
    order.total_amount = total_amount
    order.completed_at = datetime.now()
    
    current_user.total_orders += 1
    current_user.total_weight += complete_data.actual_weight
    current_user.total_income += total_amount
    
    log = OrderLog(
        order_id=order.id,
        operator_type="collector",
        operator_id=current_user.id,
        action="complete_order",
        description=f"完成回收，实际重量: {complete_data.actual_weight}kg, 金额: ¥{total_amount}"
    )
    db.add(log)
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/{order_id}/logs", response_model=List[OrderLogResponse], summary="获取订单日志")
async def get_order_logs(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单操作日志
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    logs = db.query(OrderLog).filter(OrderLog.order_id == order_id).order_by(OrderLog.created_at.asc()).all()
    
    return logs

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from app.database import get_db
from app.models.order import Order, OrderItem
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderStatistics, DailyStatistics
)
from app.schemas.common import ApiResponse, PageParams, PageResult

router = APIRouter(prefix="/orders", tags=["订单管理"])

@router.post("/", response_model=ApiResponse[OrderResponse])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    创建订单
    """
    existing_order = db.query(Order).filter(Order.order_no == order.order_no).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="订单编号已存在")
    
    order_data = order.model_dump()
    items = order_data.pop('items', [])
    
    db_order = Order(**order_data)
    db.add(db_order)
    db.flush()
    
    for item in items:
        db_item = OrderItem(order_id=db_order.id, **item)
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    
    db_order.items = db.query(OrderItem).filter(OrderItem.order_id == db_order.id).all()
    return ApiResponse(data=db_order)

@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    获取订单详情
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return ApiResponse(data=order)

@router.get("/", response_model=ApiResponse[PageResult[OrderResponse]])
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    order_no: Optional[str] = None,
    user_id: Optional[int] = None,
    recycler_id: Optional[int] = None,
    status: Optional[int] = None,
    area: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取订单列表（分页）
    """
    query = db.query(Order)
    
    if order_no:
        query = query.filter(Order.order_no.like(f"%{order_no}%"))
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if recycler_id:
        query = query.filter(Order.recycler_id == recycler_id)
    if status is not None:
        query = query.filter(Order.status == status)
    if area:
        query = query.filter(Order.area.like(f"%{area}%"))
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(cast(Order.created_at, Date) >= start_dt.date())
        except:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(cast(Order.created_at, Date) <= end_dt.date())
        except:
            pass
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    orders = query.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    for order in orders:
        order.items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    result = PageResult[OrderResponse](
        list=orders,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return ApiResponse(data=result)

@router.put("/{order_id}", response_model=ApiResponse[OrderResponse])
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """
    更新订单信息
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    update_data = order_update.model_dump(exclude_unset=True)
    
    if 'status' in update_data:
        status = update_data['status']
        if status == 1 and order.status == 0:
            update_data['accept_time'] = datetime.now()
        elif status == 3 and order.status != 3:
            update_data['complete_time'] = datetime.now()
        elif status == 4 and order.status != 4:
            update_data['cancel_time'] = datetime.now()
    
    for key, value in update_data.items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    return ApiResponse(data=order)

@router.post("/{order_id}/assign/{recycler_id}", response_model=ApiResponse[OrderResponse])
def assign_order(order_id: int, recycler_id: int, db: Session = Depends(get_db)):
    """
    分配订单给回收人员
    """
    from app.models.recycler import Recycler
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    recycler = db.query(Recycler).filter(Recycler.id == recycler_id).first()
    if not recycler:
        raise HTTPException(status_code=404, detail="回收人员不存在")
    
    order.recycler_id = recycler_id
    order.recycler_name = recycler.real_name
    order.status = 1
    order.accept_time = datetime.now()
    
    db.commit()
    db.refresh(order)
    return ApiResponse(data=order)

@router.get("/statistics/overview", response_model=ApiResponse[OrderStatistics])
def get_order_statistics(db: Session = Depends(get_db)):
    """
    获取订单统计概览
    """
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    pending_orders = db.query(func.count(Order.id)).filter(Order.status == 0).scalar() or 0
    accepted_orders = db.query(func.count(Order.id)).filter(Order.status == 1).scalar() or 0
    completed_orders = db.query(func.count(Order.id)).filter(Order.status == 3).scalar() or 0
    cancelled_orders = db.query(func.count(Order.id)).filter(Order.status == 4).scalar() or 0
    exception_orders = db.query(func.count(Order.id)).filter(Order.status == 5).scalar() or 0
    
    total_weight = db.query(func.sum(Order.total_weight)).filter(Order.status == 3).scalar() or Decimal('0.00')
    total_amount = db.query(func.sum(Order.total_amount)).filter(Order.status == 3).scalar() or Decimal('0.00')
    
    complete_rate = Decimal('0.00')
    if total_orders > 0:
        complete_rate = round(Decimal(completed_orders * 100) / Decimal(total_orders), 2)
    
    stats = OrderStatistics(
        total_orders=total_orders,
        pending_orders=pending_orders,
        accepted_orders=accepted_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        exception_orders=exception_orders,
        total_weight=total_weight,
        total_amount=total_amount,
        complete_rate=complete_rate
    )
    return ApiResponse(data=stats)

@router.get("/statistics/daily", response_model=ApiResponse[List[DailyStatistics]])
def get_daily_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    获取每日统计数据
    """
    start_date = datetime.now() - timedelta(days=days)
    
    query = db.query(
        cast(Order.created_at, Date).label('date'),
        func.count(Order.id).label('order_count'),
        func.coalesce(func.sum(Order.total_weight), 0).label('total_weight'),
        func.coalesce(func.sum(Order.total_amount), 0).label('total_amount')
    ).filter(
        cast(Order.created_at, Date) >= start_date.date(),
        Order.status == 3
    ).group_by(
        cast(Order.created_at, Date)
    ).order_by(
        'date'
    ).all()
    
    result = []
    for row in query:
        result.append(DailyStatistics(
            date=str(row.date),
            order_count=row.order_count,
            total_weight=row.total_weight or Decimal('0.00'),
            total_amount=row.total_amount or Decimal('0.00')
        ))
    
    return ApiResponse(data=result)

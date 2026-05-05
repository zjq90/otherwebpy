from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.user import User, Feedback
from app.models.product import PointsExchange, Product
from app.models.recycler import Recycler
from app.models.announcement import Announcement
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/statistics", tags=["数据统计与分析"])

@router.get("/dashboard", response_model=ApiResponse[Dict[str, Any]])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    获取仪表盘统计数据
    """
    today = datetime.now().date()
    
    total_users = db.query(func.count(User.id)).scalar() or 0
    today_users = db.query(func.count(User.id)).filter(
        cast(User.created_at, Date) == today
    ).scalar() or 0
    
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    today_orders = db.query(func.count(Order.id)).filter(
        cast(Order.created_at, Date) == today
    ).scalar() or 0
    
    completed_orders = db.query(func.count(Order.id)).filter(
        Order.status == 3
    ).scalar() or 0
    today_completed = db.query(func.count(Order.id)).filter(
        cast(Order.complete_time, Date) == today,
        Order.status == 3
    ).scalar() or 0
    
    total_amount = db.query(func.sum(Order.total_amount)).filter(
        Order.status == 3
    ).scalar() or Decimal('0.00')
    today_amount = db.query(func.sum(Order.total_amount)).filter(
        cast(Order.complete_time, Date) == today,
        Order.status == 3
    ).scalar() or Decimal('0.00')
    
    total_weight = db.query(func.sum(Order.total_weight)).filter(
        Order.status == 3
    ).scalar() or Decimal('0.00')
    today_weight = db.query(func.sum(Order.total_weight)).filter(
        cast(Order.complete_time, Date) == today,
        Order.status == 3
    ).scalar() or Decimal('0.00')
    
    total_points_exchanged = db.query(func.sum(PointsExchange.total_points)).scalar() or 0
    total_products = db.query(func.count(Product.id)).filter(Product.status == 1).scalar() or 0
    
    pending_feedbacks = db.query(func.count(Feedback.id)).filter(
        Feedback.status.in_([0, 1])
    ).scalar() or 0
    
    pending_orders = db.query(func.count(Order.id)).filter(Order.status == 0).scalar() or 0
    exception_orders = db.query(func.count(Order.id)).filter(Order.status == 5).scalar() or 0
    
    result = {
        "total_users": total_users,
        "today_users": today_users,
        "total_orders": total_orders,
        "today_orders": today_orders,
        "completed_orders": completed_orders,
        "today_completed": today_completed,
        "total_amount": float(total_amount),
        "today_amount": float(today_amount),
        "total_weight": float(total_weight),
        "today_weight": float(today_weight),
        "total_points_exchanged": total_points_exchanged,
        "total_products": total_products,
        "pending_feedbacks": pending_feedbacks,
        "pending_orders": pending_orders,
        "exception_orders": exception_orders
    }
    
    return ApiResponse(data=result)

@router.get("/recycling-trend", response_model=ApiResponse[List[Dict[str, Any]]])
def get_recycling_trend(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    获取回收趋势数据
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
        result.append({
            "date": str(row.date),
            "order_count": row.order_count,
            "total_weight": float(row.total_weight) if row.total_weight else 0,
            "total_amount": float(row.total_amount) if row.total_amount else 0
        })
    
    return ApiResponse(data=result)

@router.get("/user-growth", response_model=ApiResponse[List[Dict[str, Any]]])
def get_user_growth(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    获取用户增长趋势
    """
    start_date = datetime.now() - timedelta(days=days)
    
    query = db.query(
        cast(User.created_at, Date).label('date'),
        func.count(User.id).label('new_users')
    ).filter(
        cast(User.created_at, Date) >= start_date.date()
    ).group_by(
        cast(User.created_at, Date)
    ).order_by(
        'date'
    ).all()
    
    result = []
    cumulative = 0
    for row in query:
        cumulative += row.new_users
        result.append({
            "date": str(row.date),
            "new_users": row.new_users,
            "cumulative_users": cumulative
        })
    
    return ApiResponse(data=result)

@router.get("/category-stats", response_model=ApiResponse[List[Dict[str, Any]]])
def get_category_statistics(db: Session = Depends(get_db)):
    """
    获取分类统计数据
    """
    query = db.query(
        OrderItem.category_name,
        func.count(OrderItem.id).label('item_count'),
        func.coalesce(func.sum(OrderItem.weight), 0).label('total_weight'),
        func.coalesce(func.sum(OrderItem.amount), 0).label('total_amount')
    ).filter(
        OrderItem.category_name.isnot(None)
    ).group_by(
        OrderItem.category_name
    ).order_by(
        func.count(OrderItem.id).desc()
    ).all()
    
    result = []
    for row in query:
        result.append({
            "category_name": row.category_name,
            "item_count": row.item_count,
            "total_weight": float(row.total_weight) if row.total_weight else 0,
            "total_amount": float(row.total_amount) if row.total_amount else 0
        })
    
    return ApiResponse(data=result)

@router.get("/points-exchange-stats", response_model=ApiResponse[Dict[str, Any]])
def get_points_exchange_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    获取积分兑换统计
    """
    start_date = datetime.now() - timedelta(days=days)
    
    total_exchanges = db.query(func.count(PointsExchange.id)).scalar() or 0
    
    period_exchanges = db.query(func.count(PointsExchange.id)).filter(
        cast(PointsExchange.created_at, Date) >= start_date.date()
    ).scalar() or 0
    
    total_points = db.query(func.sum(PointsExchange.total_points)).scalar() or 0
    
    period_points = db.query(func.sum(PointsExchange.total_points)).filter(
        cast(PointsExchange.created_at, Date) >= start_date.date()
    ).scalar() or 0
    
    status_stats = db.query(
        PointsExchange.status,
        func.count(PointsExchange.id).label('count')
    ).group_by(
        PointsExchange.status
    ).all()
    
    status_distribution = {}
    for row in status_stats:
        status_name = {0: "待发货", 1: "已发货", 2: "已收货", 3: "已取消"}.get(row.status, str(row.status))
        status_distribution[status_name] = row.count
    
    result = {
        "total_exchanges": total_exchanges,
        "period_exchanges": period_exchanges,
        "total_points_exchanged": total_points,
        "period_points_exchanged": period_points,
        "status_distribution": status_distribution
    }
    
    return ApiResponse(data=result)

@router.get("/recycler-performance", response_model=ApiResponse[List[Dict[str, Any]]])
def get_recycler_performance(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取回收人员业绩排行
    """
    query = db.query(
        Recycler.id,
        Recycler.real_name,
        Recycler.phone,
        Recycler.area,
        Recycler.total_orders,
        Recycler.completed_orders,
        Recycler.total_weight,
        Recycler.total_amount,
        Recycler.performance_score
    ).filter(
        Recycler.status == 1
    ).order_by(
        Recycler.completed_orders.desc()
    ).limit(limit).all()
    
    result = []
    for row in query:
        complete_rate = 0
        if row.total_orders > 0:
            complete_rate = round(row.completed_orders * 100 / row.total_orders, 2)
        
        result.append({
            "id": row.id,
            "real_name": row.real_name,
            "phone": row.phone,
            "area": row.area,
            "total_orders": row.total_orders,
            "completed_orders": row.completed_orders,
            "total_weight": float(row.total_weight) if row.total_weight else 0,
            "total_amount": float(row.total_amount) if row.total_amount else 0,
            "performance_score": float(row.performance_score),
            "complete_rate": complete_rate
        })
    
    return ApiResponse(data=result)

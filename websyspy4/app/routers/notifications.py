"""
通知管理路由
包含消息通知的查询、已读等API接口
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.reservation import Reservation
from app.routers.users import get_current_user, get_current_admin

router = APIRouter()


def create_new_reservation_notification(db: Session, reservation: Reservation):
    """
    创建新预约通知（内部函数）
    
    Args:
        db: 数据库会话
        reservation: 预约对象
    """
    notification = Notification(
        user_id=None,
        reservation_id=reservation.id,
        notification_type=NotificationType.NEW_RESERVATION,
        title=f"新预约通知 - {reservation.reservation_no}",
        content=f"用户 {reservation.user.phone if reservation.user else '未知'} 提交了新预约，预约单号：{reservation.reservation_no}",
        status=NotificationStatus.UNREAD
    )
    db.add(notification)
    db.commit()


def create_deposit_paid_notification(db: Session, reservation: Reservation):
    """
    创建押金支付通知（内部函数）
    
    Args:
        db: 数据库会话
        reservation: 预约对象
    """
    notification = Notification(
        user_id=None,
        reservation_id=reservation.id,
        notification_type=NotificationType.DEPOSIT_PAID,
        title=f"押金支付通知 - {reservation.reservation_no}",
        content=f"用户 {reservation.user.phone if reservation.user else '未知'} 已支付押金，金额：{reservation.deposit}元",
        status=NotificationStatus.UNREAD
    )
    db.add(notification)
    db.commit()


@router.get("/")
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取通知列表
    
    Args:
        skip: 跳过的数量
        limit: 返回的最大数量
        unread_only: 是否只获取未读通知
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        List[dict]: 通知列表
    """
    query = db.query(Notification).filter(
        Notification.user_id == None
    )
    
    if unread_only:
        query = query.filter(Notification.status == NotificationStatus.UNREAD)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [notification.to_dict() for notification in notifications]


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取未读通知数量
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 未读通知数量
    """
    count = db.query(Notification).filter(
        Notification.user_id == None,
        Notification.status == NotificationStatus.UNREAD
    ).count()
    
    return {"unread_count": count}


@router.get("/{notification_id}")
def get_notification_by_id(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取通知详情
    
    Args:
        notification_id: 通知ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 通知信息
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return notification.to_dict()


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记通知为已读
    
    Args:
        notification_id: 通知ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 操作成功提示
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    if notification.status != NotificationStatus.READ:
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()
        db.commit()
    
    return {"message": "通知已标记为已读"}


@router.post("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记所有通知为已读
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 操作成功提示
    """
    notifications = db.query(Notification).filter(
        Notification.user_id == None,
        Notification.status == NotificationStatus.UNREAD
    ).all()
    
    for notification in notifications:
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "所有通知已标记为已读"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除通知（管理员权限）
    
    Args:
        notification_id: 通知ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 删除成功提示
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"message": "通知删除成功"}

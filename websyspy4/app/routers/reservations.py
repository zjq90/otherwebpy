"""
预约管理路由
包含预约的创建、查询、更新等API接口
"""

from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.reservation import Reservation, ReservationStatus
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate
from app.routers.users import get_current_user, get_current_admin
from app.utils.helpers import (
    generate_reservation_no,
    calculate_rental_days,
    calculate_total_rent,
    calculate_total_deposit
)

router = APIRouter()


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_data: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建预约（登录用户）
    
    Args:
        reservation_data: 预约数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ReservationResponse: 创建的预约信息
    """
    product = db.query(Product).filter(
        Product.id == reservation_data.product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品不存在"
        )
    
    if product.available_quantity < reservation_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"产品库存不足，当前可用数量为{product.available_quantity}"
        )
    
    if reservation_data.end_date < reservation_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束日期不能早于开始日期"
        )
    
    rental_days = calculate_rental_days(reservation_data.start_date, reservation_data.end_date)
    total_rent = calculate_total_rent(
        float(product.daily_rent),
        rental_days,
        reservation_data.quantity
    )
    total_deposit = calculate_total_deposit(
        float(product.deposit),
        reservation_data.quantity
    )
    
    new_reservation = Reservation(
        reservation_no=generate_reservation_no(),
        user_id=current_user.id,
        product_id=reservation_data.product_id,
        start_date=reservation_data.start_date,
        end_date=reservation_data.end_date,
        rental_days=rental_days,
        quantity=reservation_data.quantity,
        daily_rent=product.daily_rent,
        total_rent=total_rent,
        deposit=total_deposit,
        remark=reservation_data.remark,
        status=ReservationStatus.PENDING
    )
    
    product.available_quantity -= reservation_data.quantity
    
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    
    try:
        from app.routers.notifications import create_new_reservation_notification
        create_new_reservation_notification(db, new_reservation)
    except Exception:
        pass
    
    return new_reservation.to_dict()


@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="预约状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取预约列表
    
    Args:
        skip: 跳过的数量
        limit: 返回的最大数量
        status: 预约状态过滤
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        List[ReservationResponse]: 预约列表
    """
    query = db.query(Reservation).filter(Reservation.is_deleted == False)
    
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Reservation.user_id == current_user.id)
    
    if status is not None:
        query = query.filter(Reservation.status == status)
    
    reservations = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
    
    return [reservation.to_dict() for reservation in reservations]


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation_by_id(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取预约详情
    
    Args:
        reservation_id: 预约ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ReservationResponse: 预约信息
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if current_user.role != UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此预约"
        )
    
    return reservation.to_dict()


@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation_data: ReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新预约信息
    
    Args:
        reservation_id: 预约ID
        reservation_data: 更新的数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ReservationResponse: 更新后的预约信息
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if current_user.role != UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此预约"
        )
    
    if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态下无法修改预约"
        )
    
    update_data = reservation_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == 'start_date' or key == 'end_date':
            setattr(reservation, key, value)
    
    if reservation_data.start_date and reservation_data.end_date:
        reservation.rental_days = calculate_rental_days(
            reservation.start_date,
            reservation.end_date
        )
        reservation.total_rent = calculate_total_rent(
            float(reservation.daily_rent),
            reservation.rental_days,
            reservation.quantity
        )
    
    db.commit()
    db.refresh(reservation)
    
    return reservation.to_dict()


@router.post("/{reservation_id}/pay-deposit")
def pay_deposit(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    支付押金
    
    Args:
        reservation_id: 预约ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 支付成功提示
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此预约"
        )
    
    if reservation.deposit_paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="押金已支付"
        )
    
    reservation.deposit_paid = True
    reservation.deposit_paid_at = datetime.utcnow()
    reservation.status = ReservationStatus.PAID
    
    db.commit()
    
    return {"message": "押金支付成功"}


@router.post("/{reservation_id}/confirm")
def confirm_reservation(
    reservation_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    确认预约（管理员权限）
    
    Args:
        reservation_id: 预约ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 确认成功提示
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != ReservationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态下无法确认预约"
        )
    
    reservation.status = ReservationStatus.CONFIRMED
    db.commit()
    
    return {"message": "预约确认成功"}


@router.post("/{reservation_id}/pickup")
def pickup_product(
    reservation_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    领取物品（管理员权限）
    
    Args:
        reservation_id: 预约ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 领取成功提示
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status not in [ReservationStatus.CONFIRMED, ReservationStatus.PAID]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态下无法领取物品"
        )
    
    reservation.status = ReservationStatus.PICKED_UP
    reservation.picked_up_at = datetime.utcnow()
    db.commit()
    
    return {"message": "物品领取成功"}


@router.post("/{reservation_id}/return")
def return_product(
    reservation_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    归还物品（管理员权限）
    
    Args:
        reservation_id: 预约ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 归还成功提示
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != ReservationStatus.PICKED_UP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态下无法归还物品"
        )
    
    reservation.status = ReservationStatus.RETURNED
    reservation.returned_at = datetime.utcnow()
    
    if reservation.product:
        reservation.product.available_quantity += reservation.quantity
    
    db.commit()
    
    return {"message": "物品归还成功"}


@router.post("/{reservation_id}/complete")
def complete_reservation(
    reservation_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    完成预约（管理员权限）
    
    Args:
        reservation_id: 预约ID
        current_admin: 当前管理员
        db: 数据库会话
        
    Returns:
        dict: 完成成功提示
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != ReservationStatus.RETURNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态下无法完成预约"
        )
    
    reservation.status = ReservationStatus.COMPLETED
    db.commit()
    
    return {"message": "预约完成成功"}


@router.post("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消预约
    
    Args:
        reservation_id: 预约ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 取消成功提示
    """
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.is_deleted == False
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if current_user.role != UserRole.ADMIN and reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权取消此预约"
        )
    
    if reservation.status in [ReservationStatus.PICKED_UP, ReservationStatus.RETURNED, ReservationStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态下无法取消预约"
        )
    
    if reservation.status != ReservationStatus.CANCELLED:
        reservation.status = ReservationStatus.CANCELLED
        
        if reservation.product:
            reservation.product.available_quantity += reservation.quantity
        
        db.commit()
    
    return {"message": "预约取消成功"}

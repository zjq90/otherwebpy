"""
预约管理路由模块
处理课程预约的增删改查、状态管理等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date

from database import get_db
from models import (
    User, UserRole, Booking, BookingStatus,
    Course, Coach
)
from schemas import (
    BookingCreate, BookingUpdate, BookingResponse, ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取预约列表
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_bookings(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[BookingStatus] = Query(None, description="预约状态筛选"),
    start_date: Optional[date] = Query(None, description="开始日期筛选"),
    end_date: Optional[date] = Query(None, description="结束日期筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取预约列表
    
    会员只能查看自己的预约
    管理员和工作人员可以查看所有预约
    
    Args:
        page: 页码
        page_size: 每页数量
        status: 预约状态筛选
        start_date: 开始日期筛选
        end_date: 结束日期筛选
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的预约列表
    """
    # 构建查询
    query = db.query(Booking)
    
    # 权限控制：会员只能查看自己的预约
    if current_user.role == UserRole.MEMBER:
        query = query.filter(Booking.user_id == current_user.id)
    
    # 状态筛选
    if status:
        query = query.filter(Booking.status == status)
    
    # 日期范围筛选
    if start_date:
        query = query.filter(Booking.booking_date >= start_date)
    if end_date:
        query = query.filter(Booking.booking_date <= end_date)
    
    # 按预约日期倒序排列
    query = query.order_by(Booking.booking_date.desc(), Booking.start_time.desc())
    
    # 分页查询
    paginated = paginate_query(query, page, page_size)
    
    # 转换为响应模型
    bookings_response = []
    for booking in paginated.items:
        booking_response = BookingResponse.model_validate(booking)
        if booking.user:
            booking_response.user = booking_response.user.model_validate(booking.user)
        if booking.course:
            booking_response.course = booking_response.course.model_validate(booking.course)
        bookings_response.append(booking_response)
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"bookings": [b.model_dump() for b in bookings_response]},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取预约详情
# ========================================

@router.get("/{booking_id}", response_model=ResponseModel)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取预约详情
    
    会员只能查看自己的预约详情
    管理员和工作人员可以查看所有预约详情
    
    Args:
        booking_id: 预约ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含预约信息的响应
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    # 权限检查：会员只能查看自己的预约
    if (current_user.role == UserRole.MEMBER and 
        current_user.id != booking.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该预约详情"
        )
    
    booking_response = BookingResponse.model_validate(booking)
    if booking.user:
        booking_response.user = booking_response.user.model_validate(booking.user)
    if booking.course:
        booking_response.course = booking_response.course.model_validate(booking.course)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"booking": booking_response.model_dump()}
    )

# ========================================
# 创建预约
# ========================================

@router.post("", response_model=ResponseModel)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建课程预约
    
    会员可以预约课程
    管理员和工作人员也可以为会员预约
    
    Args:
        booking_data: 预约数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新预约信息的响应
    """
    # 权限检查：会员只能为自己预约
    if (current_user.role == UserRole.MEMBER and 
        current_user.id != booking_data.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己预约课程"
        )
    
    # 检查课程是否存在且可用
    course = db.query(Course).filter(
        Course.id == booking_data.course_id,
        Course.is_active == True
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在或已下架"
        )
    
    # 私教课需要指定教练
    if course.course_type.value == "private" and not booking_data.coach_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="私教课必须指定教练"
        )
    
    # 检查教练是否存在且可预约（如果指定了教练）
    if booking_data.coach_id:
        coach = db.query(Coach).filter(
            Coach.id == booking_data.coach_id,
            Coach.is_available == True
        ).first()
        
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练不存在或不可预约"
            )
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == booking_data.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查同一时间是否有冲突预约
    conflicting_booking = db.query(Booking).filter(
        Booking.user_id == booking_data.user_id,
        Booking.booking_date == booking_data.booking_date,
        Booking.start_time == booking_data.start_time,
        Booking.status.notin_([BookingStatus.CANCELLED])
    ).first()
    
    if conflicting_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已在该时间段有预约"
        )
    
    # 创建预约
    new_booking = Booking(
        user_id=booking_data.user_id,
        course_id=booking_data.course_id,
        coach_id=booking_data.coach_id,
        booking_date=booking_data.booking_date,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        notes=booking_data.notes,
        status=BookingStatus.PENDING
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    booking_response = BookingResponse.model_validate(new_booking)
    
    return ResponseModel(
        code=200,
        message="预约成功",
        data={"booking": booking_response.model_dump()}
    )

# ========================================
# 更新预约状态
# ========================================

@router.put("/{booking_id}", response_model=ResponseModel)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新预约信息
    
    会员可以取消自己的预约
    管理员和工作人员可以更新所有预约的状态
    
    Args:
        booking_id: 预约ID
        booking_data: 更新数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后预约信息的响应
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    # 权限检查：会员只能取消自己的预约
    if current_user.role == UserRole.MEMBER:
        if current_user.id != booking.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改该预约"
            )
        # 会员只能将状态改为已取消
        if booking_data.status and booking_data.status != BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您只能取消预约"
            )
    
    # 更新预约信息
    update_data = booking_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(booking, key, value)
    
    db.commit()
    db.refresh(booking)
    
    booking_response = BookingResponse.model_validate(booking)
    
    status_text = {
        BookingStatus.PENDING: "待确认",
        BookingStatus.CONFIRMED: "已确认",
        BookingStatus.COMPLETED: "已完成",
        BookingStatus.CANCELLED: "已取消",
        BookingStatus.NO_SHOW: "未出席"
    }.get(booking.status, "未知状态")
    
    return ResponseModel(
        code=200,
        message=f"预约状态已更新为：{status_text}",
        data={"booking": booking_response.model_dump()}
    )

# ========================================
# 取消预约
# ========================================

@router.post("/{booking_id}/cancel", response_model=ResponseModel)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消预约
    
    会员可以取消自己的预约
    管理员和工作人员也可以取消预约
    
    Args:
        booking_id: 预约ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    # 权限检查
    if (current_user.role == UserRole.MEMBER and 
        current_user.id != booking.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权取消该预约"
        )
    
    # 检查是否可以取消
    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已完成的预约不能取消"
        )
    
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="预约已取消"
        )
    
    # 取消预约
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    
    booking_response = BookingResponse.model_validate(booking)
    
    return ResponseModel(
        code=200,
        message="预约已取消",
        data={"booking": booking_response.model_dump()}
    )

# ========================================
# 获取我的预约（快捷接口）
# ========================================

@router.get("/list/my", response_model=ResponseModel)
async def get_my_bookings(
    status: Optional[BookingStatus] = Query(None, description="状态筛选"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的预约列表（快捷接口）
    
    Args:
        status: 状态筛选
        limit: 返回数量
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含预约列表的响应
    """
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.order_by(
        Booking.booking_date.desc(),
        Booking.start_time.desc()
    ).limit(limit).all()
    
    bookings_response = []
    for booking in bookings:
        booking_response = BookingResponse.model_validate(booking)
        if booking.course:
            booking_response.course = booking_response.course.model_validate(booking.course)
        bookings_response.append(booking_response.model_dump())
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"bookings": bookings_response}
    )

# ========================================
# 获取待确认预约数量
# ========================================

@router.get("/stats/pending-count", response_model=ResponseModel)
async def get_pending_bookings_count(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
    db: Session = Depends(get_db)
):
    """
    获取待确认预约的数量
    
    需要管理员或工作人员权限
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含待确认数量的响应
    """
    pending_count = db.query(Booking).filter(
        Booking.status == BookingStatus.PENDING
    ).count()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"pending_count": pending_count}
    )

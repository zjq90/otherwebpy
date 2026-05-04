"""
服务评价路由模块
处理会员对教练的评分与文字评价功能
每节私教课后可对教练进行评分与文字评价，评价内容将用于教练绩效考核
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import User, UserRole, Review, Coach, Booking, BookingStatus
from schemas import (
    ReviewCreate, ReviewUpdate, CoachReplyUpdate, ReviewResponse,
    ResponseModel, PaginatedResponse
)
from utils import (
    get_current_active_user, require_role, paginate_query
)

router = APIRouter()

# ========================================
# 获取评价列表
# ========================================

@router.get("", response_model=PaginatedResponse)
async def get_reviews(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    coach_id: Optional[int] = Query(None, description="教练ID筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="评分筛选"),
    db: Session = Depends(get_db)
):
    """
    获取评价列表
    
    支持分页、教练筛选、用户筛选、评分筛选
    所有用户都可以查看评价列表
    
    Args:
        page: 页码
        page_size: 每页数量
        coach_id: 教练ID筛选
        user_id: 用户ID筛选
        rating: 评分筛选
        db: 数据库会话
        
    Returns:
        PaginatedResponse: 分页的评价列表
    """
    query = db.query(Review).filter(Review.is_visible == True)
    
    if coach_id:
        query = query.filter(Review.coach_id == coach_id)
    
    if user_id:
        query = query.filter(Review.user_id == user_id)
    
    if rating:
        query = query.filter(Review.rating == rating)
    
    query = query.order_by(Review.created_at.desc())
    
    paginated = paginate_query(query, page, page_size)
    
    reviews_response = []
    for review in paginated.items:
        review_dict = ReviewResponse.model_validate(review).model_dump()
        if review.user:
            review_dict["user"] = {
                "id": review.user.id,
                "real_name": review.user.real_name if not review.is_anonymous else "匿名用户",
                "avatar": review.user.avatar
            }
        if review.coach and review.coach.user:
            review_dict["coach"] = {
                "id": review.coach.id,
                "user_id": review.coach.user_id,
                "specialization": review.coach.specialization,
                "rating": review.coach.rating,
                "real_name": review.coach.user.real_name,
                "avatar": review.coach.user.avatar
            }
        reviews_response.append(review_dict)
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"reviews": reviews_response},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取评价详情
# ========================================

@router.get("/{review_id}", response_model=ResponseModel)
async def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """
    获取评价详情
    
    Args:
        review_id: 评价ID
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含评价信息的响应
    """
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.is_visible == True
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在或已隐藏"
        )
    
    review_dict = ReviewResponse.model_validate(review).model_dump()
    if review.user:
        review_dict["user"] = {
            "id": review.user.id,
            "real_name": review.user.real_name if not review.is_anonymous else "匿名用户",
            "avatar": review.user.avatar
        }
    if review.coach and review.coach.user:
        review_dict["coach"] = {
            "id": review.coach.id,
            "user_id": review.coach.user_id,
            "specialization": review.coach.specialization,
            "rating": review.coach.rating,
            "real_name": review.coach.user.real_name,
            "avatar": review.coach.user.avatar
        }
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"review": review_dict}
    )

# ========================================
# 创建评价（会员权限）
# ========================================

@router.post("", response_model=ResponseModel)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(require_role(UserRole.MEMBER)),
    db: Session = Depends(get_db)
):
    """
    创建评价
    
    会员在私教课后对教练进行评分与文字评价
    需要会员权限
    
    Args:
        review_data: 评价数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含新评价信息的响应
    """
    booking = db.query(Booking).filter(
        Booking.id == review_data.booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约记录不存在"
        )
    
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能对已完成的课程进行评价"
        )
    
    existing_review = db.query(Review).filter(
        Review.booking_id == review_data.booking_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约已存在评价"
        )
    
    coach = db.query(Coach).filter(Coach.id == review_data.coach_id).first()
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    new_review = Review(
        user_id=current_user.id,
        coach_id=review_data.coach_id,
        booking_id=review_data.booking_id,
        rating=review_data.rating,
        professionalism_rating=review_data.professionalism_rating,
        punctuality_rating=review_data.punctuality_rating,
        attitude_rating=review_data.attitude_rating,
        content=review_data.content,
        image_urls=review_data.image_urls,
        is_anonymous=review_data.is_anonymous,
        is_visible=True
    )
    
    db.add(new_review)
    db.flush()
    
    total_reviews = coach.review_count + 1
    new_rating = (coach.rating * coach.review_count + review_data.rating) / total_reviews
    
    coach.rating = round(new_rating, 1)
    coach.review_count = total_reviews
    
    db.commit()
    db.refresh(new_review)
    
    review_response = ReviewResponse.model_validate(new_review)
    
    return ResponseModel(
        code=200,
        message="评价创建成功",
        data={"review": review_response.model_dump()}
    )

# ========================================
# 更新评价（用户本人权限）
# ========================================

@router.put("/{review_id}", response_model=ResponseModel)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新评价内容
    
    只有评价的创建者可以更新评价
    注意：评分不可修改，只能修改文字内容和图片
    
    Args:
        review_id: 评价ID
        review_data: 更新数据
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含更新后评价信息的响应
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    update_data = review_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)
    
    db.commit()
    db.refresh(review)
    
    review_response = ReviewResponse.model_validate(review)
    
    return ResponseModel(
        code=200,
        message="更新成功",
        data={"review": review_response.model_dump()}
    )

# ========================================
# 教练回复评价（教练权限）
# ========================================

@router.put("/{review_id}/reply", response_model=ResponseModel)
async def reply_review(
    review_id: int,
    reply_data: CoachReplyUpdate,
    current_user: User = Depends(require_role(UserRole.COACH)),
    db: Session = Depends(get_db)
):
    """
    教练回复评价
    
    被评价的教练可以对评价进行回复
    
    Args:
        review_id: 评价ID
        reply_data: 回复数据
        current_user: 当前认证用户（教练）
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    
    coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
    if not coach or review.coach_id != coach.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能回复自己收到的评价"
        )
    
    review.coach_reply = reply_data.coach_reply
    review.coach_reply_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    
    review_response = ReviewResponse.model_validate(review)
    
    return ResponseModel(
        code=200,
        message="回复成功",
        data={"review": review_response.model_dump()}
    )

# ========================================
# 删除/隐藏评价（管理员权限）
# ========================================

@router.delete("/{review_id}", response_model=ResponseModel)
async def delete_review(
    review_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    删除/隐藏评价
    
    需要管理员权限
    软删除：设置is_visible为False，而不是物理删除
    
    Args:
        review_id: 评价ID
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    
    review.is_visible = False
    db.commit()
    
    return ResponseModel(
        code=200,
        message="评价已隐藏",
        data=None
    )

# ========================================
# 获取我的评价列表（当前用户）
# ========================================

@router.get("/list/my", response_model=ResponseModel)
async def get_my_reviews(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的评价列表
    
    会员可以查看自己发表的评价
    教练可以查看收到的评价
    
    Args:
        page: 页码
        page_size: 每页数量
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含评价列表的响应
    """
    if current_user.role == UserRole.COACH:
        coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
        if coach:
            query = db.query(Review).filter(Review.coach_id == coach.id)
        else:
            query = db.query(Review).filter(False)
    else:
        query = db.query(Review).filter(Review.user_id == current_user.id)
    
    query = query.order_by(Review.created_at.desc())
    
    paginated = paginate_query(query, page, page_size)
    
    reviews_response = []
    for review in paginated.items:
        review_dict = ReviewResponse.model_validate(review).model_dump()
        if review.user:
            review_dict["user"] = {
                "id": review.user.id,
                "real_name": review.user.real_name if not review.is_anonymous else "匿名用户",
                "avatar": review.user.avatar
            }
        if review.coach and review.coach.user:
            review_dict["coach"] = {
                "id": review.coach.id,
                "user_id": review.coach.user_id,
                "specialization": review.coach.specialization,
                "rating": review.coach.rating,
                "real_name": review.coach.user.real_name,
                "avatar": review.coach.user.avatar
            }
        reviews_response.append(review_dict)
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={"reviews": reviews_response},
        total=paginated.total,
        page=paginated.page,
        page_size=paginated.page_size,
        total_pages=paginated.total_pages
    )

# ========================================
# 获取待评价的预约列表
# ========================================

@router.get("/pending/list", response_model=ResponseModel)
async def get_pending_reviews(
    current_user: User = Depends(require_role(UserRole.MEMBER)),
    db: Session = Depends(get_db)
):
    """
    获取待评价的预约列表
    
    会员可以查看已完成但尚未评价的预约
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含待评价预约列表的响应
    """
    from models import Course
    
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.status == BookingStatus.COMPLETED
    ).all()
    
    pending_bookings = []
    for booking in bookings:
        review = db.query(Review).filter(Review.booking_id == booking.id).first()
        if not review:
            booking_dict = {
                "id": booking.id,
                "course_id": booking.course_id,
                "coach_id": booking.coach_id,
                "booking_date": booking.booking_date.strftime("%Y-%m-%d") if booking.booking_date else None,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "course_name": booking.course.name if booking.course else None,
                "coach_name": None
            }
            
            if booking.coach and booking.coach.user:
                booking_dict["coach_name"] = booking.coach.user.real_name
            
            pending_bookings.append(booking_dict)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"pending_bookings": pending_bookings}
    )

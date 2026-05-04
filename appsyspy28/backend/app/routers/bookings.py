from typing import List, Optional
from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, BookingStatus, Class, CardType
from app.schemas.schemas import (
    BookingCreate, BookingResponse, BookingListResponse, CancelLimitResponse
)
from app.crud.crud import (
    booking_crud, class_crud, card_crud
)
from app.core.security import get_current_active_member

router = APIRouter(prefix="/api/bookings", tags=["在线预约"])

CANCEL_WINDOW_HOURS = 72
MAX_CANCELS_IN_WINDOW = 3

def check_cancel_eligibility(db: Session, user_id: int) -> tuple:
    now = datetime.utcnow()
    window_start = now - timedelta(hours=CANCEL_WINDOW_HOURS)
    
    cancel_count = db.execute(
        "SELECT COUNT(*) FROM bookings "
        "WHERE user_id = ? AND status = 'cancelled' AND updated_at >= ?",
        (user_id, window_start)
    ).scalar() or 0
    
    remaining = MAX_CANCELS_IN_WINDOW - cancel_count
    can_cancel = remaining > 0
    
    message = f"72小时内已取消 {cancel_count} 次，还可取消 {remaining} 次"
    if not can_cancel:
        message = "72小时内取消次数已达上限（3次），无法继续取消"
    
    return can_cancel, remaining, message

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    class_id: int = Body(..., embed=True, description="课程ID"),
    card_id: Optional[int] = Body(None, embed=True, description="会员卡ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    cls = class_crud.get_by_id(db, class_id=class_id)
    if not cls or not cls.is_active:
        raise HTTPException(status_code=404, detail="课程不存在或已下架")
    
    class_datetime = datetime.combine(cls.class_date, cls.start_time)
    if class_datetime < datetime.utcnow():
        raise HTTPException(status_code=400, detail="课程已过期，无法预约")
    
    if cls.booked_count >= cls.capacity:
        raise HTTPException(status_code=400, detail="课程名额已满")
    
    existing_booking = booking_crud.get_by_user_and_class(
        db, user_id=current_user.id, class_id=class_id
    )
    if existing_booking:
        raise HTTPException(status_code=400, detail="您已预约过该课程")
    
    active_cards = card_crud.get_active_valid_cards(db, user_id=current_user.id)
    if not active_cards:
        raise HTTPException(status_code=400, detail="没有可用的会员卡")
    
    category_id = cls.category_id
    valid_cards = []
    for card in active_cards:
        if card_crud.can_use_for_category(db, card.id, category_id):
            valid_cards.append(card)
    
    if not valid_cards:
        raise HTTPException(status_code=400, detail="您的会员卡不包含该课程")
    
    selected_card = None
    if card_id:
        selected_card = next((c for c in valid_cards if c.id == card_id), None)
        if not selected_card:
            raise HTTPException(status_code=400, detail="指定的会员卡无效或不包含该课程")
    else:
        selected_card = valid_cards[0]
    
    booking = booking_crud.create(
        db,
        BookingCreate(
            user_id=current_user.id,
            class_id=class_id,
            card_id=selected_card.id
        )
    )
    
    class_crud.increment_booked(db, class_id=class_id)
    card_crud.use_card(db, card_id=selected_card.id)
    
    db.refresh(booking)
    return BookingResponse.model_validate(booking)

@router.get("/my", response_model=BookingListResponse)
def get_my_bookings(
    status: Optional[str] = Query(None, description="预约状态过滤: pending/confirmed/cancelled/completed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking_status = None
    if status:
        try:
            booking_status = BookingStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的预约状态")
    
    bookings = booking_crud.get_by_user(
        db,
        user_id=current_user.id,
        status=booking_status,
        skip=skip,
        limit=limit
    )
    
    return BookingListResponse(
        total=len(bookings),
        items=[BookingResponse.model_validate(b) for b in bookings]
    )

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_detail(
    booking_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = booking_crud.get_by_id_with_details(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看该预约")
    
    return BookingResponse.model_validate(booking)

@router.delete("/{booking_id}", response_model=dict)
def cancel_booking(
    booking_id: int = Path(..., gt=0),
    reason: Optional[str] = Query(None, description="取消原因"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = booking_crud.get_by_id(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权取消该预约")
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="该预约无法取消")
    
    cls = class_crud.get_by_id(db, class_id=booking.class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="关联课程不存在")
    
    class_datetime = datetime.combine(cls.class_date, cls.start_time)
    now = datetime.utcnow()
    
    if class_datetime <= now:
        raise HTTPException(status_code=400, detail="课程已开始，无法取消")
    
    can_cancel, remaining, message = check_cancel_eligibility(db, user_id=current_user.id)
    if not can_cancel:
        raise HTTPException(status_code=400, detail=message)
    
    if booking.card_id:
        card_crud.return_card(db, card_id=booking.card_id)
    
    class_crud.decrement_booked(db, class_id=booking.class_id)
    
    booking_crud.cancel(db, booking_id=booking_id, reason=reason)
    
    return {"success": True, "message": "取消成功", "remaining_cancels": remaining}

@router.get("/check/cancel-limit", response_model=CancelLimitResponse)
def check_cancel_limit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    can_cancel, remaining, message = check_cancel_eligibility(db, user_id=current_user.id)
    return CancelLimitResponse(
        can_cancel=can_cancel,
        remaining_cancels=remaining,
        message=message
    )

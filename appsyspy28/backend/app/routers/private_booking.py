from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, BookingStatus, CardType
from app.schemas.schemas import (
    CoachScheduleResponse, PrivateBookingCreate, PrivateBookingResponse,
    PrivateBookingUpdate
)
from app.crud.crud import (
    coach_schedule_crud, private_booking_crud, card_crud, user_crud
)
from app.core.security import get_current_active_member, get_current_active_coach

router = APIRouter(prefix="/api/private", tags=["私教约课"])

@router.get("/coaches", response_model=List[dict])
def get_available_coaches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    coaches = user_crud.get_coaches(db)
    
    result = []
    for coach in coaches:
        result.append({
            "id": coach.id,
            "name": coach.name,
            "phone": coach.phone,
            "avatar": coach.avatar,
            "role": coach.role.value
        })
    
    return result

@router.get("/schedules/{coach_id}", response_model=List[CoachScheduleResponse])
def get_coach_available_slots(
    coach_id: int = Path(..., gt=0),
    start_date: Optional[date] = Query(None, description="开始日期，默认为今天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    coach = user_crud.get_by_id(db, user_id=coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    schedules = coach_schedule_crud.get_available_slots(
        db,
        coach_id=coach_id,
        start_date=start_date
    )
    
    return [CoachScheduleResponse.model_validate(s) for s in schedules]

@router.post("/book", response_model=PrivateBookingResponse, status_code=201)
def create_private_booking(
    booking_data: PrivateBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    schedule = coach_schedule_crud.get_by_id(db, schedule_id=booking_data.schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="时段不存在")
    
    if schedule.coach_id != booking_data.coach_id:
        raise HTTPException(status_code=400, detail="教练与时段不匹配")
    
    if not schedule.is_available or schedule.is_booked:
        raise HTTPException(status_code=400, detail="该时段不可预约")
    
    coach = user_crud.get_by_id(db, user_id=booking_data.coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    active_cards = card_crud.get_active_valid_cards(db, user_id=current_user.id)
    if not active_cards:
        raise HTTPException(status_code=400, detail="没有可用的会员卡")
    
    private_cards = [c for c in active_cards if c.card_type in [CardType.PRIVATE, CardType.TIMES, CardType.YEARLY, CardType.MONTHLY]]
    
    if not private_cards:
        raise HTTPException(status_code=400, detail="没有可用于私教课的会员卡")
    
    selected_card = None
    if booking_data.card_id:
        selected_card = next((c for c in private_cards if c.id == booking_data.card_id), None)
        if not selected_card:
            raise HTTPException(status_code=400, detail="指定的会员卡无效或不适用于私教课")
    else:
        selected_card = private_cards[0]
    
    coach_schedule_crud.book_slot(db, schedule_id=booking_data.schedule_id)
    
    booking = private_booking_crud.create(
        db,
        member_id=current_user.id,
        booking_in=booking_data
    )
    
    if selected_card:
        card_crud.use_card(db, card_id=selected_card.id)
        booking.card_id = selected_card.id
        db.commit()
    
    db.refresh(booking)
    return PrivateBookingResponse.model_validate(booking)

@router.get("/my-bookings", response_model=List[PrivateBookingResponse])
def get_my_private_bookings(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking_status = None
    if status:
        try:
            booking_status = BookingStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的预约状态")
    
    bookings = private_booking_crud.get_by_member(
        db,
        member_id=current_user.id,
        status=booking_status
    )
    
    return [PrivateBookingResponse.model_validate(b) for b in bookings]

@router.get("/coach-bookings", response_model=List[PrivateBookingResponse])
def get_coach_private_bookings(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_coach)
):
    booking_status = None
    if status:
        try:
            booking_status = BookingStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的预约状态")
    
    bookings = private_booking_crud.get_by_coach(
        db,
        coach_id=current_user.id,
        status=booking_status
    )
    
    return [PrivateBookingResponse.model_validate(b) for b in bookings]

@router.get("/{booking_id}", response_model=PrivateBookingResponse)
def get_private_booking_detail(
    booking_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = private_booking_crud.get_by_id(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if booking.member_id != current_user.id and booking.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看该预约")
    
    return PrivateBookingResponse.model_validate(booking)

@router.put("/confirm/{booking_id}", response_model=PrivateBookingResponse)
def confirm_private_booking(
    booking_id: int = Path(..., gt=0),
    coach_notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_coach)
):
    booking = private_booking_crud.get_by_id(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if booking.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该预约")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能确认待处理的预约")
    
    private_booking_crud.confirm(db, booking_id=booking_id, coach_notes=coach_notes)
    db.refresh(booking)
    
    return PrivateBookingResponse.model_validate(booking)

@router.put("/reject/{booking_id}", response_model=PrivateBookingResponse)
def reject_private_booking(
    booking_id: int = Path(..., gt=0),
    cancel_reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_coach)
):
    booking = private_booking_crud.get_by_id(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if booking.coach_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该预约")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能拒绝待处理的预约")
    
    if booking.card_id:
        card_crud.return_card(db, card_id=booking.card_id)
    
    private_booking_crud.reject(db, booking_id=booking_id, cancel_reason=cancel_reason)
    db.refresh(booking)
    
    return PrivateBookingResponse.model_validate(booking)

@router.delete("/{booking_id}", response_model=dict)
def cancel_private_booking(
    booking_id: int = Path(..., gt=0),
    cancel_reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = private_booking_crud.get_by_id(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if booking.member_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权取消该预约")
    
    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="该预约无法取消")
    
    schedule = booking.schedule
    class_start_datetime = datetime.combine(schedule.schedule_date, schedule.start_time)
    now = datetime.utcnow()
    
    if class_start_datetime <= now:
        raise HTTPException(status_code=400, detail="课程已开始，无法取消")
    
    if booking.card_id:
        card_crud.return_card(db, card_id=booking.card_id)
    
    private_booking_crud.cancel(db, booking_id=booking_id, cancel_reason=cancel_reason or "会员主动取消")
    
    return {"success": True, "message": "取消成功"}

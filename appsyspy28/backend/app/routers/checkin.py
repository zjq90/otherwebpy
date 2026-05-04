from typing import List, Optional
from datetime import datetime, date, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, CheckinMethod, BookingStatus, Class, Room
from app.schemas.schemas import (
    CheckinResponse, QRCodeCheckin, FaceCheckin
)
from app.crud.crud import (
    checkin_crud, booking_crud, class_crud, room_crud, private_booking_crud,
    private_checkin_crud
)
from app.core.security import get_current_active_member

router = APIRouter(prefix="/api/checkin", tags=["扫码签到"])

def verify_qr_code(qr_code: str) -> bool:
    return qr_code is not None and len(qr_code) > 0

def verify_face(face_image: str, user_id: int) -> bool:
    return True

@router.post("/qrcode", response_model=CheckinResponse)
def qrcode_checkin(
    checkin_data: QRCodeCheckin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = booking_crud.get_by_id(db, booking_id=checkin_data.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作他人的预约")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail=f"预约状态不正确，当前状态: {booking.status}")
    
    existing_checkin = checkin_crud.get_by_booking(db, booking_id=checkin_data.booking_id)
    if existing_checkin:
        raise HTTPException(status_code=400, detail="您已签到过了")
    
    cls = class_crud.get_by_id(db, class_id=booking.class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="关联课程不存在")
    
    room = room_crud.get_by_id(db, room_id=cls.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="关联教室不存在")
    
    if room.qr_code != checkin_data.qr_code:
        raise HTTPException(status_code=400, detail="二维码无效，请扫描正确的教室二维码")
    
    class_start_datetime = datetime.combine(cls.class_date, cls.start_time)
    now = datetime.utcnow()
    
    if now < class_start_datetime - timedelta(minutes=30):
        raise HTTPException(status_code=400, detail="签到时间未到，提前30分钟开始签到")
    
    if now > class_start_datetime + timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="已迟到超过15分钟，无法签到")
    
    checkin = checkin_crud.create(
        db,
        user_id=current_user.id,
        booking_id=checkin_data.booking_id,
        class_id=cls.id,
        checkin_method=CheckinMethod.QRCODE,
        face_verified=False
    )
    
    return CheckinResponse.model_validate(checkin)

@router.post("/face", response_model=CheckinResponse)
def face_checkin(
    checkin_data: FaceCheckin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = booking_crud.get_by_id(db, booking_id=checkin_data.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作他人的预约")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail=f"预约状态不正确，当前状态: {booking.status}")
    
    existing_checkin = checkin_crud.get_by_booking(db, booking_id=checkin_data.booking_id)
    if existing_checkin:
        raise HTTPException(status_code=400, detail="您已签到过了")
    
    cls = class_crud.get_by_id(db, class_id=booking.class_id)
    if not cls:
        raise HTTPException(status_code=404, detail="关联课程不存在")
    
    class_start_datetime = datetime.combine(cls.class_date, cls.start_time)
    now = datetime.utcnow()
    
    if now < class_start_datetime - timedelta(minutes=30):
        raise HTTPException(status_code=400, detail="签到时间未到，提前30分钟开始签到")
    
    if now > class_start_datetime + timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="已迟到超过15分钟，无法签到")
    
    face_verified = verify_face(checkin_data.face_image, current_user.id)
    if not face_verified:
        raise HTTPException(status_code=400, detail="人脸识别失败，无法代签")
    
    checkin = checkin_crud.create(
        db,
        user_id=current_user.id,
        booking_id=checkin_data.booking_id,
        class_id=cls.id,
        checkin_method=CheckinMethod.FACE,
        face_verified=True
    )
    
    return CheckinResponse.model_validate(checkin)

@router.get("/my", response_model=List[CheckinResponse])
def get_my_checkins(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    checkins = checkin_crud.get_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return [CheckinResponse.model_validate(c) for c in checkins]

@router.post("/private/qrcode", response_model=dict)
def private_qrcode_checkin(
    private_booking_id: int = Body(..., embed=True),
    qr_code: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = private_booking_crud.get_by_id(db, booking_id=private_booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="私教预约不存在")
    
    if booking.member_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作他人的预约")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="预约状态不正确")
    
    existing_checkin = private_checkin_crud.get_by_booking(db, private_booking_id=private_booking_id)
    if existing_checkin:
        raise HTTPException(status_code=400, detail="您已签到过了")
    
    schedule = booking.schedule
    class_start_datetime = datetime.combine(schedule.schedule_date, schedule.start_time)
    now = datetime.utcnow()
    
    if now < class_start_datetime - timedelta(minutes=30):
        raise HTTPException(status_code=400, detail="签到时间未到")
    
    if now > class_start_datetime + timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="已迟到超过15分钟，无法签到")
    
    checkin = private_checkin_crud.create(
        db,
        user_id=current_user.id,
        private_booking_id=private_booking_id,
        checkin_method=CheckinMethod.QRCODE,
        face_verified=False
    )
    
    return {"success": True, "checkin_id": checkin.id, "message": "签到成功"}

@router.post("/private/face", response_model=dict)
def private_face_checkin(
    private_booking_id: int = Body(..., embed=True),
    face_image: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_member)
):
    booking = private_booking_crud.get_by_id(db, booking_id=private_booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="私教预约不存在")
    
    if booking.member_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作他人的预约")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="预约状态不正确")
    
    existing_checkin = private_checkin_crud.get_by_booking(db, private_booking_id=private_booking_id)
    if existing_checkin:
        raise HTTPException(status_code=400, detail="您已签到过了")
    
    schedule = booking.schedule
    class_start_datetime = datetime.combine(schedule.schedule_date, schedule.start_time)
    now = datetime.utcnow()
    
    if now < class_start_datetime - timedelta(minutes=30):
        raise HTTPException(status_code=400, detail="签到时间未到")
    
    if now > class_start_datetime + timedelta(minutes=15):
        raise HTTPException(status_code=400, detail="已迟到超过15分钟，无法签到")
    
    face_verified = verify_face(face_image, current_user.id)
    if not face_verified:
        raise HTTPException(status_code=400, detail="人脸识别失败，无法代签")
    
    checkin = private_checkin_crud.create(
        db,
        user_id=current_user.id,
        private_booking_id=private_booking_id,
        checkin_method=CheckinMethod.FACE,
        face_verified=True
    )
    
    return {"success": True, "checkin_id": checkin.id, "message": "签到成功"}

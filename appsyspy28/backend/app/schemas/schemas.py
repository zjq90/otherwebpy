from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from app.models.models import (
    UserRole, BookingStatus, CheckinMethod, CardType
)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    name: str = Field(..., min_length=2, max_length=100, description="真实姓名")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像路径")
    role: UserRole = Field(default=UserRole.MEMBER, description="用户角色")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="密码")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=11, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True

class UserLogin(BaseModel):
    username: str
    password: str

class ClassCategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="课程类别名称")
    description: Optional[str] = Field(None, description="描述")
    icon: Optional[str] = Field(None, description="图标")
    is_active: bool = Field(default=True, description="是否启用")

class ClassCategoryCreate(ClassCategoryBase):
    pass

class ClassCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None

class ClassCategoryResponse(ClassCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoomBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="教室名称")
    capacity: int = Field(..., gt=0, description="容量")
    location: Optional[str] = Field(None, max_length=100, description="位置描述")
    qr_code: Optional[str] = Field(None, description="签到二维码内容")
    is_active: bool = Field(default=True, description="是否启用")

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    location: Optional[str] = None
    qr_code: Optional[str] = None
    is_active: Optional[bool] = None

class RoomResponse(RoomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ClassBase(BaseModel):
    category_id: int = Field(..., gt=0, description="课程类别ID")
    coach_id: int = Field(..., gt=0, description="教练ID")
    room_id: int = Field(..., gt=0, description="教室ID")
    name: str = Field(..., min_length=2, max_length=100, description="课程名称")
    description: Optional[str] = Field(None, description="课程描述")
    class_date: date = Field(..., description="课程日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    capacity: int = Field(..., gt=0, description="课程容量")
    is_active: bool = Field(default=True, description="是否启用")

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    category_id: Optional[int] = Field(None, gt=0)
    coach_id: Optional[int] = Field(None, gt=0)
    room_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    class_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class ClassResponse(ClassBase):
    id: int
    booked_count: int
    created_at: datetime
    updated_at: datetime
    category: Optional[ClassCategoryResponse] = None
    coach: Optional[UserResponse] = None
    room: Optional[RoomResponse] = None

    class Config:
        from_attributes = True

class ClassSimpleResponse(BaseModel):
    id: int
    name: str
    class_date: date
    start_time: time
    end_time: time
    capacity: int
    booked_count: int
    category_name: Optional[str] = None
    coach_name: Optional[str] = None
    room_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class MemberCardBase(BaseModel):
    user_id: int = Field(..., gt=0, description="用户ID")
    card_type: CardType = Field(..., description="卡类型")
    card_name: str = Field(..., min_length=2, max_length=100, description="卡名称")
    total_times: Optional[int] = Field(None, gt=0, description="总次数（次卡）")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    is_active: bool = Field(default=True, description="是否激活")
    category_ids: List[int] = Field(default=[], description="可使用的课程类别ID列表")

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('结束日期必须大于开始日期')
        return v

class MemberCardCreate(MemberCardBase):
    pass

class MemberCardUpdate(BaseModel):
    card_name: Optional[str] = Field(None, min_length=2, max_length=100)
    total_times: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    category_ids: Optional[List[int]] = None

class MemberCardResponse(BaseModel):
    id: int
    user_id: int
    card_type: CardType
    card_name: str
    total_times: Optional[int]
    used_times: int
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime
    categories: List[ClassCategoryResponse] = []

    class Config:
        from_attributes = True
        use_enum_values = True

class BookingBase(BaseModel):
    user_id: int = Field(..., gt=0, description="用户ID")
    class_id: int = Field(..., gt=0, description="课程ID")
    card_id: Optional[int] = Field(None, gt=0, description="使用的会员卡ID")

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    cancel_reason: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    user_id: int
    class_id: int
    card_id: Optional[int]
    status: BookingStatus
    cancel_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    class_: Optional[ClassSimpleResponse] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class CheckinBase(BaseModel):
    user_id: int = Field(..., gt=0, description="用户ID")
    booking_id: int = Field(..., gt=0, description="预约ID")
    class_id: int = Field(..., gt=0, description="课程ID")
    checkin_method: CheckinMethod = Field(..., description="签到方式")
    face_verified: bool = Field(default=False, description="人脸识别是否通过")
    notes: Optional[str] = Field(None, description="备注")

class CheckinCreate(CheckinBase):
    pass

class CheckinResponse(BaseModel):
    id: int
    user_id: int
    booking_id: int
    class_id: int
    checkin_method: CheckinMethod
    checkin_time: datetime
    face_verified: bool
    notes: Optional[str]

    class Config:
        from_attributes = True
        use_enum_values = True

class CoachScheduleBase(BaseModel):
    coach_id: int = Field(..., gt=0, description="教练ID")
    schedule_date: date = Field(..., description="日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    is_available: bool = Field(default=True, description="是否可预约")

class CoachScheduleCreate(CoachScheduleBase):
    pass

class CoachScheduleUpdate(BaseModel):
    is_available: Optional[bool] = None

class CoachScheduleResponse(BaseModel):
    id: int
    coach_id: int
    schedule_date: date
    start_time: time
    end_time: time
    is_available: bool
    is_booked: bool
    created_at: datetime
    updated_at: datetime
    coach: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class PrivateBookingBase(BaseModel):
    coach_id: int = Field(..., gt=0, description="教练ID")
    schedule_id: int = Field(..., gt=0, description="教练时段ID")
    card_id: Optional[int] = Field(None, gt=0, description="使用的会员卡ID")
    class_name: str = Field(..., min_length=2, max_length=100, description="课程名称")
    class_description: Optional[str] = Field(None, description="课程描述")
    location: Optional[str] = Field(None, max_length=100, description="地点")
    member_notes: Optional[str] = Field(None, description="会员备注")

class PrivateBookingCreate(PrivateBookingBase):
    pass

class PrivateBookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    coach_notes: Optional[str] = None
    cancel_reason: Optional[str] = None

class PrivateBookingResponse(BaseModel):
    id: int
    member_id: int
    coach_id: int
    schedule_id: int
    card_id: Optional[int]
    status: BookingStatus
    class_name: str
    class_description: Optional[str]
    location: Optional[str]
    member_notes: Optional[str]
    coach_notes: Optional[str]
    cancel_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    member: Optional[UserResponse] = None
    coach: Optional[UserResponse] = None
    schedule: Optional[CoachScheduleResponse] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class QRCodeCheckin(BaseModel):
    qr_code: str = Field(..., description="二维码内容")
    booking_id: int = Field(..., gt=0, description="预约ID")

class FaceCheckin(BaseModel):
    booking_id: int = Field(..., gt=0, description="预约ID")
    face_image: str = Field(..., description="人脸图像数据（base64）")

class CancelLimitResponse(BaseModel):
    can_cancel: bool
    remaining_cancels: int
    message: str

class BookingListResponse(BaseModel):
    total: int
    items: List[BookingResponse]

class ClassListResponse(BaseModel):
    total: int
    items: List[ClassResponse]

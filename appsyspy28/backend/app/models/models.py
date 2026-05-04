from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Time, Boolean, 
    ForeignKey, Text, Numeric, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    MEMBER = "member"
    COACH = "coach"
    ADMIN = "admin"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class CheckinMethod(str, enum.Enum):
    QRCODE = "qrcode"
    FACE = "face"

class CardType(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    TIMES = "times"
    GROUP = "group"
    PRIVATE = "private"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    name = Column(String(100), nullable=False, comment="真实姓名")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    avatar = Column(String(255), nullable=True, comment="头像路径")
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, comment="用户角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    member_cards = relationship("MemberCard", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")
    coach_schedules = relationship("CoachSchedule", back_populates="coach", cascade="all, delete-orphan")
    private_bookings_as_coach = relationship(
        "PrivateBooking", 
        foreign_keys="PrivateBooking.coach_id",
        back_populates="coach"
    )
    private_bookings_as_member = relationship(
        "PrivateBooking", 
        foreign_keys="PrivateBooking.member_id",
        back_populates="member"
    )
    coach_classes = relationship("Class", back_populates="coach", cascade="all, delete-orphan")

class ClassCategory(Base):
    __tablename__ = "class_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="课程类别名称")
    description = Column(Text, nullable=True, comment="描述")
    icon = Column(String(255), nullable=True, comment="图标")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    classes = relationship("Class", back_populates="category")
    card_category_links = relationship("CardCategoryLink", back_populates="category")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="教室名称")
    capacity = Column(Integer, nullable=False, comment="容量")
    location = Column(String(100), nullable=True, comment="位置描述")
    qr_code = Column(String(255), nullable=True, comment="签到二维码内容")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    classes = relationship("Class", back_populates="room")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("class_categories.id"), nullable=False, comment="课程类别ID")
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="教练ID")
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, comment="教室ID")
    name = Column(String(100), nullable=False, comment="课程名称")
    description = Column(Text, nullable=True, comment="课程描述")
    class_date = Column(Date, nullable=False, comment="课程日期")
    start_time = Column(Time, nullable=False, comment="开始时间")
    end_time = Column(Time, nullable=False, comment="结束时间")
    capacity = Column(Integer, nullable=False, comment="课程容量")
    booked_count = Column(Integer, default=0, comment="已预约人数")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("ClassCategory", back_populates="classes")
    coach = relationship("User", back_populates="coach_classes")
    room = relationship("Room", back_populates="classes")
    bookings = relationship("Booking", back_populates="class_", cascade="all, delete-orphan")

class MemberCard(Base):
    __tablename__ = "member_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    card_type = Column(SQLEnum(CardType), nullable=False, comment="卡类型")
    card_name = Column(String(100), nullable=False, comment="卡名称")
    total_times = Column(Integer, nullable=True, comment="总次数（次卡）")
    used_times = Column(Integer, default=0, comment="已用次数")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="member_cards")
    card_category_links = relationship("CardCategoryLink", back_populates="card", cascade="all, delete-orphan")

class CardCategoryLink(Base):
    __tablename__ = "card_category_links"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("member_cards.id"), nullable=False, comment="会员卡ID")
    category_id = Column(Integer, ForeignKey("class_categories.id"), nullable=False, comment="课程类别ID")
    
    card = relationship("MemberCard", back_populates="card_category_links")
    category = relationship("ClassCategory", back_populates="card_category_links")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, comment="课程ID")
    card_id = Column(Integer, ForeignKey("member_cards.id"), nullable=True, comment="使用的会员卡ID")
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CONFIRMED, comment="预约状态")
    cancel_reason = Column(Text, nullable=True, comment="取消原因")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="bookings")
    class_ = relationship("Class", back_populates="bookings")
    checkin = relationship("Checkin", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class Checkin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, comment="预约ID")
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, comment="课程ID")
    checkin_method = Column(SQLEnum(CheckinMethod), nullable=False, comment="签到方式")
    checkin_time = Column(DateTime, default=datetime.utcnow, comment="签到时间")
    face_verified = Column(Boolean, default=False, comment="人脸识别是否通过")
    notes = Column(Text, nullable=True, comment="备注")
    
    user = relationship("User", back_populates="checkins")
    booking = relationship("Booking", back_populates="checkin")

class CoachSchedule(Base):
    __tablename__ = "coach_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="教练ID")
    schedule_date = Column(Date, nullable=False, comment="日期")
    start_time = Column(Time, nullable=False, comment="开始时间")
    end_time = Column(Time, nullable=False, comment="结束时间")
    is_available = Column(Boolean, default=True, comment="是否可预约")
    is_booked = Column(Boolean, default=False, comment="是否已被预约")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    coach = relationship("User", back_populates="coach_schedules")
    private_booking = relationship("PrivateBooking", back_populates="schedule", uselist=False)

class PrivateBooking(Base):
    __tablename__ = "private_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="会员ID")
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="教练ID")
    schedule_id = Column(Integer, ForeignKey("coach_schedules.id"), nullable=False, comment="教练时段ID")
    card_id = Column(Integer, ForeignKey("member_cards.id"), nullable=True, comment="使用的会员卡ID")
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, comment="预约状态")
    class_name = Column(String(100), nullable=False, comment="课程名称")
    class_description = Column(Text, nullable=True, comment="课程描述")
    location = Column(String(100), nullable=True, comment="地点")
    member_notes = Column(Text, nullable=True, comment="会员备注")
    coach_notes = Column(Text, nullable=True, comment="教练备注")
    cancel_reason = Column(Text, nullable=True, comment="取消原因")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    member = relationship("User", foreign_keys=[member_id], back_populates="private_bookings_as_member")
    coach = relationship("User", foreign_keys=[coach_id], back_populates="private_bookings_as_coach")
    schedule = relationship("CoachSchedule", back_populates="private_booking")
    checkin = relationship("PrivateCheckin", back_populates="private_booking", uselist=False, cascade="all, delete-orphan")

class PrivateCheckin(Base):
    __tablename__ = "private_checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    private_booking_id = Column(Integer, ForeignKey("private_bookings.id"), nullable=False, comment="私教预约ID")
    checkin_method = Column(SQLEnum(CheckinMethod), nullable=False, comment="签到方式")
    checkin_time = Column(DateTime, default=datetime.utcnow, comment="签到时间")
    face_verified = Column(Boolean, default=False, comment="人脸识别是否通过")
    
    private_booking = relationship("PrivateBooking", back_populates="checkin")

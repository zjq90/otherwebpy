from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ActivityStatus(str, enum.Enum):
    """
    活动状态枚举
    """
    DRAFT = "draft"
    PUBLISHED = "published"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityType(str, enum.Enum):
    """
    活动类型枚举
    """
    FESTIVAL = "festival"
    NEIGHBOR_INTERACTION = "neighbor_interaction"
    SPORTS = "sports"
    CULTURAL = "cultural"
    CHARITY = "charity"
    OTHER = "other"


class Activity(Base):
    """
    活动模型
    存储社区发布的各类活动信息
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, comment="活动ID")
    title = Column(String(200), nullable=False, comment="活动标题")
    description = Column(Text, comment="活动详细描述")
    activity_type = Column(String(50), default=ActivityType.OTHER.value, comment="活动类型")
    status = Column(String(20), default=ActivityStatus.DRAFT.value, comment="活动状态")
    
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="活动发布人ID")
    
    start_time = Column(DateTime, nullable=False, comment="活动开始时间")
    end_time = Column(DateTime, nullable=False, comment="活动结束时间")
    registration_deadline = Column(DateTime, nullable=True, comment="报名截止时间")
    
    location = Column(String(200), comment="活动地点")
    max_participants = Column(Integer, nullable=True, comment="最大参与人数")
    current_participants = Column(Integer, default=0, comment="当前报名人数")
    
    image_url = Column(String(500), comment="活动图片URL")
    contact_name = Column(String(50), comment="联系人姓名")
    contact_phone = Column(String(20), comment="联系电话")
    
    is_featured = Column(Boolean, default=False, comment="是否为推荐活动")
    views_count = Column(Integer, default=0, comment="浏览次数")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    organizer = relationship("User", backref="organized_activities")

    def __repr__(self):
        return f"<Activity(id={self.id}, title={self.title}, status={self.status})>"


class ActivityRegistration(Base):
    """
    活动报名模型
    存储业主的活动报名信息
    """
    __tablename__ = "activity_registrations"

    id = Column(Integer, primary_key=True, index=True, comment="报名ID")
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, comment="活动ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="报名用户ID")
    
    participant_name = Column(String(50), nullable=False, comment="参与者姓名")
    participant_phone = Column(String(20), nullable=False, comment="联系电话")
    participant_count = Column(Integer, default=1, comment="参与人数")
    room_number = Column(String(20), comment="房间号")
    
    remarks = Column(String(500), comment="备注信息")
    is_attended = Column(Boolean, default=False, comment="是否实际参加")
    
    created_at = Column(DateTime, default=datetime.now, comment="报名时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    activity = relationship("Activity", backref="registrations")
    user = relationship("User", backref="activity_registrations")

    def __repr__(self):
        return f"<ActivityRegistration(id={self.id}, activity_id={self.activity_id}, user_id={self.user_id})>"

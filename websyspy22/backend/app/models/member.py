"""
会员相关数据模型
包含会员基本信息和状态变更日志
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class MemberStatus(str, enum.Enum):
    """会员状态枚举"""
    ACTIVE = "active"        # 正常
    FROZEN = "frozen"        # 冻结
    CANCELLED = "cancelled"  # 已注销


class RegistrationChannel(str, enum.Enum):
    """注册渠道枚举"""
    ONLINE = "online"      # 线上（官网）
    OFFLINE = "offline"    # 线下（前台录入）


class VerificationMethod(str, enum.Enum):
    """实名认证方式枚举"""
    PHONE = "phone"           # 手机号验证
    FACE_RECOGNITION = "face" # 人脸识别


class Member(Base):
    """
    会员表
    存储会员的基本信息
    """
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, comment="会员ID")
    name = Column(String(100), nullable=False, comment="姓名")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    id_card = Column(String(18), unique=True, index=True, nullable=True, comment="身份证号")
    email = Column(String(100), nullable=True, comment="邮箱")
    gender = Column(String(10), nullable=True, comment="性别")
    birth_date = Column(Date, nullable=True, comment="出生日期")
    address = Column(String(500), nullable=True, comment="联系地址")
    
    # 健康状况
    health_status = Column(String(1000), nullable=True, comment="健康状况描述")
    allergies = Column(String(500), nullable=True, comment="过敏史")
    emergency_contact = Column(String(100), nullable=True, comment="紧急联系人")
    emergency_phone = Column(String(20), nullable=True, comment="紧急联系电话")
    
    # 注册相关
    registration_channel = Column(SQLEnum(RegistrationChannel), nullable=False, comment="注册渠道")
    verification_method = Column(SQLEnum(VerificationMethod), nullable=True, comment="实名认证方式")
    is_verified = Column(Integer, default=0, comment="是否已实名认证: 0-否, 1-是")
    
    # 等级相关
    current_level = Column(String(20), default="bronze", comment="当前会员等级: bronze/silver/gold")
    total_consumption = Column(Integer, default=0, comment="累计消费金额（分）")
    total_visits = Column(Integer, default=0, comment="累计到店次数")
    
    # 状态相关
    status = Column(SQLEnum(MemberStatus), default=MemberStatus.ACTIVE, comment="账户状态")
    status_reason = Column(String(500), nullable=True, comment="状态变更原因")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    physical_tests = relationship("PhysicalTest", back_populates="member")
    fitness_goals = relationship("FitnessGoal", back_populates="member")
    consumption_records = relationship("ConsumptionRecord", back_populates="member")
    course_participations = relationship("CourseParticipation", back_populates="member")
    status_change_logs = relationship("StatusChangeLog", back_populates="member")
    sms_notifications = relationship("SmsNotification", back_populates="member")


class StatusChangeLog(Base):
    """
    会员状态变更日志表
    记录会员账户状态的变更历史
    """
    __tablename__ = "status_change_logs"

    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    old_status = Column(SQLEnum(MemberStatus), nullable=True, comment="变更前状态")
    new_status = Column(SQLEnum(MemberStatus), nullable=False, comment="变更后状态")
    reason = Column(String(500), nullable=True, comment="变更原因")
    operator = Column(String(100), nullable=True, comment="操作人")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="变更时间")
    
    # 关系
    member = relationship("Member", back_populates="status_change_logs")

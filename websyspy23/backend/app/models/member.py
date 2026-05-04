"""
会员管理数据模型
包含会员(Member)、会员卡(MemberCard)和课程预约(CourseBooking)三个核心模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date

from ..database import Base


class Member(Base):
    """
    会员模型
    定义会员基本信息
    """
    
    __tablename__ = "members"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="会员ID")
    
    # 会员编号（系统自动生成）
    member_no = Column(String(50), unique=True, nullable=False, index=True, comment="会员编号")
    
    # 姓名
    name = Column(String(100), nullable=False, index=True, comment="姓名")
    
    # 性别：男/女
    gender = Column(String(10), comment="性别")
    
    # 手机号码
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号码")
    
    # 邮箱
    email = Column(String(100), comment="邮箱")
    
    # 出生日期
    birthday = Column(Date, comment="出生日期")
    
    # 身份证号
    id_card = Column(String(50), comment="身份证号")
    
    # 头像URL
    avatar_url = Column(String(500), comment="头像URL")
    
    # 紧急联系人
    emergency_contact = Column(String(100), comment="紧急联系人")
    
    # 紧急联系电话
    emergency_phone = Column(String(20), comment="紧急联系电话")
    
    # 健康状况
    health_status = Column(Text, comment="健康状况")
    
    # 备注
    remarks = Column(Text, comment="备注")
    
    # 会员状态：active(活跃), inactive(非活跃), frozen(冻结)
    status = Column(String(20), default="active", index=True, comment="会员状态")
    
    # 注册时间
    register_time = Column(DateTime, default=datetime.now, comment="注册时间")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：一个会员对应多个会员卡
    member_cards = relationship("MemberCard", back_populates="member")
    
    # 关系：一个会员对应多个课程预约
    bookings = relationship("CourseBooking", back_populates="member")
    
    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', member_no='{self.member_no}')>"


class MemberCard(Base):
    """
    会员卡模型
    定义会员持有的卡信息，关联会员和卡项
    """
    
    __tablename__ = "member_cards"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="会员卡ID")
    
    # 外键：关联会员
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    
    # 外键：关联卡项
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, comment="卡项ID")
    
    # 会员卡编号
    card_no = Column(String(50), unique=True, nullable=False, index=True, comment="会员卡编号")
    
    # 开始日期
    start_date = Column(Date, nullable=False, comment="开始日期")
    
    # 结束日期
    end_date = Column(Date, comment="结束日期")
    
    # 总次数（次卡/私教包使用）
    total_count = Column(Integer, comment="总次数")
    
    # 剩余次数
    remaining_count = Column(Integer, comment="剩余次数")
    
    # 储值余额
    balance = Column(Float, default=0, comment="储值余额")
    
    # 赠送余额
    bonus_balance = Column(Float, default=0, comment="赠送余额")
    
    # 购买价格
    purchase_price = Column(Float, nullable=False, comment="购买价格")
    
    # 会员卡状态：active(有效), expired(已过期), used_up(已用完), frozen(冻结)
    status = Column(String(20), default="active", index=True, comment="会员卡状态")
    
    # 备注
    remarks = Column(Text, comment="备注")
    
    # 激活时间
    activate_time = Column(DateTime, default=datetime.now, comment="激活时间")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：多个会员卡对应一个会员
    member = relationship("Member", back_populates="member_cards")
    
    # 关系：多个会员卡对应一个卡项
    card = relationship("Card", back_populates="member_cards")
    
    def __repr__(self):
        return f"<MemberCard(id={self.id}, member_id={self.member_id}, card_id={self.card_id})>"


class CourseBooking(Base):
    """
    课程预约模型
    定义会员预约的课程信息
    """
    
    __tablename__ = "course_bookings"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="预约ID")
    
    # 外键：关联会员
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    
    # 外键：关联课程排期
    schedule_id = Column(Integer, ForeignKey("course_schedules.id"), nullable=False, comment="排期ID")
    
    # 预约编号
    booking_no = Column(String(50), unique=True, nullable=False, index=True, comment="预约编号")
    
    # 预约状态：booked(已预约), checked_in(已签到), cancelled(已取消), no_show(未签到)
    status = Column(String(20), default="booked", index=True, comment="预约状态")
    
    # 签到时间
    check_in_time = Column(DateTime, comment="签到时间")
    
    # 取消时间
    cancel_time = Column(DateTime, comment="取消时间")
    
    # 取消原因
    cancel_reason = Column(Text, comment="取消原因")
    
    # 备注
    remarks = Column(Text, comment="备注")
    
    # 预约时间
    booking_time = Column(DateTime, default=datetime.now, comment="预约时间")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：多个预约对应一个会员
    member = relationship("Member", back_populates="bookings")
    
    # 关系：多个预约对应一个课程排期
    schedule = relationship("CourseSchedule", back_populates="bookings")
    
    def __repr__(self):
        return f"<CourseBooking(id={self.id}, member_id={self.member_id}, schedule_id={self.schedule_id})>"

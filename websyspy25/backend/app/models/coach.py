from sqlalchemy import Column, Integer, String, DateTime, Float, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Coach(Base):
    """
    教练信息表
    存储教练的基本信息、擅长领域、薪资比例等
    """
    __tablename__ = "coaches"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 教练姓名
    name = Column(String(50), nullable=False, index=True)
    
    # 性别: 男/女
    gender = Column(String(10), default="男")
    
    # 手机号码
    phone = Column(String(20), unique=True, index=True)
    
    # 身份证号
    id_card = Column(String(18), unique=True, nullable=True)
    
    # 邮箱
    email = Column(String(100), nullable=True)
    
    # 住址
    address = Column(String(200), nullable=True)
    
    # 入职日期
    hire_date = Column(Date, default=datetime.now().date)
    
    # 教练级别: 初级/中级/高级/金牌
    level = Column(String(20), default="初级")
    
    # 擅长领域: 多个领域用逗号分隔，如"减脂,增肌,康复"
    expertise = Column(String(200), nullable=True)
    
    # 个人简介
    bio = Column(Text, nullable=True)
    
    # 课时费率(每小时)
    hourly_rate = Column(Float, default=100.0)
    
    # 业绩提成比例(百分比，如30表示30%)
    commission_rate = Column(Float, default=30.0)
    
    # 状态: 在职/离职/休假
    status = Column(String(20), default="在职")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    # 与排班表的一对多关系
    schedules = relationship("CoachSchedule", back_populates="coach", cascade="all, delete-orphan")
    
    # 与课时记录的一对多关系
    lesson_records = relationship("LessonRecord", back_populates="coach")
    
    # 与业绩记录的一对多关系
    performance_records = relationship("PerformanceRecord", back_populates="coach")


class CoachSchedule(Base):
    """
    教练排班表
    记录教练每周的排班时间，支持灵活的时间安排
    """
    __tablename__ = "coach_schedules"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的教练ID
    coach_id = Column(Integer, nullable=False, index=True)
    
    # 星期几: 1-7 表示周一到周日
    day_of_week = Column(Integer, nullable=False)
    
    # 开始时间(格式: HH:MM)
    start_time = Column(String(10), nullable=False)
    
    # 结束时间(格式: HH:MM)
    end_time = Column(String(10), nullable=False)
    
    # 状态: 可用/已预约/休息
    status = Column(String(20), default="可用")
    
    # 备注
    note = Column(String(200), nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    coach = relationship("Coach", back_populates="schedules")

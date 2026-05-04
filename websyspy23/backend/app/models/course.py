"""
课程管理数据模型
包含课程类型(CourseType)、课程(Course)和课程排期(CourseSchedule)三个核心模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class CourseType(Base):
    """
    课程类型模型
    定义系统支持的课程类型：团操课、私教课、定制课程等
    """
    
    __tablename__ = "course_types"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="课程类型ID")
    
    # 课程类型名称：团操课、私教课、定制课程
    name = Column(String(50), unique=True, nullable=False, index=True, comment="课程类型名称")
    
    # 课程类型代码：group, private, custom
    code = Column(String(50), unique=True, nullable=False, index=True, comment="课程类型代码")
    
    # 课程类型描述
    description = Column(Text, comment="课程类型描述")
    
    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：一个课程类型对应多个课程
    courses = relationship("Course", back_populates="course_type")
    
    def __repr__(self):
        return f"<CourseType(id={self.id}, name='{self.name}')>"


class Course(Base):
    """
    课程模型
    定义具体的课程信息
    """
    
    __tablename__ = "courses"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="课程ID")
    
    # 课程名称
    name = Column(String(100), nullable=False, index=True, comment="课程名称")
    
    # 外键：关联课程类型
    course_type_id = Column(Integer, ForeignKey("course_types.id"), nullable=False, comment="课程类型ID")
    
    # 课程时长（分钟）
    duration = Column(Integer, nullable=False, default=60, comment="课程时长(分钟)")
    
    # 最大容量
    max_capacity = Column(Integer, default=20, comment="最大容量")
    
    # 课程描述
    description = Column(Text, comment="课程描述")
    
    # 课程难度等级（1-5）
    difficulty_level = Column(Integer, default=3, comment="难度等级(1-5)")
    
    # 适合人群
    suitable_for = Column(String(200), comment="适合人群")
    
    # 注意事项
    precautions = Column(Text, comment="注意事项")
    
    # 课程图片URL
    image_url = Column(String(500), comment="课程图片URL")
    
    # 教练/老师名称
    instructor = Column(String(100), comment="教练/老师名称")
    
    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：多个课程对应一个课程类型
    course_type = relationship("CourseType", back_populates="courses")
    
    # 关系：一个课程对应多个课程排期
    schedules = relationship("CourseSchedule", back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}')>"


class CourseSchedule(Base):
    """
    课程排期模型
    定义具体的课程排班信息，包含时间、场地、教练等
    """
    
    __tablename__ = "course_schedules"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="排期ID")
    
    # 外键：关联课程
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, comment="课程ID")
    
    # 外键：关联场地
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, comment="场地ID")
    
    # 课程日期
    schedule_date = Column(Date, nullable=False, index=True, comment="课程日期")
    
    # 开始时间
    start_time = Column(Time, nullable=False, comment="开始时间")
    
    # 结束时间
    end_time = Column(Time, nullable=False, comment="结束时间")
    
    # 教练名称
    instructor = Column(String(100), comment="教练名称")
    
    # 已预约人数
    booked_count = Column(Integer, default=0, comment="已预约人数")
    
    # 最大容量（可以覆盖课程的默认容量）
    max_capacity = Column(Integer, comment="最大容量")
    
    # 排期状态：scheduled(已排期), completed(已完成), cancelled(已取消)
    status = Column(String(20), default="scheduled", index=True, comment="排期状态")
    
    # 备注
    remarks = Column(Text, comment="备注")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：多个排期对应一个课程
    course = relationship("Course", back_populates="schedules")
    
    # 关系：多个排期对应一个场地
    venue = relationship("Venue", back_populates="schedules")
    
    # 关系：一个排期对应多个课程预约
    bookings = relationship("CourseBooking", back_populates="schedule")
    
    def __repr__(self):
        return f"<CourseSchedule(id={self.id}, course_id={self.course_id}, schedule_date={self.schedule_date})>"

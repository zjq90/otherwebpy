from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Member(Base):
    """
    会员信息表
    存储购买私教课的会员基本信息
    """
    __tablename__ = "members"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 会员姓名
    name = Column(String(50), nullable=False, index=True)
    
    # 性别: 男/女
    gender = Column(String(10), default="男")
    
    # 手机号码
    phone = Column(String(20), unique=True, index=True)
    
    # 身份证号
    id_card = Column(String(18), unique=True, nullable=True)
    
    # 邮箱
    email = Column(String(100), nullable=True)
    
    # 年龄
    age = Column(Integer, nullable=True)
    
    # 会员等级: 普通/银卡/金卡/钻石
    level = Column(String(20), default="普通")
    
    # 健身目标: 减脂/增肌/康复/塑形等
    fitness_goal = Column(String(100), nullable=True)
    
    # 健康状况/禁忌症
    health_condition = Column(Text, nullable=True)
    
    # 状态: 正常/冻结/过期
    status = Column(String(20), default="正常")
    
    # 注册日期
    register_date = Column(Date, default=datetime.now().date)
    
    # 备注
    note = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    # 与课程包购买记录的一对多关系
    course_packages = relationship("CoursePackage", back_populates="member")
    
    # 与课时记录的一对多关系
    lesson_records = relationship("LessonRecord", back_populates="member")
    
    # 与冻结记录的一对多关系
    freeze_records = relationship("FreezeRecord", back_populates="member")


class CoursePackage(Base):
    """
    课程包购买记录表
    记录会员购买的私教课程包信息
    """
    __tablename__ = "course_packages"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 包编号，自动生成
    package_no = Column(String(50), unique=True, index=True, nullable=False)
    
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    
    # 关联的教练ID（可以为空，预约时确定）
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True, index=True)
    
    # 课程包名称
    name = Column(String(100), nullable=False)
    
    # 课程类型: 常规课/特色课/拉伸课等
    course_type = Column(String(50), default="常规课")
    
    # 购买总课时
    total_lessons = Column(Integer, default=0)
    
    # 已使用课时
    used_lessons = Column(Integer, default=0)
    
    # 剩余课时
    remaining_lessons = Column(Integer, default=0)
    
    # 赠送课时
    bonus_lessons = Column(Integer, default=0)
    
    # 冻结课时（用于冻结功能）
    frozen_lessons = Column(Integer, default=0)
    
    # 课程单价
    unit_price = Column(Float, default=0.0)
    
    # 总金额
    total_amount = Column(Float, default=0.0)
    
    # 优惠金额
    discount_amount = Column(Float, default=0.0)
    
    # 实付金额
    paid_amount = Column(Float, default=0.0)
    
    # 购买日期
    purchase_date = Column(Date, default=datetime.now().date)
    
    # 开始生效日期
    start_date = Column(Date, default=datetime.now().date)
    
    # 有效期截止日期
    expire_date = Column(Date, nullable=True)
    
    # 状态: 有效/已用完/已过期/已冻结
    status = Column(String(20), default="有效")
    
    # 支付方式: 现金/微信/支付宝/银行卡
    payment_method = Column(String(20), default="微信")
    
    # 备注
    note = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    member = relationship("Member", back_populates="course_packages")
    
    # 与课时记录的一对多关系
    lesson_records = relationship("LessonRecord", back_populates="course_package")
    
    # 与冻结记录的一对多关系
    freeze_records = relationship("FreezeRecord", back_populates="course_package")

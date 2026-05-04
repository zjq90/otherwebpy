"""
档案管理数据模型
包含体测数据、运动目标、消费记录、课程参与等
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.database import Base


class PhysicalTest(Base):
    """
    体测数据表
    记录会员的身体健康测试数据
    """
    __tablename__ = "physical_tests"

    id = Column(Integer, primary_key=True, index=True, comment="体测记录ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    
    # 基本身体指标
    test_date = Column(Date, nullable=False, comment="体测日期")
    height = Column(Numeric(5, 2), nullable=True, comment="身高（cm）")
    weight = Column(Numeric(5, 2), nullable=True, comment="体重（kg）")
    bmi = Column(Numeric(4, 2), nullable=True, comment="BMI指数")
    
    # 身体成分
    body_fat = Column(Numeric(4, 2), nullable=True, comment="体脂率（%）")
    muscle_mass = Column(Numeric(5, 2), nullable=True, comment="肌肉量（kg）")
    bone_mass = Column(Numeric(5, 2), nullable=True, comment="骨量（kg）")
    body_water = Column(Numeric(5, 2), nullable=True, comment="体内水分（kg）")
    
    # 心肺功能
    resting_heart_rate = Column(Integer, nullable=True, comment="静息心率（次/分）")
    blood_pressure_systolic = Column(Integer, nullable=True, comment="收缩压（mmHg）")
    blood_pressure_diastolic = Column(Integer, nullable=True, comment="舒张压（mmHg）")
    vital_capacity = Column(Numeric(5, 2), nullable=True, comment="肺活量（L）")
    
    # 力量与柔韧
    grip_strength = Column(Numeric(4, 2), nullable=True, comment="握力（kg）")
    sit_and_reach = Column(Numeric(4, 1), nullable=True, comment="坐位体前屈（cm）")
    
    # 测试信息
    tester = Column(String(100), nullable=True, comment="测试员")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    member = relationship("Member", back_populates="physical_tests")


class FitnessGoal(Base):
    """
    运动目标表
    记录会员的健身目标
    """
    __tablename__ = "fitness_goals"

    id = Column(Integer, primary_key=True, index=True, comment="目标ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    
    # 目标信息
    goal_type = Column(String(50), nullable=False, comment="目标类型: 减肥/增肌/塑形/康复/其他")
    target_value = Column(Numeric(10, 2), nullable=True, comment="目标值")
    current_value = Column(Numeric(10, 2), nullable=True, comment="当前值")
    unit = Column(String(20), nullable=True, comment="单位")
    
    # 时间规划
    start_date = Column(Date, nullable=False, comment="开始日期")
    target_date = Column(Date, nullable=True, comment="目标完成日期")
    actual_completion_date = Column(Date, nullable=True, comment="实际完成日期")
    
    # 状态
    status = Column(String(20), default="active", comment="目标状态: active/achieved/cancelled")
    progress = Column(Integer, default=0, comment="进度百分比")
    
    # 备注
    description = Column(Text, nullable=True, comment="目标描述")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    member = relationship("Member", back_populates="fitness_goals")


class ConsumptionRecord(Base):
    """
    消费记录表
    记录会员的消费历史
    """
    __tablename__ = "consumption_records"

    id = Column(Integer, primary_key=True, index=True, comment="消费记录ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    
    # 消费信息
    consumption_type = Column(String(50), nullable=False, comment="消费类型: 办卡/续卡/私教/团课/商品/其他")
    item_name = Column(String(200), nullable=False, comment="消费项目名称")
    amount = Column(Integer, nullable=False, comment="消费金额（分）")
    discount_amount = Column(Integer, default=0, comment="优惠金额（分）")
    actual_amount = Column(Integer, nullable=False, comment="实付金额（分）")
    
    # 支付信息
    payment_method = Column(String(50), nullable=True, comment="支付方式: 现金/微信/支付宝/刷卡/其他")
    transaction_no = Column(String(100), nullable=True, comment="交易流水号")
    
    # 操作员
    operator = Column(String(100), nullable=True, comment="操作人")
    
    # 备注
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    consumption_time = Column(DateTime, default=datetime.now, comment="消费时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系
    member = relationship("Member", back_populates="consumption_records")


class CourseParticipation(Base):
    """
    课程参与记录表
    记录会员参与的课程情况
    """
    __tablename__ = "course_participations"

    id = Column(Integer, primary_key=True, index=True, comment="参与记录ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    
    # 课程信息
    course_name = Column(String(200), nullable=False, comment="课程名称")
    course_type = Column(String(50), nullable=True, comment="课程类型: 私教/团课/公开课")
    coach_name = Column(String(100), nullable=True, comment="教练姓名")
    
    # 参与信息
    participation_date = Column(Date, nullable=False, comment="参与日期")
    start_time = Column(String(20), nullable=True, comment="开始时间")
    end_time = Column(String(20), nullable=True, comment="结束时间")
    duration_minutes = Column(Integer, nullable=True, comment="时长（分钟）")
    
    # 状态
    status = Column(String(20), default="attended", comment="参与状态: attended/absent/cancelled")
    
    # 评价
    rating = Column(Integer, nullable=True, comment="评分（1-5星）")
    feedback = Column(Text, nullable=True, comment="反馈意见")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    member = relationship("Member", back_populates="course_participations")

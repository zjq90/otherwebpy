from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class LessonRecord(Base):
    """
    课时消耗记录表
    记录每一次私教课的消耗情况，包括上课、补课等
    """
    __tablename__ = "lesson_records"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 记录编号，自动生成
    record_no = Column(String(50), unique=True, index=True, nullable=False)
    
    # 关联的课程包ID
    package_id = Column(Integer, ForeignKey("course_packages.id"), nullable=False, index=True)
    
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    
    # 关联的教练ID
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, index=True)
    
    # 课程类型: 常规课/补课/赠送课
    lesson_type = Column(String(20), default="常规课")
    
    # 消耗课时数（通常为1，但可以是小数如1.5小时）
    hours_used = Column(Float, default=1.0)
    
    # 上课日期
    lesson_date = Column(Date, default=datetime.now().date)
    
    # 开始时间(格式: HH:MM)
    start_time = Column(String(10), nullable=True)
    
    # 结束时间(格式: HH:MM)
    end_time = Column(String(10), nullable=True)
    
    # 课程内容
    lesson_content = Column(Text, nullable=True)
    
    # 会员反馈/评价（1-5星）
    member_rating = Column(Integer, nullable=True)
    
    # 会员反馈文字
    member_feedback = Column(Text, nullable=True)
    
    # 教练备注
    coach_note = Column(Text, nullable=True)
    
    # 课程状态: 已预约/已完成/已取消/已缺席
    status = Column(String(20), default="已预约")
    
    # 是否是补课
    is_makeup = Column(Boolean, default=False)
    
    # 关联的补课记录ID（如果是补课）
    makeup_id = Column(Integer, ForeignKey("makeup_lessons.id"), nullable=True)
    
    # 教练应得报酬（根据课时数和教练费率计算）
    coach_commission = Column(Float, default=0.0)
    
    # 本次课收入贡献
    revenue_contribution = Column(Float, default=0.0)
    
    # 核销人员ID（如果有系统操作人员）
    operator_id = Column(Integer, nullable=True)
    
    # 备注
    note = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    course_package = relationship("CoursePackage", back_populates="lesson_records")
    member = relationship("Member", back_populates="lesson_records")
    coach = relationship("Coach", back_populates="lesson_records")


class MakeupLesson(Base):
    """
    补课记录表
    记录会员因特殊原因需要补课的申请和使用情况
    """
    __tablename__ = "makeup_lessons"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 补课编号
    makeup_no = Column(String(50), unique=True, index=True, nullable=False)
    
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    
    # 关联的课程包ID
    package_id = Column(Integer, ForeignKey("course_packages.id"), nullable=False, index=True)
    
    # 关联的原课程记录ID（哪次课需要补）
    original_lesson_id = Column(Integer, ForeignKey("lesson_records.id"), nullable=True)
    
    # 补课原因: 会员请假/教练有事/其他
    reason = Column(String(100), nullable=False)
    
    # 原因详情
    reason_detail = Column(Text, nullable=True)
    
    # 申请补课数量
    requested_count = Column(Integer, default=1)
    
    # 已使用补课数量
    used_count = Column(Integer, default=0)
    
    # 剩余补课数量
    remaining_count = Column(Integer, default=1)
    
    # 申请日期
    apply_date = Column(Date, default=datetime.now().date)
    
    # 有效期截止日期
    expire_date = Column(Date, nullable=True)
    
    # 状态: 待审批/已批准/已拒绝/已用完/已过期
    status = Column(String(20), default="待审批")
    
    # 审批意见
    approval_note = Column(Text, nullable=True)
    
    # 审批人ID
    approver_id = Column(Integer, nullable=True)
    
    # 备注
    note = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class FreezeRecord(Base):
    """
    冻结记录表
    记录会员课程包的冻结/解冻操作
    """
    __tablename__ = "freeze_records"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 冻结编号
    freeze_no = Column(String(50), unique=True, index=True, nullable=False)
    
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    
    # 关联的课程包ID
    package_id = Column(Integer, ForeignKey("course_packages.id"), nullable=False, index=True)
    
    # 操作类型: 冻结/解冻
    operation_type = Column(String(20), nullable=False)
    
    # 冻结原因
    reason = Column(String(200), nullable=True)
    
    # 冻结开始日期
    freeze_start_date = Column(Date, default=datetime.now().date)
    
    # 计划冻结结束日期
    planned_end_date = Column(Date, nullable=True)
    
    # 实际解冻日期
    actual_end_date = Column(Date, nullable=True)
    
    # 冻结课时数量
    frozen_lessons = Column(Integer, default=0)
    
    # 状态: 冻结中/已解冻
    status = Column(String(20), default="冻结中")
    
    # 操作人ID
    operator_id = Column(Integer, nullable=True)
    
    # 备注
    note = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    member = relationship("Member", back_populates="freeze_records")
    course_package = relationship("CoursePackage", back_populates="freeze_records")

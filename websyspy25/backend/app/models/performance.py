from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class PerformanceRecord(Base):
    """
    业绩追踪表
    按时间段统计教练的授课数量、会员反馈和收入贡献
    可以按月或季度进行统计
    """
    __tablename__ = "performance_records"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的教练ID
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, index=True)
    
    # 统计类型: 月度/季度
    period_type = Column(String(20), default="月度")
    
    # 年份
    year = Column(Integer, nullable=False)
    
    # 月份(1-12)，季度统计时可为空
    month = Column(Integer, nullable=True)
    
    # 季度(1-4)，月度统计时可为空
    quarter = Column(Integer, nullable=True)
    
    # 该周期内总授课课时
    total_lessons = Column(Integer, default=0)
    
    # 该周期内常规课数量
    regular_lessons = Column(Integer, default=0)
    
    # 该周期内补课数量
    makeup_lessons = Column(Integer, default=0)
    
    # 该周期内总授课小时数
    total_hours = Column(Float, default=0.0)
    
    # 该周期内获得的平均评分(1-5星)
    avg_rating = Column(Float, default=0.0)
    
    # 该周期内有评分的课程数
    rated_lessons = Column(Integer, default=0)
    
    # 该周期内5星评价数量
    five_star_count = Column(Integer, default=0)
    
    # 该周期内4星评价数量
    four_star_count = Column(Integer, default=0)
    
    # 该周期内3星评价数量
    three_star_count = Column(Integer, default=0)
    
    # 该周期内收入贡献总额
    total_revenue = Column(Float, default=0.0)
    
    # 该周期内新会员数
    new_members_count = Column(Integer, default=0)
    
    # 该周期内续约会员数
    renewal_members_count = Column(Integer, default=0)
    
    # 该周期内教练提成总额
    total_commission = Column(Float, default=0.0)
    
    # 该周期内排名（在所有教练中的排名）
    rank = Column(Integer, nullable=True)
    
    # 备注
    note = Column(String(500), nullable=True)
    
    # 统计记录的创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 统计记录的更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    coach = relationship("Coach", back_populates="performance_records")


class MonthlySummary(Base):
    """
    月度汇总表
    更轻量级的月度统计，用于快速查询和报表展示
    """
    __tablename__ = "monthly_summaries"
    
    # 主键，自增ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的教练ID
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, index=True)
    
    # 年份
    year = Column(Integer, nullable=False)
    
    # 月份
    month = Column(Integer, nullable=False)
    
    # 总课时数
    lessons_count = Column(Integer, default=0)
    
    # 总小时数
    hours_count = Column(Float, default=0.0)
    
    # 总收入
    revenue = Column(Float, default=0.0)
    
    # 总提成
    commission = Column(Float, default=0.0)
    
    # 平均评分
    avg_score = Column(Float, default=0.0)
    
    # 状态: 未结算/已结算
    status = Column(String(20), default="未结算")
    
    # 结算日期
    settlement_date = Column(Date, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

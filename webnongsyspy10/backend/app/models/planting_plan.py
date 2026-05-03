"""
种植计划管理模型
定义种植计划表的结构，用于存储年度/季度种植计划信息
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from backend.app.database import Base


class PlanTypeEnum(enum.Enum):
    """
    计划类型枚举
    """
    ANNUAL = "年度计划"
    QUARTERLY = "季度计划"
    MONTHLY = "月度计划"


class PlanStatusEnum(enum.Enum):
    """
    计划状态枚举
    """
    DRAFT = "草稿"
    APPROVED = "已批准"
    IN_PROGRESS = "执行中"
    COMPLETED = "已完成"
    ADJUSTED = "已调整"
    CANCELLED = "已取消"


class PlantingPlan(Base):
    """
    种植计划表
    用于存储年度/季度种植计划的详细信息
    """
    
    __tablename__ = "planting_plans"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="种植计划ID")
    
    # 计划编号
    plan_code = Column(String(50), unique=True, nullable=False, index=True, comment="计划编号")
    
    # 计划名称
    plan_name = Column(String(200), nullable=False, comment="计划名称")
    
    # 计划类型
    plan_type = Column(SQLEnum(PlanTypeEnum), nullable=False, comment="计划类型：年度/季度/月度")
    
    # 年度
    year = Column(Integer, nullable=False, comment="计划年度")
    
    # 季度（可选，年度计划可为空）
    quarter = Column(Integer, nullable=True, comment="季度：1-4，年度计划可为空")
    
    # 月份（可选，季度计划可为空）
    month = Column(Integer, nullable=True, comment="月份：1-12，季度计划可为空")
    
    # 作物种类
    crop_type = Column(String(100), nullable=False, comment="作物种类")
    
    # 作物品种
    crop_variety = Column(String(100), nullable=True, comment="作物品种")
    
    # 种植面积（亩）
    planting_area = Column(Numeric(10, 2), nullable=False, comment="种植面积（亩）")
    
    # 播种时间
    sowing_date = Column(Date, nullable=False, comment="预计播种时间")
    
    # 预计收获时间
    expected_harvest_date = Column(Date, nullable=False, comment="预计收获时间")
    
    # 实际收获时间
    actual_harvest_date = Column(Date, nullable=True, comment="实际收获时间")
    
    # 目标产量（公斤/亩）
    target_yield_per_mu = Column(Numeric(10, 2), nullable=False, comment="目标产量（公斤/亩）")
    
    # 目标总产量（公斤）
    target_total_yield = Column(Numeric(12, 2), nullable=True, comment="目标总产量（公斤）")
    
    # 实际产量（公斤/亩）
    actual_yield_per_mu = Column(Numeric(10, 2), nullable=True, comment="实际产量（公斤/亩）")
    
    # 实际总产量（公斤）
    actual_total_yield = Column(Numeric(12, 2), nullable=True, comment="实际总产量（公斤）")
    
    # 种植地点/地块
    location = Column(String(200), nullable=True, comment="种植地点/地块")
    
    # 计划状态
    status = Column(SQLEnum(PlanStatusEnum), default=PlanStatusEnum.DRAFT, comment="计划状态")
    
    # 执行进度（百分比）
    progress = Column(Numeric(5, 2), default=0.00, comment="执行进度（百分比）")
    
    # 责任人
    responsible_person = Column(String(100), nullable=True, comment="责任人")
    
    # 备注说明
    remarks = Column(Text, nullable=True, comment="备注说明")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 创建人
    created_by = Column(String(100), nullable=True, comment="创建人")
    
    def calculate_target_total_yield(self):
        """
        计算目标总产量
        目标总产量 = 种植面积 × 目标亩产量
        """
        if self.planting_area and self.target_yield_per_mu:
            self.target_total_yield = self.planting_area * self.target_yield_per_mu
        return self.target_total_yield
    
    def calculate_actual_total_yield(self):
        """
        计算实际总产量
        实际总产量 = 种植面积 × 实际亩产量
        """
        if self.planting_area and self.actual_yield_per_mu:
            self.actual_total_yield = self.planting_area * self.actual_yield_per_mu
        return self.actual_total_yield
    
    def update_progress(self, completed_percentage: float):
        """
        更新执行进度
        
        参数:
            completed_percentage: 已完成的百分比（0-100）
        """
        self.progress = min(max(completed_percentage, 0.00), 100.00)
        
        # 根据进度自动更新状态
        if self.progress >= 100:
            self.status = PlanStatusEnum.COMPLETED
        elif self.progress > 0:
            self.status = PlanStatusEnum.IN_PROGRESS
    
    def __repr__(self):
        """
        字符串表示
        """
        return f"<PlantingPlan(plan_code='{self.plan_code}', plan_name='{self.plan_name}', crop_type='{self.crop_type}')>"

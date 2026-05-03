"""
精准施肥与灌溉模型
定义水肥一体化管理的表结构，用于存储土壤检测数据、施肥方案、灌溉方案及实际执行记录
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from backend.app.database import Base


class FertilizerTypeEnum(enum.Enum):
    """
    肥料类型枚举
    """
    NITROGEN = "氮肥"
    PHOSPHATE = "磷肥"
    POTASSIUM = "钾肥"
    COMPOUND = "复合肥"
    ORGANIC = "有机肥"
    MICROELEMENT = "微肥"
    BIOLOGICAL = "生物肥"
    OTHER = "其他"


class IrrigationTypeEnum(enum.Enum):
    """
    灌溉类型枚举
    """
    DRIP = "滴灌"
    SPRINKLER = "喷灌"
    FLOOD = "漫灌"
    SUBSURFACE = "渗灌"
    FERTIGATION = "水肥一体化"
    OTHER = "其他"


class WaterSourceEnum(enum.Enum):
    """
    水源类型枚举
    """
    RIVER = "河水"
    LAKE = "湖水"
    GROUNDWATER = "地下水"
    RESERVOIR = "水库"
    RAINWATER = "雨水"
    TAP = "自来水"
    OTHER = "其他"


class FertilizationIrrigation(Base):
    """
    精准施肥与灌溉记录表
    用于存储水肥一体化方案制定和实际执行记录，支持与计划对比分析
    """
    
    __tablename__ = "fertilization_irrigations"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    
    # 关联的种植计划ID
    planting_plan_id = Column(Integer, ForeignKey("planting_plans.id"), nullable=True, index=True, comment="关联种植计划ID")
    
    # 记录编号
    record_code = Column(String(50), unique=True, nullable=False, index=True, comment="记录编号")
    
    # 记录类型
    record_type = Column(String(20), nullable=False, comment="记录类型：施肥/灌溉/水肥一体化")
    
    # 记录日期
    record_date = Column(Date, nullable=False, comment="记录日期")
    
    # 作物种类
    crop_type = Column(String(100), nullable=True, comment="作物种类")
    
    # 作物生育期
    growth_stage = Column(String(100), nullable=True, comment="作物生育期")
    
    # 作业地块
    plot_location = Column(String(200), nullable=True, comment="作业地块")
    
    # 作业面积（亩）
    operation_area = Column(Numeric(10, 2), nullable=True, comment="作业面积（亩）")
    
    # ========== 土壤检测数据 ==========
    # 检测日期
    soil_test_date = Column(Date, nullable=True, comment="土壤检测日期")
    
    # pH值
    soil_ph = Column(Numeric(5, 2), nullable=True, comment="土壤pH值")
    
    # 有机质含量（g/kg）
    organic_matter = Column(Numeric(8, 2), nullable=True, comment="有机质含量（g/kg）")
    
    # 全氮含量（g/kg）
    total_nitrogen = Column(Numeric(8, 2), nullable=True, comment="全氮含量（g/kg）")
    
    # 有效磷含量（mg/kg）
    available_phosphorus = Column(Numeric(8, 2), nullable=True, comment="有效磷含量（mg/kg）")
    
    # 速效钾含量（mg/kg）
    available_potassium = Column(Numeric(8, 2), nullable=True, comment="速效钾含量（mg/kg）")
    
    # 碱解氮含量（mg/kg）
    alkali_hydrolyzable_nitrogen = Column(Numeric(8, 2), nullable=True, comment="碱解氮含量（mg/kg）")
    
    # 土壤湿度（%）
    soil_moisture = Column(Numeric(5, 2), nullable=True, comment="土壤湿度（%）")
    
    # ========== 计划施肥数据 ==========
    # 计划肥料类型
    planned_fertilizer_type = Column(SQLEnum(FertilizerTypeEnum), nullable=True, comment="计划肥料类型")
    
    # 计划肥料名称
    planned_fertilizer_name = Column(String(200), nullable=True, comment="计划肥料名称")
    
    # 计划施肥量（公斤/亩）
    planned_fertilizer_amount_per_mu = Column(Numeric(10, 3), nullable=True, comment="计划施肥量（公斤/亩）")
    
    # 计划总施肥量（公斤）
    planned_total_fertilizer = Column(Numeric(12, 3), nullable=True, comment="计划总施肥量（公斤）")
    
    # 计划施肥方法
    planned_fertilization_method = Column(String(200), nullable=True, comment="计划施肥方法")
    
    # ========== 实际施肥数据 ==========
    # 实际肥料类型
    actual_fertilizer_type = Column(SQLEnum(FertilizerTypeEnum), nullable=True, comment="实际肥料类型")
    
    # 实际肥料名称
    actual_fertilizer_name = Column(String(200), nullable=True, comment="实际肥料名称")
    
    # 实际施肥量（公斤/亩）
    actual_fertilizer_amount_per_mu = Column(Numeric(10, 3), nullable=True, comment="实际施肥量（公斤/亩）")
    
    # 实际总施肥量（公斤）
    actual_total_fertilizer = Column(Numeric(12, 3), nullable=True, comment="实际总施肥量（公斤）")
    
    # 实际施肥方法
    actual_fertilization_method = Column(String(200), nullable=True, comment="实际施肥方法")
    
    # 施肥日期
    fertilization_date = Column(Date, nullable=True, comment="实际施肥日期")
    
    # ========== 计划灌溉数据 ==========
    # 计划灌溉类型
    planned_irrigation_type = Column(SQLEnum(IrrigationTypeEnum), nullable=True, comment="计划灌溉类型")
    
    # 计划水源类型
    planned_water_source = Column(SQLEnum(WaterSourceEnum), nullable=True, comment="计划水源类型")
    
    # 计划灌溉量（立方米/亩）
    planned_irrigation_amount_per_mu = Column(Numeric(10, 3), nullable=True, comment="计划灌溉量（立方米/亩）")
    
    # 计划总灌溉量（立方米）
    planned_total_irrigation = Column(Numeric(12, 3), nullable=True, comment="计划总灌溉量（立方米）")
    
    # 计划灌溉时间（小时）
    planned_irrigation_duration = Column(Numeric(8, 2), nullable=True, comment="计划灌溉时间（小时）")
    
    # ========== 实际灌溉数据 ==========
    # 实际灌溉类型
    actual_irrigation_type = Column(SQLEnum(IrrigationTypeEnum), nullable=True, comment="实际灌溉类型")
    
    # 实际水源类型
    actual_water_source = Column(SQLEnum(WaterSourceEnum), nullable=True, comment="实际水源类型")
    
    # 实际灌溉量（立方米/亩）
    actual_irrigation_amount_per_mu = Column(Numeric(10, 3), nullable=True, comment="实际灌溉量（立方米/亩）")
    
    # 实际总灌溉量（立方米）
    actual_total_irrigation = Column(Numeric(12, 3), nullable=True, comment="实际总灌溉量（立方米）")
    
    # 实际灌溉时间（小时）
    actual_irrigation_duration = Column(Numeric(8, 2), nullable=True, comment="实际灌溉时间（小时）")
    
    # 灌溉日期
    irrigation_date = Column(Date, nullable=True, comment="实际灌溉日期")
    
    # ========== 水肥一体化数据 ==========
    # 是否水肥一体化
    is_fertigation = Column(Integer, default=0, comment="是否水肥一体化：0-否，1-是")
    
    # 水肥配比（肥料:水）
    fertigation_ratio = Column(String(50), nullable=True, comment="水肥配比（肥料:水）")
    
    # ========== 对比分析数据 ==========
    # 施肥量偏差（%）
    fertilizer_deviation_percent = Column(Numeric(8, 2), nullable=True, comment="施肥量偏差（%）")
    
    # 灌溉量偏差（%）
    irrigation_deviation_percent = Column(Numeric(8, 2), nullable=True, comment="灌溉量偏差（%）")
    
    # 是否符合计划
    is_according_to_plan = Column(Integer, default=1, comment="是否符合计划：0-否，1-是")
    
    # ========== 其他信息 ==========
    # 操作人员
    operator = Column(String(100), nullable=True, comment="操作人员")
    
    # 设备编号
    equipment_code = Column(String(100), nullable=True, comment="设备编号")
    
    # 天气情况
    weather_condition = Column(String(100), nullable=True, comment="作业时天气情况")
    
    # 备注说明
    remarks = Column(Text, nullable=True, comment="备注说明")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 创建人
    created_by = Column(String(100), nullable=True, comment="创建人")
    
    # 关系定义
    planting_plan = relationship("PlantingPlan", backref="fertilization_irrigations")
    
    def calculate_deviations(self):
        """
        计算计划与实际的偏差百分比
        """
        # 计算施肥量偏差
        if self.planned_fertilizer_amount_per_mu and self.actual_fertilizer_amount_per_mu:
            if self.planned_fertilizer_amount_per_mu > 0:
                self.fertilizer_deviation_percent = (
                    (self.actual_fertilizer_amount_per_mu - self.planned_fertilizer_amount_per_mu) 
                    / self.planned_fertilizer_amount_per_mu * 100
                )
        
        # 计算灌溉量偏差
        if self.planned_irrigation_amount_per_mu and self.actual_irrigation_amount_per_mu:
            if self.planned_irrigation_amount_per_mu > 0:
                self.irrigation_deviation_percent = (
                    (self.actual_irrigation_amount_per_mu - self.planned_irrigation_amount_per_mu) 
                    / self.planned_irrigation_amount_per_mu * 100
                )
        
        # 判断是否符合计划（偏差在±10%以内视为符合）
        fertilizer_ok = True
        irrigation_ok = True
        
        if self.fertilizer_deviation_percent is not None:
            fertilizer_ok = abs(self.fertilizer_deviation_percent) <= 10
        
        if self.irrigation_deviation_percent is not None:
            irrigation_ok = abs(self.irrigation_deviation_percent) <= 10
        
        self.is_according_to_plan = 1 if (fertilizer_ok and irrigation_ok) else 0
    
    def calculate_totals(self):
        """
        计算总量
        """
        # 计算计划施肥总量
        if self.operation_area and self.planned_fertilizer_amount_per_mu:
            self.planned_total_fertilizer = self.operation_area * self.planned_fertilizer_amount_per_mu
        
        # 计算实际施肥总量
        if self.operation_area and self.actual_fertilizer_amount_per_mu:
            self.actual_total_fertilizer = self.operation_area * self.actual_fertilizer_amount_per_mu
        
        # 计算计划灌溉总量
        if self.operation_area and self.planned_irrigation_amount_per_mu:
            self.planned_total_irrigation = self.operation_area * self.planned_irrigation_amount_per_mu
        
        # 计算实际灌溉总量
        if self.operation_area and self.actual_irrigation_amount_per_mu:
            self.actual_total_irrigation = self.operation_area * self.actual_irrigation_amount_per_mu
    
    def __repr__(self):
        """
        字符串表示
        """
        return f"<FertilizationIrrigation(record_code='{self.record_code}', record_type='{self.record_type}', record_date='{self.record_date}')>"

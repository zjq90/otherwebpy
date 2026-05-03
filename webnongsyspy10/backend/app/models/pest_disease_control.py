"""
病虫害防治管理模型
定义病虫害发生记录和防治措施记录表结构，包含高毒农药预警功能
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum

from backend.app.database import Base
from backend.app.config import settings


class PestDiseaseTypeEnum(enum.Enum):
    """
    病虫害类型枚举
    """
    PEST = "虫害"
    DISEASE = "病害"
    WEED = "草害"
    NEMATODE = "线虫病"
    OTHER = "其他"


class ControlMethodEnum(enum.Enum):
    """
    防治措施类型枚举
    """
    BIOLOGICAL = "生物防治"
    PHYSICAL = "物理防治"
    CHEMICAL = "化学防治"
    AGRICULTURAL = "农业防治"
    COMBINED = "综合防治"


class SeverityLevelEnum(enum.Enum):
    """
    严重程度枚举
    """
    LIGHT = "轻度"
    MODERATE = "中度"
    SEVERE = "重度"
    VERY_SEVERE = "极重度"


class TreatmentStatusEnum(enum.Enum):
    """
    防治状态枚举
    """
    DETECTED = "已发现"
    TREATING = "防治中"
    CONTROLLED = "已控制"
    ERADICATED = "已根除"
    REOCCURRING = "复发"


class PestDiseaseControl(Base):
    """
    病虫害防治记录表
    用于存储病虫害发生记录、防治措施及效果评估，包含高毒农药预警功能
    """
    
    __tablename__ = "pest_disease_controls"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    
    # 关联的种植计划ID
    planting_plan_id = Column(Integer, ForeignKey("planting_plans.id"), nullable=True, index=True, comment="关联种植计划ID")
    
    # 记录编号
    record_code = Column(String(50), unique=True, nullable=False, index=True, comment="记录编号")
    
    # ========== 病虫害发生信息 ==========
    # 发现日期
    discovery_date = Column(Date, nullable=False, comment="发现日期")
    
    # 病虫害类型
    pest_disease_type = Column(SQLEnum(PestDiseaseTypeEnum), nullable=False, comment="病虫害类型")
    
    # 病虫害名称
    pest_disease_name = Column(String(200), nullable=False, comment="病虫害名称")
    
    # 病虫害学名
    scientific_name = Column(String(200), nullable=True, comment="病虫害学名")
    
    # 作物种类
    crop_type = Column(String(100), nullable=True, comment="受害作物种类")
    
    # 作物品种
    crop_variety = Column(String(100), nullable=True, comment="受害作物品种")
    
    # 作物生育期
    growth_stage = Column(String(100), nullable=True, comment="作物生育期")
    
    # 发生地块
    plot_location = Column(String(200), nullable=True, comment="发生地块")
    
    # 影响面积（亩）
    affected_area = Column(Numeric(10, 2), nullable=False, comment="影响面积（亩）")
    
    # 严重程度
    severity = Column(SQLEnum(SeverityLevelEnum), nullable=True, comment="严重程度")
    
    # 发生率（%）
    incidence_rate = Column(Numeric(5, 2), nullable=True, comment="发生率（%）")
    
    # 危害症状描述
    symptoms_description = Column(Text, nullable=True, comment="危害症状描述")
    
    # 现场照片URL（多个用逗号分隔）
    photo_urls = Column(Text, nullable=True, comment="现场照片URL")
    
    # ========== 防治措施信息 ==========
    # 防治措施类型
    control_method = Column(SQLEnum(ControlMethodEnum), nullable=True, comment="防治措施类型")
    
    # 防治日期
    treatment_date = Column(Date, nullable=True, comment="防治日期")
    
    # 操作人员
    operator = Column(String(100), nullable=True, comment="操作人员")
    
    # ========== 化学防治专用字段 ==========
    # 药剂名称
    pesticide_name = Column(String(200), nullable=True, comment="药剂名称")
    
    # 药剂类型（杀虫剂/杀菌剂/除草剂/杀螨剂等）
    pesticide_type = Column(String(50), nullable=True, comment="药剂类型")
    
    # 农药登记证号
    registration_number = Column(String(100), nullable=True, comment="农药登记证号")
    
    # 生产厂家
    manufacturer = Column(String(200), nullable=True, comment="生产厂家")
    
    # 使用剂量（每亩）
    dosage_per_mu = Column(Numeric(10, 3), nullable=True, comment="使用剂量（每亩）")
    
    # 剂量单位
    dosage_unit = Column(String(20), nullable=True, comment="剂量单位")
    
    # 稀释倍数
    dilution_ratio = Column(Integer, nullable=True, comment="稀释倍数")
    
    # 施药方法
    application_method = Column(String(200), nullable=True, comment="施药方法")
    
    # 施药器械
    equipment_used = Column(String(200), nullable=True, comment="施药器械")
    
    # 安全间隔期（天）
    safety_interval_days = Column(Integer, nullable=True, comment="安全间隔期（天）")
    
    # 允许使用日期（根据安全间隔期计算）
    allowed_use_date = Column(Date, nullable=True, comment="允许使用日期")
    
    # ========== 高毒农药预警相关 ==========
    # 是否为高毒农药
    is_high_toxic = Column(Boolean, default=False, comment="是否为高毒农药")
    
    # 是否触发预警
    has_warning = Column(Boolean, default=False, comment="是否触发预警")
    
    # 预警信息
    warning_message = Column(Text, nullable=True, comment="预警信息")
    
    # ========== 生物防治专用字段 ==========
    # 天敌种类
    natural_enemy_type = Column(String(200), nullable=True, comment="天敌种类")
    
    # 释放数量
    release_quantity = Column(Numeric(12, 2), nullable=True, comment="释放数量")
    
    # 释放方式
    release_method = Column(String(200), nullable=True, comment="释放方式")
    
    # ========== 物理防治专用字段 ==========
    # 物理措施类型（诱虫板/杀虫灯/防虫网等）
    physical_measure_type = Column(String(200), nullable=True, comment="物理措施类型")
    
    # 数量/密度
    quantity_density = Column(String(100), nullable=True, comment="数量/密度")
    
    # ========== 效果评估 ==========
    # 防治状态
    treatment_status = Column(SQLEnum(TreatmentStatusEnum), default=TreatmentStatusEnum.DETECTED, comment="防治状态")
    
    # 防治效果评估日期
    assessment_date = Column(Date, nullable=True, comment="防治效果评估日期")
    
    # 防治效果（%）
    control_effect = Column(Numeric(5, 2), nullable=True, comment="防治效果（%）")
    
    # 效果描述
    effect_description = Column(Text, nullable=True, comment="效果描述")
    
    # 是否需要再次防治
    needs_retreatment = Column(Boolean, default=False, comment="是否需要再次防治")
    
    # 建议再次防治日期
    suggested_retreatment_date = Column(Date, nullable=True, comment="建议再次防治日期")
    
    # ========== 其他信息 ==========
    # 备注说明
    remarks = Column(Text, nullable=True, comment="备注说明")
    
    # 天气情况
    weather_condition = Column(String(100), nullable=True, comment="作业时天气情况")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 创建人
    created_by = Column(String(100), nullable=True, comment="创建人")
    
    # 关系定义
    planting_plan = relationship("PlantingPlan", backref="pest_disease_controls")
    
    def check_high_toxic_pesticide(self):
        """
        检查是否使用高毒农药
        根据配置中的高毒农药列表进行检查
        
        返回:
            tuple: (是否为高毒农药, 预警信息)
        """
        if not self.pesticide_name:
            return False, None
        
        # 检查农药名称是否包含高毒农药关键词
        pesticide_name_lower = self.pesticide_name.lower()
        
        for high_toxic in settings.HIGH_TOXIC_PESTICIDES:
            if high_toxic.lower() in pesticide_name_lower:
                warning_msg = f"预警：检测到使用高毒农药「{high_toxic}」，该农药已被禁用！请立即停止使用并更换低毒农药。"
                return True, warning_msg
        
        return False, None
    
    def update_warning_status(self):
        """
        更新预警状态
        检查农药使用情况，设置预警标志和信息
        """
        # 仅当使用化学防治时检查
        if self.control_method == ControlMethodEnum.CHEMICAL and self.pesticide_name:
            is_high_toxic, warning_msg = self.check_high_toxic_pesticide()
            self.is_high_toxic = is_high_toxic
            self.has_warning = is_high_toxic
            self.warning_message = warning_msg if is_high_toxic else None
        else:
            self.is_high_toxic = False
            self.has_warning = False
            self.warning_message = None
    
    def calculate_allowed_use_date(self):
        """
        根据安全间隔期计算允许使用日期
        """
        if self.treatment_date and self.safety_interval_days:
            self.allowed_use_date = self.treatment_date + timedelta(days=self.safety_interval_days)
        return self.allowed_use_date
    
    def calculate_control_effect(self, before_count: int, after_count: int):
        """
        计算防治效果
        
        参数:
            before_count: 防治前虫口密度或病情指数
            after_count: 防治后虫口密度或病情指数
        
        返回:
            float: 防治效果百分比
        """
        if before_count == 0:
            return 100.0
        
        control_effect = ((before_count - after_count) / before_count) * 100
        self.control_effect = round(control_effect, 2)
        
        # 根据防治效果更新状态
        if self.control_effect >= 90:
            self.treatment_status = TreatmentStatusEnum.ERADICATED
        elif self.control_effect >= 70:
            self.treatment_status = TreatmentStatusEnum.CONTROLLED
        elif self.control_effect >= 40:
            self.treatment_status = TreatmentStatusEnum.TREATING
            self.needs_retreatment = True
        else:
            self.treatment_status = TreatmentStatusEnum.REOCCURRING
            self.needs_retreatment = True
        
        return self.control_effect
    
    def get_severity_display(self):
        """
        获取严重程度的显示名称
        """
        return self.severity.value if self.severity else None
    
    def get_control_method_display(self):
        """
        获取防治措施类型的显示名称
        """
        return self.control_method.value if self.control_method else None
    
    def get_treatment_status_display(self):
        """
        获取防治状态的显示名称
        """
        return self.treatment_status.value if self.treatment_status else None
    
    def __repr__(self):
        """
        字符串表示
        """
        return f"<PestDiseaseControl(record_code='{self.record_code}', pest_disease_name='{self.pest_disease_name}', discovery_date='{self.discovery_date}')>"

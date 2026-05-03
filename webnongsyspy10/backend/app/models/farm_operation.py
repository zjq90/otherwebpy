"""
农事作业记录模型
定义农事作业记录表的结构，用于存储播种、施肥、灌溉、除草、病虫害防治等操作记录
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from backend.app.database import Base


class OperationTypeEnum(enum.Enum):
    """
    作业类型枚举
    """
    SOWING = "播种"
    FERTILIZATION = "施肥"
    IRRIGATION = "灌溉"
    WEEDING = "除草"
    PEST_CONTROL = "病虫害防治"
    HARVEST = "收获"
    OTHER = "其他"


class OperationStatusEnum(enum.Enum):
    """
    作业状态枚举
    """
    PLANNED = "计划中"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class FarmOperation(Base):
    """
    农事作业记录表
    用于存储各类农事作业的详细记录信息，确保数据真实可追溯
    """
    
    __tablename__ = "farm_operations"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="作业记录ID")
    
    # 关联的种植计划ID
    planting_plan_id = Column(Integer, ForeignKey("planting_plans.id"), nullable=True, index=True, comment="关联种植计划ID")
    
    # 作业编号
    operation_code = Column(String(50), unique=True, nullable=False, index=True, comment="作业编号")
    
    # 作业类型
    operation_type = Column(SQLEnum(OperationTypeEnum), nullable=False, comment="作业类型")
    
    # 作业名称
    operation_name = Column(String(200), nullable=False, comment="作业名称")
    
    # 计划作业日期
    planned_date = Column(Date, nullable=True, comment="计划作业日期")
    
    # 实际作业日期
    actual_date = Column(Date, nullable=False, comment="实际作业日期")
    
    # 作物种类
    crop_type = Column(String(100), nullable=True, comment="作物种类")
    
    # 作业地块
    plot_location = Column(String(200), nullable=True, comment="作业地块")
    
    # 作业面积（亩）
    operation_area = Column(Numeric(10, 2), nullable=True, comment="作业面积（亩）")
    
    # 操作人员
    operator = Column(String(100), nullable=False, comment="操作人员")
    
    # 操作人员联系方式
    operator_contact = Column(String(50), nullable=True, comment="操作人员联系方式")
    
    # 扫码记录ID（用于快速录入追溯）
    scan_code_id = Column(String(100), nullable=True, comment="扫码记录ID（用于快速录入追溯）")
    
    # APP端录入标识
    is_app_entry = Column(Integer, default=0, comment="是否APP端录入：0-否，1-是")
    
    # 录入设备信息
    entry_device = Column(String(200), nullable=True, comment="录入设备信息")
    
    # 用量（根据作业类型不同，含义不同）
    # 播种：播种量（公斤）
    # 施肥：施肥量（公斤）
    # 灌溉：灌溉量（立方米）
    # 除草：除草面积（亩）
    # 病虫害防治：用药量（公斤/升）
    quantity = Column(Numeric(12, 3), nullable=True, comment="用量")
    
    # 用量单位
    quantity_unit = Column(String(20), nullable=True, comment="用量单位")
    
    # 作业方法描述
    operation_method = Column(Text, nullable=True, comment="作业方法描述")
    
    # 工具/设备
    tools_used = Column(String(200), nullable=True, comment="使用的工具/设备")
    
    # 天气情况
    weather_condition = Column(String(100), nullable=True, comment="作业时天气情况")
    
    # 作业状态
    status = Column(SQLEnum(OperationStatusEnum), default=OperationStatusEnum.COMPLETED, comment="作业状态")
    
    # 作业效果评估
    effect_assessment = Column(Text, nullable=True, comment="作业效果评估")
    
    # 备注说明
    remarks = Column(Text, nullable=True, comment="备注说明")
    
    # 现场照片URL（多个用逗号分隔）
    photo_urls = Column(Text, nullable=True, comment="现场照片URL")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 创建人
    created_by = Column(String(100), nullable=True, comment="创建人")
    
    # 审核人
    reviewed_by = Column(String(100), nullable=True, comment="审核人")
    
    # 审核时间
    reviewed_at = Column(DateTime, nullable=True, comment="审核时间")
    
    # 关系定义
    planting_plan = relationship("PlantingPlan", backref="farm_operations")
    
    def get_operation_type_display(self):
        """
        获取作业类型的显示名称
        """
        return self.operation_type.value
    
    def get_status_display(self):
        """
        获取状态的显示名称
        """
        return self.status.value
    
    def mark_completed(self):
        """
        标记作业为已完成
        """
        self.status = OperationStatusEnum.COMPLETED
    
    def generate_traceability_code(self):
        """
        生成追溯码
        格式：作业类型代码 + 日期时间戳 + 随机码
        """
        import random
        import string
        
        # 作业类型代码映射
        type_code_map = {
            OperationTypeEnum.SOWING: "SW",
            OperationTypeEnum.FERTILIZATION: "FS",
            OperationTypeEnum.IRRIGATION: "GG",
            OperationTypeEnum.WEEDING: "CC",
            OperationTypeEnum.PEST_CONTROL: "FB",
            OperationTypeEnum.HARVEST: "SH",
            OperationTypeEnum.OTHER: "QT"
        }
        
        type_code = type_code_map.get(self.operation_type, "QT")
        date_str = self.actual_date.strftime("%Y%m%d") if self.actual_date else datetime.now().strftime("%Y%m%d")
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        return f"{type_code}-{date_str}-{random_code}"
    
    def __repr__(self):
        """
        字符串表示
        """
        return f"<FarmOperation(operation_code='{self.operation_code}', operation_type='{self.operation_type.value}', actual_date='{self.actual_date}')>"

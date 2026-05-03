from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Plot(Base):
    """
    地块管理模型
    存储农场各个地块的详细信息
    """
    
    __tablename__ = "plots"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 地块编号
    plot_number = Column(String(50), nullable=False, unique=True, comment="地块编号")
    
    # 关联的农场ID
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True, comment="所属农场ID")
    
    # 地块面积（单位：亩）
    area = Column(Float, nullable=False, comment="地块面积(亩)")
    
    # 土壤类型
    soil_type = Column(String(100), nullable=False, comment="土壤类型")
    
    # pH值
    ph_value = Column(Float, nullable=False, comment="土壤pH值")
    
    # 种植历史（文本描述）
    planting_history = Column(Text, nullable=True, comment="种植历史")
    
    # 轮作计划（文本描述）
    crop_rotation_plan = Column(Text, nullable=True, comment="轮作计划")
    
    # 是否禁用农药（是/否）
    pesticide_prohibited = Column(Boolean, nullable=False, default=False, comment="是否禁用农药")
    
    # 地块位置描述
    location = Column(String(500), nullable=True, comment="地块位置描述")
    
    # 备注信息
    remarks = Column(Text, nullable=True, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Plot(id={self.id}, plot_number='{self.plot_number}')>"

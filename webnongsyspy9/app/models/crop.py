from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Crop(Base):
    """
    作物档案模型
    存储各种作物的详细档案信息
    """
    
    __tablename__ = "crops"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 作物名称
    name = Column(String(200), nullable=False, comment="作物名称")
    
    # 品种
    variety = Column(String(200), nullable=False, comment="品种")
    
    # 生长周期（单位：天）
    growth_cycle = Column(Integer, nullable=False, comment="生长周期(天)")
    
    # 适宜环境（文本描述，如温度、湿度、光照等）
    suitable_environment = Column(Text, nullable=True, comment="适宜环境")
    
    # 病虫害记录（文本描述）
    pest_disease_records = Column(Text, nullable=True, comment="病虫害记录")
    
    # 施肥标准（文本描述）
    fertilization_standard = Column(Text, nullable=True, comment="施肥标准")
    
    # 播种季节
    planting_season = Column(String(100), nullable=True, comment="播种季节")
    
    # 收获季节
    harvest_season = Column(String(100), nullable=True, comment="收获季节")
    
    # 备注信息
    remarks = Column(Text, nullable=True, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Crop(id={self.id}, name='{self.name}')>"

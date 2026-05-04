"""
场地管理数据模型
定义场地信息，用于课程排期时选择场地
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Venue(Base):
    """
    场地模型
    定义场馆内的各种场地信息，如瑜伽室、动感单车室等
    """
    
    __tablename__ = "venues"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="场地ID")
    
    # 场地名称
    name = Column(String(100), nullable=False, index=True, comment="场地名称")
    
    # 场地代码：用于内部标识
    code = Column(String(50), unique=True, nullable=False, index=True, comment="场地代码")
    
    # 场地类型：瑜伽室、动感单车室、私教室等
    venue_type = Column(String(50), nullable=False, comment="场地类型")
    
    # 场地容量
    capacity = Column(Integer, default=20, comment="场地容量")
    
    # 场地位置描述
    location = Column(String(200), comment="场地位置")
    
    # 场地设施描述（JSON格式）
    facilities = Column(Text, comment="场地设施")
    
    # 场地描述
    description = Column(Text, comment="场地描述")
    
    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 排序权重
    sort_order = Column(Integer, default=0, comment="排序权重")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：一个场地对应多个课程排期
    schedules = relationship("CourseSchedule", back_populates="venue")
    
    def __repr__(self):
        return f"<Venue(id={self.id}, name='{self.name}', capacity={self.capacity})>"

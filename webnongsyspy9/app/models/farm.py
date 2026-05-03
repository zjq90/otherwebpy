from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base


class Farm(Base):
    """
    农场信息模型
    存储农场的基本信息
    """
    
    __tablename__ = "farms"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 农场名称
    name = Column(String(200), nullable=False, comment="农场名称")
    
    # 农场地址
    address = Column(String(500), nullable=False, comment="农场地址")
    
    # 负责人姓名
    manager = Column(String(100), nullable=False, comment="负责人")
    
    # 联系方式（电话/手机）
    contact = Column(String(50), nullable=False, comment="联系方式")
    
    # 土地面积（单位：亩）
    land_area = Column(Float, nullable=False, comment="土地面积(亩)")
    
    # 认证类型：绿色/有机/无公害
    certification_type = Column(String(50), nullable=False, default="绿色", comment="认证类型")
    
    # 农场描述/备注
    description = Column(Text, nullable=True, comment="农场描述")
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Farm(id={self.id}, name='{self.name}')>"

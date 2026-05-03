"""
分类模型
定义产品分类表结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    """
    产品分类模型类
    对应数据库中的categories表
    """
    __tablename__ = "categories"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="分类ID")
    
    # 分类名称
    name = Column(String(100), nullable=False, unique=True, comment="分类名称")
    
    # 分类描述
    description = Column(Text, nullable=True, comment="分类描述")
    
    # 分类排序
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 是否删除（软删除）
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    # 关联产品（一对多关系）
    products = relationship("Product", back_populates="category")

    def to_dict(self):
        """
        将分类对象转换为字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

"""
产品模型
定义租借产品表结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    """
    产品模型类
    对应数据库中的products表
    """
    __tablename__ = "products"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    
    # 产品名称
    name = Column(String(200), nullable=False, comment="产品名称")
    
    # 产品描述
    description = Column(Text, nullable=True, comment="产品描述")
    
    # 分类ID（外键）
    category_id = Column(Integer, ForeignKey("categories.id"), comment="分类ID")
    
    # 日租金
    daily_rent = Column(DECIMAL(10, 2), nullable=False, comment="日租金")
    
    # 押金
    deposit = Column(DECIMAL(10, 2), nullable=False, comment="押金")
    
    # 库存数量
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    
    # 可用数量
    available_quantity = Column(Integer, default=0, comment="可用数量")
    
    # 产品图片
    image_url = Column(String(500), nullable=True, comment="产品图片")
    
    # 产品状态：1-上架，2-下架
    status = Column(Integer, default=1, comment="产品状态")
    
    # 是否热门
    is_hot = Column(Boolean, default=False, comment="是否热门")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 是否删除（软删除）
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    # 关联分类
    category = relationship("Category", back_populates="products")
    
    # 关联预约（一对多关系）
    reservations = relationship("Reservation", back_populates="product")

    def to_dict(self):
        """
        将产品对象转换为字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id,
            "daily_rent": float(self.daily_rent) if self.daily_rent else 0,
            "deposit": float(self.deposit) if self.deposit else 0,
            "stock_quantity": self.stock_quantity,
            "available_quantity": self.available_quantity,
            "image_url": self.image_url,
            "status": self.status,
            "is_hot": self.is_hot,
            "category_name": self.category.name if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

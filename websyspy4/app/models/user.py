"""
用户模型
定义用户表结构和相关方法
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """
    用户角色枚举
    USER: 普通用户
    ADMIN: 管理员
    """
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    用户模型类
    对应数据库中的users表
    """
    __tablename__ = "users"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    
    # 手机号（登录用）
    phone = Column(String(11), unique=True, index=True, nullable=False, comment="手机号")
    
    # 姓名
    name = Column(String(50), nullable=True, comment="姓名")
    
    # 密码（加密存储）
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 用户角色
    role = Column(String(20), default=UserRole.USER, comment="用户角色")
    
    # 手机号是否验证
    is_verified = Column(Boolean, default=False, comment="是否验证")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 是否删除（软删除）
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    def to_dict(self):
        """
        将用户对象转换为字典
        """
        return {
            "id": self.id,
            "phone": self.phone,
            "name": self.name,
            "role": self.role,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

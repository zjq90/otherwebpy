"""
权限数据模型
定义权限表结构和与角色的多对多关�?
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Permission(Base):
    """
    权限数据模型
    存储系统权限信息，用于细粒度的权限控�?
    """
    
    __tablename__ = "permissions"
    __table_args__ = {"comment": "系统权限�?}
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="权限ID")
    
    # 权限基本信息
    name = Column(String(100), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, index=True, nullable=False, comment="权限代码（用于权限检查）")
    description = Column(String(255), nullable=True, comment="权限描述")
    
    # 权限分类
    module = Column(String(50), nullable=True, comment="所属模块（如：user, role, permission等）")
    action = Column(String(50), nullable=True, comment="操作类型（如：create, read, update, delete等）")
    
    # 状态字�?
    is_active = Column(Boolean, default=True, comment="是否激�?)
    is_system = Column(Boolean, default=False, comment="是否系统内置权限（不可删除）")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 多对多关系：一个权限可以属于多个角�?
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")
    
    def __repr__(self):
        """字符串表�?""
        return f"<Permission(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    @staticmethod
    def generate_code(module: str, action: str) -> str:
        """
        生成权限代码
        格式：{module}:{action}
        
        参数:
            module: 模块名称
            action: 操作类型
        
        返回:
            权限代码字符�?
        """
        return f"{module}:{action}"

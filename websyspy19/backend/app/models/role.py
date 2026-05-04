"""
角色数据模型
定义角色表结构和与用户、权限的多对多关�?
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


# 角色-权限关联表（多对多关系）
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
    comment="角色与权限的关联�?
)


class Role(Base):
    """
    角色数据模型
    存储系统角色信息，用于权限分�?
    """
    
    __tablename__ = "roles"
    __table_args__ = {"comment": "系统角色�?}
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="角色ID")
    
    # 角色基本信息
    name = Column(String(50), unique=True, index=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, index=True, nullable=False, comment="角色代码（用于权限检查）")
    description = Column(String(255), nullable=True, comment="角色描述")
    
    # 状态字�?
    is_active = Column(Boolean, default=True, comment="是否激�?)
    is_system = Column(Boolean, default=False, comment="是否系统内置角色（不可删除）")
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 多对多关�?
    # 一个角色可以有多个用户
    users = relationship("User", secondary="user_role", back_populates="roles")
    # 一个角色可以有多个权限
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    
    def __repr__(self):
        """字符串表�?""
        return f"<Role(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def has_permission(self, permission_code: str) -> bool:
        """
        检查角色是否拥有指定权�?
        
        参数:
            permission_code: 权限代码
        
        返回:
            拥有权限返回True，否则返回False
        """
        for permission in self.permissions:
            if permission.code == permission_code:
                return True
        return False

"""
用户数据模型
定义用户表结构和与角色的多对多关�?
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


# 用户-角色关联表（多对多关系）
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    comment="用户与角色的关联�?
)


class User(Base):
    """
    用户数据模型
    存储系统用户的基本信�?
    """
    
    __tablename__ = "users"
    __table_args__ = {"comment": "系统用户�?}
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    
    # 用户基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户�?)
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机�?)
    hashed_password = Column(String(255), nullable=False, comment="加密后的密码")
    full_name = Column(String(50), nullable=True, comment="真实姓名")
    
    # 状态字�?
    is_active = Column(Boolean, default=True, comment="是否激�?)
    is_superuser = Column(Boolean, default=False, comment="是否超级管理�?)
    
    # 时间字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_login = Column(DateTime, nullable=True, comment="最后登录时�?)
    
    # 多对多关系：一个用户可以有多个角色
    roles = relationship("Role", secondary=user_role, back_populates="users")
    
    def __repr__(self):
        """字符串表�?""
        return f"<User(id={self.id}, username='{self.username}')>"
    
    def has_permission(self, permission_code: str) -> bool:
        """
        检查用户是否拥有指定权�?
        
        参数:
            permission_code: 权限代码
        
        返回:
            拥有权限返回True，否则返回False
        """
        # 超级管理员拥有所有权�?
        if self.is_superuser:
            return True
        
        # 遍历用户的所有角色，检查是否拥有该权限
        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        
        return False
    
    def get_all_permissions(self) -> list:
        """
        获取用户拥有的所有权�?
        
        返回:
            权限对象列表
        """
        permissions = set()
        
        # 超级管理员返回空集合，由权限检查逻辑单独处理
        if self.is_superuser:
            return []
        
        # 遍历用户的所有角色，收集权限
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission)
        
        return list(permissions)

"""
用户相关数据模型
包含用户、角色、权限等核心模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from ..database import Base


# 用户角色关联表 (多对多)
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


# 角色权限关联表 (多对多)
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class User(Base):
    """
    用户模型
    存储系统用户的基本信息
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, comment='用户ID')
    username = Column(String(50), unique=True, index=True, comment='用户名')
    password_hash = Column(String(255), comment='密码哈希')
    phone = Column(String(20), unique=True, index=True, comment='手机号')
    real_name = Column(String(50), comment='真实姓名')
    id_card = Column(String(50), comment='身份证号')
    is_verified = Column(Boolean, default=False, comment='是否实名认证')
    is_active = Column(Boolean, default=True, comment='是否激活')
    is_first_login = Column(Boolean, default=True, comment='是否首次登录')
    last_login_at = Column(DateTime, nullable=True, comment='最后登录时间')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    roles = relationship('Role', secondary=user_role, back_populates='users')
    verification_codes = relationship('VerificationCode', back_populates='user')


class Role(Base):
    """
    角色模型
    定义系统中的角色类型
    """
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True, comment='角色ID')
    name = Column(String(50), unique=True, index=True, comment='角色名称')
    code = Column(String(50), unique=True, index=True, comment='角色代码')
    description = Column(String(255), comment='角色描述')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    users = relationship('User', secondary=user_role, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permission, back_populates='roles')


class Permission(Base):
    """
    权限模型
    定义系统中的权限项
    """
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True, comment='权限ID')
    name = Column(String(100), unique=True, index=True, comment='权限名称')
    code = Column(String(100), unique=True, index=True, comment='权限代码')
    description = Column(String(255), comment='权限描述')
    module = Column(String(50), comment='所属模块')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系
    roles = relationship('Role', secondary=role_permission, back_populates='permissions')


class VerificationCode(Base):
    """
    验证码模型
    存储短信验证码信息
    """
    __tablename__ = 'verification_codes'

    id = Column(Integer, primary_key=True, index=True, comment='验证码ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment='用户ID')
    phone = Column(String(20), index=True, comment='手机号')
    code = Column(String(10), comment='验证码')
    is_used = Column(Boolean, default=False, comment='是否已使用')
    expires_at = Column(DateTime, comment='过期时间')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系
    user = relationship('User', back_populates='verification_codes')

"""
用户模型模块
定义用户相关的数据库表结构，包括用户信息、绑定关系等
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.database import Base


class User(Base):
    """
    用户信息表
    存储用户的基本账户信息
    """
    __tablename__ = "users"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用户名（登录用）
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # 密码哈希（不存储明文密码）
    password_hash = Column(String(255), nullable=False)
    
    # 真实姓名
    real_name = Column(String(50), nullable=True)
    
    # 头像URL
    avatar = Column(String(500), nullable=True)
    
    # 手机号
    phone = Column(String(20), unique=True, index=True, nullable=True)
    
    # 邮箱
    email = Column(String(100), nullable=True)
    
    # 微信OpenID（绑定微信登录）
    wechat_openid = Column(String(100), unique=True, nullable=True)
    
    # 微信UnionID
    wechat_unionid = Column(String(100), nullable=True)
    
    # 是否激活
    is_active = Column(Boolean, default=True)
    
    # 是否管理员
    is_admin = Column(Boolean, default=False)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 最后登录时间
    last_login_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        """字符串表示"""
        return f"<User(id={self.id}, username='{self.username}')>"

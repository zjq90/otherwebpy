from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """
    用户角色枚举
    """
    ADMIN = "admin"
    PROPERTY = "property"
    RESIDENT = "resident"


class User(Base):
    """
    用户模型
    存储系统用户信息，包括管理员、物业人员和业主
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="电子邮箱")
    room_number = Column(String(20), comment="房间号/门牌号")
    role = Column(String(20), default=UserRole.RESIDENT.value, comment="用户角色：admin/property/resident")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

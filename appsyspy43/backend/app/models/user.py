"""
用户模型
定义用户表结构，包括管理员、调度员、司机三种角色
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """
    用户角色枚举
    定义系统中的三种用户角色
    """
    ADMIN = "admin"  # 管理员：拥有所有权限
    DISPATCHER = "dispatcher"  # 调度员：负责任务分配
    DRIVER = "driver"  # 司机：执行运输任务


class UserStatus(str, enum.Enum):
    """
    用户状态枚举
    定义用户的当前状态
    """
    ACTIVE = "active"  # 活跃：正常使用
    INACTIVE = "inactive"  # 非活跃：暂时禁用
    BUSY = "busy"  # 忙碌：司机执行任务中
    IDLE = "idle"  # 空闲：司机可以接受任务


class User(Base):
    """
    用户模型
    存储系统用户的基本信息
    """
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用户基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号码")
    
    # 角色和状态
    role = Column(Enum(UserRole), default=UserRole.DRIVER, nullable=False, comment="用户角色")
    status = Column(Enum(UserStatus), default=UserStatus.IDLE, nullable=False, comment="用户状态")
    
    # 司机相关字段（仅司机用户使用）
    driver_license = Column(String(50), nullable=True, comment="驾驶证号")
    vehicle_id = Column(Integer, nullable=True, comment="关联车辆ID")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 软删除标志
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    # 关系定义
    # 一个用户（司机）可以有多个运输任务
    transport_tasks = relationship("TransportTask", back_populates="driver", foreign_keys="TransportTask.driver_id")
    
    # 一个用户（调度员）可以分配多个运输任务
    assigned_tasks = relationship("TransportTask", back_populates="dispatcher", foreign_keys="TransportTask.dispatcher_id")
    
    # 一个用户可以有多个位置记录（司机）
    location_records = relationship("LocationRecord", back_populates="user")
    
    # 一个用户可以有多个任务更新记录
    task_updates = relationship("TaskUpdate", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

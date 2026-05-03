"""
预约模型
定义预约单表结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ReservationStatus(str, enum.Enum):
    """
    预约状态枚举
    PENDING: 待确认
    CONFIRMED: 已确认
    PAID: 已支付押金
    PICKED_UP: 已领取
    RETURNED: 已归还
    COMPLETED: 已完成
    CANCELLED: 已取消
    """
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    PICKED_UP = "picked_up"
    RETURNED = "returned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Reservation(Base):
    """
    预约模型类
    对应数据库中的reservations表
    """
    __tablename__ = "reservations"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="预约ID")
    
    # 预约单号（自动生成）
    reservation_no = Column(String(50), unique=True, index=True, nullable=False, comment="预约单号")
    
    # 用户ID（外键）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 产品ID（外键）
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="产品ID")
    
    # 预约开始日期
    start_date = Column(Date, nullable=False, comment="开始日期")
    
    # 预约结束日期
    end_date = Column(Date, nullable=False, comment="结束日期")
    
    # 租借天数
    rental_days = Column(Integer, nullable=False, comment="租借天数")
    
    # 数量
    quantity = Column(Integer, default=1, comment="数量")
    
    # 日租金单价
    daily_rent = Column(DECIMAL(10, 2), nullable=False, comment="日租金")
    
    # 租金总额
    total_rent = Column(DECIMAL(10, 2), nullable=False, comment="租金总额")
    
    # 押金金额
    deposit = Column(DECIMAL(10, 2), nullable=False, comment="押金金额")
    
    # 押金支付状态
    deposit_paid = Column(Boolean, default=False, comment="押金是否支付")
    
    # 押金支付时间
    deposit_paid_at = Column(DateTime, nullable=True, comment="押金支付时间")
    
    # 实际领取时间
    picked_up_at = Column(DateTime, nullable=True, comment="实际领取时间")
    
    # 实际归还时间
    returned_at = Column(DateTime, nullable=True, comment="实际归还时间")
    
    # 预约状态
    status = Column(String(20), default=ReservationStatus.PENDING, comment="预约状态")
    
    # 备注
    remark = Column(String(500), nullable=True, comment="备注")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 是否删除（软删除）
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    # 关联用户
    user = relationship("User")
    
    # 关联产品
    product = relationship("Product", back_populates="reservations")

    def to_dict(self):
        """
        将预约对象转换为字典
        """
        return {
            "id": self.id,
            "reservation_no": self.reservation_no,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "rental_days": self.rental_days,
            "quantity": self.quantity,
            "daily_rent": float(self.daily_rent) if self.daily_rent else 0,
            "total_rent": float(self.total_rent) if self.total_rent else 0,
            "deposit": float(self.deposit) if self.deposit else 0,
            "deposit_paid": self.deposit_paid,
            "deposit_paid_at": self.deposit_paid_at.isoformat() if self.deposit_paid_at else None,
            "picked_up_at": self.picked_up_at.isoformat() if self.picked_up_at else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "status": self.status,
            "remark": self.remark,
            "user_name": self.user.name if self.user else None,
            "user_phone": self.user.phone if self.user else None,
            "product_name": self.product.name if self.product else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

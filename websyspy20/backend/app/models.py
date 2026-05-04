"""
数据库模型定义
包含物业管理系统的所有数据模型
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import relationship

from app.database import Base


class FeeItem(Base):
    """
    费用项目表
    用于存储物业费、停车费、水电公摊、维修基金等收费项目
    """

    __tablename__ = "fee_items"

    id = Column(Integer, primary_key=True, index=True, comment="费用项目ID")
    name = Column(String(100), nullable=False, comment="费用项目名称")
    code = Column(String(50), unique=True, nullable=False, comment="费用项目编码")
    description = Column(Text, nullable=True, comment="费用项目描述")

    # 计费周期: monthly(月), quarterly(季), half_yearly(半年), yearly(年), one_time(一次性)
    billing_cycle = Column(String(20), default="monthly", comment="计费周期")

    # 计费标准: area(按面积), unit(按单位), fixed(固定金额)
    billing_type = Column(String(20), default="area", comment="计费标准类型")

    # 计费单价
    unit_price = Column(Numeric(10, 2), default=0, comment="单位价格")

    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联账单
    bills = relationship("Bill", back_populates="fee_item")


class Property(Base):
    """
    房产信息表
    存储业主房产的基本信息
    """

    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True, comment="房产ID")
    property_number = Column(String(50), unique=True, nullable=False, comment="房产编号")

    # 位置信息
    building = Column(String(50), nullable=True, comment="楼栋号")
    unit = Column(String(50), nullable=True, comment="单元号")
    room_number = Column(String(50), nullable=True, comment="房间号")

    # 房产属性
    area = Column(Numeric(10, 2), default=0, comment="建筑面积(平方米)")
    property_type = Column(String(50), default="住宅", comment="房产类型: 住宅/商铺/车位等")

    # 业主信息
    owner_name = Column(String(100), nullable=True, comment="业主姓名")
    owner_phone = Column(String(20), nullable=True, comment="业主电话")
    owner_id_card = Column(String(20), nullable=True, comment="业主身份证号")

    # 入住状态
    is_occupied = Column(Boolean, default=True, comment="是否入住")
    move_in_date = Column(Date, nullable=True, comment="入住日期")

    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 备注
    remark = Column(Text, nullable=True, comment="备注")

    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联账单
    bills = relationship("Bill", back_populates="property")


class Bill(Base):
    """
    账单表
    存储生成的账单信息
    """

    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True, comment="账单ID")
    bill_number = Column(String(50), unique=True, nullable=False, comment="账单编号")

    # 关联房产和费用项目
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, comment="房产ID")
    fee_item_id = Column(Integer, ForeignKey("fee_items.id"), nullable=False, comment="费用项目ID")

    # 账单周期
    billing_year = Column(Integer, nullable=False, comment="计费年份")
    billing_month = Column(Integer, nullable=False, comment="计费月份")

    # 费用明细
    amount = Column(Numeric(10, 2), default=0, comment="账单金额")
    paid_amount = Column(Numeric(10, 2), default=0, comment="已付金额")

    # 账单状态: pending(待缴费), partial(部分缴费), paid(已缴费), overdue(逾期), cancelled(已取消)
    status = Column(String(20), default="pending", comment="账单状态")

    # 缴费截止日期
    due_date = Column(Date, nullable=True, comment="缴费截止日期")

    # 生成时间和支付时间
    generated_at = Column(DateTime, default=datetime.now, comment="账单生成时间")
    paid_at = Column(DateTime, nullable=True, comment="支付时间")

    # 支付方式: cash(现金), wechat(微信), alipay(支付宝), bank_transfer(银行转账), other(其他)
    payment_method = Column(String(20), nullable=True, comment="支付方式")

    # 备注
    remark = Column(Text, nullable=True, comment="备注")

    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    property = relationship("Property", back_populates="bills")
    fee_item = relationship("FeeItem", back_populates="bills")
    payment_records = relationship("PaymentRecord", back_populates="bill")
    reminders = relationship("Reminder", back_populates="bill")
    invoices = relationship("Invoice", back_populates="bill")


class PaymentRecord(Base):
    """
    缴费记录表
    存储每次缴费的详细记录
    """

    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    record_number = Column(String(50), unique=True, nullable=False, comment="记录编号")

    # 关联账单
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, comment="账单ID")

    # 缴费信息
    amount = Column(Numeric(10, 2), default=0, comment="缴费金额")

    # 支付方式: cash(现金), wechat(微信), alipay(支付宝), bank_transfer(银行转账), other(其他)
    payment_method = Column(String(20), default="cash", comment="支付方式")

    # 支付详情
    transaction_id = Column(String(100), nullable=True, comment="交易流水号")
    paid_at = Column(DateTime, default=datetime.now, comment="支付时间")

    # 收款人信息
    collector = Column(String(50), nullable=True, comment="收款人")

    # 备注
    remark = Column(Text, nullable=True, comment="备注")

    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    bill = relationship("Bill", back_populates="payment_records")


class Reminder(Base):
    """
    催缴记录表
    存储催缴通知的发送记录
    """

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")

    # 关联账单
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, comment="账单ID")

    # 催缴方式: sms(短信), phone(电话), notice(通知单), wechat(微信)
    method = Column(String(20), default="notice", comment="催缴方式")

    # 催缴次数
    reminder_count = Column(Integer, default=1, comment="催缴次数")

    # 催缴内容
    content = Column(Text, nullable=True, comment="催缴内容")

    # 催缴时间
    reminded_at = Column(DateTime, default=datetime.now, comment="催缴时间")

    # 执行人
    operator = Column(String(50), nullable=True, comment="执行人")

    # 备注
    remark = Column(Text, nullable=True, comment="备注")

    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    bill = relationship("Bill", back_populates="reminders")


class Invoice(Base):
    """
    票据表
    存储电子发票或收据信息
    """

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, comment="票据ID")
    invoice_number = Column(String(50), unique=True, nullable=False, comment="票据编号")

    # 关联账单
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, comment="账单ID")

    # 票据类型: receipt(收据), invoice(发票)
    invoice_type = Column(String(20), default="receipt", comment="票据类型")

    # 金额信息
    amount = Column(Numeric(10, 2), default=0, comment="票据金额")

    # 开票信息
    invoice_title = Column(String(200), nullable=True, comment="发票抬头")
    tax_number = Column(String(50), nullable=True, comment="税号")

    # 开票时间
    issued_at = Column(DateTime, default=datetime.now, comment="开票时间")

    # 开票人
    issuer = Column(String(50), nullable=True, comment="开票人")

    # 票据状态: pending(待开具), issued(已开具), voided(已作废)
    status = Column(String(20), default="pending", comment="票据状态")

    # 备注
    remark = Column(Text, nullable=True, comment="备注")

    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    bill = relationship("Bill", back_populates="invoices")

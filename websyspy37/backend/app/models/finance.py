"""
财务模块数据模型
包含账户、收入、支出、发票等模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.config import Base


class Account(Base):
    """
    账户模型
    存储账户基本信息
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, comment="账户ID")
    account_no = Column(String(50), unique=True, nullable=False, comment="账户编号")
    name = Column(String(100), nullable=False, comment="账户名称")
    type = Column(String(20), default="银行账户", comment="账户类型：银行账户/现金账户/支付宝/微信/其他")
    bank_name = Column(String(100), comment="银行名称")
    bank_account = Column(String(50), comment="银行账号")
    balance = Column(Float, default=0.0, comment="账户余额")
    description = Column(Text, comment="账户描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个账户可以有多个收入记录
    incomes = relationship("Income", back_populates="account")
    # 关系：一个账户可以有多个支出记录
    expenses = relationship("Expense", back_populates="account")


class Income(Base):
    """
    收入模型
    存储收入记录
    """
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True, comment="收入ID")
    income_no = Column(String(50), unique=True, nullable=False, comment="收入编号")
    account_id = Column(Integer, ForeignKey("accounts.id"), comment="账户ID")
    income_date = Column(Date, default=date.today, comment="收入日期")
    amount = Column(Float, nullable=False, comment="收入金额")
    category = Column(String(50), comment="收入类别：销售收入/服务收入/投资收益/其他收入")
    source = Column(String(100), comment="收入来源")
    description = Column(Text, comment="收入描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：收入属于一个账户
    account = relationship("Account", back_populates="incomes")


class Expense(Base):
    """
    支出模型
    存储支出记录
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, comment="支出ID")
    expense_no = Column(String(50), unique=True, nullable=False, comment="支出编号")
    account_id = Column(Integer, ForeignKey("accounts.id"), comment="账户ID")
    expense_date = Column(Date, default=date.today, comment="支出日期")
    amount = Column(Float, nullable=False, comment="支出金额")
    category = Column(String(50), comment="支出类别：采购成本/人工成本/办公费用/营销费用/其他支出")
    recipient = Column(String(100), comment="收款方")
    description = Column(Text, comment="支出描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：支出属于一个账户
    account = relationship("Account", back_populates="expenses")


class Invoice(Base):
    """
    发票模型
    存储发票信息
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, comment="发票ID")
    invoice_no = Column(String(50), unique=True, nullable=False, comment="发票编号")
    type = Column(String(20), default="销售发票", comment="发票类型：销售发票/采购发票")
    invoice_date = Column(Date, default=date.today, comment="发票日期")
    amount = Column(Float, nullable=False, comment="发票金额")
    tax_amount = Column(Float, default=0.0, comment="税额")
    total_amount = Column(Float, nullable=False, comment="价税合计")
    party_name = Column(String(100), comment="对方名称")
    party_tax_no = Column(String(50), comment="对方税号")
    status = Column(String(20), default="待开票", comment="状态：待开票/已开票/已作废")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

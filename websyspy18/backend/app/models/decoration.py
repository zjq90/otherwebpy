"""
装修管理模块 - 数据模型
包含装修申请、施工记录、押金管理等模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class DecorationApplication(Base):
    """
    装修申请表
    记录业主装修申请的基本信息
    """
    __tablename__ = "decoration_applications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_no = Column(String(50), unique=True, index=True, comment="申请编号")
    room_number = Column(String(50), nullable=False, comment="房间号")
    owner_name = Column(String(50), nullable=False, comment="业主姓名")
    owner_phone = Column(String(20), comment="业主联系电话")
    decoration_company = Column(String(100), comment="装修公司名称")
    company_contact = Column(String(50), comment="装修公司联系人")
    company_phone = Column(String(20), comment="装修公司联系电话")
    decoration_type = Column(String(50), comment="装修类型（简装、精装、豪装）")
    estimated_start_date = Column(Date, comment="预计开工日期")
    estimated_end_date = Column(Date, comment="预计竣工日期")
    decoration_scope = Column(Text, comment="装修范围说明")
    special_requirements = Column(Text, comment="特殊要求")
    application_date = Column(Date, default=datetime.now, comment="申请日期")
    status = Column(String(20), default="待审批", comment="申请状态（待审批、已通过、已驳回、已完成）")
    approval_opinion = Column(Text, comment="审批意见")
    approved_by = Column(String(50), comment="审批人")
    approval_date = Column(Date, comment="审批日期")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    deposits = relationship("DecorationDeposit", back_populates="application")
    inspections = relationship("DecorationInspection", back_populates="application")

class DecorationDeposit(Base):
    """
    装修押金记录表
    记录装修押金的缴纳和退还情况
    """
    __tablename__ = "decoration_deposits"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("decoration_applications.id"), nullable=False, comment="装修申请ID")
    deposit_type = Column(String(50), comment="押金类型（装修押金、垃圾清运费、出入证押金等）")
    amount = Column(Float, nullable=False, comment="押金金额")
    paid_date = Column(Date, comment="缴纳日期")
    paid_by = Column(String(50), comment="缴纳人")
    receipt_no = Column(String(50), comment="收据编号")
    refund_date = Column(Date, comment="退还日期")
    refund_amount = Column(Float, comment="退还金额")
    refund_by = Column(String(50), comment="退还经办人")
    deduction_reason = Column(Text, comment="扣款原因")
    deduction_amount = Column(Float, default=0, comment="扣款金额")
    status = Column(String(20), default="待缴纳", comment="状态（待缴纳、已缴纳、已退还、部分退还）")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    application = relationship("DecorationApplication", back_populates="deposits")

class DecorationInspection(Base):
    """
    装修巡检记录表
    记录装修过程中的巡检情况
    """
    __tablename__ = "decoration_inspections"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("decoration_applications.id"), nullable=False, comment="装修申请ID")
    inspection_date = Column(Date, nullable=False, comment="巡检日期")
    inspector = Column(String(50), comment="巡检人")
    inspection_items = Column(Text, comment="巡检项目（JSON格式）")
    result = Column(String(20), default="正常", comment="巡检结果（正常、异常）")
    issues_found = Column(Text, comment="发现的问题")
    rectification_requirements = Column(Text, comment="整改要求")
    rectification_deadline = Column(Date, comment="整改期限")
    is_rectified = Column(Boolean, default=False, comment="是否已整改")
    rectification_date = Column(Date, comment="整改完成日期")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    application = relationship("DecorationApplication", back_populates="inspections")

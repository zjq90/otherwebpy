"""
合同与供应商管理模块 - 数据模型
包含合同管理、供应商管理、服务质量评估等模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Supplier(Base):
    """
    供应商模型
    记录外包公司（如保洁、安保）的基本信息
    """
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="供应商名称")
    code = Column(String(50), unique=True, index=True, comment="供应商编号")
    category = Column(String(50), comment="供应商类别（保洁、安保、绿化、维修等）")
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    address = Column(String(200), comment="公司地址")
    business_license = Column(String(100), comment="营业执照编号")
    qualification_level = Column(String(50), comment="资质等级")
    description = Column(Text, comment="公司简介")
    status = Column(String(20), default="合作中", comment="状态（合作中、已终止、黑名单）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    contracts = relationship("Contract", back_populates="supplier")
    evaluations = relationship("ServiceEvaluation", back_populates="supplier")

class Contract(Base):
    """
    合同模型
    记录物业与供应商之间的合同信息
    """
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_no = Column(String(50), unique=True, index=True, comment="合同编号")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    contract_name = Column(String(200), nullable=False, comment="合同名称")
    contract_type = Column(String(50), comment="合同类型（保洁服务、安保服务、绿化服务等）")
    start_date = Column(Date, comment="合同开始日期")
    end_date = Column(Date, comment="合同结束日期")
    total_amount = Column(Float, comment="合同总金额")
    payment_method = Column(String(100), comment="付款方式")
    payment_cycle = Column(String(50), comment="付款周期（月付、季付、年付）")
    contract_content = Column(Text, comment="合同内容")
    attachment = Column(String(200), comment="合同附件路径")
    sign_date = Column(Date, comment="签订日期")
    signatory_party_a = Column(String(50), comment="甲方签字人")
    signatory_party_b = Column(String(50), comment="乙方签字人")
    status = Column(String(20), default="执行中", comment="合同状态（待执行、执行中、已到期、已终止）")
    renewal_reminder = Column(Integer, default=30, comment="续约提醒天数")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    supplier = relationship("Supplier", back_populates="contracts")
    payments = relationship("ContractPayment", back_populates="contract")

class ContractPayment(Base):
    """
    合同付款记录表
    记录合同的付款情况
    """
    __tablename__ = "contract_payments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, comment="合同ID")
    payment_no = Column(String(50), unique=True, index=True, comment="付款编号")
    payment_period = Column(String(50), comment="付款周期（如：2024年第一季度）")
    amount = Column(Float, nullable=False, comment="付款金额")
    due_date = Column(Date, comment="到期日期")
    actual_date = Column(Date, comment="实际付款日期")
    payment_method = Column(String(50), comment="付款方式")
    invoice_no = Column(String(50), comment="发票编号")
    status = Column(String(20), default="待付款", comment="状态（待付款、已付款、已逾期）")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    contract = relationship("Contract", back_populates="payments")

class ServiceEvaluation(Base):
    """
    服务质量评估表
    记录对供应商服务质量的评估
    """
    __tablename__ = "service_evaluations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    evaluation_date = Column(Date, nullable=False, comment="评估日期")
    evaluation_period = Column(String(50), comment="评估周期（如：2024年第一季度）")
    evaluator = Column(String(50), comment="评估人")
    
    # 各项评分（1-5分）
    service_quality_score = Column(Integer, comment="服务质量评分")
    response_speed_score = Column(Integer, comment="响应速度评分")
    personnel_quality_score = Column(Integer, comment="人员素质评分")
    compliance_score = Column(Integer, comment="合规性评分")
    cost_effectiveness_score = Column(Integer, comment="性价比评分")
    
    total_score = Column(Float, comment="综合评分")
    level = Column(String(20), comment="评估等级（优秀、良好、合格、不合格）")
    advantages = Column(Text, comment="优点")
    disadvantages = Column(Text, comment="缺点")
    improvement_suggestions = Column(Text, comment="改进建议")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    supplier = relationship("Supplier", back_populates="evaluations")

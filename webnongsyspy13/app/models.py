"""
数据库模型定义模块
定义所有数据库表的ORM模型，包括：
- 农产品 (Product)
- 批次 (Batch)
- 种植记录 (PlantingRecord)
- 农资使用 (AgrochemicalUsage)
- 检测结果 (TestResult)
- 认证证书 (Certificate)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Product(Base):
    """
    农产品模型
    存储农产品的基本信息
    """
    __tablename__ = "products"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    # 产品名称
    name = Column(String(100), nullable=False, index=True, comment="产品名称")
    # 产品类别（蔬菜、水果、谷物等）
    category = Column(String(50), comment="产品类别")
    # 产品描述
    description = Column(Text, comment="产品描述")
    # 产地
    origin = Column(String(200), comment="产地")
    # 种植者/供应商
    supplier = Column(String(100), comment="供应商")
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系：一个产品可以有多个批次
    batches = relationship("Batch", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class Batch(Base):
    """
    批次模型
    存储每批农产品的详细信息，包括二维码
    """
    __tablename__ = "batches"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="批次ID")
    # 批次编号（唯一）
    batch_number = Column(String(50), unique=True, nullable=False, index=True, comment="批次编号")
    # 关联的产品ID
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="产品ID")
    # 批次数量
    quantity = Column(Float, comment="数量")
    # 单位（公斤、吨、个等）
    unit = Column(String(20), default="公斤", comment="单位")
    # 种植开始日期
    planting_date = Column(Date, comment="种植开始日期")
    # 收获日期
    harvest_date = Column(Date, comment="收获日期")
    # 二维码内容（通常是URL）
    qrcode_content = Column(Text, comment="二维码内容")
    # 二维码图片路径
    qrcode_path = Column(String(200), comment="二维码图片路径")
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系：关联产品
    product = relationship("Product", back_populates="batches")
    # 关系：一个批次可以有多个种植记录
    planting_records = relationship("PlantingRecord", back_populates="batch")
    # 关系：一个批次可以有多个农资使用记录
    agrochemical_usages = relationship("AgrochemicalUsage", back_populates="batch")
    # 关系：一个批次可以有多个检测结果
    test_results = relationship("TestResult", back_populates="batch")
    
    def __repr__(self):
        return f"<Batch(id={self.id}, batch_number='{self.batch_number}')>"


class PlantingRecord(Base):
    """
    种植记录模型
    记录农产品的种植过程信息
    """
    __tablename__ = "planting_records"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    # 关联的批次ID
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True, comment="批次ID")
    # 记录日期
    record_date = Column(Date, nullable=False, comment="记录日期")
    # 操作类型（播种、施肥、浇水、除草、病虫害防治等）
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    # 详细描述
    description = Column(Text, comment="详细描述")
    # 操作人员
    operator = Column(String(50), comment="操作人员")
    # 备注
    remarks = Column(Text, comment="备注")
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系：关联批次
    batch = relationship("Batch", back_populates="planting_records")
    
    def __repr__(self):
        return f"<PlantingRecord(id={self.id}, batch_id={self.batch_id})>"


class AgrochemicalUsage(Base):
    """
    农资使用记录模型
    记录农药、化肥等农资的使用情况
    """
    __tablename__ = "agrochemical_usages"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    # 关联的批次ID
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True, comment="批次ID")
    # 使用日期
    usage_date = Column(Date, nullable=False, comment="使用日期")
    # 农资类型（农药、化肥、除草剂等）
    chemical_type = Column(String(50), nullable=False, comment="农资类型")
    # 农资名称
    chemical_name = Column(String(100), nullable=False, comment="农资名称")
    # 使用量
    quantity = Column(Float, comment="使用量")
    # 单位
    unit = Column(String(20), comment="单位")
    # 使用方法（喷雾、撒施、浇灌等）
    usage_method = Column(String(100), comment="使用方法")
    # 安全间隔期（天数）
    safety_interval = Column(Integer, comment="安全间隔期(天)")
    # 操作人员
    operator = Column(String(50), comment="操作人员")
    # 备注
    remarks = Column(Text, comment="备注")
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系：关联批次
    batch = relationship("Batch", back_populates="agrochemical_usages")
    
    def __repr__(self):
        return f"<AgrochemicalUsage(id={self.id}, chemical_name='{self.chemical_name}')>"


class TestResult(Base):
    """
    检测结果模型
    记录自检或第三方检测结果
    """
    __tablename__ = "test_results"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="检测ID")
    # 关联的批次ID
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True, comment="批次ID")
    # 检测类型（自检、第三方检测）
    test_type = Column(String(20), nullable=False, comment="检测类型")
    # 检测机构名称
    test_organization = Column(String(100), comment="检测机构")
    # 检测日期
    test_date = Column(Date, nullable=False, comment="检测日期")
    # 检测项目（农残、重金属、微生物等）
    test_item = Column(String(50), comment="检测项目")
    # 检测参数名称
    parameter_name = Column(String(100), nullable=False, comment="检测参数")
    # 检测值
    test_value = Column(String(100), comment="检测值")
    # 标准限值
    limit_value = Column(String(100), comment="标准限值")
    # 检测结果（合格/不合格）
    result = Column(String(20), nullable=False, comment="检测结果")
    # 检测报告编号
    report_number = Column(String(100), comment="报告编号")
    # 检测人员
    tester = Column(String(50), comment="检测人员")
    # 备注
    remarks = Column(Text, comment="备注")
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系：关联批次
    batch = relationship("Batch", back_populates="test_results")
    
    def __repr__(self):
        return f"<TestResult(id={self.id}, parameter_name='{self.parameter_name}')>"


class Certificate(Base):
    """
    认证证书模型
    管理绿色食品、有机产品等认证证书
    """
    __tablename__ = "certificates"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="证书ID")
    # 关联的产品ID
    product_id = Column(Integer, ForeignKey("products.id"), index=True, comment="产品ID")
    # 证书编号（唯一）
    certificate_number = Column(String(100), unique=True, nullable=False, index=True, comment="证书编号")
    # 认证类型（绿色食品、有机产品、无公害产品等）
    certificate_type = Column(String(50), nullable=False, comment="认证类型")
    # 认证机构名称
    issuing_organization = Column(String(100), nullable=False, comment="发证机构")
    # 发证日期
    issue_date = Column(Date, nullable=False, comment="发证日期")
    # 有效期至
    valid_until = Column(Date, nullable=False, comment="有效期至")
    # 证书状态（有效、过期、即将过期）
    status = Column(String(20), default="有效", comment="证书状态")
    # 是否已提醒续证
    is_reminded = Column(Boolean, default=False, comment="是否已提醒续证")
    # 证书持有人
    holder = Column(String(100), comment="证书持有人")
    # 认证范围
    scope = Column(Text, comment="认证范围")
    # 备注
    remarks = Column(Text, comment="备注")
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, certificate_number='{self.certificate_number}')>"

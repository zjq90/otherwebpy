"""
Pydantic数据验证模型模块
定义API请求和响应的数据结构，用于数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class TestTypeEnum(str, Enum):
    """检测类型枚举"""
    SELF_TEST = "自检"
    THIRD_PARTY = "第三方检测"


class CertificateTypeEnum(str, Enum):
    """认证类型枚举"""
    GREEN = "绿色食品"
    ORGANIC = "有机产品"
    POLLUTION_FREE = "无公害产品"
    GEOGRAPHIC_INDICATION = "地理标志产品"


class CertificateStatusEnum(str, Enum):
    """证书状态枚举"""
    VALID = "有效"
    EXPIRING = "即将过期"
    EXPIRED = "过期"


class ProductBase(BaseModel):
    """产品基础模型"""
    name: str = Field(..., title="产品名称", max_length=100)
    category: Optional[str] = Field(None, title="产品类别", max_length=50)
    description: Optional[str] = Field(None, title="产品描述")
    origin: Optional[str] = Field(None, title="产地", max_length=200)
    supplier: Optional[str] = Field(None, title="供应商", max_length=100)


class ProductCreate(ProductBase):
    """产品创建模型"""
    pass


class ProductUpdate(BaseModel):
    """产品更新模型"""
    name: Optional[str] = Field(None, title="产品名称", max_length=100)
    category: Optional[str] = Field(None, title="产品类别", max_length=50)
    description: Optional[str] = Field(None, title="产品描述")
    origin: Optional[str] = Field(None, title="产地", max_length=200)
    supplier: Optional[str] = Field(None, title="供应商", max_length=100)


class Product(ProductBase):
    """产品响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BatchBase(BaseModel):
    """批次基础模型"""
    batch_number: str = Field(..., title="批次编号", max_length=50)
    product_id: int = Field(..., title="产品ID")
    quantity: Optional[float] = Field(None, title="数量")
    unit: Optional[str] = Field("公斤", title="单位", max_length=20)
    planting_date: Optional[date] = Field(None, title="种植开始日期")
    harvest_date: Optional[date] = Field(None, title="收获日期")


class BatchCreate(BatchBase):
    """批次创建模型"""
    pass


class BatchUpdate(BaseModel):
    """批次更新模型"""
    batch_number: Optional[str] = Field(None, title="批次编号", max_length=50)
    product_id: Optional[int] = Field(None, title="产品ID")
    quantity: Optional[float] = Field(None, title="数量")
    unit: Optional[str] = Field(None, title="单位", max_length=20)
    planting_date: Optional[date] = Field(None, title="种植开始日期")
    harvest_date: Optional[date] = Field(None, title="收获日期")


class Batch(BatchBase):
    """批次响应模型"""
    id: int
    qrcode_content: Optional[str] = None
    qrcode_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True


class BatchWithDetails(Batch):
    """批次详情模型（包含关联数据）"""
    planting_records: List["PlantingRecord"] = []
    agrochemical_usages: List["AgrochemicalUsage"] = []
    test_results: List["TestResult"] = []


class PlantingRecordBase(BaseModel):
    """种植记录基础模型"""
    batch_id: int = Field(..., title="批次ID")
    record_date: date = Field(..., title="记录日期")
    operation_type: str = Field(..., title="操作类型", max_length=50)
    description: Optional[str] = Field(None, title="详细描述")
    operator: Optional[str] = Field(None, title="操作人员", max_length=50)
    remarks: Optional[str] = Field(None, title="备注")


class PlantingRecordCreate(PlantingRecordBase):
    """种植记录创建模型"""
    pass


class PlantingRecordUpdate(BaseModel):
    """种植记录更新模型"""
    batch_id: Optional[int] = Field(None, title="批次ID")
    record_date: Optional[date] = Field(None, title="记录日期")
    operation_type: Optional[str] = Field(None, title="操作类型", max_length=50)
    description: Optional[str] = Field(None, title="详细描述")
    operator: Optional[str] = Field(None, title="操作人员", max_length=50)
    remarks: Optional[str] = Field(None, title="备注")


class PlantingRecord(PlantingRecordBase):
    """种植记录响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgrochemicalUsageBase(BaseModel):
    """农资使用记录基础模型"""
    batch_id: int = Field(..., title="批次ID")
    usage_date: date = Field(..., title="使用日期")
    chemical_type: str = Field(..., title="农资类型", max_length=50)
    chemical_name: str = Field(..., title="农资名称", max_length=100)
    quantity: Optional[float] = Field(None, title="使用量")
    unit: Optional[str] = Field(None, title="单位", max_length=20)
    usage_method: Optional[str] = Field(None, title="使用方法", max_length=100)
    safety_interval: Optional[int] = Field(None, title="安全间隔期(天)")
    operator: Optional[str] = Field(None, title="操作人员", max_length=50)
    remarks: Optional[str] = Field(None, title="备注")


class AgrochemicalUsageCreate(AgrochemicalUsageBase):
    """农资使用记录创建模型"""
    pass


class AgrochemicalUsageUpdate(BaseModel):
    """农资使用记录更新模型"""
    batch_id: Optional[int] = Field(None, title="批次ID")
    usage_date: Optional[date] = Field(None, title="使用日期")
    chemical_type: Optional[str] = Field(None, title="农资类型", max_length=50)
    chemical_name: Optional[str] = Field(None, title="农资名称", max_length=100)
    quantity: Optional[float] = Field(None, title="使用量")
    unit: Optional[str] = Field(None, title="单位", max_length=20)
    usage_method: Optional[str] = Field(None, title="使用方法", max_length=100)
    safety_interval: Optional[int] = Field(None, title="安全间隔期(天)")
    operator: Optional[str] = Field(None, title="操作人员", max_length=50)
    remarks: Optional[str] = Field(None, title="备注")


class AgrochemicalUsage(AgrochemicalUsageBase):
    """农资使用记录响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TestResultBase(BaseModel):
    """检测结果基础模型"""
    batch_id: int = Field(..., title="批次ID")
    test_type: str = Field(..., title="检测类型")
    test_organization: Optional[str] = Field(None, title="检测机构", max_length=100)
    test_date: date = Field(..., title="检测日期")
    test_item: Optional[str] = Field(None, title="检测项目", max_length=50)
    parameter_name: str = Field(..., title="检测参数", max_length=100)
    test_value: Optional[str] = Field(None, title="检测值", max_length=100)
    limit_value: Optional[str] = Field(None, title="标准限值", max_length=100)
    result: str = Field(..., title="检测结果", max_length=20)
    report_number: Optional[str] = Field(None, title="报告编号", max_length=100)
    tester: Optional[str] = Field(None, title="检测人员", max_length=50)
    remarks: Optional[str] = Field(None, title="备注")


class TestResultCreate(TestResultBase):
    """检测结果创建模型"""
    pass


class TestResultUpdate(BaseModel):
    """检测结果更新模型"""
    batch_id: Optional[int] = Field(None, title="批次ID")
    test_type: Optional[str] = Field(None, title="检测类型")
    test_organization: Optional[str] = Field(None, title="检测机构", max_length=100)
    test_date: Optional[date] = Field(None, title="检测日期")
    test_item: Optional[str] = Field(None, title="检测项目", max_length=50)
    parameter_name: Optional[str] = Field(None, title="检测参数", max_length=100)
    test_value: Optional[str] = Field(None, title="检测值", max_length=100)
    limit_value: Optional[str] = Field(None, title="标准限值", max_length=100)
    result: Optional[str] = Field(None, title="检测结果", max_length=20)
    report_number: Optional[str] = Field(None, title="报告编号", max_length=100)
    tester: Optional[str] = Field(None, title="检测人员", max_length=50)
    remarks: Optional[str] = Field(None, title="备注")


class TestResult(TestResultBase):
    """检测结果响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CertificateBase(BaseModel):
    """认证证书基础模型"""
    product_id: Optional[int] = Field(None, title="产品ID")
    certificate_number: str = Field(..., title="证书编号", max_length=100)
    certificate_type: str = Field(..., title="认证类型", max_length=50)
    issuing_organization: str = Field(..., title="发证机构", max_length=100)
    issue_date: date = Field(..., title="发证日期")
    valid_until: date = Field(..., title="有效期至")
    status: str = Field("有效", title="证书状态", max_length=20)
    holder: Optional[str] = Field(None, title="证书持有人", max_length=100)
    scope: Optional[str] = Field(None, title="认证范围")
    remarks: Optional[str] = Field(None, title="备注")


class CertificateCreate(CertificateBase):
    """认证证书创建模型"""
    pass


class CertificateUpdate(BaseModel):
    """认证证书更新模型"""
    product_id: Optional[int] = Field(None, title="产品ID")
    certificate_number: Optional[str] = Field(None, title="证书编号", max_length=100)
    certificate_type: Optional[str] = Field(None, title="认证类型", max_length=50)
    issuing_organization: Optional[str] = Field(None, title="发证机构", max_length=100)
    issue_date: Optional[date] = Field(None, title="发证日期")
    valid_until: Optional[date] = Field(None, title="有效期至")
    status: Optional[str] = Field(None, title="证书状态", max_length=20)
    is_reminded: Optional[bool] = Field(None, title="是否已提醒续证")
    holder: Optional[str] = Field(None, title="证书持有人", max_length=100)
    scope: Optional[str] = Field(None, title="认证范围")
    remarks: Optional[str] = Field(None, title="备注")


class Certificate(CertificateBase):
    """认证证书响应模型"""
    id: int
    is_reminded: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TraceabilityInfo(BaseModel):
    """溯源信息模型"""
    batch: Batch
    product: Product
    planting_records: List[PlantingRecord] = []
    agrochemical_usages: List[AgrochemicalUsage] = []
    test_results: List[TestResult] = []


BatchWithDetails.model_rebuild()

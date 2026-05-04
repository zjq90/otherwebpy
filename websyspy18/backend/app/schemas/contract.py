"""
合同与供应商管理模块 - Pydantic Schema
定义合同管理相关API的请求和响应数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

# ==================== 供应商相关 Schema ====================

class SupplierBase(BaseModel):
    """
    供应商基础Schema
    """
    name: str = Field(..., min_length=1, max_length=100, description="供应商名称")
    code: Optional[str] = Field(None, max_length=50, description="供应商编号")
    category: Optional[str] = Field(None, max_length=50, description="供应商类别")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, max_length=200, description="公司地址")
    business_license: Optional[str] = Field(None, max_length=100, description="营业执照编号")
    qualification_level: Optional[str] = Field(None, max_length=50, description="资质等级")
    description: Optional[str] = Field(None, description="公司简介")
    status: Optional[str] = Field("合作中", max_length=20, description="状态")

class SupplierCreate(SupplierBase):
    """
    创建供应商Schema
    """
    pass

class SupplierUpdate(BaseModel):
    """
    更新供应商Schema
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=50)
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=200)
    business_license: Optional[str] = Field(None, max_length=100)
    qualification_level: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)

class SupplierResponse(SupplierBase):
    """
    供应商响应Schema
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 合同相关 Schema ====================

class ContractBase(BaseModel):
    """
    合同基础Schema
    """
    contract_no: Optional[str] = Field(None, max_length=50, description="合同编号")
    supplier_id: int = Field(..., description="供应商ID")
    contract_name: str = Field(..., min_length=1, max_length=200, description="合同名称")
    contract_type: Optional[str] = Field(None, max_length=50, description="合同类型")
    start_date: Optional[date] = Field(None, description="合同开始日期")
    end_date: Optional[date] = Field(None, description="合同结束日期")
    total_amount: Optional[float] = Field(None, description="合同总金额")
    payment_method: Optional[str] = Field(None, max_length=100, description="付款方式")
    payment_cycle: Optional[str] = Field(None, max_length=50, description="付款周期")
    contract_content: Optional[str] = Field(None, description="合同内容")
    attachment: Optional[str] = Field(None, max_length=200, description="合同附件路径")
    sign_date: Optional[date] = Field(None, description="签订日期")
    signatory_party_a: Optional[str] = Field(None, max_length=50, description="甲方签字人")
    signatory_party_b: Optional[str] = Field(None, max_length=50, description="乙方签字人")
    status: Optional[str] = Field("执行中", max_length=20, description="合同状态")
    renewal_reminder: Optional[int] = Field(30, description="续约提醒天数")
    description: Optional[str] = Field(None, description="备注")

class ContractCreate(ContractBase):
    """
    创建合同Schema
    """
    pass

class ContractUpdate(BaseModel):
    """
    更新合同Schema
    """
    contract_name: Optional[str] = Field(None, min_length=1, max_length=200)
    contract_type: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = Field(None, max_length=100)
    payment_cycle: Optional[str] = Field(None, max_length=50)
    contract_content: Optional[str] = None
    attachment: Optional[str] = Field(None, max_length=200)
    sign_date: Optional[date] = None
    signatory_party_a: Optional[str] = Field(None, max_length=50)
    signatory_party_b: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    renewal_reminder: Optional[int] = None
    description: Optional[str] = None

class ContractResponse(ContractBase):
    """
    合同响应Schema
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 合同付款相关 Schema ====================

class ContractPaymentBase(BaseModel):
    """
    合同付款基础Schema
    """
    contract_id: int = Field(..., description="合同ID")
    payment_no: Optional[str] = Field(None, max_length=50, description="付款编号")
    payment_period: Optional[str] = Field(None, max_length=50, description="付款周期")
    amount: float = Field(..., gt=0, description="付款金额")
    due_date: Optional[date] = Field(None, description="到期日期")
    actual_date: Optional[date] = Field(None, description="实际付款日期")
    payment_method: Optional[str] = Field(None, max_length=50, description="付款方式")
    invoice_no: Optional[str] = Field(None, max_length=50, description="发票编号")
    status: Optional[str] = Field("待付款", max_length=20, description="状态")
    description: Optional[str] = Field(None, description="备注")

class ContractPaymentCreate(ContractPaymentBase):
    """
    创建合同付款Schema
    """
    pass

class ContractPaymentUpdate(BaseModel):
    """
    更新合同付款Schema
    """
    payment_period: Optional[str] = Field(None, max_length=50)
    amount: Optional[float] = None
    due_date: Optional[date] = None
    actual_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    invoice_no: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None

class ContractPaymentResponse(ContractPaymentBase):
    """
    合同付款响应Schema
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 服务质量评估相关 Schema ====================

class ServiceEvaluationBase(BaseModel):
    """
    服务质量评估基础Schema
    """
    supplier_id: int = Field(..., description="供应商ID")
    evaluation_date: date = Field(..., description="评估日期")
    evaluation_period: Optional[str] = Field(None, max_length=50, description="评估周期")
    evaluator: Optional[str] = Field(None, max_length=50, description="评估人")
    service_quality_score: Optional[int] = Field(None, ge=1, le=5, description="服务质量评分")
    response_speed_score: Optional[int] = Field(None, ge=1, le=5, description="响应速度评分")
    personnel_quality_score: Optional[int] = Field(None, ge=1, le=5, description="人员素质评分")
    compliance_score: Optional[int] = Field(None, ge=1, le=5, description="合规性评分")
    cost_effectiveness_score: Optional[int] = Field(None, ge=1, le=5, description="性价比评分")
    total_score: Optional[float] = Field(None, description="综合评分")
    level: Optional[str] = Field(None, max_length=20, description="评估等级")
    advantages: Optional[str] = Field(None, description="优点")
    disadvantages: Optional[str] = Field(None, description="缺点")
    improvement_suggestions: Optional[str] = Field(None, description="改进建议")
    description: Optional[str] = Field(None, description="备注")

class ServiceEvaluationCreate(ServiceEvaluationBase):
    """
    创建服务质量评估Schema
    """
    pass

class ServiceEvaluationUpdate(BaseModel):
    """
    更新服务质量评估Schema
    """
    evaluation_date: Optional[date] = None
    evaluation_period: Optional[str] = Field(None, max_length=50)
    evaluator: Optional[str] = Field(None, max_length=50)
    service_quality_score: Optional[int] = Field(None, ge=1, le=5)
    response_speed_score: Optional[int] = Field(None, ge=1, le=5)
    personnel_quality_score: Optional[int] = Field(None, ge=1, le=5)
    compliance_score: Optional[int] = Field(None, ge=1, le=5)
    cost_effectiveness_score: Optional[int] = Field(None, ge=1, le=5)
    total_score: Optional[float] = None
    level: Optional[str] = Field(None, max_length=20)
    advantages: Optional[str] = None
    disadvantages: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    description: Optional[str] = None

class ServiceEvaluationResponse(ServiceEvaluationBase):
    """
    服务质量评估响应Schema
    """
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

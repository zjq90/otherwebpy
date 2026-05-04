"""
装修管理模块 - Pydantic Schema
定义装修管理相关API的请求和响应数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

# ==================== 装修申请相关 Schema ====================

class DecorationApplicationBase(BaseModel):
    """
    装修申请基础Schema
    """
    application_no: Optional[str] = Field(None, max_length=50, description="申请编号")
    room_number: str = Field(..., min_length=1, max_length=50, description="房间号")
    owner_name: str = Field(..., min_length=1, max_length=50, description="业主姓名")
    owner_phone: Optional[str] = Field(None, max_length=20, description="业主联系电话")
    decoration_company: Optional[str] = Field(None, max_length=100, description="装修公司名称")
    company_contact: Optional[str] = Field(None, max_length=50, description="装修公司联系人")
    company_phone: Optional[str] = Field(None, max_length=20, description="装修公司联系电话")
    decoration_type: Optional[str] = Field(None, max_length=50, description="装修类型")
    estimated_start_date: Optional[date] = Field(None, description="预计开工日期")
    estimated_end_date: Optional[date] = Field(None, description="预计竣工日期")
    decoration_scope: Optional[str] = Field(None, description="装修范围说明")
    special_requirements: Optional[str] = Field(None, description="特殊要求")
    status: Optional[str] = Field("待审批", max_length=20, description="申请状态")
    approval_opinion: Optional[str] = Field(None, description="审批意见")
    approved_by: Optional[str] = Field(None, max_length=50, description="审批人")
    approval_date: Optional[date] = Field(None, description="审批日期")
    description: Optional[str] = Field(None, description="备注")

class DecorationApplicationCreate(DecorationApplicationBase):
    """
    创建装修申请Schema
    """
    pass

class DecorationApplicationUpdate(BaseModel):
    """
    更新装修申请Schema
    """
    room_number: Optional[str] = Field(None, min_length=1, max_length=50)
    owner_name: Optional[str] = Field(None, min_length=1, max_length=50)
    owner_phone: Optional[str] = Field(None, max_length=20)
    decoration_company: Optional[str] = Field(None, max_length=100)
    company_contact: Optional[str] = Field(None, max_length=50)
    company_phone: Optional[str] = Field(None, max_length=20)
    decoration_type: Optional[str] = Field(None, max_length=50)
    estimated_start_date: Optional[date] = None
    estimated_end_date: Optional[date] = None
    decoration_scope: Optional[str] = None
    special_requirements: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    approval_opinion: Optional[str] = None
    approved_by: Optional[str] = Field(None, max_length=50)
    approval_date: Optional[date] = None
    description: Optional[str] = None

class DecorationApplicationResponse(DecorationApplicationBase):
    """
    装修申请响应Schema
    """
    id: int
    application_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 装修押金相关 Schema ====================

class DecorationDepositBase(BaseModel):
    """
    装修押金基础Schema
    """
    application_id: int = Field(..., description="装修申请ID")
    deposit_type: Optional[str] = Field(None, max_length=50, description="押金类型")
    amount: float = Field(..., gt=0, description="押金金额")
    paid_date: Optional[date] = Field(None, description="缴纳日期")
    paid_by: Optional[str] = Field(None, max_length=50, description="缴纳人")
    receipt_no: Optional[str] = Field(None, max_length=50, description="收据编号")
    refund_date: Optional[date] = Field(None, description="退还日期")
    refund_amount: Optional[float] = Field(None, description="退还金额")
    refund_by: Optional[str] = Field(None, max_length=50, description="退还经办人")
    deduction_reason: Optional[str] = Field(None, description="扣款原因")
    deduction_amount: Optional[float] = Field(0, description="扣款金额")
    status: Optional[str] = Field("待缴纳", max_length=20, description="状态")
    description: Optional[str] = Field(None, description="备注")

class DecorationDepositCreate(DecorationDepositBase):
    """
    创建装修押金Schema
    """
    pass

class DecorationDepositUpdate(BaseModel):
    """
    更新装修押金Schema
    """
    deposit_type: Optional[str] = Field(None, max_length=50)
    amount: Optional[float] = None
    paid_date: Optional[date] = None
    paid_by: Optional[str] = Field(None, max_length=50)
    receipt_no: Optional[str] = Field(None, max_length=50)
    refund_date: Optional[date] = None
    refund_amount: Optional[float] = None
    refund_by: Optional[str] = Field(None, max_length=50)
    deduction_reason: Optional[str] = None
    deduction_amount: Optional[float] = None
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None

class DecorationDepositResponse(DecorationDepositBase):
    """
    装修押金响应Schema
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 装修巡检相关 Schema ====================

class DecorationInspectionBase(BaseModel):
    """
    装修巡检基础Schema
    """
    application_id: int = Field(..., description="装修申请ID")
    inspection_date: date = Field(..., description="巡检日期")
    inspector: Optional[str] = Field(None, max_length=50, description="巡检人")
    inspection_items: Optional[str] = Field(None, description="巡检项目（JSON格式）")
    result: Optional[str] = Field("正常", max_length=20, description="巡检结果")
    issues_found: Optional[str] = Field(None, description="发现的问题")
    rectification_requirements: Optional[str] = Field(None, description="整改要求")
    rectification_deadline: Optional[date] = Field(None, description="整改期限")
    is_rectified: Optional[bool] = Field(False, description="是否已整改")
    rectification_date: Optional[date] = Field(None, description="整改完成日期")
    description: Optional[str] = Field(None, description="备注")

class DecorationInspectionCreate(DecorationInspectionBase):
    """
    创建装修巡检Schema
    """
    pass

class DecorationInspectionUpdate(BaseModel):
    """
    更新装修巡检Schema
    """
    inspection_date: Optional[date] = None
    inspector: Optional[str] = Field(None, max_length=50)
    inspection_items: Optional[str] = None
    result: Optional[str] = Field(None, max_length=20)
    issues_found: Optional[str] = None
    rectification_requirements: Optional[str] = None
    rectification_deadline: Optional[date] = None
    is_rectified: Optional[bool] = None
    rectification_date: Optional[date] = None
    description: Optional[str] = None

class DecorationInspectionResponse(DecorationInspectionBase):
    """
    装修巡检响应Schema
    """
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

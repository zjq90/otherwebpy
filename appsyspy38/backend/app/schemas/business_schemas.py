"""
业务相关Pydantic模型
用于业务API请求和响应的数据验证
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class ProductionTaskBase(BaseModel):
    """生产任务基础模型"""
    project_name: str = Field(..., description="项目名称")
    concrete_type: str = Field(..., description="混凝土类型")
    volume: float = Field(..., description="方量(立方米)")
    delivery_location: str = Field(..., description="浇筑地点")
    required_time: datetime = Field(..., description="要求时间")
    operator_id: Optional[int] = Field(None, description="操作员ID")
    notes: Optional[str] = Field(None, description="备注")


class ProductionTaskCreate(ProductionTaskBase):
    """创建生产任务模型"""
    pass


class ProductionTaskUpdate(BaseModel):
    """更新生产任务模型"""
    project_name: Optional[str] = None
    concrete_type: Optional[str] = None
    volume: Optional[float] = None
    status: Optional[str] = None
    operator_id: Optional[int] = None


class ProductionTaskResponse(ProductionTaskBase):
    """生产任务响应模型"""
    id: int
    task_no: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductionRecordBase(BaseModel):
    """生产记录基础模型"""
    task_id: int = Field(..., description="任务ID")
    production_date: date = Field(..., description="生产日期")
    concrete_type: str = Field(..., description="混凝土类型")
    actual_volume: float = Field(..., description="实际方量")
    slump: Optional[str] = Field(None, description="坍落度")
    temperature: Optional[float] = Field(None, description="出机温度")
    equipment_no: Optional[str] = Field(None, description="设备编号")
    batch_no: Optional[str] = Field(None, description="批次号")
    notes: Optional[str] = Field(None, description="备注")


class ProductionRecordCreate(ProductionRecordBase):
    """创建生产记录模型"""
    pass


class ProductionRecordResponse(ProductionRecordBase):
    """生产记录响应模型"""
    id: int
    operator_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialInspectionBase(BaseModel):
    """原材料检验基础模型"""
    material_type: str = Field(..., description="材料类型")
    material_name: str = Field(..., description="材料名称")
    batch_no: str = Field(..., description="批次号")
    supplier: str = Field(..., description="供应商")
    quantity: float = Field(..., description="数量")
    inspection_date: date = Field(..., description="检验日期")
    inspection_result: str = Field(..., description="检验结果")
    inspection_items: Optional[str] = Field(None, description="检验项目明细")
    notes: Optional[str] = Field(None, description="备注")


class MaterialInspectionCreate(MaterialInspectionBase):
    """创建原材料检验模型"""
    pass


class MaterialInspectionResponse(MaterialInspectionBase):
    """原材料检验响应模型"""
    id: int
    inspection_no: str
    inspector_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QualityReportBase(BaseModel):
    """成品质量报告基础模型"""
    project_name: str = Field(..., description="项目名称")
    concrete_type: str = Field(..., description="混凝土类型")
    batch_no: str = Field(..., description="批次号")
    production_date: date = Field(..., description="生产日期")
    strength_grade: str = Field(..., description="强度等级")
    test_age: int = Field(..., description="试验龄期(天)")
    compressive_strength: float = Field(..., description="抗压强度(MPa)")
    flexural_strength: Optional[float] = Field(None, description="抗折强度(MPa)")
    report_date: date = Field(..., description="报告日期")
    conclusion: str = Field(..., description="结论")
    notes: Optional[str] = Field(None, description="备注")


class QualityReportCreate(QualityReportBase):
    """创建成品质量报告模型"""
    pass


class QualityReportResponse(QualityReportBase):
    """成品质量报告响应模型"""
    id: int
    report_no: str
    inspector_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class QualityAlertBase(BaseModel):
    """质量预警基础模型"""
    alert_type: str = Field(..., description="预警类型")
    alert_level: str = Field(..., description="预警级别")
    project_name: str = Field(..., description="项目名称")
    concrete_type: str = Field(..., description="混凝土类型")
    batch_no: str = Field(..., description="批次号")
    description: str = Field(..., description="问题描述")


class QualityAlertCreate(QualityAlertBase):
    """创建质量预警模型"""
    pass


class QualityAlertUpdate(BaseModel):
    """更新质量预警模型"""
    status: Optional[str] = None
    handler_id: Optional[int] = None
    handle_result: Optional[str] = None


class QualityAlertResponse(QualityAlertBase):
    """质量预警响应模型"""
    id: int
    alert_no: str
    initiator_id: int
    status: str
    handler_id: Optional[int]
    handle_result: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialInventoryBase(BaseModel):
    """原材料库存基础模型"""
    material_code: str = Field(..., description="材料编码")
    material_name: str = Field(..., description="材料名称")
    material_type: str = Field(..., description="材料类型")
    specification: str = Field(..., description="规格型号")
    unit: str = Field(..., description="单位")
    quantity: float = Field(..., description="库存数量")
    min_warning: float = Field(..., description="最低预警值")
    supplier: Optional[str] = Field(None, description="供应商")
    warehouse: Optional[str] = Field(None, description="仓库")
    notes: Optional[str] = Field(None, description="备注")


class MaterialInventoryCreate(MaterialInventoryBase):
    """创建原材料库存模型"""
    pass


class MaterialInventoryUpdate(BaseModel):
    """更新原材料库存模型"""
    quantity: Optional[float] = None
    min_warning: Optional[float] = None


class MaterialInventoryResponse(MaterialInventoryBase):
    """原材料库存响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequestBase(BaseModel):
    """采购申请基础模型"""
    material_name: str = Field(..., description="材料名称")
    specification: str = Field(..., description="规格型号")
    quantity: float = Field(..., description="申请数量")
    unit: str = Field(..., description="单位")
    expected_price: Optional[float] = Field(None, description="预估单价")
    supplier: Optional[str] = Field(None, description="推荐供应商")
    reason: str = Field(..., description="申请原因")
    urgency: str = Field(default="normal", description="紧急程度")
    notes: Optional[str] = Field(None, description="备注")


class PurchaseRequestCreate(PurchaseRequestBase):
    """创建采购申请模型"""
    pass


class PurchaseRequestUpdate(BaseModel):
    """更新采购申请模型"""
    status: Optional[str] = None
    approver_id: Optional[int] = None
    approval_opinion: Optional[str] = None


class PurchaseRequestResponse(PurchaseRequestBase):
    """采购申请响应模型"""
    id: int
    request_no: str
    applicant_id: int
    status: str
    approver_id: Optional[int]
    approval_opinion: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    """供应商基础模型"""
    supplier_code: str = Field(..., description="供应商编码")
    supplier_name: str = Field(..., description="供应商名称")
    contact_person: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="联系电话")
    address: Optional[str] = Field(None, description="地址")
    business_scope: Optional[str] = Field(None, description="经营范围")
    credit_rating: Optional[str] = Field(None, description="信用等级")
    notes: Optional[str] = Field(None, description="备注")


class SupplierCreate(SupplierBase):
    """创建供应商模型"""
    pass


class SupplierResponse(SupplierBase):
    """供应商响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    """车辆基础模型"""
    vehicle_no: str = Field(..., description="车牌号")
    vehicle_type: str = Field(..., description="车辆类型")
    load_capacity: float = Field(..., description="载重能力(吨)")
    volume_capacity: Optional[float] = Field(None, description="容积(立方米)")
    driver_name: Optional[str] = Field(None, description="驾驶员姓名")
    driver_phone: Optional[str] = Field(None, description="驾驶员电话")
    notes: Optional[str] = Field(None, description="备注")


class VehicleCreate(VehicleBase):
    """创建车辆模型"""
    pass


class VehicleUpdate(BaseModel):
    """更新车辆模型"""
    status: Optional[str] = None
    current_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class VehicleResponse(VehicleBase):
    """车辆响应模型"""
    id: int
    status: str
    current_location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    location_updated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransportTaskBase(BaseModel):
    """运输任务基础模型"""
    project_name: str = Field(..., description="项目名称")
    delivery_location: str = Field(..., description="送达地点")
    concrete_type: str = Field(..., description="混凝土类型")
    volume: float = Field(..., description="方量(立方米)")
    vehicle_id: int = Field(..., description="车辆ID")
    scheduled_time: datetime = Field(..., description="计划时间")
    notes: Optional[str] = Field(None, description="备注")


class TransportTaskCreate(TransportTaskBase):
    """创建运输任务模型"""
    pass


class TransportTaskUpdate(BaseModel):
    """更新运输任务模型"""
    status: Optional[str] = None
    progress: Optional[int] = None
    actual_departure_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None


class TransportTaskResponse(TransportTaskBase):
    """运输任务响应模型"""
    id: int
    task_no: str
    scheduler_id: int
    actual_departure_time: Optional[datetime]
    actual_arrival_time: Optional[datetime]
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

"""
工程维保管理模块 - Pydantic Schema
定义设备管理相关API的请求和响应数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# ==================== 设备台账相关 Schema ====================

class EquipmentBase(BaseModel):
    """
    设备基础信息Schema
    用于创建设备和更新设备时的基础字段
    """
    name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    code: str = Field(..., min_length=1, max_length=50, description="设备编号")
    category: str = Field(..., min_length=1, max_length=50, description="设备类别（电梯、水泵、空调等）")
    model: Optional[str] = Field(None, max_length=100, description="设备型号")
    manufacturer: Optional[str] = Field(None, max_length=100, description="生产厂家")
    purchase_date: Optional[date] = Field(None, description="购买日期")
    warranty_expiry: Optional[date] = Field(None, description="保修到期日期")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    status: Optional[str] = Field("正常", max_length=20, description="设备状态")
    description: Optional[str] = Field(None, description="设备描述")

class EquipmentCreate(EquipmentBase):
    """
    创建设备Schema
    继承EquipmentBase，用于POST请求
    """
    pass

class EquipmentUpdate(BaseModel):
    """
    更新设备Schema
    所有字段可选，用于PATCH/PUT请求
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None

class EquipmentResponse(EquipmentBase):
    """
    设备响应Schema
    包含数据库中所有字段，用于GET响应
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 巡检计划相关 Schema ====================

class InspectionPlanBase(BaseModel):
    """
    巡检计划基础Schema
    """
    equipment_id: int = Field(..., description="设备ID")
    plan_name: str = Field(..., min_length=1, max_length=100, description="计划名称")
    cycle: Optional[str] = Field(None, max_length=50, description="巡检周期")
    next_inspection_date: Optional[date] = Field(None, description="下次巡检日期")
    inspector: Optional[str] = Field(None, max_length=50, description="巡检负责人")
    items: Optional[str] = Field(None, description="巡检项目（JSON格式）")
    status: Optional[str] = Field("待执行", max_length=20, description="计划状态")
    description: Optional[str] = Field(None, description="备注说明")

class InspectionPlanCreate(InspectionPlanBase):
    """
    创建巡检计划Schema
    """
    pass

class InspectionPlanUpdate(BaseModel):
    """
    更新巡检计划Schema
    """
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    cycle: Optional[str] = Field(None, max_length=50)
    next_inspection_date: Optional[date] = None
    inspector: Optional[str] = Field(None, max_length=50)
    items: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None

class InspectionPlanResponse(InspectionPlanBase):
    """
    巡检计划响应Schema
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 巡检记录相关 Schema ====================

class InspectionRecordBase(BaseModel):
    """
    巡检记录基础Schema
    """
    plan_id: int = Field(..., description="巡检计划ID")
    inspection_date: date = Field(..., description="巡检日期")
    inspector: Optional[str] = Field(None, max_length=50, description="巡检人")
    result: Optional[str] = Field("正常", max_length=20, description="巡检结果")
    issues: Optional[str] = Field(None, description="发现的问题")
    suggestion: Optional[str] = Field(None, description="处理建议")
    description: Optional[str] = Field(None, description="备注")

class InspectionRecordCreate(InspectionRecordBase):
    """
    创建巡检记录Schema
    """
    pass

class InspectionRecordResponse(InspectionRecordBase):
    """
    巡检记录响应Schema
    """
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 保养计划相关 Schema ====================

class MaintenancePlanBase(BaseModel):
    """
    保养计划基础Schema
    """
    equipment_id: int = Field(..., description="设备ID")
    plan_name: str = Field(..., min_length=1, max_length=100, description="计划名称")
    cycle: Optional[str] = Field(None, max_length=50, description="保养周期")
    next_maintenance_date: Optional[date] = Field(None, description="下次保养日期")
    maintainer: Optional[str] = Field(None, max_length=50, description="保养负责人")
    items: Optional[str] = Field(None, description="保养项目（JSON格式）")
    estimated_cost: Optional[float] = Field(0, description="预估费用")
    status: Optional[str] = Field("待执行", max_length=20, description="计划状态")
    description: Optional[str] = Field(None, description="备注说明")

class MaintenancePlanCreate(MaintenancePlanBase):
    """
    创建保养计划Schema
    """
    pass

class MaintenancePlanUpdate(BaseModel):
    """
    更新保养计划Schema
    """
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    cycle: Optional[str] = Field(None, max_length=50)
    next_maintenance_date: Optional[date] = None
    maintainer: Optional[str] = Field(None, max_length=50)
    items: Optional[str] = None
    estimated_cost: Optional[float] = None
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None

class MaintenancePlanResponse(MaintenancePlanBase):
    """
    保养计划响应Schema
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 保养记录相关 Schema ====================

class MaintenanceRecordBase(BaseModel):
    """
    保养记录基础Schema
    """
    plan_id: int = Field(..., description="保养计划ID")
    maintenance_date: date = Field(..., description="保养日期")
    maintainer: Optional[str] = Field(None, max_length=50, description="保养人")
    items_done: Optional[str] = Field(None, description="完成的保养项目（JSON格式）")
    actual_cost: Optional[float] = Field(0, description="实际费用")
    result: Optional[str] = Field("完成", max_length=20, description="保养结果")
    description: Optional[str] = Field(None, description="备注")

class MaintenanceRecordCreate(MaintenanceRecordBase):
    """
    创建保养记录Schema
    """
    pass

class MaintenanceRecordResponse(MaintenanceRecordBase):
    """
    保养记录响应Schema
    """
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 故障维修记录相关 Schema ====================

class FaultRecordBase(BaseModel):
    """
    故障维修记录基础Schema
    """
    equipment_id: int = Field(..., description="设备ID")
    fault_code: str = Field(..., min_length=1, max_length=50, description="故障编号")
    fault_type: Optional[str] = Field(None, max_length=50, description="故障类型")
    fault_description: str = Field(..., description="故障描述")
    reporter: Optional[str] = Field(None, max_length=50, description="报修人")
    assign_to: Optional[str] = Field(None, max_length=50, description="维修负责人")
    solution: Optional[str] = Field(None, description="维修方案")
    parts_used: Optional[str] = Field(None, description="使用配件（JSON格式）")
    labor_cost: Optional[float] = Field(0, description="人工费用")
    parts_cost: Optional[float] = Field(0, description="配件费用")
    total_cost: Optional[float] = Field(0, description="总费用")
    status: Optional[str] = Field("待处理", max_length=20, description="故障状态")
    satisfaction: Optional[int] = Field(None, ge=1, le=5, description="满意度（1-5分）")
    description: Optional[str] = Field(None, description="备注")

class FaultRecordCreate(FaultRecordBase):
    """
    创建故障维修记录Schema
    """
    pass

class FaultRecordUpdate(BaseModel):
    """
    更新故障维修记录Schema
    """
    fault_type: Optional[str] = Field(None, max_length=50)
    fault_description: Optional[str] = None
    reporter: Optional[str] = Field(None, max_length=50)
    assign_to: Optional[str] = Field(None, max_length=50)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    solution: Optional[str] = None
    parts_used: Optional[str] = None
    labor_cost: Optional[float] = None
    parts_cost: Optional[float] = None
    total_cost: Optional[float] = None
    status: Optional[str] = Field(None, max_length=20)
    satisfaction: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = None

class FaultRecordResponse(FaultRecordBase):
    """
    故障维修记录响应Schema
    """
    id: int
    report_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== 费用统计相关 Schema ====================

class CostStatisticsResponse(BaseModel):
    """
    费用统计响应Schema
    用于费用核算与数据分析功能
    """
    total_fault_cost: float = Field(0, description="故障维修总费用")
    total_maintenance_cost: float = Field(0, description="保养总费用")
    fault_count: int = Field(0, description="故障数量")
    maintenance_count: int = Field(0, description="保养数量")
    avg_fault_cost: float = Field(0, description="平均单次故障费用")
    avg_maintenance_cost: float = Field(0, description="平均单次保养费用")

class EquipmentStatusStatistics(BaseModel):
    """
    设备状态统计Schema
    """
    status: str
    count: int

class FaultTypeStatistics(BaseModel):
    """
    故障类型统计Schema
    """
    fault_type: Optional[str]
    count: int
    total_cost: float

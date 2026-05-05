from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class MaintenancePlanBase(BaseModel):
    """
    保养计划基础模型
    """
    plan_code: str = Field(..., min_length=1, max_length=50, description="计划编号")
    name: str = Field(..., min_length=1, max_length=200, description="计划名称")
    maintenance_type: str = Field(..., min_length=1, max_length=50, description="保养类型")
    cycle_days: int = Field(..., gt=0, description="执行周期（天数）")
    cycle_description: Optional[str] = Field(None, max_length=100, description="周期描述")
    content: str = Field(..., description="保养内容")
    standard: Optional[str] = Field(None, description="保养标准")
    estimated_hours: Optional[float] = Field(None, ge=0, description="预计耗时（小时）")
    responsible_person: Optional[str] = Field(None, max_length=50, description="负责人")
    status: Optional[str] = Field("启用", max_length=20, description="计划状态")
    description: Optional[str] = Field(None, description="备注信息")


class MaintenancePlanCreate(MaintenancePlanBase):
    """
    保养计划创建模型
    """
    pass


class MaintenancePlanUpdate(BaseModel):
    """
    保养计划更新模型
    """
    plan_code: Optional[str] = Field(None, min_length=1, max_length=50, description="计划编号")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="计划名称")
    maintenance_type: Optional[str] = Field(None, min_length=1, max_length=50, description="保养类型")
    cycle_days: Optional[int] = Field(None, gt=0, description="执行周期（天数）")
    cycle_description: Optional[str] = Field(None, max_length=100, description="周期描述")
    content: Optional[str] = Field(None, description="保养内容")
    standard: Optional[str] = Field(None, description="保养标准")
    estimated_hours: Optional[float] = Field(None, ge=0, description="预计耗时（小时）")
    responsible_person: Optional[str] = Field(None, max_length=50, description="负责人")
    status: Optional[str] = Field(None, max_length=20, description="计划状态")
    description: Optional[str] = Field(None, description="备注信息")


class MaintenancePlanResponse(MaintenancePlanBase):
    """
    保养计划响应模型
    """
    id: int = Field(..., description="计划ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class MaintenanceTaskBase(BaseModel):
    """
    保养任务基础模型
    """
    task_code: str = Field(..., min_length=1, max_length=50, description="任务编号")
    plan_id: Optional[int] = Field(None, description="关联计划ID")
    equipment_id: int = Field(..., description="关联设备ID")
    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    maintenance_type: str = Field(..., min_length=1, max_length=50, description="保养类型")
    plan_date: date = Field(..., description="计划执行日期")
    actual_date: Optional[date] = Field(None, description="实际执行日期")
    content: str = Field(..., description="保养内容")
    standard: Optional[str] = Field(None, description="保养标准")
    responsible_person: Optional[str] = Field(None, max_length=50, description="负责人")
    executor: Optional[str] = Field(None, max_length=100, description="执行人员")
    status: Optional[str] = Field("待执行", max_length=20, description="任务状态")
    completion_status: Optional[str] = Field(None, max_length=50, description="完成情况")
    description: Optional[str] = Field(None, description="备注信息")


class MaintenanceTaskCreate(MaintenanceTaskBase):
    """
    保养任务创建模型
    """
    pass


class MaintenanceTaskUpdate(BaseModel):
    """
    保养任务更新模型
    """
    task_code: Optional[str] = Field(None, min_length=1, max_length=50, description="任务编号")
    plan_id: Optional[int] = Field(None, description="关联计划ID")
    equipment_id: Optional[int] = Field(None, description="关联设备ID")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="任务名称")
    maintenance_type: Optional[str] = Field(None, min_length=1, max_length=50, description="保养类型")
    plan_date: Optional[date] = Field(None, description="计划执行日期")
    actual_date: Optional[date] = Field(None, description="实际执行日期")
    content: Optional[str] = Field(None, description="保养内容")
    standard: Optional[str] = Field(None, description="保养标准")
    responsible_person: Optional[str] = Field(None, max_length=50, description="负责人")
    executor: Optional[str] = Field(None, max_length=100, description="执行人员")
    status: Optional[str] = Field(None, max_length=20, description="任务状态")
    completion_status: Optional[str] = Field(None, max_length=50, description="完成情况")
    description: Optional[str] = Field(None, description="备注信息")


class MaintenanceTaskResponse(MaintenanceTaskBase):
    """
    保养任务响应模型
    """
    id: int = Field(..., description="任务ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class MaintenanceRecordBase(BaseModel):
    """
    保养记录基础模型
    """
    record_code: str = Field(..., min_length=1, max_length=50, description="记录编号")
    task_id: int = Field(..., description="关联任务ID")
    execution_date: date = Field(..., description="执行日期")
    executor: str = Field(..., min_length=1, max_length=100, description="执行人员")
    work_hours: Optional[float] = Field(None, ge=0, description="工作时长（小时）")
    content: str = Field(..., description="保养内容")
    result: str = Field(..., description="保养结果")
    has_issues: Optional[bool] = Field(False, description="是否发现问题")
    issue_description: Optional[str] = Field(None, description="问题描述")
    treatment_measures: Optional[str] = Field(None, description="处理措施")
    replaced_parts: Optional[str] = Field(None, description="更换的零部件")
    next_maintenance_suggestion: Optional[str] = Field(None, description="下次保养建议")
    inspector: Optional[str] = Field(None, max_length=50, description="验收人员")
    inspection_date: Optional[date] = Field(None, description="验收日期")
    inspection_result: Optional[str] = Field(None, max_length=20, description="验收结果")
    description: Optional[str] = Field(None, description="备注信息")


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """
    保养记录创建模型
    """
    pass


class MaintenanceRecordUpdate(BaseModel):
    """
    保养记录更新模型
    """
    record_code: Optional[str] = Field(None, min_length=1, max_length=50, description="记录编号")
    task_id: Optional[int] = Field(None, description="关联任务ID")
    execution_date: Optional[date] = Field(None, description="执行日期")
    executor: Optional[str] = Field(None, min_length=1, max_length=100, description="执行人员")
    work_hours: Optional[float] = Field(None, ge=0, description="工作时长（小时）")
    content: Optional[str] = Field(None, description="保养内容")
    result: Optional[str] = Field(None, description="保养结果")
    has_issues: Optional[bool] = Field(None, description="是否发现问题")
    issue_description: Optional[str] = Field(None, description="问题描述")
    treatment_measures: Optional[str] = Field(None, description="处理措施")
    replaced_parts: Optional[str] = Field(None, description="更换的零部件")
    next_maintenance_suggestion: Optional[str] = Field(None, description="下次保养建议")
    inspector: Optional[str] = Field(None, max_length=50, description="验收人员")
    inspection_date: Optional[date] = Field(None, description="验收日期")
    inspection_result: Optional[str] = Field(None, max_length=20, description="验收结果")
    description: Optional[str] = Field(None, description="备注信息")


class MaintenanceRecordResponse(MaintenanceRecordBase):
    """
    保养记录响应模型
    """
    id: int = Field(..., description="记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

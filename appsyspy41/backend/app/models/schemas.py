"""
Pydantic模型定义
定义API请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., title='用户名', max_length=50)
    real_name: str = Field(..., title='真实姓名', max_length=50)
    role: str = Field(..., title='角色')
    phone: Optional[str] = Field(None, title='手机号', max_length=20)
    email: Optional[str] = Field(None, title='邮箱', max_length=100)
    status: str = Field('active', title='状态')


class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., title='密码', min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户模型"""
    real_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., title='用户名')
    password: str = Field(..., title='密码')


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 设备相关模型 ====================

class DeviceBase(BaseModel):
    """设备基础模型"""
    device_code: str = Field(..., title='设备编号', max_length=50)
    device_name: str = Field(..., title='设备名称', max_length=100)
    device_type: str = Field(..., title='设备类型')
    location: Optional[str] = Field(None, title='位置', max_length=200)
    install_date: Optional[date] = Field(None, title='安装日期')
    specification: Optional[str] = Field(None, title='规格型号', max_length=200)
    manufacturer: Optional[str] = Field(None, title='制造商', max_length=100)
    status: str = Field('normal', title='设备状态')
    total_running_hours: float = Field(0, title='总运行时长(小时)')


class DeviceCreate(DeviceBase):
    """创建设备模型"""
    pass


class DeviceUpdate(BaseModel):
    """更新设备模型"""
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    status: Optional[str] = None
    total_running_hours: Optional[float] = None


class DeviceStatus(BaseModel):
    """设备状态模型"""
    device_id: int
    current: Optional[float] = Field(None, title='电流(A)')
    temperature: Optional[float] = Field(None, title='温度(°C)')
    voltage: Optional[float] = Field(None, title='电压(V)')
    power: Optional[float] = Field(None, title='功率(kW)')
    running_hours: Optional[float] = Field(None, title='运行时长(小时)')
    status: str = Field(..., title='运行状态')
    alarm_level: str = Field('none', title='告警级别')


class DeviceResponse(DeviceBase):
    """设备响应模型"""
    id: int
    last_maintenance_date: Optional[date]
    next_maintenance_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    current_status: Optional[DeviceStatus] = None

    class Config:
        from_attributes = True


# ==================== 保养任务相关模型 ====================

class MaintenanceTaskBase(BaseModel):
    """保养任务基础模型"""
    device_id: int = Field(..., title='设备ID')
    task_name: str = Field(..., title='任务名称', max_length=200)
    task_description: Optional[str] = Field(None, title='任务描述')
    maintenance_cycle_hours: float = Field(..., title='保养周期(小时)')
    last_maintenance_hours: float = Field(0, title='上次保养运行时长')
    next_maintenance_hours: Optional[float] = Field(None, title='下次保养运行时长')
    status: str = Field('pending', title='任务状态')
    priority: str = Field('medium', title='优先级')
    operation_guide: Optional[str] = Field(None, title='操作指南')


class MaintenanceTaskCreate(MaintenanceTaskBase):
    """创建保养任务模型"""
    pass


class MaintenanceTaskUpdate(BaseModel):
    """更新保养任务模型"""
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    maintenance_cycle_hours: Optional[float] = None
    last_maintenance_hours: Optional[float] = None
    next_maintenance_hours: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    operation_guide: Optional[str] = None


class MaintenanceTaskResponse(MaintenanceTaskBase):
    """保养任务响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 保养记录相关模型 ====================

class MaintenanceRecordBase(BaseModel):
    """保养记录基础模型"""
    task_id: int = Field(..., title='任务ID')
    device_id: int = Field(..., title='设备ID')
    operator_id: int = Field(..., title='操作员ID')
    maintenance_content: Optional[str] = Field(None, title='保养内容')
    maintenance_result: str = Field(..., title='保养结果')
    remark: Optional[str] = Field(None, title='备注')
    photo_urls: Optional[str] = Field(None, title='照片URL列表(逗号分隔)')


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """创建保养记录模型"""
    pass


class MaintenanceRecordResponse(MaintenanceRecordBase):
    """保养记录响应模型"""
    id: int
    maintenance_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 故障报修相关模型 ====================

class FaultReportBase(BaseModel):
    """故障报修基础模型"""
    device_id: int = Field(..., title='设备ID')
    reporter_id: int = Field(..., title='上报人ID')
    fault_title: str = Field(..., title='故障标题', max_length=200)
    fault_description: Optional[str] = Field(None, title='故障描述')
    fault_level: str = Field('medium', title='故障级别')
    photo_urls: Optional[str] = Field(None, title='照片URL列表(逗号分隔)')
    status: str = Field('pending', title='报修状态')
    assigned_to: Optional[int] = Field(None, title='分配给的维修人员ID')


class FaultReportCreate(BaseModel):
    """创建故障报修模型"""
    device_id: int = Field(..., title='设备ID')
    fault_title: str = Field(..., title='故障标题', max_length=200)
    fault_description: Optional[str] = Field(None, title='故障描述')
    fault_level: str = Field('medium', title='故障级别')
    photo_urls: Optional[str] = Field(None, title='照片URL列表(逗号分隔)')


class FaultReportUpdate(BaseModel):
    """更新故障报修模型"""
    fault_title: Optional[str] = None
    fault_description: Optional[str] = None
    fault_level: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None


class FaultReportResponse(FaultReportBase):
    """故障报修响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 维修记录相关模型 ====================

class RepairRecordBase(BaseModel):
    """维修记录基础模型"""
    report_id: int = Field(..., title='报修单ID')
    operator_id: int = Field(..., title='操作员ID')
    action: str = Field(..., title='操作类型', max_length=50)
    description: Optional[str] = Field(None, title='描述')
    progress: int = Field(0, title='进度百分比', ge=0, le=100)
    photo_urls: Optional[str] = Field(None, title='照片URL列表(逗号分隔)')


class RepairRecordCreate(RepairRecordBase):
    """创建维修记录模型"""
    pass


class RepairRecordResponse(RepairRecordBase):
    """维修记录响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 通用响应模型 ====================

class ApiResponse(BaseModel):
    """通用API响应模型"""
    code: int = Field(200, title='状态码')
    message: str = Field('success', title='消息')
    data: Optional[dict] = Field(None, title='数据')


class PaginatedResponse(ApiResponse):
    """分页响应模型"""
    total: int = Field(0, title='总数')
    page: int = Field(1, title='当前页')
    page_size: int = Field(10, title='每页大小')
    total_pages: int = Field(0, title='总页数')

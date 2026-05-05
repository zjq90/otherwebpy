from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class EquipmentBase(BaseModel):
    """
    设备档案基础模型
    用于创建设备时的输入验证
    """
    equipment_code: str = Field(..., min_length=1, max_length=50, description="设备编号")
    name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    equipment_type: str = Field(..., min_length=1, max_length=50, description="设备类型")
    model: Optional[str] = Field(None, max_length=100, description="设备型号")
    specification: Optional[str] = Field(None, max_length=200, description="设备规格")
    manufacturer: Optional[str] = Field(None, max_length=100, description="生产厂家")
    production_date: Optional[date] = Field(None, description="出厂日期")
    installation_date: Optional[date] = Field(None, description="投入使用日期")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    status: Optional[str] = Field("运行中", max_length=20, description="设备状态")
    responsible_person: Optional[str] = Field(None, max_length=50, description="负责人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    description: Optional[str] = Field(None, description="备注信息")


class EquipmentCreate(EquipmentBase):
    """
    设备创建设备模型
    继承自 EquipmentBase，用于创建设备时的输入
    """
    pass


class EquipmentUpdate(BaseModel):
    """
    设备更新模型
    用于更新设备时的输入，所有字段都是可选的
    """
    equipment_code: Optional[str] = Field(None, min_length=1, max_length=50, description="设备编号")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="设备名称")
    equipment_type: Optional[str] = Field(None, min_length=1, max_length=50, description="设备类型")
    model: Optional[str] = Field(None, max_length=100, description="设备型号")
    specification: Optional[str] = Field(None, max_length=200, description="设备规格")
    manufacturer: Optional[str] = Field(None, max_length=100, description="生产厂家")
    production_date: Optional[date] = Field(None, description="出厂日期")
    installation_date: Optional[date] = Field(None, description="投入使用日期")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    status: Optional[str] = Field(None, max_length=20, description="设备状态")
    responsible_person: Optional[str] = Field(None, max_length=50, description="负责人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    description: Optional[str] = Field(None, description="备注信息")


class EquipmentResponse(EquipmentBase):
    """
    设备响应模型
    用于API返回设备数据
    """
    id: int = Field(..., description="设备ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "equipment_code": "EQ-001",
                "name": "搅拌主机",
                "equipment_type": "搅拌主机",
                "model": "JS2000",
                "specification": "2000L",
                "manufacturer": "三一重工",
                "production_date": "2023-01-15",
                "installation_date": "2023-03-20",
                "location": "生产车间A区",
                "status": "运行中",
                "responsible_person": "张三",
                "contact_phone": "13800138000",
                "description": "主要搅拌设备",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class SensorBase(BaseModel):
    """
    传感器基础模型
    """
    sensor_code: str = Field(..., min_length=1, max_length=50, description="传感器编号")
    name: str = Field(..., min_length=1, max_length=100, description="传感器名称")
    sensor_type: str = Field(..., min_length=1, max_length=50, description="传感器类型")
    equipment_id: int = Field(..., description="关联设备ID")
    installation_location: Optional[str] = Field(None, max_length=200, description="安装位置")
    unit: Optional[str] = Field(None, max_length=20, description="数据单位")
    min_value: Optional[float] = Field(None, description="正常范围最小值")
    max_value: Optional[float] = Field(None, description="正常范围最大值")
    warning_threshold: Optional[float] = Field(None, description="预警阈值")
    alarm_threshold: Optional[float] = Field(None, description="报警阈值")
    status: Optional[str] = Field("正常", max_length=20, description="传感器状态")
    description: Optional[str] = Field(None, description="备注信息")


class SensorCreate(SensorBase):
    """
    传感器创建设备模型
    """
    pass


class SensorUpdate(BaseModel):
    """
    传感器更新模型
    """
    sensor_code: Optional[str] = Field(None, min_length=1, max_length=50, description="传感器编号")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="传感器名称")
    sensor_type: Optional[str] = Field(None, min_length=1, max_length=50, description="传感器类型")
    equipment_id: Optional[int] = Field(None, description="关联设备ID")
    installation_location: Optional[str] = Field(None, max_length=200, description="安装位置")
    unit: Optional[str] = Field(None, max_length=20, description="数据单位")
    min_value: Optional[float] = Field(None, description="正常范围最小值")
    max_value: Optional[float] = Field(None, description="正常范围最大值")
    warning_threshold: Optional[float] = Field(None, description="预警阈值")
    alarm_threshold: Optional[float] = Field(None, description="报警阈值")
    status: Optional[str] = Field(None, max_length=20, description="传感器状态")
    description: Optional[str] = Field(None, description="备注信息")


class SensorResponse(SensorBase):
    """
    传感器响应模型
    """
    id: int = Field(..., description="传感器ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

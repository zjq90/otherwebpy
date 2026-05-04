from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum


class StatusEnum(str, Enum):
    在职 = "在职"
    离职 = "离职"


class ShiftTypeEnum(str, Enum):
    早班 = "早班"
    中班 = "中班"
    晚班 = "晚班"


class ScheduleStatusEnum(str, Enum):
    待执行 = "待执行"
    执行中 = "执行中"
    已完成 = "已完成"
    取消 = "取消"


class EnableStatusEnum(str, Enum):
    启用 = "启用"
    停用 = "停用"


class PatrolStatusEnum(str, Enum):
    进行中 = "进行中"
    已完成 = "已完成"
    异常 = "异常"


class DeviceStatusEnum(str, Enum):
    正常 = "正常"
    离线 = "离线"
    故障 = "故障"


class VehicleStatusEnum(str, Enum):
    在场 = "在场"
    已离开 = "已离开"


class VisitorStatusEnum(str, Enum):
    在场 = "在场"
    已离开 = "已离开"


class EmergencyStatusEnum(str, Enum):
    待处理 = "待处理"
    处理中 = "处理中"
    已处理 = "已处理"


class PriorityEnum(str, Enum):
    紧急 = "紧急"
    重要 = "重要"
    一般 = "一般"


class EventTypeEnum(str, Enum):
    火灾 = "火灾"
    盗窃 = "盗窃"
    斗殴 = "斗殴"
    其他 = "其他"


class CleaningQualityEnum(str, Enum):
    优秀 = "优秀"
    良好 = "良好"
    合格 = "合格"
    不合格 = "不合格"


class GrowthStatusEnum(str, Enum):
    良好 = "良好"
    一般 = "一般"
    较差 = "较差"
    死亡 = "死亡"


class MaintenanceTypeEnum(str, Enum):
    浇水 = "浇水"
    施肥 = "施肥"
    修剪 = "修剪"
    病虫害防治 = "病虫害防治"
    其他 = "其他"


class MaintenanceStatusEnum(str, Enum):
    待执行 = "待执行"
    执行中 = "执行中"
    已完成 = "已完成"
    取消 = "取消"


class SecurityPersonnelBase(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    id_card: Optional[str] = Field(None, max_length=18, description="身份证号")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    status: StatusEnum = Field(default=StatusEnum.在职, description="状态")


class SecurityPersonnelCreate(SecurityPersonnelBase):
    pass


class SecurityPersonnelUpdate(SecurityPersonnelBase):
    name: Optional[str] = Field(None, max_length=50, description="姓名")


class SecurityPersonnel(SecurityPersonnelBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class SecurityScheduleBase(BaseModel):
    personnel_id: int = Field(..., description="安保人员ID")
    schedule_date: date = Field(..., description="排班日期")
    shift_type: ShiftTypeEnum = Field(..., description="班次")
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    post: Optional[str] = Field(None, max_length=100, description="岗位")
    status: ScheduleStatusEnum = Field(default=ScheduleStatusEnum.待执行, description="状态")


class SecurityScheduleCreate(SecurityScheduleBase):
    pass


class SecurityScheduleUpdate(SecurityScheduleBase):
    personnel_id: Optional[int] = Field(None, description="安保人员ID")
    schedule_date: Optional[date] = Field(None, description="排班日期")
    shift_type: Optional[ShiftTypeEnum] = Field(None, description="班次")


class SecuritySchedule(SecurityScheduleBase):
    id: int
    create_time: datetime
    update_time: datetime
    personnel: Optional[SecurityPersonnel] = None

    class Config:
        from_attributes = True


class PatrolRouteBase(BaseModel):
    route_name: str = Field(..., max_length=100, description="路线名称")
    route_code: Optional[str] = Field(None, max_length=50, description="路线编号")
    description: Optional[str] = Field(None, description="路线描述")
    checkpoints: Optional[str] = Field(None, description="巡检点列表")
    patrol_frequency: Optional[str] = Field(None, max_length=50, description="巡逻频次")
    status: EnableStatusEnum = Field(default=EnableStatusEnum.启用, description="状态")


class PatrolRouteCreate(PatrolRouteBase):
    pass


class PatrolRouteUpdate(PatrolRouteBase):
    route_name: Optional[str] = Field(None, max_length=100, description="路线名称")


class PatrolRoute(PatrolRouteBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class PatrolRecordBase(BaseModel):
    route_id: int = Field(..., description="路线ID")
    personnel_id: int = Field(..., description="安保人员ID")
    patrol_date: date = Field(..., description="巡逻日期")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    checkpoints_completed: Optional[str] = Field(None, description="已完成巡检点")
    abnormalities: Optional[str] = Field(None, description="异常情况")
    status: PatrolStatusEnum = Field(default=PatrolStatusEnum.进行中, description="状态")


class PatrolRecordCreate(PatrolRecordBase):
    pass


class PatrolRecordUpdate(PatrolRecordBase):
    route_id: Optional[int] = Field(None, description="路线ID")
    personnel_id: Optional[int] = Field(None, description="安保人员ID")
    patrol_date: Optional[date] = Field(None, description="巡逻日期")


class PatrolRecord(PatrolRecordBase):
    id: int
    create_time: datetime
    update_time: datetime
    route: Optional[PatrolRoute] = None

    class Config:
        from_attributes = True


class MonitorDeviceBase(BaseModel):
    device_name: str = Field(..., max_length=100, description="设备名称")
    device_code: Optional[str] = Field(None, max_length=50, description="设备编号")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    ip_address: Optional[str] = Field(None, max_length=50, description="IP地址")
    device_type: Optional[str] = Field(None, max_length=50, description="设备类型")
    status: DeviceStatusEnum = Field(default=DeviceStatusEnum.正常, description="状态")
    installation_date: Optional[date] = Field(None, description="安装日期")
    last_maintenance: Optional[date] = Field(None, description="上次维护时间")


class MonitorDeviceCreate(MonitorDeviceBase):
    pass


class MonitorDeviceUpdate(MonitorDeviceBase):
    device_name: Optional[str] = Field(None, max_length=100, description="设备名称")


class MonitorDevice(MonitorDeviceBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class VehicleRecordBase(BaseModel):
    plate_number: str = Field(..., max_length=20, description="车牌号")
    vehicle_type: Optional[str] = Field(None, max_length=50, description="车辆类型")
    owner_name: Optional[str] = Field(None, max_length=50, description="车主姓名")
    owner_phone: Optional[str] = Field(None, max_length=20, description="车主电话")
    entry_time: Optional[datetime] = Field(default_factory=datetime.now, description="进入时间")
    exit_time: Optional[datetime] = Field(None, description="离开时间")
    entry_gate: Optional[str] = Field(None, max_length=50, description="入口门岗")
    exit_gate: Optional[str] = Field(None, max_length=50, description="出口门岗")
    purpose: Optional[str] = Field(None, max_length=100, description="来访目的")
    remarks: Optional[str] = Field(None, description="备注")
    status: VehicleStatusEnum = Field(default=VehicleStatusEnum.在场, description="状态")


class VehicleRecordCreate(VehicleRecordBase):
    pass


class VehicleRecordUpdate(VehicleRecordBase):
    plate_number: Optional[str] = Field(None, max_length=20, description="车牌号")


class VehicleRecord(VehicleRecordBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class VisitorRecordBase(BaseModel):
    visitor_name: str = Field(..., max_length=50, description="访客姓名")
    visitor_phone: Optional[str] = Field(None, max_length=20, description="访客电话")
    visitor_id_card: Optional[str] = Field(None, max_length=18, description="访客身份证号")
    visit_unit: Optional[str] = Field(None, max_length=100, description="访问单位")
    visited_person: Optional[str] = Field(None, max_length=50, description="被访人")
    visit_purpose: Optional[str] = Field(None, max_length=100, description="来访目的")
    entry_time: Optional[datetime] = Field(default_factory=datetime.now, description="进入时间")
    exit_time: Optional[datetime] = Field(None, description="离开时间")
    visitor_count: int = Field(default=1, description="访客人数")
    credentials: Optional[str] = Field(None, description="携带证件")
    remarks: Optional[str] = Field(None, description="备注")
    status: VisitorStatusEnum = Field(default=VisitorStatusEnum.在场, description="状态")


class VisitorRecordCreate(VisitorRecordBase):
    pass


class VisitorRecordUpdate(VisitorRecordBase):
    visitor_name: Optional[str] = Field(None, max_length=50, description="访客姓名")


class VisitorRecord(VisitorRecordBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class EmergencyReportBase(BaseModel):
    report_title: str = Field(..., max_length=200, description="事件标题")
    event_type: EventTypeEnum = Field(default=EventTypeEnum.其他, description="事件类型")
    location: Optional[str] = Field(None, max_length=200, description="发生地点")
    reporter_name: Optional[str] = Field(None, max_length=50, description="上报人姓名")
    reporter_phone: Optional[str] = Field(None, max_length=20, description="上报人电话")
    report_time: Optional[datetime] = Field(default_factory=datetime.now, description="上报时间")
    event_description: Optional[str] = Field(None, description="事件描述")
    handle_person: Optional[str] = Field(None, max_length=50, description="处理人")
    handle_time: Optional[datetime] = Field(None, description="处理时间")
    handle_result: Optional[str] = Field(None, description="处理结果")
    status: EmergencyStatusEnum = Field(default=EmergencyStatusEnum.待处理, description="状态")
    priority: PriorityEnum = Field(default=PriorityEnum.一般, description="优先级")


class EmergencyReportCreate(EmergencyReportBase):
    pass


class EmergencyReportUpdate(EmergencyReportBase):
    report_title: Optional[str] = Field(None, max_length=200, description="事件标题")


class EmergencyReport(EmergencyReportBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class CleaningAreaBase(BaseModel):
    area_name: str = Field(..., max_length=100, description="区域名称")
    area_code: Optional[str] = Field(None, max_length=50, description="区域编号")
    parent_id: Optional[int] = Field(None, description="父区域ID")
    area_type: Optional[str] = Field(None, max_length=50, description="区域类型")
    area_size: Optional[int] = Field(None, description="区域面积")
    cleaning_frequency: Optional[str] = Field(None, max_length=50, description="清洁频次")
    cleaning_standard: Optional[str] = Field(None, description="清洁标准")
    responsible_person: Optional[str] = Field(None, max_length=50, description="责任人")
    responsible_phone: Optional[str] = Field(None, max_length=20, description="责任人电话")
    status: EnableStatusEnum = Field(default=EnableStatusEnum.启用, description="状态")


class CleaningAreaCreate(CleaningAreaBase):
    pass


class CleaningAreaUpdate(CleaningAreaBase):
    area_name: Optional[str] = Field(None, max_length=100, description="区域名称")


class CleaningArea(CleaningAreaBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class CleaningRecordBase(BaseModel):
    area_id: int = Field(..., description="区域ID")
    cleaning_date: date = Field(..., description="清洁日期")
    cleaner_name: Optional[str] = Field(None, max_length=50, description="清洁员姓名")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    cleaning_items: Optional[str] = Field(None, description="清洁项目")
    cleaning_quality: Optional[CleaningQualityEnum] = Field(None, description="清洁质量")
    remarks: Optional[str] = Field(None, description="备注")


class CleaningRecordCreate(CleaningRecordBase):
    pass


class CleaningRecordUpdate(CleaningRecordBase):
    area_id: Optional[int] = Field(None, description="区域ID")
    cleaning_date: Optional[date] = Field(None, description="清洁日期")


class CleaningRecord(CleaningRecordBase):
    id: int
    create_time: datetime
    update_time: datetime
    area: Optional[CleaningArea] = None

    class Config:
        from_attributes = True


class GreenPlantBase(BaseModel):
    plant_name: str = Field(..., max_length=100, description="植物名称")
    plant_code: Optional[str] = Field(None, max_length=50, description="植物编号")
    plant_type: Optional[str] = Field(None, max_length=50, description="植物类型")
    scientific_name: Optional[str] = Field(None, max_length=100, description="学名")
    location: Optional[str] = Field(None, max_length=200, description="种植位置")
    planting_date: Optional[date] = Field(None, description="种植日期")
    quantity: int = Field(default=1, description="数量")
    growth_status: GrowthStatusEnum = Field(default=GrowthStatusEnum.良好, description="生长状态")
    responsible_person: Optional[str] = Field(None, max_length=50, description="责任人")
    remarks: Optional[str] = Field(None, description="备注")


class GreenPlantCreate(GreenPlantBase):
    pass


class GreenPlantUpdate(GreenPlantBase):
    plant_name: Optional[str] = Field(None, max_length=100, description="植物名称")


class GreenPlant(GreenPlantBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class MaintenancePlanBase(BaseModel):
    plant_id: int = Field(..., description="植物ID")
    plan_name: str = Field(..., max_length=100, description="计划名称")
    maintenance_type: Optional[MaintenanceTypeEnum] = Field(None, description="养护类型")
    frequency: Optional[str] = Field(None, max_length=50, description="养护频次")
    start_date: date = Field(..., description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    description: Optional[str] = Field(None, description="养护描述")
    responsible_person: Optional[str] = Field(None, max_length=50, description="责任人")
    status: MaintenanceStatusEnum = Field(default=MaintenanceStatusEnum.待执行, description="状态")


class MaintenancePlanCreate(MaintenancePlanBase):
    pass


class MaintenancePlanUpdate(MaintenancePlanBase):
    plant_id: Optional[int] = Field(None, description="植物ID")
    plan_name: Optional[str] = Field(None, max_length=100, description="计划名称")
    start_date: Optional[date] = Field(None, description="开始日期")


class MaintenancePlan(MaintenancePlanBase):
    id: int
    create_time: datetime
    update_time: datetime
    plant: Optional[GreenPlant] = None

    class Config:
        from_attributes = True


class MaintenanceRecordBase(BaseModel):
    plan_id: Optional[int] = Field(None, description="养护计划ID")
    plant_id: int = Field(..., description="植物ID")
    maintenance_date: date = Field(..., description="养护日期")
    maintenance_type: Optional[MaintenanceTypeEnum] = Field(None, description="养护类型")
    operator: Optional[str] = Field(None, max_length=50, description="操作人")
    work_content: Optional[str] = Field(None, description="工作内容")
    materials_used: Optional[str] = Field(None, description="使用材料")
    quality: Optional[CleaningQualityEnum] = Field(None, description="养护质量")
    remarks: Optional[str] = Field(None, description="备注")


class MaintenanceRecordCreate(MaintenanceRecordBase):
    pass


class MaintenanceRecordUpdate(MaintenanceRecordBase):
    plant_id: Optional[int] = Field(None, description="植物ID")
    maintenance_date: Optional[date] = Field(None, description="养护日期")


class MaintenanceRecord(MaintenanceRecordBase):
    id: int
    create_time: datetime
    update_time: datetime
    plan: Optional[MaintenancePlan] = None

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: dict
    total: int
    page: int
    page_size: int

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from app.database import get_db
from app.models import (
    SecurityPersonnel, SecuritySchedule, PatrolRoute, PatrolRecord,
    MonitorDevice, VehicleRecord, VisitorRecord, EmergencyReport
)
from app.schemas import (
    SecurityPersonnelCreate, SecurityPersonnelUpdate, SecurityPersonnel,
    SecurityScheduleCreate, SecurityScheduleUpdate, SecuritySchedule,
    PatrolRouteCreate, PatrolRouteUpdate, PatrolRoute,
    PatrolRecordCreate, PatrolRecordUpdate, PatrolRecord,
    MonitorDeviceCreate, MonitorDeviceUpdate, MonitorDevice,
    VehicleRecordCreate, VehicleRecordUpdate, VehicleRecord,
    VisitorRecordCreate, VisitorRecordUpdate, VisitorRecord,
    EmergencyReportCreate, EmergencyReportUpdate, EmergencyReport,
    PaginatedResponse
)
from app.crud import CRUDBase

router = APIRouter(prefix="/api/security", tags=["秩序维护管理"])

security_personnel_crud = CRUDBase[SecurityPersonnel, SecurityPersonnelCreate, SecurityPersonnelUpdate](SecurityPersonnel)
security_schedule_crud = CRUDBase[SecuritySchedule, SecurityScheduleCreate, SecurityScheduleUpdate](SecuritySchedule)
patrol_route_crud = CRUDBase[PatrolRoute, PatrolRouteCreate, PatrolRouteUpdate](PatrolRoute)
patrol_record_crud = CRUDBase[PatrolRecord, PatrolRecordCreate, PatrolRecordUpdate](PatrolRecord)
monitor_device_crud = CRUDBase[MonitorDevice, MonitorDeviceCreate, MonitorDeviceUpdate](MonitorDevice)
vehicle_record_crud = CRUDBase[VehicleRecord, VehicleRecordCreate, VehicleRecordUpdate](VehicleRecord)
visitor_record_crud = CRUDBase[VisitorRecord, VisitorRecordCreate, VisitorRecordUpdate](VisitorRecord)
emergency_report_crud = CRUDBase[EmergencyReport, EmergencyReportCreate, EmergencyReportUpdate](EmergencyReport)


@router.post("/personnel/", response_model=SecurityPersonnel, summary="创建安保人员")
async def create_security_personnel(
    personnel: SecurityPersonnelCreate,
    db: AsyncSession = Depends(get_db)
):
    if personnel.id_card:
        existing = await security_personnel_crud.get_by_field(db, "id_card", personnel.id_card)
        if existing:
            raise HTTPException(status_code=400, detail="身份证号已存在")
    return await security_personnel_crud.create(db, personnel)


@router.get("/personnel/{personnel_id}", response_model=SecurityPersonnel, summary="获取安保人员详情")
async def get_security_personnel(
    personnel_id: int,
    db: AsyncSession = Depends(get_db)
):
    personnel = await security_personnel_crud.get(db, personnel_id)
    if not personnel:
        raise HTTPException(status_code=404, detail="安保人员不存在")
    return personnel


@router.get("/personnel/", response_model=PaginatedResponse, summary="获取安保人员列表")
async def get_security_personnel_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="姓名"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    items, total = await security_personnel_crud.get_paginated(db, page, page_size)
    return PaginatedResponse(
        data={"items": [SecurityPersonnel.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/personnel/{personnel_id}", response_model=SecurityPersonnel, summary="更新安保人员")
async def update_security_personnel(
    personnel_id: int,
    personnel: SecurityPersonnelUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_personnel = await security_personnel_crud.get(db, personnel_id)
    if not db_personnel:
        raise HTTPException(status_code=404, detail="安保人员不存在")
    return await security_personnel_crud.update(db, db_personnel, personnel)


@router.delete("/personnel/{personnel_id}", summary="删除安保人员")
async def delete_security_personnel(
    personnel_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await security_personnel_crud.remove(db, personnel_id)
    if not success:
        raise HTTPException(status_code=404, detail="安保人员不存在")
    return {"message": "删除成功"}


@router.post("/schedule/", response_model=SecuritySchedule, summary="创建安保排班")
async def create_security_schedule(
    schedule: SecurityScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    personnel = await security_personnel_crud.get(db, schedule.personnel_id)
    if not personnel:
        raise HTTPException(status_code=400, detail="安保人员不存在")
    return await security_schedule_crud.create(db, schedule)


@router.get("/schedule/{schedule_id}", response_model=SecuritySchedule, summary="获取安保排班详情")
async def get_security_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    schedule = await security_schedule_crud.get(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="排班记录不存在")
    return schedule


@router.get("/schedule/", response_model=PaginatedResponse, summary="获取安保排班列表")
async def get_security_schedule_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    personnel_id: Optional[int] = Query(None, description="安保人员ID"),
    schedule_date: Optional[date] = Query(None, description="排班日期"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if personnel_id:
        filter_kwargs["personnel_id"] = personnel_id
    if schedule_date:
        filter_kwargs["schedule_date"] = schedule_date
    if status:
        filter_kwargs["status"] = status
    
    items, total = await security_schedule_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [SecuritySchedule.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/schedule/{schedule_id}", response_model=SecuritySchedule, summary="更新安保排班")
async def update_security_schedule(
    schedule_id: int,
    schedule: SecurityScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_schedule = await security_schedule_crud.get(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="排班记录不存在")
    return await security_schedule_crud.update(db, db_schedule, schedule)


@router.delete("/schedule/{schedule_id}", summary="删除安保排班")
async def delete_security_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await security_schedule_crud.remove(db, schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="排班记录不存在")
    return {"message": "删除成功"}


@router.post("/patrol-route/", response_model=PatrolRoute, summary="创建巡逻路线")
async def create_patrol_route(
    route: PatrolRouteCreate,
    db: AsyncSession = Depends(get_db)
):
    if route.route_code:
        existing = await patrol_route_crud.get_by_field(db, "route_code", route.route_code)
        if existing:
            raise HTTPException(status_code=400, detail="路线编号已存在")
    return await patrol_route_crud.create(db, route)


@router.get("/patrol-route/{route_id}", response_model=PatrolRoute, summary="获取巡逻路线详情")
async def get_patrol_route(
    route_id: int,
    db: AsyncSession = Depends(get_db)
):
    route = await patrol_route_crud.get(db, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="巡逻路线不存在")
    return route


@router.get("/patrol-route/", response_model=PaginatedResponse, summary="获取巡逻路线列表")
async def get_patrol_route_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if status:
        filter_kwargs["status"] = status
    
    items, total = await patrol_route_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [PatrolRoute.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/patrol-route/{route_id}", response_model=PatrolRoute, summary="更新巡逻路线")
async def update_patrol_route(
    route_id: int,
    route: PatrolRouteUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_route = await patrol_route_crud.get(db, route_id)
    if not db_route:
        raise HTTPException(status_code=404, detail="巡逻路线不存在")
    return await patrol_route_crud.update(db, db_route, route)


@router.delete("/patrol-route/{route_id}", summary="删除巡逻路线")
async def delete_patrol_route(
    route_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await patrol_route_crud.remove(db, route_id)
    if not success:
        raise HTTPException(status_code=404, detail="巡逻路线不存在")
    return {"message": "删除成功"}


@router.post("/patrol-record/", response_model=PatrolRecord, summary="创建巡逻记录")
async def create_patrol_record(
    record: PatrolRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    route = await patrol_route_crud.get(db, record.route_id)
    if not route:
        raise HTTPException(status_code=400, detail="巡逻路线不存在")
    personnel = await security_personnel_crud.get(db, record.personnel_id)
    if not personnel:
        raise HTTPException(status_code=400, detail="安保人员不存在")
    return await patrol_record_crud.create(db, record)


@router.get("/patrol-record/{record_id}", response_model=PatrolRecord, summary="获取巡逻记录详情")
async def get_patrol_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    record = await patrol_record_crud.get(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="巡逻记录不存在")
    return record


@router.get("/patrol-record/", response_model=PaginatedResponse, summary="获取巡逻记录列表")
async def get_patrol_record_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    route_id: Optional[int] = Query(None, description="路线ID"),
    personnel_id: Optional[int] = Query(None, description="安保人员ID"),
    patrol_date: Optional[date] = Query(None, description="巡逻日期"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if route_id:
        filter_kwargs["route_id"] = route_id
    if personnel_id:
        filter_kwargs["personnel_id"] = personnel_id
    if patrol_date:
        filter_kwargs["patrol_date"] = patrol_date
    if status:
        filter_kwargs["status"] = status
    
    items, total = await patrol_record_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [PatrolRecord.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/patrol-record/{record_id}", response_model=PatrolRecord, summary="更新巡逻记录")
async def update_patrol_record(
    record_id: int,
    record: PatrolRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_record = await patrol_record_crud.get(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="巡逻记录不存在")
    return await patrol_record_crud.update(db, db_record, record)


@router.delete("/patrol-record/{record_id}", summary="删除巡逻记录")
async def delete_patrol_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await patrol_record_crud.remove(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="巡逻记录不存在")
    return {"message": "删除成功"}


@router.post("/monitor-device/", response_model=MonitorDevice, summary="创建监控设备")
async def create_monitor_device(
    device: MonitorDeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    if device.device_code:
        existing = await monitor_device_crud.get_by_field(db, "device_code", device.device_code)
        if existing:
            raise HTTPException(status_code=400, detail="设备编号已存在")
    return await monitor_device_crud.create(db, device)


@router.get("/monitor-device/{device_id}", response_model=MonitorDevice, summary="获取监控设备详情")
async def get_monitor_device(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    device = await monitor_device_crud.get(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="监控设备不存在")
    return device


@router.get("/monitor-device/", response_model=PaginatedResponse, summary="获取监控设备列表")
async def get_monitor_device_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    device_type: Optional[str] = Query(None, description="设备类型"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if device_type:
        filter_kwargs["device_type"] = device_type
    if status:
        filter_kwargs["status"] = status
    
    items, total = await monitor_device_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [MonitorDevice.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/monitor-device/{device_id}", response_model=MonitorDevice, summary="更新监控设备")
async def update_monitor_device(
    device_id: int,
    device: MonitorDeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_device = await monitor_device_crud.get(db, device_id)
    if not db_device:
        raise HTTPException(status_code=404, detail="监控设备不存在")
    return await monitor_device_crud.update(db, db_device, device)


@router.delete("/monitor-device/{device_id}", summary="删除监控设备")
async def delete_monitor_device(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await monitor_device_crud.remove(db, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="监控设备不存在")
    return {"message": "删除成功"}


@router.post("/vehicle-record/", response_model=VehicleRecord, summary="创建车辆出入记录")
async def create_vehicle_record(
    record: VehicleRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await vehicle_record_crud.create(db, record)


@router.get("/vehicle-record/{record_id}", response_model=VehicleRecord, summary="获取车辆出入记录详情")
async def get_vehicle_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    record = await vehicle_record_crud.get(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="车辆记录不存在")
    return record


@router.get("/vehicle-record/", response_model=PaginatedResponse, summary="获取车辆出入记录列表")
async def get_vehicle_record_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    plate_number: Optional[str] = Query(None, description="车牌号"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if status:
        filter_kwargs["status"] = status
    
    items, total = await vehicle_record_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [VehicleRecord.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/vehicle-record/{record_id}", response_model=VehicleRecord, summary="更新车辆出入记录")
async def update_vehicle_record(
    record_id: int,
    record: VehicleRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_record = await vehicle_record_crud.get(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="车辆记录不存在")
    return await vehicle_record_crud.update(db, db_record, record)


@router.delete("/vehicle-record/{record_id}", summary="删除车辆出入记录")
async def delete_vehicle_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await vehicle_record_crud.remove(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="车辆记录不存在")
    return {"message": "删除成功"}


@router.post("/visitor-record/", response_model=VisitorRecord, summary="创建外来人员记录")
async def create_visitor_record(
    record: VisitorRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await visitor_record_crud.create(db, record)


@router.get("/visitor-record/{record_id}", response_model=VisitorRecord, summary="获取外来人员记录详情")
async def get_visitor_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    record = await visitor_record_crud.get(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="访客记录不存在")
    return record


@router.get("/visitor-record/", response_model=PaginatedResponse, summary="获取外来人员记录列表")
async def get_visitor_record_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    visitor_name: Optional[str] = Query(None, description="访客姓名"),
    visited_person: Optional[str] = Query(None, description="被访人"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if status:
        filter_kwargs["status"] = status
    
    items, total = await visitor_record_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [VisitorRecord.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/visitor-record/{record_id}", response_model=VisitorRecord, summary="更新外来人员记录")
async def update_visitor_record(
    record_id: int,
    record: VisitorRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_record = await visitor_record_crud.get(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="访客记录不存在")
    return await visitor_record_crud.update(db, db_record, record)


@router.delete("/visitor-record/{record_id}", summary="删除外来人员记录")
async def delete_visitor_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await visitor_record_crud.remove(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="访客记录不存在")
    return {"message": "删除成功"}


@router.post("/emergency-report/", response_model=EmergencyReport, summary="创建突发事件上报")
async def create_emergency_report(
    report: EmergencyReportCreate,
    db: AsyncSession = Depends(get_db)
):
    return await emergency_report_crud.create(db, report)


@router.get("/emergency-report/{report_id}", response_model=EmergencyReport, summary="获取突发事件上报详情")
async def get_emergency_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    report = await emergency_report_crud.get(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="突发事件报告不存在")
    return report


@router.get("/emergency-report/", response_model=PaginatedResponse, summary="获取突发事件上报列表")
async def get_emergency_report_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    event_type: Optional[str] = Query(None, description="事件类型"),
    status: Optional[str] = Query(None, description="状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if event_type:
        filter_kwargs["event_type"] = event_type
    if status:
        filter_kwargs["status"] = status
    if priority:
        filter_kwargs["priority"] = priority
    
    items, total = await emergency_report_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [EmergencyReport.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/emergency-report/{report_id}", response_model=EmergencyReport, summary="更新突发事件上报")
async def update_emergency_report(
    report_id: int,
    report: EmergencyReportUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_report = await emergency_report_crud.get(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="突发事件报告不存在")
    return await emergency_report_crud.update(db, db_report, report)


@router.delete("/emergency-report/{report_id}", summary="删除突发事件上报")
async def delete_emergency_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await emergency_report_crud.remove(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="突发事件报告不存在")
    return {"message": "删除成功"}

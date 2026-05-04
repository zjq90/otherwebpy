from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from app.database import get_db
from app.models import (
    CleaningArea, CleaningRecord, GreenPlant, MaintenancePlan, MaintenanceRecord
)
from app.schemas import (
    CleaningAreaCreate, CleaningAreaUpdate, CleaningArea,
    CleaningRecordCreate, CleaningRecordUpdate, CleaningRecord,
    GreenPlantCreate, GreenPlantUpdate, GreenPlant,
    MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlan,
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecord,
    PaginatedResponse
)
from app.crud import CRUDBase

router = APIRouter(prefix="/api/environment", tags=["环境保洁与绿化养护"])

cleaning_area_crud = CRUDBase[CleaningArea, CleaningAreaCreate, CleaningAreaUpdate](CleaningArea)
cleaning_record_crud = CRUDBase[CleaningRecord, CleaningRecordCreate, CleaningRecordUpdate](CleaningRecord)
green_plant_crud = CRUDBase[GreenPlant, GreenPlantCreate, GreenPlantUpdate](GreenPlant)
maintenance_plan_crud = CRUDBase[MaintenancePlan, MaintenancePlanCreate, MaintenancePlanUpdate](MaintenancePlan)
maintenance_record_crud = CRUDBase[MaintenanceRecord, MaintenanceRecordCreate, MaintenanceRecordUpdate](MaintenanceRecord)


@router.post("/cleaning-area/", response_model=CleaningArea, summary="创建保洁区域")
async def create_cleaning_area(
    area: CleaningAreaCreate,
    db: AsyncSession = Depends(get_db)
):
    if area.area_code:
        existing = await cleaning_area_crud.get_by_field(db, "area_code", area.area_code)
        if existing:
            raise HTTPException(status_code=400, detail="区域编号已存在")
    if area.parent_id:
        parent = await cleaning_area_crud.get(db, area.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父区域不存在")
    return await cleaning_area_crud.create(db, area)


@router.get("/cleaning-area/{area_id}", response_model=CleaningArea, summary="获取保洁区域详情")
async def get_cleaning_area(
    area_id: int,
    db: AsyncSession = Depends(get_db)
):
    area = await cleaning_area_crud.get(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="保洁区域不存在")
    return area


@router.get("/cleaning-area/", response_model=PaginatedResponse, summary="获取保洁区域列表")
async def get_cleaning_area_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    area_type: Optional[str] = Query(None, description="区域类型"),
    parent_id: Optional[int] = Query(None, description="父区域ID"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if area_type:
        filter_kwargs["area_type"] = area_type
    if parent_id is not None:
        filter_kwargs["parent_id"] = parent_id
    if status:
        filter_kwargs["status"] = status
    
    items, total = await cleaning_area_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [CleaningArea.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/cleaning-area/{area_id}", response_model=CleaningArea, summary="更新保洁区域")
async def update_cleaning_area(
    area_id: int,
    area: CleaningAreaUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_area = await cleaning_area_crud.get(db, area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail="保洁区域不存在")
    return await cleaning_area_crud.update(db, db_area, area)


@router.delete("/cleaning-area/{area_id}", summary="删除保洁区域")
async def delete_cleaning_area(
    area_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await cleaning_area_crud.remove(db, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="保洁区域不存在")
    return {"message": "删除成功"}


@router.post("/cleaning-record/", response_model=CleaningRecord, summary="创建清洁记录")
async def create_cleaning_record(
    record: CleaningRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    area = await cleaning_area_crud.get(db, record.area_id)
    if not area:
        raise HTTPException(status_code=400, detail="保洁区域不存在")
    return await cleaning_record_crud.create(db, record)


@router.get("/cleaning-record/{record_id}", response_model=CleaningRecord, summary="获取清洁记录详情")
async def get_cleaning_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    record = await cleaning_record_crud.get(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="清洁记录不存在")
    return record


@router.get("/cleaning-record/", response_model=PaginatedResponse, summary="获取清洁记录列表")
async def get_cleaning_record_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    area_id: Optional[int] = Query(None, description="区域ID"),
    cleaning_date: Optional[date] = Query(None, description="清洁日期"),
    cleaning_quality: Optional[str] = Query(None, description="清洁质量"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if area_id:
        filter_kwargs["area_id"] = area_id
    if cleaning_date:
        filter_kwargs["cleaning_date"] = cleaning_date
    if cleaning_quality:
        filter_kwargs["cleaning_quality"] = cleaning_quality
    
    items, total = await cleaning_record_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [CleaningRecord.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/cleaning-record/{record_id}", response_model=CleaningRecord, summary="更新清洁记录")
async def update_cleaning_record(
    record_id: int,
    record: CleaningRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_record = await cleaning_record_crud.get(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="清洁记录不存在")
    return await cleaning_record_crud.update(db, db_record, record)


@router.delete("/cleaning-record/{record_id}", summary="删除清洁记录")
async def delete_cleaning_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await cleaning_record_crud.remove(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="清洁记录不存在")
    return {"message": "删除成功"}


@router.post("/green-plant/", response_model=GreenPlant, summary="创建绿化植物")
async def create_green_plant(
    plant: GreenPlantCreate,
    db: AsyncSession = Depends(get_db)
):
    if plant.plant_code:
        existing = await green_plant_crud.get_by_field(db, "plant_code", plant.plant_code)
        if existing:
            raise HTTPException(status_code=400, detail="植物编号已存在")
    return await green_plant_crud.create(db, plant)


@router.get("/green-plant/{plant_id}", response_model=GreenPlant, summary="获取绿化植物详情")
async def get_green_plant(
    plant_id: int,
    db: AsyncSession = Depends(get_db)
):
    plant = await green_plant_crud.get(db, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="绿化植物不存在")
    return plant


@router.get("/green-plant/", response_model=PaginatedResponse, summary="获取绿化植物列表")
async def get_green_plant_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    plant_type: Optional[str] = Query(None, description="植物类型"),
    growth_status: Optional[str] = Query(None, description="生长状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if plant_type:
        filter_kwargs["plant_type"] = plant_type
    if growth_status:
        filter_kwargs["growth_status"] = growth_status
    
    items, total = await green_plant_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [GreenPlant.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/green-plant/{plant_id}", response_model=GreenPlant, summary="更新绿化植物")
async def update_green_plant(
    plant_id: int,
    plant: GreenPlantUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_plant = await green_plant_crud.get(db, plant_id)
    if not db_plant:
        raise HTTPException(status_code=404, detail="绿化植物不存在")
    return await green_plant_crud.update(db, db_plant, plant)


@router.delete("/green-plant/{plant_id}", summary="删除绿化植物")
async def delete_green_plant(
    plant_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await green_plant_crud.remove(db, plant_id)
    if not success:
        raise HTTPException(status_code=404, detail="绿化植物不存在")
    return {"message": "删除成功"}


@router.post("/maintenance-plan/", response_model=MaintenancePlan, summary="创建养护计划")
async def create_maintenance_plan(
    plan: MaintenancePlanCreate,
    db: AsyncSession = Depends(get_db)
):
    plant = await green_plant_crud.get(db, plan.plant_id)
    if not plant:
        raise HTTPException(status_code=400, detail="绿化植物不存在")
    return await maintenance_plan_crud.create(db, plan)


@router.get("/maintenance-plan/{plan_id}", response_model=MaintenancePlan, summary="获取养护计划详情")
async def get_maintenance_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    plan = await maintenance_plan_crud.get(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="养护计划不存在")
    return plan


@router.get("/maintenance-plan/", response_model=PaginatedResponse, summary="获取养护计划列表")
async def get_maintenance_plan_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    plant_id: Optional[int] = Query(None, description="植物ID"),
    maintenance_type: Optional[str] = Query(None, description="养护类型"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if plant_id:
        filter_kwargs["plant_id"] = plant_id
    if maintenance_type:
        filter_kwargs["maintenance_type"] = maintenance_type
    if status:
        filter_kwargs["status"] = status
    
    items, total = await maintenance_plan_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [MaintenancePlan.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/maintenance-plan/{plan_id}", response_model=MaintenancePlan, summary="更新养护计划")
async def update_maintenance_plan(
    plan_id: int,
    plan: MaintenancePlanUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_plan = await maintenance_plan_crud.get(db, plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="养护计划不存在")
    return await maintenance_plan_crud.update(db, db_plan, plan)


@router.delete("/maintenance-plan/{plan_id}", summary="删除养护计划")
async def delete_maintenance_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await maintenance_plan_crud.remove(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="养护计划不存在")
    return {"message": "删除成功"}


@router.post("/maintenance-record/", response_model=MaintenanceRecord, summary="创建养护记录")
async def create_maintenance_record(
    record: MaintenanceRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    plant = await green_plant_crud.get(db, record.plant_id)
    if not plant:
        raise HTTPException(status_code=400, detail="绿化植物不存在")
    if record.plan_id:
        plan = await maintenance_plan_crud.get(db, record.plan_id)
        if not plan:
            raise HTTPException(status_code=400, detail="养护计划不存在")
    return await maintenance_record_crud.create(db, record)


@router.get("/maintenance-record/{record_id}", response_model=MaintenanceRecord, summary="获取养护记录详情")
async def get_maintenance_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    record = await maintenance_record_crud.get(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="养护记录不存在")
    return record


@router.get("/maintenance-record/", response_model=PaginatedResponse, summary="获取养护记录列表")
async def get_maintenance_record_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    plant_id: Optional[int] = Query(None, description="植物ID"),
    plan_id: Optional[int] = Query(None, description="计划ID"),
    maintenance_date: Optional[date] = Query(None, description="养护日期"),
    maintenance_type: Optional[str] = Query(None, description="养护类型"),
    db: AsyncSession = Depends(get_db)
):
    filter_kwargs = {}
    if plant_id:
        filter_kwargs["plant_id"] = plant_id
    if plan_id:
        filter_kwargs["plan_id"] = plan_id
    if maintenance_date:
        filter_kwargs["maintenance_date"] = maintenance_date
    if maintenance_type:
        filter_kwargs["maintenance_type"] = maintenance_type
    
    items, total = await maintenance_record_crud.get_paginated(db, page, page_size, **filter_kwargs)
    return PaginatedResponse(
        data={"items": [MaintenanceRecord.model_validate(item) for item in items]},
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/maintenance-record/{record_id}", response_model=MaintenanceRecord, summary="更新养护记录")
async def update_maintenance_record(
    record_id: int,
    record: MaintenanceRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_record = await maintenance_record_crud.get(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="养护记录不存在")
    return await maintenance_record_crud.update(db, db_record, record)


@router.delete("/maintenance-record/{record_id}", summary="删除养护记录")
async def delete_maintenance_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await maintenance_record_crud.remove(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="养护记录不存在")
    return {"message": "删除成功"}

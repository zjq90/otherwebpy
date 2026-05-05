"""
资源调度相关API路由
包含车辆管理、运输任务安排等功能
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models.user_models import User
from ..models.business_models import Vehicle, TransportTask
from ..schemas.business_schemas import (
    VehicleCreate, VehicleUpdate, VehicleResponse,
    TransportTaskCreate, TransportTaskUpdate, TransportTaskResponse
)
from ..schemas.user_schemas import ApiResponse, PaginatedResponse
from ..utils.security import (
    get_current_user, require_role, is_admin
)

router = APIRouter(prefix="/transport", tags=["资源调度管理"])


def generate_task_no() -> str:
    """生成运输任务编号"""
    import time
    timestamp = int(time.time())
    return f"TT{timestamp}"


@router.post("/vehicles", response_model=VehicleResponse)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建车辆（管理员权限）
    """
    # 检查车牌号是否已存在
    result = await db.execute(
        select(Vehicle).where(Vehicle.vehicle_no == vehicle_data.vehicle_no)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="车牌号已存在"
        )
    
    vehicle = Vehicle(**vehicle_data.model_dump(), status="idle")
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    
    return VehicleResponse.model_validate(vehicle)


@router.get("/vehicles", response_model=PaginatedResponse)
async def get_vehicles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    vehicle_type: Optional[str] = Query(None, description="车辆类型"),
    status: Optional[str] = Query(None, description="状态"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取车辆列表（资源调度员权限）
    """
    # 构建查询条件
    query = select(Vehicle)
    
    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)
    
    if status:
        query = query.where(Vehicle.status == status)
    
    if keyword:
        query = query.where(
            (Vehicle.vehicle_no.contains(keyword)) |
            (Vehicle.driver_name.contains(keyword))
        )
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(Vehicle.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    vehicle_responses = [VehicleResponse.model_validate(v) for v in vehicles]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=vehicle_responses
    )


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取车辆详情（资源调度员权限）
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    return VehicleResponse.model_validate(vehicle)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新车辆信息（资源调度员权限）
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 更新字段
    update_data = vehicle_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)
    
    # 如果更新了位置信息，更新位置时间
    if 'latitude' in update_data or 'longitude' in update_data or 'current_location' in update_data:
        vehicle.location_updated_at = datetime.utcnow()
    
    vehicle.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(vehicle)
    
    return VehicleResponse.model_validate(vehicle)


@router.delete("/vehicles/{vehicle_id}", response_model=ApiResponse)
async def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    删除车辆（管理员权限）
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 检查是否有未完成的运输任务
    task_result = await db.execute(
        select(TransportTask).where(
            TransportTask.vehicle_id == vehicle_id,
            TransportTask.status != "completed"
        )
    )
    unfinished_tasks = task_result.scalars().all()
    
    if unfinished_tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该车辆有未完成的运输任务，无法删除"
        )
    
    await db.delete(vehicle)
    await db.commit()
    
    return ApiResponse(message="车辆已删除")


@router.post("/tasks", response_model=TransportTaskResponse)
async def create_transport_task(
    task_data: TransportTaskCreate,
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    安排运输任务（资源调度员权限）
    """
    # 检查车辆是否存在且可用
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == task_data.vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 检查车辆是否空闲
    if vehicle.status == "busy":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该车辆当前正在作业中"
        )
    
    # 创建运输任务
    task = TransportTask(
        **task_data.model_dump(),
        task_no=generate_task_no(),
        scheduler_id=current_user.id,
        status="pending",
        progress=0
    )
    db.add(task)
    
    # 更新车辆状态
    vehicle.status = "busy"
    vehicle.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    
    return TransportTaskResponse.model_validate(task)


@router.get("/tasks", response_model=PaginatedResponse)
async def get_transport_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态"),
    vehicle_id: Optional[int] = Query(None, description="车辆ID"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取运输任务列表（资源调度员权限）
    """
    # 构建查询条件
    query = select(TransportTask)
    
    if status:
        query = query.where(TransportTask.status == status)
    
    if vehicle_id:
        query = query.where(TransportTask.vehicle_id == vehicle_id)
    
    if start_date:
        query = query.where(TransportTask.scheduled_time >= start_date)
    
    if end_date:
        query = query.where(TransportTask.scheduled_time <= end_date)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(TransportTask.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    task_responses = [TransportTaskResponse.model_validate(t) for t in tasks]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=task_responses
    )


@router.get("/tasks/{task_id}", response_model=TransportTaskResponse)
async def get_transport_task(
    task_id: int,
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取运输任务详情（资源调度员权限）
    """
    result = await db.execute(
        select(TransportTask).where(TransportTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运输任务不存在"
        )
    
    return TransportTaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TransportTaskResponse)
async def update_transport_task(
    task_id: int,
    task_data: TransportTaskUpdate,
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新运输任务进度（资源调度员权限）
    """
    result = await db.execute(
        select(TransportTask).options(
            # 这里需要联表查询车辆
        ).where(TransportTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运输任务不存在"
        )
    
    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    # 如果任务完成，更新车辆状态
    if task_data.status == "completed":
        # 查询车辆
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.id == task.vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        if vehicle:
            vehicle.status = "idle"
            vehicle.updated_at = datetime.utcnow()
    
    # 如果开始运输
    if task_data.status == "in_transit" and not task.actual_departure_time:
        task.actual_departure_time = datetime.utcnow()
    
    # 如果完成运输
    if task_data.status == "completed" and not task.actual_arrival_time:
        task.actual_arrival_time = datetime.utcnow()
        task.progress = 100
    
    task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    
    return TransportTaskResponse.model_validate(task)


@router.get("/vehicles/available", response_model=List[VehicleResponse])
async def get_available_vehicles(
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    获取可用车辆列表（资源调度员权限）
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.status == "idle")
    )
    vehicles = result.scalars().all()
    
    return [VehicleResponse.model_validate(v) for v in vehicles]


@router.put("/vehicles/{vehicle_id}/location", response_model=VehicleResponse)
async def update_vehicle_location(
    vehicle_id: int,
    location_data: VehicleUpdate,
    current_user: User = Depends(require_role("resource_scheduler")),
    db: AsyncSession = Depends(get_db)
):
    """
    更新车辆位置信息（资源调度员权限）
    """
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 更新位置信息
    if location_data.current_location:
        vehicle.current_location = location_data.current_location
    if location_data.latitude is not None:
        vehicle.latitude = location_data.latitude
    if location_data.longitude is not None:
        vehicle.longitude = location_data.longitude
    
    vehicle.location_updated_at = datetime.utcnow()
    vehicle.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(vehicle)
    
    return VehicleResponse.model_validate(vehicle)

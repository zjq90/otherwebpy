"""
位置记录路由模块
处理车辆位置上报、轨迹查询等操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.location_record import LocationRecord
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.user import User, UserRole
from app.models.transport_task import TransportTask
from app.schemas.location_record import (
    LocationRecordCreate,
    LocationRecordResponse,
    LocationBatchCreate,
    TrajectoryResponse,
    TrajectoryPoint,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.security import (
    get_current_user,
    require_admin,
    require_dispatcher,
    require_driver,
)
from app.utils.helpers import calculate_distance

router = APIRouter(
    prefix="/api/locations",
    tags=["位置管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("", response_model=ApiResponse[LocationRecordResponse])
async def create_location(
    location_data: LocationRecordCreate,
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    上报车辆位置
    司机上报自己车辆的位置信息
    """
    # 检查司机是否有权限上报该车辆的位置
    if current_user.vehicle_id != location_data.vehicle_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权上报该车辆的位置信息"
        )
    
    # 检查车辆是否存在
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == location_data.vehicle_id,
            Vehicle.is_deleted == False,
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 创建位置记录
    new_location = LocationRecord(
        vehicle_id=location_data.vehicle_id,
        user_id=location_data.user_id or current_user.id,
        transport_task_id=location_data.transport_task_id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        speed=location_data.speed,
        direction=location_data.direction,
        accuracy=location_data.accuracy,
        device_type=location_data.device_type,
        device_id=location_data.device_id,
        recorded_at=datetime.utcnow(),
    )
    
    db.add(new_location)
    
    # 更新车辆的当前位置
    vehicle.current_latitude = location_data.latitude
    vehicle.current_longitude = location_data.longitude
    vehicle.current_address = location_data.address
    vehicle.last_location_update = datetime.utcnow()
    
    # 如果有任务，更新任务的预计到达时间
    if location_data.transport_task_id:
        result = await db.execute(
            select(TransportTask).where(
                TransportTask.id == location_data.transport_task_id,
                TransportTask.is_deleted == False,
            )
        )
        task = result.scalar_one_or_none()
        if task and task.unloading_latitude and task.unloading_longitude:
            # 计算预计到达时间（简化处理，实际可以根据速度计算）
            from app.utils.helpers import calculate_estimated_arrival
            task.estimated_arrival_time = calculate_estimated_arrival(
                location_data.latitude,
                location_data.longitude,
                task.unloading_latitude,
                task.unloading_longitude,
            )
    
    await db.commit()
    await db.refresh(new_location)
    
    location_response = LocationRecordResponse.model_validate(new_location)
    return ApiResponse(
        code=200,
        message="位置上报成功",
        data=location_response,
    )


@router.post("/batch", response_model=ApiResponse[int])
async def create_locations_batch(
    batch_data: LocationBatchCreate,
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    批量上报车辆位置
    用于批量上传位置记录
    """
    if not batch_data.locations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="位置数据不能为空"
        )
    
    # 检查所有位置是否属于当前司机的车辆
    vehicle_id = batch_data.locations[0].vehicle_id
    if current_user.vehicle_id != vehicle_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权上报该车辆的位置信息"
        )
    
    # 检查车辆是否存在
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.is_deleted == False,
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 批量创建位置记录
    now = datetime.utcnow()
    location_records = []
    for location_data in batch_data.locations:
        new_location = LocationRecord(
            vehicle_id=location_data.vehicle_id,
            user_id=location_data.user_id or current_user.id,
            transport_task_id=location_data.transport_task_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            address=location_data.address,
            speed=location_data.speed,
            direction=location_data.direction,
            accuracy=location_data.accuracy,
            device_type=location_data.device_type,
            device_id=location_data.device_id,
            recorded_at=now,
        )
        location_records.append(new_location)
        db.add(new_location)
    
    # 更新车辆的最新位置（使用最后一条记录）
    last_location = batch_data.locations[-1]
    vehicle.current_latitude = last_location.latitude
    vehicle.current_longitude = last_location.longitude
    vehicle.current_address = last_location.address
    vehicle.last_location_update = now
    
    await db.commit()
    
    return ApiResponse(
        code=200,
        message=f"成功上报 {len(location_records)} 条位置记录",
        data=len(location_records),
    )


@router.get("", response_model=ApiResponse[PaginatedResponse[LocationRecordResponse]])
async def get_locations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    vehicle_id: Optional[int] = Query(None, description="车辆ID筛选"),
    transport_task_id: Optional[int] = Query(None, description="任务ID筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取位置记录列表
    支持分页、车辆筛选、任务筛选和时间范围筛选
    """
    # 构建查询条件
    query = select(LocationRecord)
    
    # 车辆筛选
    if vehicle_id:
        query = query.where(LocationRecord.vehicle_id == vehicle_id)
    
    # 任务筛选
    if transport_task_id:
        query = query.where(LocationRecord.transport_task_id == transport_task_id)
    
    # 时间范围筛选
    if start_time:
        query = query.where(LocationRecord.recorded_at >= start_time)
    if end_time:
        query = query.where(LocationRecord.recorded_at <= end_time)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(LocationRecord.recorded_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    locations = result.scalars().all()
    
    # 构建响应
    location_responses = [LocationRecordResponse.model_validate(location) for location in locations]
    paginated_response = PaginatedResponse(
        items=location_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=paginated_response,
    )


@router.get("/trajectory/{vehicle_id}", response_model=ApiResponse[TrajectoryResponse])
async def get_vehicle_trajectory(
    vehicle_id: int,
    start_time: Optional[datetime] = Query(None, description="开始时间，默认24小时前"),
    end_time: Optional[datetime] = Query(None, description="结束时间，默认当前时间"),
    transport_task_id: Optional[int] = Query(None, description="任务ID筛选"),
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取车辆行驶轨迹
    查询指定车辆在指定时间范围内的行驶轨迹
    """
    # 检查车辆是否存在
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.is_deleted == False,
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 设置默认时间范围
    if not start_time:
        start_time = datetime.utcnow() - timedelta(hours=24)
    if not end_time:
        end_time = datetime.utcnow()
    
    # 构建查询条件
    query = select(LocationRecord).where(
        LocationRecord.vehicle_id == vehicle_id,
        LocationRecord.recorded_at >= start_time,
        LocationRecord.recorded_at <= end_time,
    )
    
    # 任务筛选
    if transport_task_id:
        query = query.where(LocationRecord.transport_task_id == transport_task_id)
    
    # 按时间排序
    query = query.order_by(LocationRecord.recorded_at.asc())
    result = await db.execute(query)
    locations = result.scalars().all()
    
    if not locations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该时间范围内没有位置记录"
        )
    
    # 计算总距离
    total_distance = 0.0
    trajectory_points = []
    for i, location in enumerate(locations):
        trajectory_point = TrajectoryPoint(
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            speed=location.speed,
            recorded_at=location.recorded_at,
        )
        trajectory_points.append(trajectory_point)
        
        # 计算距离
        if i > 0:
            prev_location = locations[i-1]
            distance = calculate_distance(
                prev_location.latitude,
                prev_location.longitude,
                location.latitude,
                location.longitude,
            )
            total_distance += distance
    
    # 构建响应
    trajectory_response = TrajectoryResponse(
        vehicle_id=vehicle_id,
        transport_task_id=transport_task_id,
        start_time=start_time,
        end_time=end_time,
        points=trajectory_points,
        total_distance=total_distance,
        total_points=len(trajectory_points),
    )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=trajectory_response,
    )


@router.get("/latest", response_model=ApiResponse[list[LocationRecordResponse]])
async def get_latest_locations(
    vehicle_ids: Optional[str] = Query(None, description="车辆ID列表，逗号分隔"),
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取车辆最新位置
    获取指定车辆的最新位置，用于地图监控
    """
    # 解析车辆ID列表
    if vehicle_ids:
        vehicle_id_list = [int(vid.strip()) for vid in vehicle_ids.split(",") if vid.strip()]
    else:
        # 获取所有未删除的车辆ID
        vehicle_result = await db.execute(
            select(Vehicle.id).where(Vehicle.is_deleted == False)
        )
        vehicle_id_list = [vid[0] for vid in vehicle_result.all()]
    
    if not vehicle_id_list:
        return ApiResponse(
            code=200,
            message="没有车辆",
            data=[],
        )
    
    # 查询每辆车的最新位置
    latest_locations = []
    for vehicle_id in vehicle_id_list:
        result = await db.execute(
            select(LocationRecord)
            .where(LocationRecord.vehicle_id == vehicle_id)
            .order_by(LocationRecord.recorded_at.desc())
            .limit(1)
        )
        location = result.scalar_one_or_none()
        if location:
            latest_locations.append(location)
        else:
            # 如果没有位置记录，使用车辆的当前位置
            vehicle_result = await db.execute(
                select(Vehicle).where(Vehicle.id == vehicle_id)
            )
            vehicle = vehicle_result.scalar_one_or_none()
            if vehicle and vehicle.current_latitude and vehicle.current_longitude:
                # 创建一个临时的位置记录
                fake_location = LocationRecord(
                    id=0,
                    vehicle_id=vehicle_id,
                    user_id=None,
                    transport_task_id=None,
                    latitude=vehicle.current_latitude,
                    longitude=vehicle.current_longitude,
                    address=vehicle.current_address,
                    speed=None,
                    direction=None,
                    accuracy=None,
                    device_type=None,
                    device_id=None,
                    recorded_at=vehicle.last_location_update or datetime.utcnow(),
                    created_at=vehicle.last_location_update or datetime.utcnow(),
                )
                latest_locations.append(fake_location)
    
    # 构建响应
    location_responses = [
        LocationRecordResponse.model_validate(location) for location in latest_locations
    ]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=location_responses,
    )

"""
车辆管理路由模块
处理车辆的增删改查、位置更新等操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime

from app.database import get_db
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType
from app.models.user import User, UserRole, UserStatus
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleLocationUpdate,
    VehicleSimpleResponse,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.security import (
    get_current_user,
    require_admin,
    require_dispatcher,
    require_driver,
)

router = APIRouter(
    prefix="/api/vehicles",
    tags=["车辆管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("", response_model=ApiResponse[VehicleResponse], dependencies=[Depends(require_admin)])
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新车辆
    仅管理员可以创建车辆
    """
    # 检查车牌号是否已存在
    result = await db.execute(select(Vehicle).where(Vehicle.plate_number == vehicle_data.plate_number))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="车牌号已存在"
        )
    
    # 检查司机是否存在且可用
    if vehicle_data.driver_id:
        result = await db.execute(
            select(User).where(
                User.id == vehicle_data.driver_id,
                User.is_deleted == False,
                User.role == UserRole.DRIVER,
            )
        )
        driver = result.scalar_one_or_none()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的司机不存在或不是司机角色"
            )
    
    # 创建新车辆
    new_vehicle = Vehicle(
        plate_number=vehicle_data.plate_number,
        vehicle_name=vehicle_data.vehicle_name,
        vehicle_type=vehicle_data.vehicle_type,
        load_capacity=vehicle_data.load_capacity,
        volume=vehicle_data.volume,
        driver_id=vehicle_data.driver_id,
        status=VehicleStatus.IDLE,
    )
    
    db.add(new_vehicle)
    await db.commit()
    await db.refresh(new_vehicle)
    
    # 如果指定了司机，更新司机的车辆关联
    if vehicle_data.driver_id:
        result = await db.execute(select(User).where(User.id == vehicle_data.driver_id))
        driver = result.scalar_one_or_none()
        if driver:
            driver.vehicle_id = new_vehicle.id
            await db.commit()
    
    vehicle_response = VehicleResponse.model_validate(new_vehicle)
    return ApiResponse(
        code=200,
        message="车辆创建成功",
        data=vehicle_response,
    )


@router.get("", response_model=ApiResponse[PaginatedResponse[VehicleResponse]])
async def get_vehicles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[VehicleStatus] = Query(None, description="车辆状态筛选"),
    vehicle_type: Optional[VehicleType] = Query(None, description="车辆类型筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（车牌号、车辆名称）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取车辆列表
    支持分页、状态筛选、类型筛选和关键词搜索
    """
    # 构建查询条件
    query = select(Vehicle).where(Vehicle.is_deleted == False)
    
    # 状态筛选
    if status:
        query = query.where(Vehicle.status == status)
    
    # 类型筛选
    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Vehicle.plate_number.contains(keyword),
                Vehicle.vehicle_name.contains(keyword),
            )
        )
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    # 构建响应
    vehicle_responses = [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]
    paginated_response = PaginatedResponse(
        items=vehicle_responses,
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


@router.get("/available", response_model=ApiResponse[list[VehicleSimpleResponse]])
async def get_available_vehicles(
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取可用车辆列表
    用于任务分配时选择车辆
    """
    query = select(Vehicle).where(
        Vehicle.is_deleted == False,
        Vehicle.status == VehicleStatus.IDLE,
    ).order_by(Vehicle.created_at.desc())
    
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    vehicle_responses = [VehicleSimpleResponse.model_validate(vehicle) for vehicle in vehicles]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=vehicle_responses,
    )


@router.get("/with-location", response_model=ApiResponse[list[VehicleSimpleResponse]])
async def get_vehicles_with_location(
    status: Optional[VehicleStatus] = Query(None, description="车辆状态筛选"),
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取带位置信息的车辆列表
    用于地图监控显示车辆位置
    """
    query = select(Vehicle).where(Vehicle.is_deleted == False)
    
    if status:
        query = query.where(Vehicle.status == status)
    
    query = query.order_by(Vehicle.created_at.desc())
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    vehicle_responses = [VehicleSimpleResponse.model_validate(vehicle) for vehicle in vehicles]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=vehicle_responses,
    )


@router.get("/{vehicle_id}", response_model=ApiResponse[VehicleResponse])
async def get_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个车辆详情
    """
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == False))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    vehicle_response = VehicleResponse.model_validate(vehicle)
    return ApiResponse(
        code=200,
        message="获取成功",
        data=vehicle_response,
    )


@router.put("/{vehicle_id}", response_model=ApiResponse[VehicleResponse])
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    更新车辆信息
    仅管理员可以更新车辆信息
    """
    # 查询车辆
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == False))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 更新车辆信息
    update_data = vehicle_data.model_dump(exclude_unset=True)
    
    # 检查车牌号是否已被其他车辆使用
    if "plate_number" in update_data and update_data["plate_number"] != vehicle.plate_number:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.plate_number == update_data["plate_number"],
                Vehicle.id != vehicle_id,
                Vehicle.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="车牌号已被使用"
            )
    
    # 检查司机变更
    old_driver_id = vehicle.driver_id
    new_driver_id = update_data.get("driver_id")
    
    # 如果指定了新司机，检查司机是否存在且可用
    if new_driver_id and new_driver_id != old_driver_id:
        result = await db.execute(
            select(User).where(
                User.id == new_driver_id,
                User.is_deleted == False,
                User.role == UserRole.DRIVER,
            )
        )
        new_driver = result.scalar_one_or_none()
        if not new_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的司机不存在或不是司机角色"
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(vehicle, key, value)
    
    vehicle.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(vehicle)
    
    # 处理司机关联变更
    if new_driver_id and new_driver_id != old_driver_id:
        # 清除旧司机的车辆关联
        if old_driver_id:
            result = await db.execute(select(User).where(User.id == old_driver_id))
            old_driver = result.scalar_one_or_none()
            if old_driver:
                old_driver.vehicle_id = None
                old_driver.status = UserStatus.IDLE
        
        # 设置新司机的车辆关联
        result = await db.execute(select(User).where(User.id == new_driver_id))
        new_driver = result.scalar_one_or_none()
        if new_driver:
            new_driver.vehicle_id = vehicle.id
        
        await db.commit()
    
    vehicle_response = VehicleResponse.model_validate(vehicle)
    return ApiResponse(
        code=200,
        message="更新成功",
        data=vehicle_response,
    )


@router.put("/{vehicle_id}/location", response_model=ApiResponse[VehicleResponse])
async def update_vehicle_location(
    vehicle_id: int,
    location_data: VehicleLocationUpdate,
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    更新车辆位置
    司机可以更新自己车辆的位置信息
    """
    # 检查司机是否有权限更新该车辆
    if current_user.vehicle_id != vehicle_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新该车辆的位置信息"
        )
    
    # 查询车辆
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == False))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 更新位置信息
    vehicle.current_latitude = location_data.latitude
    vehicle.current_longitude = location_data.longitude
    vehicle.current_address = location_data.address
    vehicle.last_location_update = datetime.utcnow()
    vehicle.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(vehicle)
    
    vehicle_response = VehicleResponse.model_validate(vehicle)
    return ApiResponse(
        code=200,
        message="位置更新成功",
        data=vehicle_response,
    )


@router.delete("/{vehicle_id}", response_model=ApiResponse[dict], dependencies=[Depends(require_admin)])
async def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除车辆（软删除）
    仅管理员可以删除车辆
    """
    # 查询车辆
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == False))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="车辆不存在"
        )
    
    # 检查车辆是否在使用中
    if vehicle.status == VehicleStatus.IN_TRANSIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="车辆正在运输中，无法删除"
        )
    
    # 清除关联司机的车辆关联
    if vehicle.driver_id:
        result = await db.execute(select(User).where(User.id == vehicle.driver_id))
        driver = result.scalar_one_or_none()
        if driver:
            driver.vehicle_id = None
            driver.status = UserStatus.IDLE
    
    # 软删除
    vehicle.is_deleted = True
    vehicle.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功",
        data={},
    )

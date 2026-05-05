"""
运输任务管理路由模块
处理运输任务的增删改查、分配、状态更新等操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime
import os

from app.database import get_db
from app.models.transport_task import TransportTask, TaskStatus
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.user import User, UserRole, UserStatus
from app.models.task_update import TaskUpdate
from app.models.location_record import LocationRecord
from app.schemas.transport_task import (
    TransportTaskCreate,
    TransportTaskUpdate,
    TransportTaskResponse,
    TaskAssignRequest,
    TaskStatusUpdateRequest,
)
from app.schemas.task_update import PhotoUploadResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.security import (
    get_current_user,
    require_admin,
    require_dispatcher,
    require_driver,
)
from app.utils.helpers import (
    generate_task_no,
    save_upload_file,
    calculate_estimated_arrival,
)
from app.config import settings

router = APIRouter(
    prefix="/api/tasks",
    tags=["运输任务管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("", response_model=ApiResponse[TransportTaskResponse])
async def create_task(
    task_data: TransportTaskCreate,
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新运输任务
    调度员和管理员可以创建运输任务
    """
    # 生成任务编号
    task_no = generate_task_no()
    
    # 创建新任务
    new_task = TransportTask(
        task_no=task_no,
        task_name=task_data.task_name,
        task_description=task_data.task_description,
        cargo_name=task_data.cargo_name,
        cargo_weight=task_data.cargo_weight,
        cargo_volume=task_data.cargo_volume,
        cargo_quantity=task_data.cargo_quantity,
        loading_address=task_data.loading_address,
        loading_latitude=task_data.loading_latitude,
        loading_longitude=task_data.loading_longitude,
        loading_contact=task_data.loading_contact,
        loading_phone=task_data.loading_phone,
        unloading_address=task_data.unloading_address,
        unloading_latitude=task_data.unloading_latitude,
        unloading_longitude=task_data.unloading_longitude,
        unloading_contact=task_data.unloading_contact,
        unloading_phone=task_data.unloading_phone,
        scheduled_departure_time=task_data.scheduled_departure_time,
        scheduled_arrival_time=task_data.scheduled_arrival_time,
        remarks=task_data.remarks,
        dispatcher_id=current_user.id,
        status=TaskStatus.PENDING,
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    task_response = TransportTaskResponse.model_validate(new_task)
    return ApiResponse(
        code=200,
        message="任务创建成功",
        data=task_response,
    )


@router.get("", response_model=ApiResponse[PaginatedResponse[TransportTaskResponse]])
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[TaskStatus] = Query(None, description="任务状态筛选"),
    driver_id: Optional[int] = Query(None, description="司机ID筛选"),
    vehicle_id: Optional[int] = Query(None, description="车辆ID筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（任务编号、名称、货物名称）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取运输任务列表
    支持分页、状态筛选、司机筛选、车辆筛选和关键词搜索
    司机只能看到自己的任务
    """
    # 构建查询条件
    query = select(TransportTask).where(TransportTask.is_deleted == False)
    
    # 司机只能看到自己的任务
    if current_user.role == UserRole.DRIVER:
        query = query.where(TransportTask.driver_id == current_user.id)
    
    # 状态筛选
    if status:
        query = query.where(TransportTask.status == status)
    
    # 司机筛选
    if driver_id:
        query = query.where(TransportTask.driver_id == driver_id)
    
    # 车辆筛选
    if vehicle_id:
        query = query.where(TransportTask.vehicle_id == vehicle_id)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                TransportTask.task_no.contains(keyword),
                TransportTask.task_name.contains(keyword),
                TransportTask.cargo_name.contains(keyword),
            )
        )
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(TransportTask.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # 构建响应
    task_responses = [TransportTaskResponse.model_validate(task) for task in tasks]
    paginated_response = PaginatedResponse(
        items=task_responses,
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


@router.get("/my-tasks", response_model=ApiResponse[PaginatedResponse[TransportTaskResponse]])
async def get_my_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[TaskStatus] = Query(None, description="任务状态筛选"),
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前司机的任务列表
    司机专用接口，查看自己的任务
    """
    # 构建查询条件
    query = select(TransportTask).where(
        TransportTask.is_deleted == False,
        TransportTask.driver_id == current_user.id,
    )
    
    # 状态筛选
    if status:
        query = query.where(TransportTask.status == status)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(TransportTask.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # 构建响应
    task_responses = [TransportTaskResponse.model_validate(task) for task in tasks]
    paginated_response = PaginatedResponse(
        items=task_responses,
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


@router.get("/{task_id}", response_model=ApiResponse[TransportTaskResponse])
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个运输任务详情
    """
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 司机只能看到自己的任务
    if current_user.role == UserRole.DRIVER and task.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该任务"
        )
    
    task_response = TransportTaskResponse.model_validate(task)
    return ApiResponse(
        code=200,
        message="获取成功",
        data=task_response,
    )


@router.put("/{task_id}", response_model=ApiResponse[TransportTaskResponse])
async def update_task(
    task_id: int,
    task_data: TransportTaskUpdate,
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    更新运输任务信息
    调度员和管理员可以更新任务信息
    """
    # 查询任务
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查任务状态，已出发的任务不能修改基本信息
    if task.status in [TaskStatus.DEPARTED, TaskStatus.ARRIVED, TaskStatus.UNLOADING, TaskStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务已出发，无法修改基本信息"
        )
    
    # 更新任务信息
    update_data = task_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    
    task_response = TransportTaskResponse.model_validate(task)
    return ApiResponse(
        code=200,
        message="更新成功",
        data=task_response,
    )


@router.post("/{task_id}/assign", response_model=ApiResponse[TransportTaskResponse])
async def assign_task(
    task_id: int,
    assign_data: TaskAssignRequest,
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    分配运输任务
    调度员为任务分配车辆和司机
    """
    # 查询任务
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待分配的任务才能分配"
        )
    
    # 检查车辆是否存在且可用
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == assign_data.vehicle_id,
            Vehicle.is_deleted == False,
            Vehicle.status == VehicleStatus.IDLE,
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="车辆不存在或不可用"
        )
    
    # 检查司机是否存在且可用
    result = await db.execute(
        select(User).where(
            User.id == assign_data.driver_id,
            User.is_deleted == False,
            User.role == UserRole.DRIVER,
            User.status == UserStatus.IDLE,
        )
    )
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="司机不存在或不可用"
        )
    
    # 更新任务信息
    task.vehicle_id = assign_data.vehicle_id
    task.driver_id = assign_data.driver_id
    task.dispatcher_id = current_user.id
    task.status = TaskStatus.ASSIGNED
    task.updated_at = datetime.utcnow()
    
    # 更新车辆状态
    vehicle.status = VehicleStatus.IN_TRANSIT
    
    # 更新司机状态
    driver.status = UserStatus.BUSY
    driver.vehicle_id = assign_data.vehicle_id
    
    # 计算预计到达时间
    if vehicle.current_latitude and vehicle.current_longitude and task.unloading_latitude and task.unloading_longitude:
        task.estimated_arrival_time = calculate_estimated_arrival(
            vehicle.current_latitude,
            vehicle.current_longitude,
            task.unloading_latitude,
            task.unloading_longitude,
        )
    
    # 创建任务更新记录
    task_update = TaskUpdate(
        transport_task_id=task.id,
        user_id=current_user.id,
        old_status=TaskStatus.PENDING,
        new_status=TaskStatus.ASSIGNED,
        update_type="assign",
        description=f"调度员 {current_user.real_name} 分配了任务",
    )
    db.add(task_update)
    
    await db.commit()
    await db.refresh(task)
    
    task_response = TransportTaskResponse.model_validate(task)
    return ApiResponse(
        code=200,
        message="任务分配成功",
        data=task_response,
    )


@router.post("/{task_id}/confirm", response_model=ApiResponse[TransportTaskResponse])
async def confirm_task(
    task_id: int,
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    司机确认接受任务
    司机确认接受分配的任务
    """
    # 查询任务
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查是否是任务的司机
    if task.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权确认该任务"
        )
    
    # 检查任务状态
    if task.status != TaskStatus.ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有已分配的任务才能确认"
        )
    
    # 更新任务状态
    old_status = task.status
    task.status = TaskStatus.CONFIRMED
    task.updated_at = datetime.utcnow()
    
    # 创建任务更新记录
    task_update = TaskUpdate(
        transport_task_id=task.id,
        user_id=current_user.id,
        old_status=old_status,
        new_status=TaskStatus.CONFIRMED,
        update_type="confirm",
        description=f"司机 {current_user.real_name} 确认接受任务",
    )
    db.add(task_update)
    
    await db.commit()
    await db.refresh(task)
    
    task_response = TransportTaskResponse.model_validate(task)
    return ApiResponse(
        code=200,
        message="任务确认成功",
        data=task_response,
    )


@router.post("/{task_id}/status", response_model=ApiResponse[TransportTaskResponse])
async def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdateRequest,
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    司机更新任务状态
    司机可以更新任务状态：已出发、已到达、已卸料等
    """
    # 查询任务
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查是否是任务的司机
    if task.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新该任务状态"
        )
    
    # 验证状态转移是否合法
    old_status = task.status
    new_status = status_data.new_status
    
    # 状态转移验证
    valid_transitions = {
        TaskStatus.CONFIRMED: [TaskStatus.DEPARTED],
        TaskStatus.DEPARTED: [TaskStatus.ARRIVED],
        TaskStatus.ARRIVED: [TaskStatus.UNLOADING],
        TaskStatus.UNLOADING: [TaskStatus.COMPLETED],
    }
    
    if new_status not in valid_transitions.get(old_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法从 {old_status.value} 状态转换到 {new_status.value} 状态"
        )
    
    # 更新任务状态
    task.status = new_status
    task.updated_at = datetime.utcnow()
    
    # 更新相关时间字段
    now = datetime.utcnow()
    if new_status == TaskStatus.DEPARTED:
        task.actual_departure_time = now
    elif new_status == TaskStatus.ARRIVED:
        task.actual_arrival_time = now
    elif new_status == TaskStatus.UNLOADING:
        task.actual_unload_time = now
    elif new_status == TaskStatus.COMPLETED:
        task.completed_time = now
    
    # 创建任务更新记录
    task_update = TaskUpdate(
        transport_task_id=task.id,
        user_id=current_user.id,
        old_status=old_status,
        new_status=new_status,
        update_type="status_change",
        description=status_data.description or f"状态更新为 {new_status.value}",
        latitude=str(status_data.latitude) if status_data.latitude else None,
        longitude=str(status_data.longitude) if status_data.longitude else None,
        address=status_data.address,
    )
    db.add(task_update)
    
    # 如果任务完成，释放车辆和司机
    if new_status == TaskStatus.COMPLETED:
        # 更新车辆状态
        if task.vehicle_id:
            result = await db.execute(select(Vehicle).where(Vehicle.id == task.vehicle_id))
            vehicle = result.scalar_one_or_none()
            if vehicle:
                vehicle.status = VehicleStatus.IDLE
        
        # 更新司机状态
        result = await db.execute(select(User).where(User.id == current_user.id))
        driver = result.scalar_one_or_none()
        if driver:
            driver.status = UserStatus.IDLE
    
    await db.commit()
    await db.refresh(task)
    
    task_response = TransportTaskResponse.model_validate(task)
    return ApiResponse(
        code=200,
        message="状态更新成功",
        data=task_response,
    )


@router.post("/{task_id}/upload-photo", response_model=ApiResponse[PhotoUploadResponse])
async def upload_unload_photo(
    task_id: int,
    file: UploadFile = File(..., description="卸料照片文件"),
    current_user: User = Depends(require_driver),
    db: AsyncSession = Depends(get_db),
):
    """
    上传卸料照片
    司机上传卸料照片作为任务完成的依据
    """
    # 查询任务
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查是否是任务的司机
    if task.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权上传该任务的照片"
        )
    
    # 检查任务状态
    if task.status not in [TaskStatus.ARRIVED, TaskStatus.UNLOADING, TaskStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有到达或卸料中的任务才能上传照片"
        )
    
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，支持的类型: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # 保存文件
    file_info = await save_upload_file(file, subdirectory="unload_photos")
    
    # 更新任务的照片字段
    if task.unload_photos:
        task.unload_photos = f"{task.unload_photos},{file_info['relative_path']}"
    else:
        task.unload_photos = file_info['relative_path']
    
    task.updated_at = datetime.utcnow()
    
    # 创建任务更新记录
    task_update = TaskUpdate(
        transport_task_id=task.id,
        user_id=current_user.id,
        old_status=task.status,
        new_status=task.status,
        update_type="photo_upload",
        description=f"司机 {current_user.real_name} 上传了卸料照片",
        photo_paths=file_info['relative_path'],
    )
    db.add(task_update)
    
    await db.commit()
    await db.refresh(task)
    
    photo_response = PhotoUploadResponse(
        file_name=file_info['file_name'],
        file_path=file_info['relative_path'],
        file_size=file_info['file_size'],
        content_type=file_info['content_type'],
        access_url=file_info['relative_path'],
    )
    
    return ApiResponse(
        code=200,
        message="照片上传成功",
        data=photo_response,
    )


@router.delete("/{task_id}", response_model=ApiResponse[dict])
async def delete_task(
    task_id: int,
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    删除运输任务（软删除）
    调度员和管理员可以删除任务
    """
    # 查询任务
    result = await db.execute(select(TransportTask).where(TransportTask.id == task_id, TransportTask.is_deleted == False))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查任务状态
    if task.status in [TaskStatus.DEPARTED, TaskStatus.ARRIVED, TaskStatus.UNLOADING, TaskStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已出发的任务无法删除"
        )
    
    # 如果任务已分配，释放车辆和司机
    if task.status in [TaskStatus.ASSIGNED, TaskStatus.CONFIRMED]:
        if task.vehicle_id:
            result = await db.execute(select(Vehicle).where(Vehicle.id == task.vehicle_id))
            vehicle = result.scalar_one_or_none()
            if vehicle:
                vehicle.status = VehicleStatus.IDLE
        
        if task.driver_id:
            result = await db.execute(select(User).where(User.id == task.driver_id))
            driver = result.scalar_one_or_none()
            if driver:
                driver.status = UserStatus.IDLE
                driver.vehicle_id = None
    
    # 软删除
    task.is_deleted = True
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功",
        data={},
    )

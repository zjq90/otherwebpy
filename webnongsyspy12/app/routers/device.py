from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    ApiResponse, ApiListResponse
)
from app.crud import DeviceCRUD

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.get("", response_model=ApiListResponse)
def get_devices(
    skip: int = 0,
    limit: int = 100,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备列表（支持分页和筛选）
    
    Args:
        skip: 跳过条数
        limit: 获取条数
        device_type: 设备类型筛选
        status: 设备状态筛选
        db: 数据库会话
    
    Returns:
        设备列表数据
    """
    total, devices = DeviceCRUD.get_list(
        db, skip=skip, limit=limit, 
        device_type=device_type, status=status
    )
    
    return ApiListResponse(
        success=True,
        message="获取设备列表成功",
        total=total,
        data=[DeviceResponse.model_validate(device) for device in devices]
    )


@router.get("/{device_id}", response_model=ApiResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取设备详情
    
    Args:
        device_id: 设备ID
        db: 数据库会话
    
    Returns:
        设备详情
    """
    device = DeviceCRUD.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    
    return ApiResponse(
        success=True,
        message="获取设备详情成功",
        data=DeviceResponse.model_validate(device).model_dump()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_device(device_in: DeviceCreate, db: Session = Depends(get_db)):
    """
    创建设备
    
    Args:
        device_in: 设备创建数据
        db: 数据库会话
    
    Returns:
        创建的设备信息
    """
    # 检查设备编号是否已存在
    existing = DeviceCRUD.get_by_code(db, device_in.device_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备编号 {device_in.device_code} 已存在"
        )
    
    device = DeviceCRUD.create(db, device_in)
    
    return ApiResponse(
        success=True,
        message="创建设备成功",
        data=DeviceResponse.model_validate(device).model_dump()
    )


@router.put("/{device_id}", response_model=ApiResponse)
def update_device(
    device_id: int,
    device_in: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    更新设备信息
    
    Args:
        device_id: 设备ID
        device_in: 更新数据
        db: 数据库会话
    
    Returns:
        更新后的设备信息
    """
    device = DeviceCRUD.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    
    updated_device = DeviceCRUD.update(db, device, device_in)
    
    return ApiResponse(
        success=True,
        message="更新设备成功",
        data=DeviceResponse.model_validate(updated_device).model_dump()
    )


@router.delete("/{device_id}", response_model=ApiResponse)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """
    删除设备
    
    Args:
        device_id: 设备ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    device = DeviceCRUD.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    
    DeviceCRUD.delete(db, device)
    
    return ApiResponse(
        success=True,
        message="删除设备成功",
        data={"id": device_id}
    )

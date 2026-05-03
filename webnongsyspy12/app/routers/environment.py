from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    EnvironmentDataCreate, EnvironmentDataResponse,
    ApiResponse, ApiListResponse
)
from app.crud import EnvironmentDataCRUD, DeviceCRUD

router = APIRouter(prefix="/environment", tags=["环境数据"])


@router.get("", response_model=ApiListResponse)
def get_environment_data(
    skip: int = 0,
    limit: int = 100,
    device_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    获取环境数据列表（支持分页和筛选）
    
    Args:
        skip: 跳过条数
        limit: 获取条数
        device_id: 设备ID筛选
        start_time: 开始时间筛选
        end_time: 结束时间筛选
        db: 数据库会话
    
    Returns:
        环境数据列表
    """
    total, data_list = EnvironmentDataCRUD.get_list(
        db, skip=skip, limit=limit,
        device_id=device_id,
        start_time=start_time, end_time=end_time
    )
    
    return ApiListResponse(
        success=True,
        message="获取环境数据列表成功",
        total=total,
        data=[EnvironmentDataResponse.model_validate(data) for data in data_list]
    )


@router.get("/statistics", response_model=ApiResponse)
def get_environment_statistics(
    device_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """
    获取环境数据统计信息
    
    Args:
        device_id: 设备ID（可选，不传则统计所有设备）
        hours: 统计最近多少小时的数据（默认24小时）
        db: 数据库会话
    
    Returns:
        统计信息
    """
    # 如果指定了device_id，检查设备是否存在
    if device_id:
        device = DeviceCRUD.get_by_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备ID {device_id} 不存在"
            )
    
    statistics = EnvironmentDataCRUD.get_statistics(db, device_id=device_id, hours=hours)
    
    return ApiResponse(
        success=True,
        message="获取统计信息成功",
        data=statistics
    )


@router.get("/trend/{device_id}", response_model=ApiResponse)
def get_trend_data(
    device_id: int,
    field: str = Query(..., description="数据字段: temperature, humidity, light_intensity, soil_moisture, co2_concentration"),
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """
    获取趋势数据（用于图表展示）
    
    Args:
        device_id: 设备ID
        field: 数据字段
        hours: 统计最近多少小时的数据
        db: 数据库会话
    
    Returns:
        趋势数据点列表
    """
    # 检查设备是否存在
    device = DeviceCRUD.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    
    # 验证字段是否有效
    valid_fields = ['temperature', 'humidity', 'light_intensity', 'soil_moisture', 'co2_concentration']
    if field not in valid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的数据字段，有效字段为: {valid_fields}"
        )
    
    trend_data = EnvironmentDataCRUD.get_trend_data(
        db, device_id=device_id, field=field, hours=hours
    )
    
    return ApiResponse(
        success=True,
        message="获取趋势数据成功",
        data={"field": field, "hours": hours, "data": trend_data}
    )


@router.get("/latest/{device_id}", response_model=ApiResponse)
def get_latest_data(device_id: int, db: Session = Depends(get_db)):
    """
    获取指定设备的最新环境数据
    
    Args:
        device_id: 设备ID
        db: 数据库会话
    
    Returns:
        最新环境数据
    """
    # 检查设备是否存在
    device = DeviceCRUD.get_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    
    latest_data = EnvironmentDataCRUD.get_latest_by_device(db, device_id)
    
    if not latest_data:
        return ApiResponse(
            success=True,
            message="该设备暂无环境数据",
            data=None
        )
    
    return ApiResponse(
        success=True,
        message="获取最新数据成功",
        data=EnvironmentDataResponse.model_validate(latest_data).model_dump()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_environment_data(
    data_in: EnvironmentDataCreate,
    db: Session = Depends(get_db)
):
    """
    创建环境数据记录（物联网设备数据上报）
    
    Args:
        data_in: 环境数据
        db: 数据库会话
    
    Returns:
        创建的数据
    """
    # 检查设备是否存在
    device = DeviceCRUD.get_by_id(db, data_in.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {data_in.device_id} 不存在"
        )
    
    data = EnvironmentDataCRUD.create(db, data_in)
    
    return ApiResponse(
        success=True,
        message="环境数据上报成功",
        data=EnvironmentDataResponse.model_validate(data).model_dump()
    )


@router.delete("/{data_id}", response_model=ApiResponse)
def delete_environment_data(data_id: int, db: Session = Depends(get_db)):
    """
    删除环境数据
    
    Args:
        data_id: 数据ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    data = EnvironmentDataCRUD.get_by_id(db, data_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"环境数据ID {data_id} 不存在"
        )
    
    EnvironmentDataCRUD.delete(db, data)
    
    return ApiResponse(
        success=True,
        message="删除环境数据成功",
        data={"id": data_id}
    )

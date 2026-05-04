"""
体测记录相关API路由模块
包含体测记录的增删改查、统计等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..config import get_db
from ..schemas import (
    BodyMeasurementCreate, BodyMeasurementUpdate, BodyMeasurementResponse, 
    BodyMeasurementStats, ApiResponse
)
from ..crud import (
    get_measurement_by_id, get_user_measurements, create_measurement, 
    update_measurement, delete_measurement, get_measurement_stats, get_latest_measurement
)

router = APIRouter(prefix="/api/measurements", tags=["体测记录"])


@router.post("/user/{user_id}", response_model=BodyMeasurementResponse, status_code=status.HTTP_201_CREATED)
def add_measurement(
    user_id: int, 
    measurement: BodyMeasurementCreate, 
    db: Session = Depends(get_db)
):
    """
    添加体测记录接口
    
    为指定用户添加新的体测记录，自动计算BMI指数
    """
    return create_measurement(db=db, user_id=user_id, measurement=measurement)


@router.get("/user/{user_id}", response_model=List[BodyMeasurementResponse])
def list_user_measurements(
    user_id: int, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取用户体测记录列表接口
    
    按测量日期倒序排列，支持分页查询
    """
    measurements = get_user_measurements(db, user_id=user_id, skip=skip, limit=limit)
    return measurements


@router.get("/{measurement_id}", response_model=BodyMeasurementResponse)
def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取体测记录接口
    """
    db_measurement = get_measurement_by_id(db, measurement_id=measurement_id)
    if not db_measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="体测记录不存在"
        )
    return db_measurement


@router.put("/{measurement_id}", response_model=BodyMeasurementResponse)
def update_measurement_info(
    measurement_id: int, 
    measurement: BodyMeasurementUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新体测记录接口
    """
    db_measurement = update_measurement(db, measurement_id=measurement_id, measurement=measurement)
    if not db_measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="体测记录不存在"
        )
    return db_measurement


@router.delete("/{measurement_id}", response_model=ApiResponse)
def delete_measurement_info(measurement_id: int, db: Session = Depends(get_db)):
    """
    删除体测记录接口
    """
    success = delete_measurement(db, measurement_id=measurement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="体测记录不存在"
        )
    return ApiResponse(
        code=status.HTTP_200_OK,
        message="体测记录删除成功"
    )


@router.get("/stats/user/{user_id}", response_model=BodyMeasurementStats)
def get_user_measurement_stats(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(30, ge=1, le=365, description="最多返回记录数"),
    db: Session = Depends(get_db)
):
    """
    获取用户体测数据统计接口
    
    返回用于折线图展示的统计数据，包括日期列表和各项指标数值列表
    """
    stats = get_measurement_stats(
        db, 
        user_id=user_id, 
        start_date=start_date, 
        end_date=end_date, 
        limit=limit
    )
    return stats


@router.get("/latest/user/{user_id}", response_model=Optional[BodyMeasurementResponse])
def get_latest_user_measurement(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户最新体测记录接口
    
    返回用户最近一次的体测记录，用于展示当前身体状态
    """
    return get_latest_measurement(db, user_id=user_id)


@router.post("/sync/user/{user_id}", response_model=List[BodyMeasurementResponse], status_code=status.HTTP_201_CREATED)
def sync_gym_measurements(
    user_id: int,
    measurements: List[BodyMeasurementCreate],
    db: Session = Depends(get_db)
):
    """
    同步健身房体测数据接口
    
    批量导入从健身房同步的体测数据，数据来源标记为gym_sync
    """
    result = []
    for measurement in measurements:
        measurement.source = "gym_sync"
        db_measurement = create_measurement(db=db, user_id=user_id, measurement=measurement)
        result.append(db_measurement)
    return result

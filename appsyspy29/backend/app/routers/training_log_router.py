"""
训练日志相关API路由模块
包含训练日志的增删改查、统计等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from ..config import get_db
from ..schemas import (
    TrainingLogCreate, TrainingLogUpdate, TrainingLogResponse, 
    TrainingLogItemCreate, TrainingLogItemResponse, ApiResponse
)
from ..crud import (
    get_training_log_by_id, get_user_training_logs, get_user_training_logs_by_date,
    create_training_log, update_training_log, delete_training_log,
    add_training_log_item, remove_training_log_item, get_training_log_with_items,
    get_user_monthly_stats
)

router = APIRouter(prefix="/api/training-logs", tags=["训练日志"])


@router.post("/user/{user_id}", response_model=TrainingLogResponse, status_code=status.HTTP_201_CREATED)
def add_training_log(
    user_id: int, 
    log: TrainingLogCreate, 
    db: Session = Depends(get_db)
):
    """
    添加训练日志接口
    
    创建新的训练日志，同时可添加训练项目详情
    """
    return create_training_log(db=db, user_id=user_id, log=log)


@router.get("/user/{user_id}", response_model=List[TrainingLogResponse])
def list_user_training_logs(
    user_id: int, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取用户训练日志列表接口
    
    按训练日期倒序排列，支持分页查询
    """
    logs = get_user_training_logs(db, user_id=user_id, skip=skip, limit=limit)
    # 转换为响应格式，添加训练项目名称
    result = []
    for log in logs:
        log_response = TrainingLogResponse.from_orm(log)
        # 为每个训练项目添加名称
        for item in log.items:
            item_response = TrainingLogItemResponse.from_orm(item)
            if item.exercise:
                item_response.exercise_name = item.exercise.name
            log_response.items.append(item_response)
        result.append(log_response)
    return result


@router.get("/{log_id}", response_model=TrainingLogResponse)
def get_training_log(log_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取训练日志接口
    """
    db_log = get_training_log_with_items(db, log_id=log_id)
    if not db_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练日志不存在"
        )
    # 转换为响应格式，添加训练项目名称
    log_response = TrainingLogResponse.from_orm(db_log)
    for item in db_log.items:
        item_response = TrainingLogItemResponse.from_orm(item)
        if item.exercise:
            item_response.exercise_name = item.exercise.name
        log_response.items.append(item_response)
    return log_response


@router.put("/{log_id}", response_model=TrainingLogResponse)
def update_training_log_info(
    log_id: int, 
    log: TrainingLogUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新训练日志接口
    """
    db_log = update_training_log(db, log_id=log_id, log=log)
    if not db_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练日志不存在"
        )
    return db_log


@router.delete("/{log_id}", response_model=ApiResponse)
def delete_training_log_info(log_id: int, db: Session = Depends(get_db)):
    """
    删除训练日志接口
    """
    success = delete_training_log(db, log_id=log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练日志不存在"
        )
    return ApiResponse(
        code=status.HTTP_200_OK,
        message="训练日志删除成功"
    )


@router.post("/{log_id}/items", response_model=TrainingLogItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_training_log(
    log_id: int, 
    item: TrainingLogItemCreate, 
    db: Session = Depends(get_db)
):
    """
    向训练日志添加训练项目接口
    """
    db_item = add_training_log_item(db, log_id=log_id, item=item)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练日志不存在"
        )
    return db_item


@router.delete("/items/{item_id}", response_model=ApiResponse)
def remove_item_from_training_log(item_id: int, db: Session = Depends(get_db)):
    """
    从训练日志中移除训练项目接口
    """
    success = remove_training_log_item(db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练项目不存在"
        )
    return ApiResponse(
        code=status.HTTP_200_OK,
        message="训练项目移除成功"
    )


@router.get("/date/user/{user_id}", response_model=List[TrainingLogResponse])
def list_training_logs_by_date(
    user_id: int,
    log_date: date = Query(..., description="查询日期"),
    db: Session = Depends(get_db)
):
    """
    获取用户指定日期的训练日志接口
    """
    logs = get_user_training_logs_by_date(db, user_id=user_id, log_date=log_date)
    # 转换为响应格式
    result = []
    for log in logs:
        log_response = TrainingLogResponse.from_orm(log)
        for item in log.items:
            item_response = TrainingLogItemResponse.from_orm(item)
            if item.exercise:
                item_response.exercise_name = item.exercise.name
            log_response.items.append(item_response)
        result.append(log_response)
    return result


@router.get("/stats/user/{user_id}/monthly", response_model=dict)
def get_monthly_training_stats(
    user_id: int,
    year: int = Query(..., ge=2000, le=2100, description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db)
):
    """
    获取用户月度训练统计接口
    
    返回指定月份的训练次数、总时长、总消耗卡路里等统计数据
    """
    stats = get_user_monthly_stats(db, user_id=user_id, year=year, month=month)
    return stats


@router.get("/today/user/{user_id}", response_model=List[TrainingLogResponse])
def get_today_training_logs(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户今日训练日志接口
    
    返回今天的所有训练记录
    """
    today = date.today()
    logs = get_user_training_logs_by_date(db, user_id=user_id, log_date=today)
    # 转换为响应格式
    result = []
    for log in logs:
        log_response = TrainingLogResponse.from_orm(log)
        for item in log.items:
            item_response = TrainingLogItemResponse.from_orm(item)
            if item.exercise:
                item_response.exercise_name = item.exercise.name
            log_response.items.append(item_response)
        result.append(log_response)
    return result

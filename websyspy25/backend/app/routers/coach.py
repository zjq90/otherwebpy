from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, date

from ..database import get_db
from ..models.coach import Coach, CoachSchedule
from ..schemas.coach import (
    CoachCreate, CoachUpdate, CoachResponse, CoachListResponse,
    CoachScheduleCreate, CoachScheduleUpdate, CoachScheduleResponse,
    CoachWithScheduleResponse
)

"""
教练管理API路由
实现教练档案的增删改查、排班管理、课时统计等功能
"""

router = APIRouter(
    prefix="/api/coaches",
    tags=["教练管理"]
)


@router.post("/", response_model=CoachResponse, summary="创建教练")
def create_coach(coach: CoachCreate, db: Session = Depends(get_db)):
    """
    创建新教练记录
    - 检查手机号是否已存在
    - 设置默认值
    """
    # 检查手机号是否已存在
    existing = db.query(Coach).filter(Coach.phone == coach.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号码已存在")
    
    db_coach = Coach(**coach.model_dump())
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    return db_coach


@router.get("/", response_model=CoachListResponse, summary="获取教练列表")
def get_coaches(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    name: Optional[str] = Query(None, description="教练姓名（模糊搜索）"),
    phone: Optional[str] = Query(None, description="手机号码（模糊搜索）"),
    status: Optional[str] = Query(None, description="状态：在职/离职/休假"),
    level: Optional[str] = Query(None, description="教练级别"),
    db: Session = Depends(get_db)
):
    """
    分页获取教练列表
    支持按姓名、手机号、状态、级别筛选
    """
    query = db.query(Coach)
    
    # 应用筛选条件
    if name:
        query = query.filter(Coach.name.contains(name))
    if phone:
        query = query.filter(Coach.phone.contains(phone))
    if status:
        query = query.filter(Coach.status == status)
    if level:
        query = query.filter(Coach.level == level)
    
    # 获取总记录数
    total = query.count()
    
    # 分页查询
    coaches = query.order_by(Coach.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return CoachListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=coaches
    )


@router.get("/{coach_id}", response_model=CoachWithScheduleResponse, summary="获取单个教练详情")
def get_coach(coach_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个教练详情，包含排班信息
    """
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    return coach


@router.put("/{coach_id}", response_model=CoachResponse, summary="更新教练信息")
def update_coach(coach_id: int, coach_update: CoachUpdate, db: Session = Depends(get_db)):
    """
    更新教练信息
    - 只更新提供的字段
    - 检查手机号冲突
    """
    db_coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not db_coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # 检查手机号是否冲突
    if coach_update.phone and coach_update.phone != db_coach.phone:
        existing = db.query(Coach).filter(Coach.phone == coach_update.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="该手机号码已被其他教练使用")
    
    # 只更新非空字段
    update_data = coach_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_coach, key, value)
    
    db.commit()
    db.refresh(db_coach)
    return db_coach


@router.delete("/{coach_id}", summary="删除教练")
def delete_coach(coach_id: int, db: Session = Depends(get_db)):
    """
    删除教练
    注意：实际生产环境可能只做逻辑删除
    """
    db_coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not db_coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    db.delete(db_coach)
    db.commit()
    return {"message": "删除成功", "coach_id": coach_id}


# 排班管理相关API

@router.post("/schedules/", response_model=CoachScheduleResponse, summary="创建排班")
def create_schedule(schedule: CoachScheduleCreate, db: Session = Depends(get_db)):
    """
    创建教练排班记录
    """
    # 检查教练是否存在
    coach = db.query(Coach).filter(Coach.id == schedule.coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    db_schedule = CoachSchedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/{coach_id}/schedules/", response_model=List[CoachScheduleResponse], summary="获取教练排班列表")
def get_coach_schedules(
    coach_id: int,
    day_of_week: Optional[int] = Query(None, ge=1, le=7, description="星期几筛选"),
    db: Session = Depends(get_db)
):
    """
    获取指定教练的排班列表
    可按星期几筛选
    """
    # 检查教练是否存在
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    query = db.query(CoachSchedule).filter(CoachSchedule.coach_id == coach_id)
    
    if day_of_week:
        query = query.filter(CoachSchedule.day_of_week == day_of_week)
    
    schedules = query.order_by(CoachSchedule.day_of_week, CoachSchedule.start_time).all()
    return schedules


@router.put("/schedules/{schedule_id}", response_model=CoachScheduleResponse, summary="更新排班")
def update_schedule(schedule_id: int, schedule_update: CoachScheduleUpdate, db: Session = Depends(get_db)):
    """
    更新排班信息
    """
    db_schedule = db.query(CoachSchedule).filter(CoachSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="排班记录不存在")
    
    # 只更新非空字段
    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.delete("/schedules/{schedule_id}", summary="删除排班")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """
    删除排班记录
    """
    db_schedule = db.query(CoachSchedule).filter(CoachSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="排班记录不存在")
    
    db.delete(db_schedule)
    db.commit()
    return {"message": "删除成功", "schedule_id": schedule_id}

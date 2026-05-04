"""
课程排期管理API路由
包含课程排期的增删改查接口，支持时间冲突检测
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import date, time, datetime

from ..database import get_db
from ..models import CourseSchedule, Course, Venue
from ..schemas import (
    CourseScheduleBase, CourseScheduleCreate, 
    CourseScheduleUpdate, CourseScheduleResponse
)

# 创建API路由实例
router = APIRouter(prefix="/api/v1/schedules", tags=["课程排期管理"])


def check_time_conflict(
    db: Session,
    venue_id: int,
    schedule_date: date,
    start_time: time,
    end_time: time,
    exclude_schedule_id: Optional[int] = None
) -> bool:
    """
    检查场地时间冲突
    
    检测在同一个场地、同一天、同一时间段内是否已有排期
    
    Args:
        db: 数据库会话
        venue_id: 场地ID
        schedule_date: 排期日期
        start_time: 开始时间
        end_time: 结束时间
        exclude_schedule_id: 需要排除的排期ID（用于更新时排除自身）
    
    Returns:
        bool: True表示有冲突，False表示无冲突
    """
    # 构建查询条件
    # 时间冲突条件：新排期与已有排期的时间段有重叠
    # 重叠条件：(新开始时间 < 已有结束时间) AND (新结束时间 > 已有开始时间)
    query = select(CourseSchedule).where(
        CourseSchedule.venue_id == venue_id,
        CourseSchedule.schedule_date == schedule_date,
        CourseSchedule.status != "cancelled",
        or_(
            and_(start_time < CourseSchedule.end_time, end_time > CourseSchedule.start_time)
        )
    )
    
    # 如果是更新操作，排除自身
    if exclude_schedule_id is not None:
        query = query.where(CourseSchedule.id != exclude_schedule_id)
    
    # 执行查询
    conflicting = db.execute(query).scalars().all()
    
    return len(conflicting) > 0


@router.post("", response_model=CourseScheduleResponse, summary="创建课程排期")
def create_schedule(schedule: CourseScheduleCreate, db: Session = Depends(get_db)):
    """
    创建新的课程排期
    系统自动检测时间与场地冲突
    
    Args:
        schedule: 课程排期创建数据
        db: 数据库会话
    
    Returns:
        创建的课程排期信息
    """
    # 检查课程是否存在
    course = db.execute(
        select(Course).where(Course.id == schedule.course_id)
    ).scalar_one_or_none()
    
    if course is None:
        raise HTTPException(status_code=400, detail=f"课程ID {schedule.course_id} 不存在")
    
    # 检查场地是否存在
    venue = db.execute(
        select(Venue).where(Venue.id == schedule.venue_id)
    ).scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(status_code=400, detail=f"场地ID {schedule.venue_id} 不存在")
    
    # 检测时间冲突
    if check_time_conflict(
        db=db,
        venue_id=schedule.venue_id,
        schedule_date=schedule.schedule_date,
        start_time=schedule.start_time,
        end_time=schedule.end_time
    ):
        raise HTTPException(
            status_code=400, 
            detail=f"场地ID {schedule.venue_id} 在 {schedule.schedule_date} {schedule.start_time}-{schedule.end_time} 时间段已有排期"
        )
    
    # 如果没有指定最大容量，使用课程的默认容量
    create_data = schedule.model_dump()
    if create_data.get("max_capacity") is None:
        create_data["max_capacity"] = course.max_capacity
    if create_data.get("instructor") is None and course.instructor:
        create_data["instructor"] = course.instructor
    
    # 创建新排期
    db_schedule = CourseSchedule(**create_data)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    # 关联查询课程信息
    db_schedule.course = course
    return db_schedule


@router.get("", response_model=List[CourseScheduleResponse], summary="获取课程排期列表")
def get_schedules(
    course_id: Optional[int] = Query(None, description="课程ID"),
    venue_id: Optional[int] = Query(None, description="场地ID"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    status: Optional[str] = Query(None, description="排期状态"),
    db: Session = Depends(get_db)
):
    """
    获取课程排期列表
    
    Args:
        course_id: 课程ID筛选
        venue_id: 场地ID筛选
        start_date: 开始日期筛选
        end_date: 结束日期筛选
        status: 排期状态筛选
        db: 数据库会话
    
    Returns:
        课程排期列表
    """
    query = select(CourseSchedule)
    
    if course_id is not None:
        query = query.where(CourseSchedule.course_id == course_id)
    if venue_id is not None:
        query = query.where(CourseSchedule.venue_id == venue_id)
    if start_date is not None:
        query = query.where(CourseSchedule.schedule_date >= start_date)
    if end_date is not None:
        query = query.where(CourseSchedule.schedule_date <= end_date)
    if status is not None:
        query = query.where(CourseSchedule.status == status)
    
    query = query.order_by(CourseSchedule.schedule_date, CourseSchedule.start_time)
    
    schedules = db.execute(query).scalars().all()
    return schedules


@router.get("/{schedule_id}", response_model=CourseScheduleResponse, summary="获取课程排期详情")
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """
    获取课程排期详情
    
    Args:
        schedule_id: 排期ID
        db: 数据库会话
    
    Returns:
        课程排期详情
    """
    schedule = db.execute(
        select(CourseSchedule).where(CourseSchedule.id == schedule_id)
    ).scalar_one_or_none()
    
    if schedule is None:
        raise HTTPException(status_code=404, detail=f"排期ID {schedule_id} 不存在")
    
    return schedule


@router.put("/{schedule_id}", response_model=CourseScheduleResponse, summary="更新课程排期")
def update_schedule(
    schedule_id: int, 
    schedule: CourseScheduleUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新课程排期信息
    系统自动检测时间与场地冲突
    
    Args:
        schedule_id: 排期ID
        schedule: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的课程排期信息
    """
    db_schedule = db.execute(
        select(CourseSchedule).where(CourseSchedule.id == schedule_id)
    ).scalar_one_or_none()
    
    if db_schedule is None:
        raise HTTPException(status_code=404, detail=f"排期ID {schedule_id} 不存在")
    
    # 获取更新数据
    update_data = schedule.model_dump(exclude_unset=True)
    
    # 如果更新了场地、日期或时间，需要检测冲突
    need_check_conflict = any(
        key in update_data 
        for key in ["venue_id", "schedule_date", "start_time", "end_time"]
    )
    
    if need_check_conflict:
        # 获取用于冲突检测的参数
        venue_id = update_data.get("venue_id", db_schedule.venue_id)
        schedule_date = update_data.get("schedule_date", db_schedule.schedule_date)
        start_time = update_data.get("start_time", db_schedule.start_time)
        end_time = update_data.get("end_time", db_schedule.end_time)
        
        # 检测时间冲突（排除自身）
        if check_time_conflict(
            db=db,
            venue_id=venue_id,
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            exclude_schedule_id=schedule_id
        ):
            raise HTTPException(
                status_code=400, 
                detail=f"场地ID {venue_id} 在 {schedule_date} {start_time}-{end_time} 时间段已有排期"
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.delete("/{schedule_id}", summary="删除课程排期")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """
    删除课程排期
    
    Args:
        schedule_id: 排期ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_schedule = db.execute(
        select(CourseSchedule).where(CourseSchedule.id == schedule_id)
    ).scalar_one_or_none()
    
    if db_schedule is None:
        raise HTTPException(status_code=404, detail=f"排期ID {schedule_id} 不存在")
    
    db.delete(db_schedule)
    db.commit()
    return {"message": "删除成功", "id": schedule_id}

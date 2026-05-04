"""
课程管理API路由
包含课程类型和课程的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from ..database import get_db
from ..models import CourseType, Course, CourseSchedule, Venue
from ..schemas import (
    CourseTypeBase, CourseTypeCreate, CourseTypeUpdate, CourseTypeResponse,
    CourseBase, CourseCreate, CourseUpdate, CourseResponse
)

# 创建API路由实例
router = APIRouter(prefix="/api/v1/courses", tags=["课程管理"])


# ==================== 课程类型相关接口 ====================

@router.post("/types", response_model=CourseTypeResponse, summary="创建课程类型")
def create_course_type(course_type: CourseTypeCreate, db: Session = Depends(get_db)):
    """
    创建新的课程类型
    
    Args:
        course_type: 课程类型创建数据
        db: 数据库会话
    
    Returns:
        创建的课程类型信息
    """
    # 检查课程类型代码是否已存在
    existing = db.execute(
        select(CourseType).where(CourseType.code == course_type.code)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"课程类型代码 '{course_type.code}' 已存在")
    
    # 创建新课程类型
    db_course_type = CourseType(**course_type.model_dump())
    db.add(db_course_type)
    db.commit()
    db.refresh(db_course_type)
    return db_course_type


@router.get("/types", response_model=List[CourseTypeResponse], summary="获取课程类型列表")
def get_course_types(
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db)
):
    """
    获取课程类型列表
    
    Args:
        is_active: 是否启用的筛选条件
        db: 数据库会话
    
    Returns:
        课程类型列表
    """
    query = select(CourseType)
    if is_active is not None:
        query = query.where(CourseType.is_active == is_active)
    query = query.order_by(CourseType.id)
    
    course_types = db.execute(query).scalars().all()
    return course_types


@router.get("/types/{course_type_id}", response_model=CourseTypeResponse, summary="获取课程类型详情")
def get_course_type(course_type_id: int, db: Session = Depends(get_db)):
    """
    获取课程类型详情
    
    Args:
        course_type_id: 课程类型ID
        db: 数据库会话
    
    Returns:
        课程类型详情
    """
    course_type = db.execute(
        select(CourseType).where(CourseType.id == course_type_id)
    ).scalar_one_or_none()
    
    if course_type is None:
        raise HTTPException(status_code=404, detail=f"课程类型ID {course_type_id} 不存在")
    
    return course_type


@router.put("/types/{course_type_id}", response_model=CourseTypeResponse, summary="更新课程类型")
def update_course_type(
    course_type_id: int, 
    course_type: CourseTypeUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新课程类型信息
    
    Args:
        course_type_id: 课程类型ID
        course_type: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的课程类型信息
    """
    db_course_type = db.execute(
        select(CourseType).where(CourseType.id == course_type_id)
    ).scalar_one_or_none()
    
    if db_course_type is None:
        raise HTTPException(status_code=404, detail=f"课程类型ID {course_type_id} 不存在")
    
    # 更新字段
    update_data = course_type.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_course_type, key, value)
    
    db.commit()
    db.refresh(db_course_type)
    return db_course_type


@router.delete("/types/{course_type_id}", summary="删除课程类型")
def delete_course_type(course_type_id: int, db: Session = Depends(get_db)):
    """
    删除课程类型
    
    Args:
        course_type_id: 课程类型ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_course_type = db.execute(
        select(CourseType).where(CourseType.id == course_type_id)
    ).scalar_one_or_none()
    
    if db_course_type is None:
        raise HTTPException(status_code=404, detail=f"课程类型ID {course_type_id} 不存在")
    
    # 检查是否有关联的课程
    course_count = db.execute(
        select(Course).where(Course.course_type_id == course_type_id)
    ).scalars().all()
    
    if course_count:
        raise HTTPException(
            status_code=400, 
            detail=f"课程类型ID {course_type_id} 有关联的课程，无法删除"
        )
    
    db.delete(db_course_type)
    db.commit()
    return {"message": "删除成功", "id": course_type_id}


# ==================== 课程相关接口 ====================

@router.post("", response_model=CourseResponse, summary="创建课程")
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """
    创建新的课程
    
    Args:
        course: 课程创建数据
        db: 数据库会话
    
    Returns:
        创建的课程信息
    """
    # 检查课程类型是否存在
    course_type = db.execute(
        select(CourseType).where(CourseType.id == course.course_type_id)
    ).scalar_one_or_none()
    
    if course_type is None:
        raise HTTPException(status_code=400, detail=f"课程类型ID {course.course_type_id} 不存在")
    
    # 创建新课程
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    # 关联查询课程类型信息
    db_course.course_type = course_type
    return db_course


@router.get("", response_model=List[CourseResponse], summary="获取课程列表")
def get_courses(
    course_type_id: Optional[int] = Query(None, description="课程类型ID"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db)
):
    """
    获取课程列表
    
    Args:
        course_type_id: 课程类型ID筛选
        is_active: 是否启用筛选
        db: 数据库会话
    
    Returns:
        课程列表
    """
    query = select(Course)
    if course_type_id is not None:
        query = query.where(Course.course_type_id == course_type_id)
    if is_active is not None:
        query = query.where(Course.is_active == is_active)
    query = query.order_by(Course.id)
    
    courses = db.execute(query).scalars().all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse, summary="获取课程详情")
def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    获取课程详情
    
    Args:
        course_id: 课程ID
        db: 数据库会话
    
    Returns:
        课程详情
    """
    course = db.execute(
        select(Course).where(Course.id == course_id)
    ).scalar_one_or_none()
    
    if course is None:
        raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
    
    return course


@router.put("/{course_id}", response_model=CourseResponse, summary="更新课程")
def update_course(
    course_id: int, 
    course: CourseUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新课程信息
    
    Args:
        course_id: 课程ID
        course: 更新的数据
        db: 数据库会话
    
    Returns:
        更新后的课程信息
    """
    db_course = db.execute(
        select(Course).where(Course.id == course_id)
    ).scalar_one_or_none()
    
    if db_course is None:
        raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
    
    # 如果更新了课程类型ID，检查课程类型是否存在
    update_data = course.model_dump(exclude_unset=True)
    if "course_type_id" in update_data:
        course_type = db.execute(
            select(CourseType).where(CourseType.id == update_data["course_type_id"])
        ).scalar_one_or_none()
        if course_type is None:
            raise HTTPException(status_code=400, detail=f"课程类型ID {update_data['course_type_id']} 不存在")
    
    # 更新字段
    for key, value in update_data.items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


@router.delete("/{course_id}", summary="删除课程")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    删除课程
    
    Args:
        course_id: 课程ID
        db: 数据库会话
    
    Returns:
        删除结果
    """
    db_course = db.execute(
        select(Course).where(Course.id == course_id)
    ).scalar_one_or_none()
    
    if db_course is None:
        raise HTTPException(status_code=404, detail=f"课程ID {course_id} 不存在")
    
    # 检查是否有关联的课程排期
    schedule_count = db.execute(
        select(CourseSchedule).where(CourseSchedule.course_id == course_id)
    ).scalars().all()
    
    if schedule_count:
        raise HTTPException(
            status_code=400, 
            detail=f"课程ID {course_id} 有关联的排期，无法删除"
        )
    
    db.delete(db_course)
    db.commit()
    return {"message": "删除成功", "id": course_id}

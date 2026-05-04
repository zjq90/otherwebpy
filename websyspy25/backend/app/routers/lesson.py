from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, date, timedelta
import uuid

from ..database import get_db
from ..models.lesson import LessonRecord, MakeupLesson, FreezeRecord
from ..models.member import Member, CoursePackage
from ..models.coach import Coach
from ..schemas.lesson import (
    LessonRecordCreate, LessonRecordComplete, LessonRecordUpdate, 
    LessonRecordResponse, LessonRecordListResponse,
    MakeupLessonCreate, MakeupLessonApprove, MakeupLessonUpdate,
    MakeupLessonResponse, MakeupLessonListResponse,
    FreezeRecordCreate, FreezeRecordResponse, FreezeRecordListResponse
)

"""
私教课管理API路由
实现课时消耗、补课申请与审批、课程包冻结/解冻等功能
"""

router = APIRouter(
    prefix="/api/lessons",
    tags=["私教课管理"]
)


def generate_record_no() -> str:
    """生成课时记录编号"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"LR{date_str}{random_str}"


def generate_makeup_no() -> str:
    """生成补课记录编号"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"MK{date_str}{random_str}"


def generate_freeze_no() -> str:
    """生成冻结记录编号"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"FZ{date_str}{random_str}"


# ========== 课时记录相关API ==========

@router.post("/", response_model=LessonRecordResponse, summary="预约/创建课时记录")
def create_lesson(lesson: LessonRecordCreate, db: Session = Depends(get_db)):
    """
    创建课时记录（预约上课）
    - 检查课程包是否有足够课时
    - 检查教练是否存在
    - 状态初始为"已预约"
    """
    # 检查课程包是否存在
    package = db.query(CoursePackage).filter(CoursePackage.id == lesson.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    
    # 检查课程包状态
    if package.status != "有效":
        raise HTTPException(status_code=400, detail=f"课程包状态为{package.status}，无法预约")
    
    # 检查课时是否足够
    if package.remaining_lessons <= 0:
        raise HTTPException(status_code=400, detail="课程包课时不足")
    
    # 检查教练是否存在
    coach = db.query(Coach).filter(Coach.id == lesson.coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # 创建课时记录
    lesson_data = lesson.model_dump()
    lesson_data["record_no"] = generate_record_no()
    lesson_data["status"] = "已预约"
    lesson_data["is_makeup"] = False
    
    db_lesson = LessonRecord(**lesson_data)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.post("/{lesson_id}/complete", response_model=LessonRecordResponse, summary="完成课时（核销）")
def complete_lesson(
    lesson_id: int,
    complete_data: LessonRecordComplete,
    db: Session = Depends(get_db)
):
    """
    完成课时，自动核销课时并计算教练报酬
    - 更新课时记录状态为"已完成"
    - 扣减课程包剩余课时
    - 计算教练报酬
    """
    # 获取课时记录
    db_lesson = db.query(LessonRecord).filter(LessonRecord.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="课时记录不存在")
    
    if db_lesson.status == "已完成":
        raise HTTPException(status_code=400, detail="该课时已完成")
    
    # 获取课程包
    package = db.query(CoursePackage).filter(CoursePackage.id == db_lesson.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    
    # 检查课时是否足够
    if package.remaining_lessons < db_lesson.hours_used:
        raise HTTPException(status_code=400, detail="课程包课时不足")
    
    # 获取教练信息
    coach = db.query(Coach).filter(Coach.id == db_lesson.coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # 计算教练报酬和收入贡献
    # 教练报酬 = 课时数 × 教练费率 × 提成比例
    coach_commission = db_lesson.hours_used * coach.hourly_rate * (coach.commission_rate / 100)
    # 收入贡献 = 课时数 × 课程单价
    revenue_contribution = db_lesson.hours_used * package.unit_price
    
    # 更新课时记录
    update_data = complete_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lesson, key, value)
    
    db_lesson.status = "已完成"
    db_lesson.coach_commission = coach_commission
    db_lesson.revenue_contribution = revenue_contribution
    
    # 更新课程包：扣减课时
    package.used_lessons += db_lesson.hours_used
    package.remaining_lessons -= db_lesson.hours_used
    
    # 检查是否用完
    if package.remaining_lessons <= 0:
        package.status = "已用完"
    
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.get("/", response_model=LessonRecordListResponse, summary="获取课时记录列表")
def get_lessons(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
    package_id: Optional[int] = Query(None, description="课程包ID"),
    status: Optional[str] = Query(None, description="状态：已预约/已完成/已取消/已缺席"),
    lesson_type: Optional[str] = Query(None, description="课程类型"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    分页获取课时记录列表
    支持多种筛选条件
    """
    query = db.query(LessonRecord)
    
    # 应用筛选条件
    if member_id:
        query = query.filter(LessonRecord.member_id == member_id)
    if coach_id:
        query = query.filter(LessonRecord.coach_id == coach_id)
    if package_id:
        query = query.filter(LessonRecord.package_id == package_id)
    if status:
        query = query.filter(LessonRecord.status == status)
    if lesson_type:
        query = query.filter(LessonRecord.lesson_type == lesson_type)
    if start_date:
        query = query.filter(LessonRecord.lesson_date >= start_date)
    if end_date:
        query = query.filter(LessonRecord.lesson_date <= end_date)
    
    # 获取总记录数
    total = query.count()
    
    # 分页查询
    lessons = query.order_by(LessonRecord.lesson_date.desc(), LessonRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return LessonRecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=lessons
    )


@router.get("/{lesson_id}", response_model=LessonRecordResponse, summary="获取单个课时记录详情")
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个课时记录详情
    """
    lesson = db.query(LessonRecord).filter(LessonRecord.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课时记录不存在")
    return lesson


@router.put("/{lesson_id}", response_model=LessonRecordResponse, summary="更新课时记录")
def update_lesson(lesson_id: int, lesson_update: LessonRecordUpdate, db: Session = Depends(get_db)):
    """
    更新课时记录信息
    仅能更新已预约的课时
    """
    db_lesson = db.query(LessonRecord).filter(LessonRecord.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="课时记录不存在")
    
    if db_lesson.status == "已完成":
        raise HTTPException(status_code=400, detail="已完成的课时无法更新")
    
    # 只更新非空字段
    update_data = lesson_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lesson, key, value)
    
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.post("/{lesson_id}/cancel", summary="取消课时预约")
def cancel_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """
    取消已预约的课时
    """
    db_lesson = db.query(LessonRecord).filter(LessonRecord.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="课时记录不存在")
    
    if db_lesson.status != "已预约":
        raise HTTPException(status_code=400, detail="只能取消已预约的课时")
    
    db_lesson.status = "已取消"
    db.commit()
    
    return {"message": "取消成功", "lesson_id": lesson_id}


# ========== 补课相关API ==========

@router.post("/makeups/", response_model=MakeupLessonResponse, summary="申请补课")
def create_makeup(makeup: MakeupLessonCreate, db: Session = Depends(get_db)):
    """
    申请补课
    状态初始为"待审批"
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == makeup.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 检查课程包是否存在
    package = db.query(CoursePackage).filter(CoursePackage.id == makeup.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    
    # 创建补课申请
    makeup_data = makeup.model_dump()
    makeup_data["makeup_no"] = generate_makeup_no()
    makeup_data["remaining_count"] = makeup.requested_count
    makeup_data["used_count"] = 0
    makeup_data["status"] = "待审批"
    
    db_makeup = MakeupLesson(**makeup_data)
    db.add(db_makeup)
    db.commit()
    db.refresh(db_makeup)
    return db_makeup


@router.post("/makeups/{makeup_id}/approve", response_model=MakeupLessonResponse, summary="审批补课申请")
def approve_makeup(
    makeup_id: int,
    approve_data: MakeupLessonApprove,
    db: Session = Depends(get_db)
):
    """
    审批补课申请
    可以批准或拒绝
    """
    db_makeup = db.query(MakeupLesson).filter(MakeupLesson.id == makeup_id).first()
    if not db_makeup:
        raise HTTPException(status_code=404, detail="补课记录不存在")
    
    if db_makeup.status != "待审批":
        raise HTTPException(status_code=400, detail="只能审批待审批的补课申请")
    
    if approve_data.status not in ["已批准", "已拒绝"]:
        raise HTTPException(status_code=400, detail="状态必须是已批准或已拒绝")
    
    db_makeup.status = approve_data.status
    db_makeup.approval_note = approve_data.approval_note
    
    db.commit()
    db.refresh(db_makeup)
    return db_makeup


@router.get("/makeups/", response_model=MakeupLessonListResponse, summary="获取补课记录列表")
def get_makeups(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    package_id: Optional[int] = Query(None, description="课程包ID"),
    status: Optional[str] = Query(None, description="状态"),
    db: Session = Depends(get_db)
):
    """
    分页获取补课记录列表
    """
    query = db.query(MakeupLesson)
    
    if member_id:
        query = query.filter(MakeupLesson.member_id == member_id)
    if package_id:
        query = query.filter(MakeupLesson.package_id == package_id)
    if status:
        query = query.filter(MakeupLesson.status == status)
    
    total = query.count()
    makeups = query.order_by(MakeupLesson.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return MakeupLessonListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=makeups
    )


@router.get("/makeups/{makeup_id}", response_model=MakeupLessonResponse, summary="获取单个补课记录详情")
def get_makeup(makeup_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个补课记录详情
    """
    makeup = db.query(MakeupLesson).filter(MakeupLesson.id == makeup_id).first()
    if not makeup:
        raise HTTPException(status_code=404, detail="补课记录不存在")
    return makeup


# ========== 冻结相关API ==========

@router.post("/freezes/", response_model=FreezeRecordResponse, summary="冻结课程包")
def create_freeze(freeze: FreezeRecordCreate, db: Session = Depends(get_db)):
    """
    冻结课程包
    - 检查课程包是否存在
    - 更新课程包状态为"已冻结"
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == freeze.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    
    # 检查课程包是否存在
    package = db.query(CoursePackage).filter(CoursePackage.id == freeze.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    
    if package.status == "已冻结":
        raise HTTPException(status_code=400, detail="课程包已被冻结")
    
    if package.status not in ["有效"]:
        raise HTTPException(status_code=400, detail=f"课程包状态为{package.status}，无法冻结")
    
    # 确定冻结的课时数
    frozen_lessons = freeze.frozen_lessons
    if frozen_lessons <= 0:
        frozen_lessons = package.remaining_lessons
    
    # 创建冻结记录
    freeze_data = freeze.model_dump()
    freeze_data["freeze_no"] = generate_freeze_no()
    freeze_data["status"] = "冻结中"
    freeze_data["operation_type"] = "冻结"
    freeze_data["frozen_lessons"] = frozen_lessons
    
    db_freeze = FreezeRecord(**freeze_data)
    db.add(db_freeze)
    
    # 更新课程包状态
    package.frozen_lessons += frozen_lessons
    package.remaining_lessons -= frozen_lessons
    package.status = "已冻结"
    
    db.commit()
    db.refresh(db_freeze)
    return db_freeze


@router.post("/freezes/{freeze_id}/unfreeze", response_model=FreezeRecordResponse, summary="解冻课程包")
def unfreeze_package(freeze_id: int, db: Session = Depends(get_db)):
    """
    解冻课程包
    """
    db_freeze = db.query(FreezeRecord).filter(FreezeRecord.id == freeze_id).first()
    if not db_freeze:
        raise HTTPException(status_code=404, detail="冻结记录不存在")
    
    if db_freeze.status != "冻结中":
        raise HTTPException(status_code=400, detail="该冻结记录已解冻")
    
    # 获取课程包
    package = db.query(CoursePackage).filter(CoursePackage.id == db_freeze.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="课程包不存在")
    
    # 更新冻结记录
    db_freeze.status = "已解冻"
    db_freeze.actual_end_date = date.today()
    db_freeze.operation_type = "解冻"
    
    # 归还冻结的课时
    package.remaining_lessons += db_freeze.frozen_lessons
    package.frozen_lessons -= db_freeze.frozen_lessons
    
    # 检查是否有剩余课时，恢复状态
    if package.remaining_lessons > 0:
        package.status = "有效"
    
    db.commit()
    db.refresh(db_freeze)
    return db_freeze


@router.get("/freezes/", response_model=FreezeRecordListResponse, summary="获取冻结记录列表")
def get_freezes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    package_id: Optional[int] = Query(None, description="课程包ID"),
    status: Optional[str] = Query(None, description="状态：冻结中/已解冻"),
    db: Session = Depends(get_db)
):
    """
    分页获取冻结记录列表
    """
    query = db.query(FreezeRecord)
    
    if member_id:
        query = query.filter(FreezeRecord.member_id == member_id)
    if package_id:
        query = query.filter(FreezeRecord.package_id == package_id)
    if status:
        query = query.filter(FreezeRecord.status == status)
    
    total = query.count()
    freezes = query.order_by(FreezeRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return FreezeRecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=freezes
    )

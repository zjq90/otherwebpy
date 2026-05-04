"""
档案管理API路由
提供体测数据、运动目标、消费记录、课程参与等档案管理功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.member import Member
from app.models.archive import (
    PhysicalTest,
    FitnessGoal,
    ConsumptionRecord,
    CourseParticipation,
)
from app.schemas.archive import (
    PhysicalTestCreate,
    PhysicalTestUpdate,
    PhysicalTestResponse,
    FitnessGoalCreate,
    FitnessGoalUpdate,
    FitnessGoalResponse,
    ConsumptionRecordCreate,
    ConsumptionRecordResponse,
    CourseParticipationCreate,
    CourseParticipationResponse,
)
from app.schemas.common import (
    ApiResponse,
    SuccessResponse,
    PaginatedResponse,
)
from app.services.level_service import level_service
from app.services.sms_service import sms_service

router = APIRouter(
    prefix="/api/archive",
    tags=["档案管理"],
    responses={404: {"description": "未找到"}},
)


# ==================== 体测数据管理 ====================

@router.post(
    "/physical-tests",
    response_model=ApiResponse[PhysicalTestResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新增体测数据",
    description="为会员创建新的体测数据记录",
)
def create_physical_test(
    member_id: int = Query(..., description="会员ID"),
    test_data: PhysicalTestCreate = Depends(),
    db: Session = Depends(get_db),
):
    """
    新增体测数据
    - **member_id**: 会员ID
    - **test_data**: 体测数据
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 自动计算BMI
    if test_data.height and test_data.weight and test_data.height > 0:
        height_m = test_data.height / 100
        bmi = test_data.weight / (height_m * height_m)
        test_data.bmi = round(bmi, 2)
    
    new_test = PhysicalTest(
        member_id=member_id,
        **test_data.model_dump()
    )
    
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return ApiResponse(
        code=201,
        message="体测数据创建成功",
        data=PhysicalTestResponse.model_validate(new_test)
    )


@router.get(
    "/physical-tests",
    response_model=ApiResponse[PaginatedResponse[PhysicalTestResponse]],
    summary="获取体测数据列表",
    description="分页查询会员的体测数据记录",
)
def get_physical_tests(
    member_id: int = Query(..., description="会员ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    获取体测数据列表
    - **member_id**: 会员ID
    - **page**: 页码
    - **page_size**: 每页数量
    - **start_date**: 开始日期筛选
    - **end_date**: 结束日期筛选
    """
    query = db.query(PhysicalTest).filter(PhysicalTest.member_id == member_id)
    
    if start_date:
        query = query.filter(PhysicalTest.test_date >= start_date)
    if end_date:
        query = query.filter(PhysicalTest.test_date <= end_date)
    
    total = query.count()
    offset = (page - 1) * page_size
    tests = query.order_by(PhysicalTest.test_date.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[PhysicalTestResponse.model_validate(t) for t in tests],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/physical-tests/{test_id}",
    response_model=ApiResponse[PhysicalTestResponse],
    summary="获取体测数据详情",
    description="根据ID获取体测数据详情",
)
def get_physical_test(
    test_id: int,
    db: Session = Depends(get_db),
):
    """
    获取体测数据详情
    - **test_id**: 体测记录ID
    """
    test = db.query(PhysicalTest).filter(PhysicalTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"体测记录ID {test_id} 不存在"
        )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PhysicalTestResponse.model_validate(test)
    )


@router.put(
    "/physical-tests/{test_id}",
    response_model=ApiResponse[PhysicalTestResponse],
    summary="更新体测数据",
    description="更新体测数据记录",
)
def update_physical_test(
    test_id: int,
    test_data: PhysicalTestUpdate,
    db: Session = Depends(get_db),
):
    """
    更新体测数据
    - **test_id**: 体测记录ID
    - **test_data**: 更新的体测数据
    """
    test = db.query(PhysicalTest).filter(PhysicalTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"体测记录ID {test_id} 不存在"
        )
    
    update_data = test_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(test, key, value)
    
    # 重新计算BMI
    if test.height and test.weight and test.height > 0:
        height_m = test.height / 100
        test.bmi = round(test.weight / (height_m * height_m), 2)
    
    db.commit()
    db.refresh(test)
    
    return ApiResponse(
        code=200,
        message="体测数据更新成功",
        data=PhysicalTestResponse.model_validate(test)
    )


@router.delete(
    "/physical-tests/{test_id}",
    response_model=SuccessResponse,
    summary="删除体测数据",
    description="删除指定的体测数据记录",
)
def delete_physical_test(
    test_id: int,
    db: Session = Depends(get_db),
):
    """
    删除体测数据
    - **test_id**: 体测记录ID
    """
    test = db.query(PhysicalTest).filter(PhysicalTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"体测记录ID {test_id} 不存在"
        )
    
    db.delete(test)
    db.commit()
    
    return SuccessResponse(
        code=200,
        message="体测数据已删除",
        data=None
    )


# ==================== 运动目标管理 ====================

@router.post(
    "/fitness-goals",
    response_model=ApiResponse[FitnessGoalResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新增运动目标",
    description="为会员创建新的运动目标",
)
def create_fitness_goal(
    member_id: int = Query(..., description="会员ID"),
    goal_data: FitnessGoalCreate = Depends(),
    db: Session = Depends(get_db),
):
    """
    新增运动目标
    - **member_id**: 会员ID
    - **goal_data**: 运动目标数据
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    new_goal = FitnessGoal(
        member_id=member_id,
        **goal_data.model_dump()
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    return ApiResponse(
        code=201,
        message="运动目标创建成功",
        data=FitnessGoalResponse.model_validate(new_goal)
    )


@router.get(
    "/fitness-goals",
    response_model=ApiResponse[PaginatedResponse[FitnessGoalResponse]],
    summary="获取运动目标列表",
    description="分页查询会员的运动目标",
)
def get_fitness_goals(
    member_id: int = Query(..., description="会员ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="目标状态"),
    db: Session = Depends(get_db),
):
    """
    获取运动目标列表
    - **member_id**: 会员ID
    - **page**: 页码
    - **page_size**: 每页数量
    - **status**: 目标状态筛选
    """
    query = db.query(FitnessGoal).filter(FitnessGoal.member_id == member_id)
    
    if status:
        query = query.filter(FitnessGoal.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    goals = query.order_by(FitnessGoal.created_at.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[FitnessGoalResponse.model_validate(g) for g in goals],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/fitness-goals/{goal_id}",
    response_model=ApiResponse[FitnessGoalResponse],
    summary="获取运动目标详情",
    description="根据ID获取运动目标详情",
)
def get_fitness_goal(
    goal_id: int,
    db: Session = Depends(get_db),
):
    """
    获取运动目标详情
    - **goal_id**: 目标ID
    """
    goal = db.query(FitnessGoal).filter(FitnessGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"运动目标ID {goal_id} 不存在"
        )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=FitnessGoalResponse.model_validate(goal)
    )


@router.put(
    "/fitness-goals/{goal_id}",
    response_model=ApiResponse[FitnessGoalResponse],
    summary="更新运动目标",
    description="更新运动目标记录",
)
def update_fitness_goal(
    goal_id: int,
    goal_data: FitnessGoalUpdate,
    db: Session = Depends(get_db),
):
    """
    更新运动目标
    - **goal_id**: 目标ID
    - **goal_data**: 更新的目标数据
    """
    goal = db.query(FitnessGoal).filter(FitnessGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"运动目标ID {goal_id} 不存在"
        )
    
    update_data = goal_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)
    
    db.commit()
    db.refresh(goal)
    
    return ApiResponse(
        code=200,
        message="运动目标更新成功",
        data=FitnessGoalResponse.model_validate(goal)
    )


@router.delete(
    "/fitness-goals/{goal_id}",
    response_model=SuccessResponse,
    summary="删除运动目标",
    description="删除指定的运动目标",
)
def delete_fitness_goal(
    goal_id: int,
    db: Session = Depends(get_db),
):
    """
    删除运动目标
    - **goal_id**: 目标ID
    """
    goal = db.query(FitnessGoal).filter(FitnessGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"运动目标ID {goal_id} 不存在"
        )
    
    db.delete(goal)
    db.commit()
    
    return SuccessResponse(
        code=200,
        message="运动目标已删除",
        data=None
    )


# ==================== 消费记录管理 ====================

@router.post(
    "/consumption-records",
    response_model=ApiResponse[ConsumptionRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新增消费记录",
    description="为会员创建消费记录，自动根据会员等级计算折扣",
)
def create_consumption_record(
    member_id: int = Query(..., description="会员ID"),
    record_data: ConsumptionRecordCreate = Depends(),
    db: Session = Depends(get_db),
):
    """
    新增消费记录
    - **member_id**: 会员ID
    - **record_data**: 消费记录数据
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 计算会员折扣
    original_amount = record_data.amount
    discount_rate = level_service.get_discount_rate(member.current_level)
    discount_amount = original_amount - int(original_amount * discount_rate)
    actual_amount = int(original_amount * discount_rate)
    
    # 如果请求中未指定折扣金额，使用自动计算的
    if record_data.discount_amount == 0 and discount_amount > 0:
        record_data.discount_amount = discount_amount
        record_data.actual_amount = actual_amount
    
    new_record = ConsumptionRecord(
        member_id=member_id,
        **record_data.model_dump()
    )
    
    db.add(new_record)
    
    # 更新会员累计消费
    member.total_consumption += new_record.actual_amount
    
    # 检查并更新会员等级
    level_service.check_and_upgrade_level(db, member)
    
    db.commit()
    db.refresh(new_record)
    
    # 发送消费通知
    sms_service.send_consumption_notification(
        db,
        member.phone,
        member.id,
        new_record.item_name,
        new_record.amount,
        new_record.actual_amount
    )
    
    return ApiResponse(
        code=201,
        message="消费记录创建成功",
        data=ConsumptionRecordResponse.model_validate(new_record)
    )


@router.get(
    "/consumption-records",
    response_model=ApiResponse[PaginatedResponse[ConsumptionRecordResponse]],
    summary="获取消费记录列表",
    description="分页查询会员的消费记录",
)
def get_consumption_records(
    member_id: int = Query(..., description="会员ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    consumption_type: Optional[str] = Query(None, description="消费类型"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    获取消费记录列表
    """
    query = db.query(ConsumptionRecord).filter(ConsumptionRecord.member_id == member_id)
    
    if consumption_type:
        query = query.filter(ConsumptionRecord.consumption_type == consumption_type)
    if start_date:
        query = query.filter(ConsumptionRecord.consumption_time >= start_date)
    if end_date:
        query = query.filter(ConsumptionRecord.consumption_time <= end_date)
    
    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(ConsumptionRecord.consumption_time.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[ConsumptionRecordResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/consumption-records/{record_id}",
    response_model=ApiResponse[ConsumptionRecordResponse],
    summary="获取消费记录详情",
    description="根据ID获取消费记录详情",
)
def get_consumption_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    """
    获取消费记录详情
    """
    record = db.query(ConsumptionRecord).filter(ConsumptionRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"消费记录ID {record_id} 不存在"
        )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=ConsumptionRecordResponse.model_validate(record)
    )


# ==================== 课程参与管理 ====================

@router.post(
    "/course-participations",
    response_model=ApiResponse[CourseParticipationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新增课程参与记录",
    description="记录会员参与的课程情况",
)
def create_course_participation(
    member_id: int = Query(..., description="会员ID"),
    participation_data: CourseParticipationCreate = Depends(),
    db: Session = Depends(get_db),
):
    """
    新增课程参与记录
    - **member_id**: 会员ID
    - **participation_data**: 课程参与数据
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    new_participation = CourseParticipation(
        member_id=member_id,
        **participation_data.model_dump()
    )
    
    db.add(new_participation)
    
    # 更新会员到店次数
    member.total_visits += 1
    
    # 检查并更新会员等级
    level_service.check_and_upgrade_level(db, member)
    
    db.commit()
    db.refresh(new_participation)
    
    return ApiResponse(
        code=201,
        message="课程参与记录创建成功",
        data=CourseParticipationResponse.model_validate(new_participation)
    )


@router.get(
    "/course-participations",
    response_model=ApiResponse[PaginatedResponse[CourseParticipationResponse]],
    summary="获取课程参与记录列表",
    description="分页查询会员的课程参与记录",
)
def get_course_participations(
    member_id: int = Query(..., description="会员ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    course_type: Optional[str] = Query(None, description="课程类型"),
    status: Optional[str] = Query(None, description="参与状态"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    获取课程参与记录列表
    """
    query = db.query(CourseParticipation).filter(CourseParticipation.member_id == member_id)
    
    if course_type:
        query = query.filter(CourseParticipation.course_type == course_type)
    if status:
        query = query.filter(CourseParticipation.status == status)
    if start_date:
        query = query.filter(CourseParticipation.participation_date >= start_date)
    if end_date:
        query = query.filter(CourseParticipation.participation_date <= end_date)
    
    total = query.count()
    offset = (page - 1) * page_size
    participations = query.order_by(CourseParticipation.participation_date.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[CourseParticipationResponse.model_validate(p) for p in participations],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/course-participations/{participation_id}",
    response_model=ApiResponse[CourseParticipationResponse],
    summary="获取课程参与记录详情",
    description="根据ID获取课程参与记录详情",
)
def get_course_participation(
    participation_id: int,
    db: Session = Depends(get_db),
):
    """
    获取课程参与记录详情
    """
    participation = db.query(CourseParticipation).filter(
        CourseParticipation.id == participation_id
    ).first()
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"课程参与记录ID {participation_id} 不存在"
        )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=CourseParticipationResponse.model_validate(participation)
    )


@router.put(
    "/course-participations/{participation_id}/rating",
    response_model=ApiResponse[CourseParticipationResponse],
    summary="评价课程",
    description="为参与的课程进行评分和反馈",
)
def rate_course(
    participation_id: int,
    rating: int = Query(..., ge=1, le=5, description="评分（1-5星）"),
    feedback: Optional[str] = Query(None, description="反馈意见"),
    db: Session = Depends(get_db),
):
    """
    评价课程
    - **participation_id**: 参与记录ID
    - **rating**: 评分（1-5星）
    - **feedback**: 反馈意见
    """
    participation = db.query(CourseParticipation).filter(
        CourseParticipation.id == participation_id
    ).first()
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"课程参与记录ID {participation_id} 不存在"
        )
    
    participation.rating = rating
    if feedback:
        participation.feedback = feedback
    
    db.commit()
    db.refresh(participation)
    
    return ApiResponse(
        code=200,
        message="评价成功",
        data=CourseParticipationResponse.model_validate(participation)
    )

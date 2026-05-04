"""
目标设定相关API路由模块
包含目标的增删改查、进度管理等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..config import get_db
from ..schemas import (
    GoalCreate, GoalUpdate, GoalResponse, GoalProgressCreate, 
    GoalProgressResponse, ApiResponse
)
from ..crud import (
    get_goal_by_id, get_user_goals, get_active_goal, create_goal,
    update_goal, delete_goal, add_goal_progress, get_goal_progress_records,
    get_goal_with_details
)

router = APIRouter(prefix="/api/goals", tags=["目标设定"])


@router.post("/user/{user_id}", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def add_goal(
    user_id: int, 
    goal: GoalCreate, 
    db: Session = Depends(get_db)
):
    """
    添加目标接口
    
    创建新的健身目标，系统会根据目标类型自动生成推荐训练计划和饮食建议
    """
    return create_goal(db=db, user_id=user_id, goal=goal)


@router.get("/user/{user_id}", response_model=List[GoalResponse])
def list_user_goals(
    user_id: int, 
    status: Optional[str] = Query(None, description="目标状态: active/completed/failed"),
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    db: Session = Depends(get_db)
):
    """
    获取用户目标列表接口
    
    支持按状态过滤，按创建时间倒序排列
    """
    goals = get_user_goals(db, user_id=user_id, status=status, skip=skip, limit=limit)
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取目标接口
    
    包含目标详情、训练计划、饮食建议和进度记录
    """
    db_goal = get_goal_with_details(db, goal_id=goal_id)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    return db_goal


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal_info(
    goal_id: int, 
    goal: GoalUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新目标接口
    """
    db_goal = update_goal(db, goal_id=goal_id, goal=goal)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    return db_goal


@router.delete("/{goal_id}", response_model=ApiResponse)
def delete_goal_info(goal_id: int, db: Session = Depends(get_db)):
    """
    删除目标接口
    """
    success = delete_goal(db, goal_id=goal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    return ApiResponse(
        code=status.HTTP_200_OK,
        message="目标删除成功"
    )


@router.get("/active/user/{user_id}", response_model=Optional[GoalResponse])
def get_active_user_goal(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户当前进行中的目标接口
    
    返回用户最近创建的进行中的目标
    """
    return get_active_goal(db, user_id=user_id)


@router.post("/{goal_id}/progress", response_model=GoalProgressResponse, status_code=status.HTTP_201_CREATED)
def add_goal_progress_record(
    goal_id: int, 
    progress: GoalProgressCreate, 
    db: Session = Depends(get_db)
):
    """
    添加目标进度记录接口
    
    记录目标的定期进度，系统会自动计算进度百分比并更新目标状态
    """
    db_progress = add_goal_progress(db, goal_id=goal_id, progress=progress)
    if not db_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    return db_progress


@router.get("/{goal_id}/progress", response_model=List[GoalProgressResponse])
def list_goal_progress_records(
    goal_id: int,
    limit: int = Query(30, ge=1, le=365, description="最多返回记录数"),
    db: Session = Depends(get_db)
):
    """
    获取目标进度记录列表接口
    
    按记录日期倒序排列
    """
    db_goal = get_goal_by_id(db, goal_id=goal_id)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    progress_records = get_goal_progress_records(db, goal_id=goal_id, limit=limit)
    return progress_records


@router.post("/{goal_id}/complete", response_model=GoalResponse)
def complete_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    标记目标为已完成接口
    """
    db_goal = get_goal_by_id(db, goal_id=goal_id)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    # 更新目标状态
    db_goal.status = "completed"
    db_goal.progress = 100.0
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.post("/{goal_id}/fail", response_model=GoalResponse)
def fail_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    标记目标为失败接口
    """
    db_goal = get_goal_by_id(db, goal_id=goal_id)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标不存在"
        )
    
    # 更新目标状态
    db_goal.status = "failed"
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/stats/user/{user_id}", response_model=dict)
def get_goal_stats(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户目标统计接口
    
    返回用户目标统计数据：进行中、已完成、已失败的数量
    """
    from sqlalchemy import func
    
    active_count = db.query(func.count(Goal.id))\
        .filter(Goal.user_id == user_id, Goal.status == "active")\
        .scalar()
    
    completed_count = db.query(func.count(Goal.id))\
        .filter(Goal.user_id == user_id, Goal.status == "completed")\
        .scalar()
    
    failed_count = db.query(func.count(Goal.id))\
        .filter(Goal.user_id == user_id, Goal.status == "failed")\
        .scalar()
    
    return {
        "active_count": active_count or 0,
        "completed_count": completed_count or 0,
        "failed_count": failed_count or 0,
        "total_count": (active_count or 0) + (completed_count or 0) + (failed_count or 0)
    }

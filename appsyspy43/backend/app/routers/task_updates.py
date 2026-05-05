"""
任务更新路由模块
处理任务状态变更记录的查询操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.database import get_db
from app.models.task_update import TaskUpdate
from app.models.transport_task import TransportTask
from app.models.user import User, UserRole
from app.schemas.task_update import (
    TaskUpdateResponse,
    TaskUpdateListResponse,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.security import (
    get_current_user,
    require_admin,
    require_dispatcher,
)

router = APIRouter(
    prefix="/api/task-updates",
    tags=["任务更新记录"],
    responses={404: {"description": "未找到"}},
)


@router.get("", response_model=ApiResponse[PaginatedResponse[TaskUpdateResponse]])
async def get_task_updates(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    transport_task_id: Optional[int] = Query(None, description="任务ID筛选"),
    user_id: Optional[int] = Query(None, description="操作人ID筛选"),
    update_type: Optional[str] = Query(None, description="更新类型筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务更新记录列表
    支持分页、任务筛选、操作人筛选、类型筛选和时间范围筛选
    """
    # 构建查询条件
    query = select(TaskUpdate)
    
    # 任务筛选
    if transport_task_id:
        query = query.where(TaskUpdate.transport_task_id == transport_task_id)
    
    # 操作人筛选
    if user_id:
        query = query.where(TaskUpdate.user_id == user_id)
    
    # 更新类型筛选
    if update_type:
        query = query.where(TaskUpdate.update_type == update_type)
    
    # 时间范围筛选
    if start_time:
        query = query.where(TaskUpdate.created_at >= start_time)
    if end_time:
        query = query.where(TaskUpdate.created_at <= end_time)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(TaskUpdate.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    updates = result.scalars().all()
    
    # 构建响应
    update_responses = [TaskUpdateResponse.model_validate(update) for update in updates]
    paginated_response = PaginatedResponse(
        items=update_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=paginated_response,
    )


@router.get("/task/{task_id}", response_model=ApiResponse[list[TaskUpdateResponse]])
async def get_task_updates_by_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定任务的所有更新记录
    按时间正序排列，方便查看任务流程
    """
    # 检查任务是否存在
    result = await db.execute(
        select(TransportTask).where(
            TransportTask.id == task_id,
            TransportTask.is_deleted == False,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 司机只能查看自己任务的更新记录
    if current_user.role == UserRole.DRIVER and task.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该任务的更新记录"
        )
    
    # 查询任务的所有更新记录
    query = select(TaskUpdate).where(
        TaskUpdate.transport_task_id == task_id
    ).order_by(TaskUpdate.created_at.asc())
    
    result = await db.execute(query)
    updates = result.scalars().all()
    
    # 构建响应
    update_responses = [TaskUpdateResponse.model_validate(update) for update in updates]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=update_responses,
    )


@router.get("/{update_id}", response_model=ApiResponse[TaskUpdateResponse])
async def get_task_update(
    update_id: int,
    current_user: User = Depends(require_dispatcher),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个任务更新记录详情
    """
    result = await db.execute(select(TaskUpdate).where(TaskUpdate.id == update_id))
    update = result.scalar_one_or_none()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="更新记录不存在"
        )
    
    update_response = TaskUpdateResponse.model_validate(update)
    return ApiResponse(
        code=200,
        message="获取成功",
        data=update_response,
    )

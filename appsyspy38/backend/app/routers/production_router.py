"""
拌合站生产相关API路由
包含生产任务、生产记录等功能
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from ..database import get_db
from ..models.user_models import User
from ..models.business_models import ProductionTask, ProductionRecord
from ..schemas.business_schemas import (
    ProductionTaskCreate, ProductionTaskUpdate, ProductionTaskResponse,
    ProductionRecordCreate, ProductionRecordResponse
)
from ..schemas.user_schemas import ApiResponse, PaginatedResponse
from ..utils.security import (
    get_current_user, require_role, has_role, is_admin
)

router = APIRouter(prefix="/production", tags=["拌合站生产管理"])


def generate_task_no() -> str:
    """生成生产任务编号"""
    import time
    timestamp = int(time.time())
    return f"PT{timestamp}"


def generate_record_no() -> str:
    """生成生产记录编号"""
    import time
    timestamp = int(time.time())
    return f"PR{timestamp}"


@router.post("/tasks", response_model=ProductionTaskResponse)
async def create_production_task(
    task_data: ProductionTaskCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    创建生产任务（管理员权限）
    """
    task = ProductionTask(
        **task_data.model_dump(),
        task_no=generate_task_no(),
        status="pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return ProductionTaskResponse.model_validate(task)


@router.get("/tasks", response_model=PaginatedResponse)
async def get_production_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="任务状态"),
    operator_id: Optional[int] = Query(None, description="操作员ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产任务列表
    - 管理员：可以查看所有任务
    - 拌合站操作员：只能查看分配给自己的任务
    """
    # 构建查询条件
    query = select(ProductionTask)
    
    # 非管理员只能看到自己的任务
    if not is_admin(current_user) and has_role(current_user, "mixer_operator"):
        query = query.where(ProductionTask.operator_id == current_user.id)
    elif operator_id and is_admin(current_user):
        query = query.where(ProductionTask.operator_id == operator_id)
    
    if status:
        query = query.where(ProductionTask.status == status)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(ProductionTask.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    task_responses = [ProductionTaskResponse.model_validate(t) for t in tasks]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=task_responses
    )


@router.get("/tasks/{task_id}", response_model=ProductionTaskResponse)
async def get_production_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产任务详情
    """
    result = await db.execute(
        select(ProductionTask).where(ProductionTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产任务不存在"
        )
    
    # 权限检查：非管理员只能查看自己的任务
    if not is_admin(current_user):
        if task.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此任务"
            )
    
    return ProductionTaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=ProductionTaskResponse)
async def update_production_task(
    task_id: int,
    task_data: ProductionTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新生产任务
    - 管理员：可以更新所有任务
    - 拌合站操作员：只能更新自己负责的任务的状态
    """
    result = await db.execute(
        select(ProductionTask).where(ProductionTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产任务不存在"
        )
    
    # 权限检查
    if not is_admin(current_user):
        if task.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此任务"
            )
        # 操作员只能更新状态
        if task_data.status is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="操作员只能更新任务状态"
            )
    
    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    
    return ProductionTaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}", response_model=ApiResponse)
async def delete_production_task(
    task_id: int,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    删除生产任务（管理员权限）
    """
    result = await db.execute(
        select(ProductionTask).where(ProductionTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产任务不存在"
        )
    
    await db.delete(task)
    await db.commit()
    
    return ApiResponse(message="生产任务已删除")


@router.post("/records", response_model=ProductionRecordResponse)
async def create_production_record(
    record_data: ProductionRecordCreate,
    current_user: User = Depends(require_role("mixer_operator")),
    db: AsyncSession = Depends(get_db)
):
    """
    提交生产记录（拌合站操作员权限）
    """
    # 验证任务是否存在且属于当前操作员
    result = await db.execute(
        select(ProductionTask).where(ProductionTask.id == record_data.task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产任务不存在"
        )
    
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能提交自己任务的生产记录"
        )
    
    # 创建生产记录
    record = ProductionRecord(
        **record_data.model_dump(),
        operator_id=current_user.id
    )
    db.add(record)
    
    # 更新任务状态
    if task.status != "completed":
        task.status = "executing"
        task.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(record)
    
    return ProductionRecordResponse.model_validate(record)


@router.get("/records", response_model=PaginatedResponse)
async def get_production_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    task_id: Optional[int] = Query(None, description="任务ID"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产记录列表
    - 管理员：可以查看所有记录
    - 拌合站操作员：只能查看自己提交的记录
    """
    # 构建查询条件
    query = select(ProductionRecord)
    
    # 非管理员只能看到自己的记录
    if not is_admin(current_user) and has_role(current_user, "mixer_operator"):
        query = query.where(ProductionRecord.operator_id == current_user.id)
    
    if task_id:
        query = query.where(ProductionRecord.task_id == task_id)
    
    if start_date:
        query = query.where(ProductionRecord.production_date >= start_date)
    
    if end_date:
        query = query.where(ProductionRecord.production_date <= end_date)
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页查询
    query = query.order_by(ProductionRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    record_responses = [ProductionRecordResponse.model_validate(r) for r in records]
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=record_responses
    )


@router.get("/records/{record_id}", response_model=ProductionRecordResponse)
async def get_production_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取生产记录详情
    """
    result = await db.execute(
        select(ProductionRecord).where(ProductionRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产记录不存在"
        )
    
    # 权限检查
    if not is_admin(current_user):
        if record.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此记录"
            )
    
    return ProductionRecordResponse.model_validate(record)


@router.post("/tasks/{task_id}/complete", response_model=ProductionTaskResponse)
async def complete_production_task(
    task_id: int,
    current_user: User = Depends(require_role("mixer_operator")),
    db: AsyncSession = Depends(get_db)
):
    """
    完成生产任务（拌合站操作员权限）
    """
    result = await db.execute(
        select(ProductionTask).where(ProductionTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生产任务不存在"
        )
    
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能完成自己的任务"
        )
    
    task.status = "completed"
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    
    return ProductionTaskResponse.model_validate(task)

"""
任务管理路由 - 处理生产任务的CRUD操作
包括任务列表、接单、开始、完成等功能
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Task, User, Formula
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    SuccessResponse
)
from app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/tasks", tags=["任务管理"])


async def get_task_with_relations(db: AsyncSession, task_id: int) -> Optional[Task]:
    """
    获取任务及其关联信息（操作员、配方）
    
    Args:
        db: 数据库会话
        task_id: 任务ID
    
    Returns:
        Task: 带关联信息的任务对象
    """
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.operator),
            selectinload(Task.formula)
        )
        .where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


def build_task_response(task: Task) -> TaskResponse:
    """
    构建任务响应对象，包含关联信息
    
    Args:
        task: 任务对象
    
    Returns:
        TaskResponse: 任务响应对象
    """
    task_dict = {
        "id": task.id,
        "task_no": task.task_no,
        "concrete_grade": task.concrete_grade,
        "quantity": task.quantity,
        "delivery_time": task.delivery_time,
        "project_name": task.project_name,
        "project_address": task.project_address,
        "customer_name": task.customer_name,
        "formula_id": task.formula_id,
        "remarks": task.remarks,
        "status": task.status,
        "operator_id": task.operator_id,
        "operator_name": task.operator.real_name if task.operator else None,
        "accepted_at": task.accepted_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "formula_info": task.formula,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }
    return TaskResponse.model_validate(task_dict)


@router.get("", response_model=TaskListResponse, summary="获取任务列表")
async def get_tasks(
    status: Optional[str] = Query(None, description="任务状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（任务编号、项目名称）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务列表，支持分页和筛选
    
    - 操作员可以看到所有待接任务和自己已接的任务
    - 管理员可以看到所有任务
    
    Args:
        status: 任务状态筛选
        keyword: 关键词搜索
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        TaskListResponse: 任务列表
    """
    # 构建查询条件
    query = select(Task).options(
        selectinload(Task.operator),
        selectinload(Task.formula)
    )
    
    # 权限控制：操作员只能看到待接和自己已接的任务
    if current_user.role != "admin":
        query = query.where(
            or_(
                Task.status == "pending",
                Task.operator_id == current_user.id
            )
        )
    
    # 状态筛选
    if status:
        query = query.where(Task.status == status)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Task.task_no.contains(keyword),
                Task.project_name.contains(keyword)
            )
        )
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    query = query.order_by(Task.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # 构建响应
    task_responses = [build_task_response(task) for task in tasks]
    
    return TaskListResponse(
        total=total,
        tasks=task_responses
    )


@router.get("/pending", response_model=TaskListResponse, summary="获取待执行任务（首页推送）")
async def get_pending_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取待执行任务列表 - 用于首页推送
    包括：
    1. 待接状态的任务（所有操作员可见）
    2. 已接但未完成的任务（仅限接单人可见）
    
    Args:
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        TaskListResponse: 待执行任务列表
    """
    # 构建查询：待接任务 + 自己已接但未完成的任务
    query = select(Task).options(
        selectinload(Task.operator),
        selectinload(Task.formula)
    ).where(
        or_(
            Task.status == "pending",
            (Task.operator_id == current_user.id) & Task.status.in_(["accepted", "in_progress"])
        )
    )
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页查询，按状态优先级排序：待接 > 已接 > 进行中
    query = query.order_by(
        # 自定义排序优先级
        Task.status == "pending",
        Task.status == "accepted",
        Task.status == "in_progress",
        Task.created_at.desc()
    )
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # 构建响应
    task_responses = [build_task_response(task) for task in tasks]
    
    return TaskListResponse(
        total=total,
        tasks=task_responses
    )


@router.get("/{task_id}", response_model=TaskResponse, summary="获取任务详情")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务详情
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        TaskResponse: 任务详情
    """
    task = await get_task_with_relations(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 权限检查：非管理员只能查看待接任务或自己已接的任务
    if current_user.role != "admin":
        if task.status != "pending" and task.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此任务"
            )
    
    return build_task_response(task)


@router.post("", response_model=TaskResponse, summary="创建任务（管理员功能）")
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    创建新任务 - 仅管理员可操作
    
    Args:
        task_data: 任务创建数据
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        TaskResponse: 创建的任务
    """
    # 检查任务编号是否已存在
    existing = await db.execute(
        select(Task).where(Task.task_no == task_data.task_no)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务编号已存在"
        )
    
    # 如果指定了配方，检查配方是否存在
    if task_data.formula_id:
        formula = await db.execute(
            select(Formula).where(Formula.id == task_data.formula_id)
        )
        if not formula.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的配方不存在"
            )
    
    # 创建任务
    new_task = Task(
        task_no=task_data.task_no,
        concrete_grade=task_data.concrete_grade,
        quantity=task_data.quantity,
        delivery_time=task_data.delivery_time,
        project_name=task_data.project_name,
        project_address=task_data.project_address,
        customer_name=task_data.customer_name,
        formula_id=task_data.formula_id,
        remarks=task_data.remarks,
        status="pending"
    )
    
    db.add(new_task)
    await db.commit()
    
    # 获取带关联信息的任务
    task = await get_task_with_relations(db, new_task.id)
    
    return build_task_response(task)


@router.put("/{task_id}", response_model=TaskResponse, summary="更新任务（管理员功能）")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    更新任务信息 - 仅管理员可操作
    
    Args:
        task_id: 任务ID
        task_data: 更新数据
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        TaskResponse: 更新后的任务
    """
    task = await get_task_with_relations(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    await db.commit()
    await db.refresh(task)
    
    # 重新获取带关联信息的任务
    task = await get_task_with_relations(db, task_id)
    
    return build_task_response(task)


@router.post("/{task_id}/accept", response_model=TaskResponse, summary="接单（一键确认接单）")
async def accept_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    一键确认接单
    
    - 将任务状态从pending更新为accepted
    - 记录接单人ID和接单时间
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户（操作员）
    
    Returns:
        TaskResponse: 接单后的任务
    """
    task = await get_task_with_relations(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查任务状态
    if task.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法接单"
        )
    
    # 更新任务状态
    task.status = "accepted"
    task.operator_id = current_user.id
    task.accepted_at = datetime.now()
    
    await db.commit()
    await db.refresh(task)
    
    # 重新获取带关联信息的任务
    task = await get_task_with_relations(db, task_id)
    
    return build_task_response(task)


@router.post("/{task_id}/start", response_model=TaskResponse, summary="开始生产")
async def start_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    开始生产
    
    - 将任务状态从accepted更新为in_progress
    - 记录开始时间
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户（必须是接单人）
    
    Returns:
        TaskResponse: 更新后的任务
    """
    task = await get_task_with_relations(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限：只有接单人可以开始生产
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有接单人可以开始生产"
        )
    
    # 检查任务状态
    if task.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法开始生产"
        )
    
    # 更新任务状态
    task.status = "in_progress"
    task.started_at = datetime.now()
    
    await db.commit()
    await db.refresh(task)
    
    # 重新获取带关联信息的任务
    task = await get_task_with_relations(db, task_id)
    
    return build_task_response(task)


@router.post("/{task_id}/complete", response_model=TaskResponse, summary="完成任务")
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    完成生产任务
    
    - 将任务状态从in_progress更新为completed
    - 记录完成时间
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户（必须是接单人）
    
    Returns:
        TaskResponse: 完成后的任务
    """
    task = await get_task_with_relations(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限：只有接单人可以完成任务
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有接单人可以完成任务"
        )
    
    # 检查任务状态
    if task.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法完成"
        )
    
    # 更新任务状态
    task.status = "completed"
    task.completed_at = datetime.now()
    
    await db.commit()
    await db.refresh(task)
    
    # 重新获取带关联信息的任务
    task = await get_task_with_relations(db, task_id)
    
    return build_task_response(task)


@router.delete("/{task_id}", response_model=SuccessResponse, summary="删除任务（管理员功能）")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    删除任务 - 仅管理员可操作
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前管理员用户
    
    Returns:
        SuccessResponse: 操作结果
    """
    task = await db.execute(select(Task).where(Task.id == task_id))
    task = task.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 只有待接状态的任务可以删除
    if task.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能删除待接状态的任务"
        )
    
    await db.delete(task)
    await db.commit()
    
    return SuccessResponse(message="任务删除成功")

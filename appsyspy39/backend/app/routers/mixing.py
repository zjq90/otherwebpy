"""
搅拌过程记录路由 - 处理搅拌记录的CRUD操作
包括自动采集搅拌数据、手动补充异常说明
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import MixingRecord, Task, FeedingRecord, User
from app.schemas import (
    MixingRecordCreate,
    MixingRecordResponse,
    MixingRecordListResponse,
    SuccessResponse
)
from app.core.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/mixing", tags=["搅拌过程记录"])


@router.get("", response_model=MixingRecordListResponse, summary="获取搅拌记录列表")
async def get_mixing_records(
    task_id: Optional[int] = Query(None, description="任务ID筛选"),
    is_abnormal: Optional[bool] = Query(None, description="是否异常筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取搅拌记录列表，支持分页和筛选
    
    Args:
        task_id: 任务ID筛选
        is_abnormal: 是否异常筛选
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        MixingRecordListResponse: 搅拌记录列表
    """
    # 构建查询条件
    query = select(MixingRecord)
    
    # 管理员可以查看所有记录，操作员只能查看自己的
    if current_user.role != "admin":
        # 查询操作员参与的任务
        task_ids_query = select(Task.id).where(Task.operator_id == current_user.id)
        task_ids_result = await db.execute(task_ids_query)
        task_ids = [row[0] for row in task_ids_result.all()]
        
        if task_ids:
            query = query.where(MixingRecord.task_id.in_(task_ids))
        else:
            return MixingRecordListResponse(total=0, records=[])
    
    # 任务ID筛选
    if task_id:
        query = query.where(MixingRecord.task_id == task_id)
    
    # 异常筛选
    if is_abnormal is not None:
        query = query.where(MixingRecord.is_abnormal == is_abnormal)
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    query = query.order_by(MixingRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 构建响应
    record_responses = [MixingRecordResponse.model_validate(r) for r in records]
    
    return MixingRecordListResponse(
        total=total,
        records=record_responses
    )


@router.get("/task/{task_id}", response_model=MixingRecordListResponse, summary="获取任务的所有搅拌记录")
async def get_task_mixing_records(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定任务的所有搅拌记录
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        MixingRecordListResponse: 搅拌记录列表
    """
    # 验证任务权限
    task_result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 非管理员只能查看自己的任务
    if current_user.role != "admin" and task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此任务的搅拌记录"
        )
    
    # 查询搅拌记录
    result = await db.execute(
        select(MixingRecord)
        .where(MixingRecord.task_id == task_id)
        .order_by(MixingRecord.batch_no.asc())
    )
    records = result.scalars().all()
    
    record_responses = [MixingRecordResponse.model_validate(r) for r in records]
    
    return MixingRecordListResponse(
        total=len(records),
        records=record_responses
    )


@router.get("/{record_id}", response_model=MixingRecordResponse, summary="获取搅拌记录详情")
async def get_mixing_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取搅拌记录详情
    
    Args:
        record_id: 记录ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        MixingRecordResponse: 搅拌记录详情
    """
    result = await db.execute(
        select(MixingRecord).where(MixingRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="搅拌记录不存在"
        )
    
    # 权限检查
    if current_user.role != "admin":
        # 检查任务是否属于当前用户
        task_result = await db.execute(
            select(Task).where(Task.id == record.task_id)
        )
        task = task_result.scalar_one_or_none()
        
        if not task or task.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此记录"
            )
    
    return MixingRecordResponse.model_validate(record)


@router.post("", response_model=MixingRecordResponse, summary="创建搅拌记录")
async def create_mixing_record(
    record_data: MixingRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建搅拌记录
    
    - 自动采集搅拌时长、转速等数据
    - 支持手动补充搅拌异常情况说明
    
    Args:
        record_data: 搅拌记录数据
        db: 数据库会话
        current_user: 当前登录用户（操作员）
    
    Returns:
        MixingRecordResponse: 创建的搅拌记录
    """
    # 验证任务
    task_result = await db.execute(
        select(Task).where(Task.id == record_data.task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限：只有接单人可以添加搅拌记录
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有接单人可以添加搅拌记录"
        )
    
    # 检查任务状态
    if task.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法添加搅拌记录"
        )
    
    # 检查盘号是否已存在
    existing = await db.execute(
        select(MixingRecord).where(
            MixingRecord.task_id == record_data.task_id,
            MixingRecord.batch_no == record_data.batch_no
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"本任务第{record_data.batch_no}盘的搅拌记录已存在"
        )
    
    # 验证关联的投料记录（如果提供了）
    if record_data.feeding_record_id:
        feeding_result = await db.execute(
            select(FeedingRecord).where(
                FeedingRecord.id == record_data.feeding_record_id,
                FeedingRecord.task_id == record_data.task_id,
                FeedingRecord.batch_no == record_data.batch_no
            )
        )
        if not feeding_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联的投料记录不存在或不匹配"
            )
    
    # 确定状态
    status_value = "completed"
    if record_data.is_abnormal:
        status_value = "abnormal"
    
    # 创建搅拌记录
    new_record = MixingRecord(
        task_id=record_data.task_id,
        feeding_record_id=record_data.feeding_record_id,
        operator_id=current_user.id,
        batch_no=record_data.batch_no,
        
        # 搅拌参数
        mixing_time_seconds=record_data.mixing_time_seconds,
        rotation_speed=record_data.rotation_speed or settings.DEFAULT_ROTATION_SPEED,
        current_temperature=record_data.current_temperature,
        
        # 状态
        status=status_value,
        
        # 异常记录
        is_abnormal=record_data.is_abnormal or False,
        abnormal_type=record_data.abnormal_type,
        abnormal_description=record_data.abnormal_description,
        handling_measures=record_data.handling_measures,
        
        # 质量检验
        slump_actual=record_data.slump_actual,
        temperature_actual=record_data.temperature_actual,
        quality_status=record_data.quality_status,
        
        remarks=record_data.remarks,
        completed_at=datetime.now()
    )
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return MixingRecordResponse.model_validate(new_record)


@router.put("/{record_id}", response_model=MixingRecordResponse, summary="更新搅拌记录（补充异常说明）")
async def update_mixing_record(
    record_id: int,
    is_abnormal: Optional[bool] = None,
    abnormal_type: Optional[str] = None,
    abnormal_description: Optional[str] = None,
    handling_measures: Optional[str] = None,
    slump_actual: Optional[float] = None,
    temperature_actual: Optional[float] = None,
    quality_status: Optional[str] = None,
    remarks: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新搅拌记录 - 主要用于手动补充异常情况说明
    
    Args:
        record_id: 记录ID
        is_abnormal: 是否异常
        abnormal_type: 异常类型
        abnormal_description: 异常情况说明
        handling_measures: 处理措施
        slump_actual: 实测坍落度
        temperature_actual: 实测温度
        quality_status: 质量状态
        remarks: 备注
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        MixingRecordResponse: 更新后的记录
    """
    result = await db.execute(
        select(MixingRecord).where(MixingRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="搅拌记录不存在"
        )
    
    # 权限检查
    if current_user.role != "admin":
        if record.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此记录"
            )
    
    # 更新字段
    if is_abnormal is not None:
        record.is_abnormal = is_abnormal
        if is_abnormal:
            record.status = "abnormal"
    
    if abnormal_type:
        record.abnormal_type = abnormal_type
    if abnormal_description:
        record.abnormal_description = abnormal_description
    if handling_measures:
        record.handling_measures = handling_measures
    if slump_actual is not None:
        record.slump_actual = slump_actual
    if temperature_actual is not None:
        record.temperature_actual = temperature_actual
    if quality_status:
        record.quality_status = quality_status
    if remarks:
        record.remarks = remarks
    
    await db.commit()
    await db.refresh(record)
    
    return MixingRecordResponse.model_validate(record)


@router.delete("/{record_id}", response_model=SuccessResponse, summary="删除搅拌记录")
async def delete_mixing_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除搅拌记录
    
    Args:
        record_id: 记录ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        SuccessResponse: 操作结果
    """
    result = await db.execute(
        select(MixingRecord).where(MixingRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="搅拌记录不存在"
        )
    
    # 权限检查
    if current_user.role != "admin":
        if record.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此记录"
            )
    
    await db.delete(record)
    await db.commit()
    
    return SuccessResponse(message="搅拌记录删除成功")


@router.get("/stats/task/{task_id}", summary="获取任务搅拌统计")
async def get_task_mixing_stats(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定任务的搅拌统计信息
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        dict: 统计信息
    """
    # 验证任务权限
    task_result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 非管理员只能查看自己的任务
    if current_user.role != "admin" and task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此任务的统计信息"
        )
    
    # 查询统计
    records_result = await db.execute(
        select(MixingRecord).where(MixingRecord.task_id == task_id)
    )
    records = records_result.scalars().all()
    
    total_batches = len(records)
    total_time_seconds = sum(r.mixing_time_seconds for r in records)
    avg_time_seconds = total_time_seconds / total_batches if total_batches > 0 else 0
    
    abnormal_count = sum(1 for r in records if r.is_abnormal)
    qualified_count = sum(1 for r in records if r.quality_status == "qualified")
    unqualified_count = sum(1 for r in records if r.quality_status == "unqualified")
    
    return {
        "task_id": task_id,
        "task_no": task.task_no,
        "total_batches": total_batches,
        "total_time_seconds": total_time_seconds,
        "total_time_minutes": round(total_time_seconds / 60, 2),
        "avg_time_seconds": round(avg_time_seconds, 2),
        "abnormal_count": abnormal_count,
        "quality_stats": {
            "qualified": qualified_count,
            "unqualified": unqualified_count,
            "pending": total_batches - qualified_count - unqualified_count
        }
    }

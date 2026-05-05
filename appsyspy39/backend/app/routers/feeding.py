"""
投料监控路由 - 处理投料记录的CRUD操作
包括扫码/手动录入投料情况、偏差计算和预警
"""

from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import FeedingRecord, Task, Formula, User
from app.schemas import (
    FeedingRecordCreate,
    FeedingRecordResponse,
    FeedingRecordListResponse,
    SuccessResponse
)
from app.core.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/feeding", tags=["投料监控"])


def calculate_deviation(theory: float, actual: float) -> Optional[float]:
    """
    计算投料偏差百分比
    
    偏差 = (实际用量 - 理论用量) / 理论用量 * 100%
    
    Args:
        theory: 理论用量
        actual: 实际用量
    
    Returns:
        float: 偏差百分比，如果理论用量为0则返回None
    """
    if theory is None or actual is None:
        return None
    if theory == 0:
        return 0
    return round(((actual - theory) / theory) * 100, 2)


def check_deviation_warning(deviation: Optional[float]) -> Dict:
    """
    检查偏差是否超过预警阈值
    
    Args:
        deviation: 偏差百分比
    
    Returns:
        dict: 包含has_warning、warning_level的字典
    """
    if deviation is None:
        return {"has_warning": False, "warning_level": None}
    
    abs_deviation = abs(deviation)
    
    if abs_deviation >= settings.DEVIATION_CRITICAL_THRESHOLD:
        return {"has_warning": True, "warning_level": "critical"}
    elif abs_deviation >= settings.DEVIATION_WARNING_THRESHOLD:
        return {"has_warning": True, "warning_level": "warning"}
    else:
        return {"has_warning": False, "warning_level": None}


def get_task_formula(task: Task) -> Optional[Formula]:
    """
    获取任务关联的配方
    
    如果任务有直接关联的配方，使用该配方；
    否则根据混凝土标号查找适用的标准配方。
    
    Args:
        task: 任务对象
    
    Returns:
        Formula: 配方对象，如果找不到则返回None
    """
    # 优先使用任务直接关联的配方
    if task.formula_id and task.formula:
        return task.formula
    
    # 否则根据混凝土标号查找标准配方
    return None


def calculate_theory_quantity(formula: Formula, batch_quantity: float) -> Dict[str, float]:
    """
    根据配方和盘方量计算理论投料量
    
    Args:
        formula: 配方对象（每立方米用量）
        batch_quantity: 本盘方量（立方米）
    
    Returns:
        dict: 各种材料的理论用量
    """
    return {
        "cement": formula.cement * batch_quantity,
        "water": formula.water * batch_quantity,
        "sand": formula.sand * batch_quantity,
        "stone": formula.stone * batch_quantity,
        "admixture": (formula.admixture or 0) * batch_quantity,
        "fly_ash": (formula.fly_ash or 0) * batch_quantity,
        "mineral_powder": (formula.mineral_powder or 0) * batch_quantity
    }


@router.get("", response_model=FeedingRecordListResponse, summary="获取投料记录列表")
async def get_feeding_records(
    task_id: Optional[int] = Query(None, description="任务ID筛选"),
    has_warning: Optional[bool] = Query(None, description="是否有预警筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取投料记录列表，支持分页和筛选
    
    Args:
        task_id: 任务ID筛选
        has_warning: 是否有预警筛选
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        FeedingRecordListResponse: 投料记录列表
    """
    # 构建查询条件
    query = select(FeedingRecord)
    
    # 管理员可以查看所有记录，操作员只能查看自己的
    if current_user.role != "admin":
        # 查询操作员参与的任务
        task_ids_query = select(Task.id).where(Task.operator_id == current_user.id)
        task_ids_result = await db.execute(task_ids_query)
        task_ids = [row[0] for row in task_ids_result.all()]
        
        if task_ids:
            query = query.where(FeedingRecord.task_id.in_(task_ids))
        else:
            return FeedingRecordListResponse(total=0, records=[])
    
    # 任务ID筛选
    if task_id:
        query = query.where(FeedingRecord.task_id == task_id)
    
    # 预警筛选
    if has_warning is not None:
        query = query.where(FeedingRecord.has_warning == has_warning)
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页查询
    query = query.order_by(FeedingRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 构建响应
    record_responses = [FeedingRecordResponse.model_validate(r) for r in records]
    
    return FeedingRecordListResponse(
        total=total,
        records=record_responses
    )


@router.get("/task/{task_id}", response_model=FeedingRecordListResponse, summary="获取任务的所有投料记录")
async def get_task_feeding_records(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定任务的所有投料记录
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        FeedingRecordListResponse: 投料记录列表
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
            detail="无权查看此任务的投料记录"
        )
    
    # 查询投料记录
    result = await db.execute(
        select(FeedingRecord)
        .where(FeedingRecord.task_id == task_id)
        .order_by(FeedingRecord.batch_no.asc())
    )
    records = result.scalars().all()
    
    record_responses = [FeedingRecordResponse.model_validate(r) for r in records]
    
    return FeedingRecordListResponse(
        total=len(records),
        records=record_responses
    )


@router.get("/{record_id}", response_model=FeedingRecordResponse, summary="获取投料记录详情")
async def get_feeding_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取投料记录详情
    
    Args:
        record_id: 记录ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        FeedingRecordResponse: 投料记录详情
    """
    result = await db.execute(
        select(FeedingRecord).where(FeedingRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投料记录不存在"
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
    
    return FeedingRecordResponse.model_validate(record)


@router.post("", response_model=FeedingRecordResponse, summary="创建投料记录（扫码/手动录入）")
async def create_feeding_record(
    record_data: FeedingRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建投料记录 - 支持扫码或手动录入
    
    - 自动计算理论投料量（根据配方和盘方量）
    - 自动计算偏差百分比
    - 偏差超过阈值时触发预警
    
    Args:
        record_data: 投料记录数据
        db: 数据库会话
        current_user: 当前登录用户（操作员）
    
    Returns:
        FeedingRecordResponse: 创建的投料记录
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
    
    # 检查权限：只有接单人可以添加投料记录
    if task.operator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有接单人可以添加投料记录"
        )
    
    # 检查任务状态
    if task.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法添加投料记录"
        )
    
    # 获取配方信息
    formula = None
    if task.formula_id:
        formula_result = await db.execute(
            select(Formula).where(Formula.id == task.formula_id)
        )
        formula = formula_result.scalar_one_or_none()
    
    if not formula:
        # 如果任务没有关联配方，尝试根据混凝土标号查找
        formula_result = await db.execute(
            select(Formula).where(
                Formula.concrete_grade == task.concrete_grade,
                Formula.is_standard == True,
                Formula.is_active == True
            ).limit(1)
        )
        formula = formula_result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"找不到混凝土标号为{task.concrete_grade}的适用配方"
        )
    
    # 检查盘号是否已存在
    existing = await db.execute(
        select(FeedingRecord).where(
            FeedingRecord.task_id == record_data.task_id,
            FeedingRecord.batch_no == record_data.batch_no
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"本任务第{record_data.batch_no}盘的投料记录已存在"
        )
    
    # 计算理论用量
    theory_qty = calculate_theory_quantity(formula, record_data.batch_quantity)
    
    # 计算偏差
    cement_deviation = calculate_deviation(theory_qty["cement"], record_data.cement_actual)
    water_deviation = calculate_deviation(theory_qty["water"], record_data.water_actual)
    sand_deviation = calculate_deviation(theory_qty["sand"], record_data.sand_actual)
    stone_deviation = calculate_deviation(theory_qty["stone"], record_data.stone_actual)
    admixture_deviation = calculate_deviation(theory_qty["admixture"], record_data.admixture_actual)
    
    # 检查预警
    all_deviations = [
        cement_deviation,
        water_deviation,
        sand_deviation,
        stone_deviation,
        admixture_deviation
    ]
    
    has_warning = False
    warning_level = None
    warning_messages = []
    
    for i, dev in enumerate(all_deviations):
        if dev is not None:
            check = check_deviation_warning(dev)
            if check["has_warning"]:
                has_warning = True
                materials = ["水泥", "水", "砂子", "石子", "外加剂"]
                level_text = "严重" if check["warning_level"] == "critical" else "警告"
                warning_messages.append(f"{materials[i]}偏差{dev:.2f}%（{level_text}）")
                
                # 更新最高预警级别
                if check["warning_level"] == "critical":
                    warning_level = "critical"
                elif not warning_level:
                    warning_level = "warning"
    
    warning_message = "; ".join(warning_messages) if warning_messages else None
    
    # 创建投料记录
    new_record = FeedingRecord(
        task_id=record_data.task_id,
        operator_id=current_user.id,
        batch_no=record_data.batch_no,
        batch_quantity=record_data.batch_quantity,
        feeding_method=record_data.feeding_method,
        
        # 扫码/录入信息
        cement_barcode=record_data.cement_barcode,
        cement_lot=record_data.cement_lot,
        sand_barcode=record_data.sand_barcode,
        sand_lot=record_data.sand_lot,
        stone_barcode=record_data.stone_barcode,
        stone_lot=record_data.stone_lot,
        admixture_barcode=record_data.admixture_barcode,
        admixture_lot=record_data.admixture_lot,
        
        # 实际用量
        cement_actual=record_data.cement_actual,
        water_actual=record_data.water_actual,
        sand_actual=record_data.sand_actual,
        stone_actual=record_data.stone_actual,
        admixture_actual=record_data.admixture_actual,
        fly_ash_actual=record_data.fly_ash_actual or 0,
        mineral_powder_actual=record_data.mineral_powder_actual or 0,
        
        # 理论用量
        cement_theory=theory_qty["cement"],
        water_theory=theory_qty["water"],
        sand_theory=theory_qty["sand"],
        stone_theory=theory_qty["stone"],
        admixture_theory=theory_qty["admixture"],
        
        # 偏差
        cement_deviation=cement_deviation,
        water_deviation=water_deviation,
        sand_deviation=sand_deviation,
        stone_deviation=stone_deviation,
        admixture_deviation=admixture_deviation,
        
        # 预警
        has_warning=has_warning,
        warning_level=warning_level,
        warning_message=warning_message,
        
        remarks=record_data.remarks
    )
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return FeedingRecordResponse.model_validate(new_record)


@router.delete("/{record_id}", response_model=SuccessResponse, summary="删除投料记录")
async def delete_feeding_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除投料记录
    
    Args:
        record_id: 记录ID
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        SuccessResponse: 操作结果
    """
    result = await db.execute(
        select(FeedingRecord).where(FeedingRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="投料记录不存在"
        )
    
    # 权限检查
    if current_user.role != "admin":
        # 检查是否为创建者
        if record.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此记录"
            )
    
    await db.delete(record)
    await db.commit()
    
    return SuccessResponse(message="投料记录删除成功")


@router.get("/stats/task/{task_id}", summary="获取任务投料统计")
async def get_task_feeding_stats(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定任务的投料统计信息
    
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
        select(FeedingRecord).where(FeedingRecord.task_id == task_id)
    )
    records = records_result.scalars().all()
    
    total_batches = len(records)
    total_quantity = sum(r.batch_quantity for r in records)
    warning_count = sum(1 for r in records if r.has_warning)
    critical_count = sum(1 for r in records if r.warning_level == "critical")
    
    # 汇总实际用量
    total_actual = {
        "cement": sum(r.cement_actual or 0 for r in records),
        "water": sum(r.water_actual or 0 for r in records),
        "sand": sum(r.sand_actual or 0 for r in records),
        "stone": sum(r.stone_actual or 0 for r in records),
        "admixture": sum(r.admixture_actual or 0 for r in records)
    }
    
    # 汇总理论用量
    total_theory = {
        "cement": sum(r.cement_theory or 0 for r in records),
        "water": sum(r.water_theory or 0 for r in records),
        "sand": sum(r.sand_theory or 0 for r in records),
        "stone": sum(r.stone_theory or 0 for r in records),
        "admixture": sum(r.admixture_theory or 0 for r in records)
    }
    
    return {
        "task_id": task_id,
        "task_no": task.task_no,
        "total_batches": total_batches,
        "total_quantity": round(total_quantity, 2),
        "warning_count": warning_count,
        "critical_count": critical_count,
        "total_actual": total_actual,
        "total_theory": total_theory
    }

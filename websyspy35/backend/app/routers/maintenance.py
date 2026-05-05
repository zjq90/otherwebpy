from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.models.maintenance import MaintenancePlan, MaintenanceTask, MaintenanceRecord
from app.models.equipment import Equipment
from app.schemas.maintenance import (
    MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlanResponse,
    MaintenanceTaskCreate, MaintenanceTaskUpdate, MaintenanceTaskResponse,
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse
)

router = APIRouter(
    prefix="/api/maintenance",
    tags=["维护保养计划管理"]
)


# ==================== 保养计划相关路由 ====================

@router.get("/plans/", response_model=List[MaintenancePlanResponse], summary="获取保养计划列表")
def get_maintenance_plan_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    maintenance_type: Optional[str] = Query(None, description="保养类型筛选"),
    status: Optional[str] = Query(None, description="计划状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    分页获取保养计划列表
    """
    query = db.query(MaintenancePlan)
    
    if maintenance_type:
        query = query.filter(MaintenancePlan.maintenance_type == maintenance_type)
    
    if status:
        query = query.filter(MaintenancePlan.status == status)
    
    if keyword:
        query = query.filter(
            (MaintenancePlan.plan_code.contains(keyword)) |
            (MaintenancePlan.name.contains(keyword))
        )
    
    query = query.order_by(desc(MaintenancePlan.created_at))
    
    plans = query.offset(skip).limit(limit).all()
    return plans


@router.get("/plans/{plan_id}", response_model=MaintenancePlanResponse, summary="获取保养计划详情")
def get_maintenance_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    获取保养计划详情
    """
    plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"保养计划ID {plan_id} 不存在")
    return plan


@router.post("/plans/", response_model=MaintenancePlanResponse, summary="创建保养计划")
def create_maintenance_plan(plan: MaintenancePlanCreate, db: Session = Depends(get_db)):
    """
    创建保养计划
    """
    # 检查计划编号是否已存在
    existing = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_code == plan.plan_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"保养计划编号 {plan.plan_code} 已存在"
        )
    
    db_plan = MaintenancePlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    return db_plan


@router.put("/plans/{plan_id}", response_model=MaintenancePlanResponse, summary="更新保养计划")
def update_maintenance_plan(
    plan_id: int,
    plan_update: MaintenancePlanUpdate,
    db: Session = Depends(get_db)
):
    """
    更新保养计划
    """
    db_plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    
    if not db_plan:
        raise HTTPException(status_code=404, detail=f"保养计划ID {plan_id} 不存在")
    
    update_data = plan_update.model_dump(exclude_unset=True)
    
    # 检查计划编号是否被其他计划使用
    if "plan_code" in update_data:
        existing = db.query(MaintenancePlan).filter(
            MaintenancePlan.plan_code == update_data["plan_code"],
            MaintenancePlan.id != plan_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"保养计划编号 {update_data['plan_code']} 已被其他计划使用"
            )
    
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    
    return db_plan


@router.delete("/plans/{plan_id}", summary="删除保养计划")
def delete_maintenance_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    删除保养计划
    """
    db_plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    
    if not db_plan:
        raise HTTPException(status_code=404, detail=f"保养计划ID {plan_id} 不存在")
    
    db.delete(db_plan)
    db.commit()
    
    return {"message": f"保养计划ID {plan_id} 已删除", "success": True}


# ==================== 保养任务相关路由 ====================

@router.get("/tasks/", response_model=List[MaintenanceTaskResponse], summary="获取保养任务列表")
def get_maintenance_task_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    equipment_id: Optional[int] = Query(None, description="设备ID筛选"),
    plan_id: Optional[int] = Query(None, description="计划ID筛选"),
    status: Optional[str] = Query(None, description="任务状态筛选"),
    maintenance_type: Optional[str] = Query(None, description="保养类型筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    分页获取保养任务列表
    """
    query = db.query(MaintenanceTask)
    
    if equipment_id:
        query = query.filter(MaintenanceTask.equipment_id == equipment_id)
    
    if plan_id:
        query = query.filter(MaintenanceTask.plan_id == plan_id)
    
    if status:
        query = query.filter(MaintenanceTask.status == status)
    
    if maintenance_type:
        query = query.filter(MaintenanceTask.maintenance_type == maintenance_type)
    
    if start_date:
        query = query.filter(MaintenanceTask.plan_date >= start_date)
    if end_date:
        query = query.filter(MaintenanceTask.plan_date <= end_date)
    
    query = query.order_by(desc(MaintenanceTask.plan_date))
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/tasks/statistics", summary="获取保养任务统计")
def get_maintenance_task_statistics(
    db: Session = Depends(get_db)
):
    """
    获取保养任务统计数据（仪表盘用）
    """
    today = date.today()
    
    # 各状态任务数量
    status_stats = db.query(
        MaintenanceTask.status,
        func.count(MaintenanceTask.id).label("count")
    ).group_by(MaintenanceTask.status).all()
    
    status_dict = {s[0]: s[1] for s in status_stats}
    
    # 今日任务
    today_tasks = db.query(MaintenanceTask).filter(
        MaintenanceTask.plan_date == today
    ).count()
    
    # 逾期任务
    overdue_tasks = db.query(MaintenanceTask).filter(
        MaintenanceTask.plan_date < today,
        MaintenanceTask.status.notin_(["已完成", "已取消"])
    ).count()
    
    # 本周任务
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_tasks = db.query(MaintenanceTask).filter(
        MaintenanceTask.plan_date >= week_start,
        MaintenanceTask.plan_date <= week_end
    ).count()
    
    return {
        "total_tasks": sum(status_dict.values()),
        "by_status": status_dict,
        "today_tasks": today_tasks,
        "overdue_tasks": overdue_tasks,
        "week_tasks": week_tasks
    }


@router.get("/tasks/{task_id}", response_model=MaintenanceTaskResponse, summary="获取保养任务详情")
def get_maintenance_task(task_id: int, db: Session = Depends(get_db)):
    """
    获取保养任务详情
    """
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"保养任务ID {task_id} 不存在")
    return task


@router.post("/tasks/", response_model=MaintenanceTaskResponse, summary="创建保养任务")
def create_maintenance_task(task: MaintenanceTaskCreate, db: Session = Depends(get_db)):
    """
    创建保养任务
    """
    # 检查任务编号是否已存在
    existing = db.query(MaintenanceTask).filter(
        MaintenanceTask.task_code == task.task_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"保养任务编号 {task.task_code} 已存在"
        )
    
    # 检查设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == task.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=400,
            detail=f"设备ID {task.equipment_id} 不存在"
        )
    
    # 检查计划是否存在（如果指定了计划ID）
    if task.plan_id:
        plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == task.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=400,
                detail=f"保养计划ID {task.plan_id} 不存在"
            )
    
    db_task = MaintenanceTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.put("/tasks/{task_id}", response_model=MaintenanceTaskResponse, summary="更新保养任务")
def update_maintenance_task(
    task_id: int,
    task_update: MaintenanceTaskUpdate,
    db: Session = Depends(get_db)
):
    """
    更新保养任务
    """
    db_task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail=f"保养任务ID {task_id} 不存在")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # 检查设备是否存在（如果更新了设备ID）
    if "equipment_id" in update_data:
        equipment = db.query(Equipment).filter(
            Equipment.id == update_data["equipment_id"]
        ).first()
        if not equipment:
            raise HTTPException(
                status_code=400,
                detail=f"设备ID {update_data['equipment_id']} 不存在"
            )
    
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.delete("/tasks/{task_id}", summary="删除保养任务")
def delete_maintenance_task(task_id: int, db: Session = Depends(get_db)):
    """
    删除保养任务
    """
    db_task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail=f"保养任务ID {task_id} 不存在")
    
    db.delete(db_task)
    db.commit()
    
    return {"message": f"保养任务ID {task_id} 已删除", "success": True}


@router.post("/tasks/{task_id}/complete", response_model=MaintenanceTaskResponse, summary="完成保养任务")
def complete_maintenance_task(
    task_id: int,
    actual_date: Optional[date] = None,
    executor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    标记保养任务为已完成
    """
    db_task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail=f"保养任务ID {task_id} 不存在")
    
    db_task.status = "已完成"
    db_task.actual_date = actual_date or date.today()
    if executor:
        db_task.executor = executor
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ==================== 保养记录相关路由 ====================

@router.get("/records/", response_model=List[MaintenanceRecordResponse], summary="获取保养记录列表")
def get_maintenance_record_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    task_id: Optional[int] = Query(None, description="任务ID筛选"),
    executor: Optional[str] = Query(None, description="执行人员筛选"),
    has_issues: Optional[bool] = Query(None, description="是否有问题筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    分页获取保养记录列表
    """
    query = db.query(MaintenanceRecord)
    
    if task_id:
        query = query.filter(MaintenanceRecord.task_id == task_id)
    
    if executor:
        query = query.filter(MaintenanceRecord.executor.contains(executor))
    
    if has_issues is not None:
        query = query.filter(MaintenanceRecord.has_issues == has_issues)
    
    if start_date:
        query = query.filter(MaintenanceRecord.execution_date >= start_date)
    if end_date:
        query = query.filter(MaintenanceRecord.execution_date <= end_date)
    
    query = query.order_by(desc(MaintenanceRecord.execution_date))
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/records/{record_id}", response_model=MaintenanceRecordResponse, summary="获取保养记录详情")
def get_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    """
    获取保养记录详情
    """
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"保养记录ID {record_id} 不存在")
    return record


@router.post("/records/", response_model=MaintenanceRecordResponse, summary="创建保养记录")
def create_maintenance_record(record: MaintenanceRecordCreate, db: Session = Depends(get_db)):
    """
    创建保养记录（上传执行保养记录）
    """
    # 检查记录编号是否已存在
    existing = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.record_code == record.record_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"保养记录编号 {record.record_code} 已存在"
        )
    
    # 检查任务是否存在
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == record.task_id).first()
    if not task:
        raise HTTPException(
            status_code=400,
            detail=f"保养任务ID {record.task_id} 不存在"
        )
    
    db_record = MaintenanceRecord(**record.model_dump())
    db.add(db_record)
    
    # 同时更新任务状态
    task.status = "已完成"
    task.actual_date = record.execution_date
    task.executor = record.executor
    
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.put("/records/{record_id}", response_model=MaintenanceRecordResponse, summary="更新保养记录")
def update_maintenance_record(
    record_id: int,
    record_update: MaintenanceRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新保养记录
    """
    db_record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail=f"保养记录ID {record_id} 不存在")
    
    update_data = record_update.model_dump(exclude_unset=True)
    
    # 检查任务是否存在（如果更新了任务ID）
    if "task_id" in update_data:
        task = db.query(MaintenanceTask).filter(
            MaintenanceTask.id == update_data["task_id"]
        ).first()
        if not task:
            raise HTTPException(
                status_code=400,
                detail=f"保养任务ID {update_data['task_id']} 不存在"
            )
    
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    
    return db_record


@router.delete("/records/{record_id}", summary="删除保养记录")
def delete_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    """
    删除保养记录
    """
    db_record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail=f"保养记录ID {record_id} 不存在")
    
    db.delete(db_record)
    db.commit()
    
    return {"message": f"保养记录ID {record_id} 已删除", "success": True}


@router.get("/task-statuses/all", summary="获取所有任务状态")
def get_task_statuses():
    """
    获取所有任务状态列表（用于下拉选择）
    """
    return {
        "statuses": [
            {"value": "待执行", "label": "待执行"},
            {"value": "执行中", "label": "执行中"},
            {"value": "已完成", "label": "已完成"},
            {"value": "已逾期", "label": "已逾期"},
            {"value": "已取消", "label": "已取消"}
        ]
    }


@router.get("/maintenance-types/all", summary="获取所有保养类型")
def get_maintenance_types():
    """
    获取所有保养类型列表（用于下拉选择）
    """
    return {
        "types": [
            {"value": "日常保养", "label": "日常保养"},
            {"value": "月度保养", "label": "月度保养"},
            {"value": "季度保养", "label": "季度保养"},
            {"value": "年度保养", "label": "年度保养"},
            {"value": "紧急维修", "label": "紧急维修"}
        ]
    }

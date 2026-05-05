"""
保养任务管理路由
提供保养任务和保养记录相关的API接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.database.connection import db
from app.models.schemas import (
    MaintenanceTaskCreate, MaintenanceTaskUpdate, MaintenanceTaskResponse,
    MaintenanceRecordCreate, MaintenanceRecordResponse,
    ApiResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/maintenance", tags=["保养管理"])


# ==================== 保养任务相关接口 ====================

@router.get("/tasks", response_model=PaginatedResponse)
async def get_maintenance_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    device_id: Optional[int] = Query(None, description="设备ID"),
    status: Optional[str] = Query(None, description="任务状态"),
    priority: Optional[str] = Query(None, description="优先级")
):
    """
    获取保养任务列表（分页）
    
    支持按设备ID、状态和优先级筛选
    """
    # 构建查询条件
    conditions = ["1=1"]
    params = []
    
    if device_id:
        conditions.append("device_id = ?")
        params.append(device_id)
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    
    where_clause = " AND ".join(conditions)
    sql = f"""
    SELECT mt.*, d.device_name, d.device_code
    FROM maintenance_tasks mt
    LEFT JOIN devices d ON mt.device_id = d.id
    WHERE {where_clause}
    ORDER BY 
        CASE mt.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        mt.created_at DESC
    """
    
    result = db.query_paginated(sql, tuple(params), page, page_size)
    
    return PaginatedResponse(
        code=200,
        message="success",
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages'],
        data={"items": result['items']}
    )


@router.get("/tasks/{task_id}", response_model=ApiResponse)
async def get_maintenance_task(task_id: int):
    """
    获取单个保养任务详情
    """
    sql = """
    SELECT mt.*, d.device_name, d.device_code, d.total_running_hours
    FROM maintenance_tasks mt
    LEFT JOIN devices d ON mt.device_id = d.id
    WHERE mt.id = ?
    """
    task = db.query_one(sql, (task_id,))
    
    if not task:
        raise HTTPException(status_code=404, detail="保养任务不存在")
    
    return ApiResponse(
        code=200,
        message="success",
        data=task
    )


@router.post("/tasks", response_model=ApiResponse)
async def create_maintenance_task(task: MaintenanceTaskCreate):
    """
    创建保养任务
    
    系统会根据保养周期自动计算下次保养时间
    """
    # 检查设备是否存在
    check_sql = "SELECT id, total_running_hours FROM devices WHERE id = ?"
    device = db.query_one(check_sql, (task.device_id,))
    
    if not device:
        raise HTTPException(status_code=400, detail="设备不存在")
    
    # 计算下次保养运行时长
    next_maintenance_hours = task.last_maintenance_hours + task.maintenance_cycle_hours
    
    # 插入任务
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
    INSERT INTO maintenance_tasks (
        device_id, task_name, task_description, maintenance_cycle_hours,
        last_maintenance_hours, next_maintenance_hours, status, priority,
        operation_guide, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        task.device_id, task.task_name, task.task_description,
        task.maintenance_cycle_hours, task.last_maintenance_hours,
        next_maintenance_hours, task.status, task.priority,
        task.operation_guide, now, now
    )
    
    task_id = db.execute_insert(sql, params)
    
    return ApiResponse(
        code=200,
        message="保养任务创建成功",
        data={"id": task_id}
    )


@router.put("/tasks/{task_id}", response_model=ApiResponse)
async def update_maintenance_task(task_id: int, task: MaintenanceTaskUpdate):
    """
    更新保养任务信息
    """
    # 检查任务是否存在
    check_sql = "SELECT id, device_id FROM maintenance_tasks WHERE id = ?"
    existing = db.query_one(check_sql, (task_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="保养任务不存在")
    
    # 构建更新字段
    update_fields = []
    params = []
    
    task_dict = task.dict(exclude_unset=True)
    for key, value in task_dict.items():
        update_fields.append(f"{key} = ?")
        params.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    # 添加更新时间
    update_fields.append("updated_at = ?")
    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    params.append(task_id)
    
    sql = f"UPDATE maintenance_tasks SET {', '.join(update_fields)} WHERE id = ?"
    db.execute(sql, tuple(params))
    
    return ApiResponse(
        code=200,
        message="保养任务更新成功"
    )


@router.delete("/tasks/{task_id}", response_model=ApiResponse)
async def delete_maintenance_task(task_id: int):
    """
    删除保养任务
    """
    # 检查任务是否存在
    check_sql = "SELECT id FROM maintenance_tasks WHERE id = ?"
    existing = db.query_one(check_sql, (task_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="保养任务不存在")
    
    # 删除任务
    try:
        sql = "DELETE FROM maintenance_tasks WHERE id = ?"
        db.execute(sql, (task_id,))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")
    
    return ApiResponse(
        code=200,
        message="保养任务删除成功"
    )


@router.post("/tasks/generate", response_model=ApiResponse)
async def generate_maintenance_tasks(device_id: Optional[int] = None):
    """
    根据设备运行时长自动生成保养提醒
    
    如果指定device_id，则只检查该设备；否则检查所有设备
    """
    # 构建查询条件
    device_condition = ""
    params = []
    if device_id:
        device_condition = "AND d.id = ?"
        params.append(device_id)
    
    # 查询需要保养的设备
    sql = f"""
    SELECT 
        d.id as device_id,
        d.device_name,
        d.total_running_hours,
        mt.id as task_id,
        mt.task_name,
        mt.maintenance_cycle_hours,
        mt.last_maintenance_hours,
        mt.next_maintenance_hours,
        mt.status
    FROM devices d
    LEFT JOIN maintenance_tasks mt ON d.id = mt.device_id
    WHERE 1=1 {device_condition}
    ORDER BY d.id
    """
    
    devices = db.query_all(sql, tuple(params))
    
    generated_count = 0
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for device in devices:
        # 如果没有保养任务，跳过或创建默认任务
        if not device['task_id']:
            continue
        
        # 检查是否需要保养
        if device['total_running_hours'] >= device['next_maintenance_hours']:
            # 更新任务状态为pending或overdue
            if device['status'] == 'pending':
                # 已在待处理状态，更新为超期
                update_sql = """
                UPDATE maintenance_tasks 
                SET status = 'overdue', updated_at = ?
                WHERE id = ?
                """
                db.execute(update_sql, (now, device['task_id']))
                generated_count += 1
            elif device['status'] == 'completed':
                # 已完成，创建新的保养任务
                new_next_hours = device['last_maintenance_hours'] + device['maintenance_cycle_hours']
                insert_sql = """
                INSERT INTO maintenance_tasks (
                    device_id, task_name, task_description, maintenance_cycle_hours,
                    last_maintenance_hours, next_maintenance_hours, status, priority,
                    operation_guide, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'pending', 'medium', ?, ?, ?)
                """
                params = (
                    device['device_id'], device['task_name'],
                    f"设备运行时长已达{device['total_running_hours']}小时，需要保养",
                    device['maintenance_cycle_hours'],
                    device['next_maintenance_hours'],
                    device['next_maintenance_hours'] + device['maintenance_cycle_hours'],
                    '', now, now
                )
                db.execute_insert(insert_sql, params)
                generated_count += 1
    
    return ApiResponse(
        code=200,
        message=f"已生成/更新 {generated_count} 条保养提醒",
        data={"count": generated_count}
    )


# ==================== 保养记录相关接口 ====================

@router.get("/records", response_model=PaginatedResponse)
async def get_maintenance_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    device_id: Optional[int] = Query(None, description="设备ID"),
    operator_id: Optional[int] = Query(None, description="操作员ID")
):
    """
    获取保养记录列表（分页）
    """
    conditions = ["1=1"]
    params = []
    
    if device_id:
        conditions.append("mr.device_id = ?")
        params.append(device_id)
    
    if operator_id:
        conditions.append("mr.operator_id = ?")
        params.append(operator_id)
    
    where_clause = " AND ".join(conditions)
    sql = f"""
    SELECT mr.*, d.device_name, d.device_code, u.real_name as operator_name,
        mt.task_name
    FROM maintenance_records mr
    LEFT JOIN devices d ON mr.device_id = d.id
    LEFT JOIN users u ON mr.operator_id = u.id
    LEFT JOIN maintenance_tasks mt ON mr.task_id = mt.id
    WHERE {where_clause}
    ORDER BY mr.maintenance_date DESC
    """
    
    result = db.query_paginated(sql, tuple(params), page, page_size)
    
    return PaginatedResponse(
        code=200,
        message="success",
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages'],
        data={"items": result['items']}
    )


@router.get("/records/{record_id}", response_model=ApiResponse)
async def get_maintenance_record(record_id: int):
    """
    获取单个保养记录详情
    """
    sql = """
    SELECT mr.*, d.device_name, d.device_code, u.real_name as operator_name,
        mt.task_name, mt.operation_guide
    FROM maintenance_records mr
    LEFT JOIN devices d ON mr.device_id = d.id
    LEFT JOIN users u ON mr.operator_id = u.id
    LEFT JOIN maintenance_tasks mt ON mr.task_id = mt.id
    WHERE mr.id = ?
    """
    record = db.query_one(sql, (record_id,))
    
    if not record:
        raise HTTPException(status_code=404, detail="保养记录不存在")
    
    return ApiResponse(
        code=200,
        message="success",
        data=record
    )


@router.post("/records", response_model=ApiResponse)
async def create_maintenance_record(record: MaintenanceRecordCreate):
    """
    创建保养记录
    
    保养完成后提交，会更新相关任务状态和设备信息
    """
    # 检查任务是否存在
    check_task_sql = "SELECT id, device_id FROM maintenance_tasks WHERE id = ?"
    task = db.query_one(check_task_sql, (record.task_id,))
    
    if not task:
        raise HTTPException(status_code=400, detail="保养任务不存在")
    
    # 检查设备是否存在
    check_device_sql = "SELECT id, total_running_hours FROM devices WHERE id = ?"
    device = db.query_one(check_device_sql, (record.device_id,))
    
    if not device:
        raise HTTPException(status_code=400, detail="设备不存在")
    
    # 检查操作员是否存在
    check_user_sql = "SELECT id FROM users WHERE id = ?"
    user = db.query_one(check_user_sql, (record.operator_id,))
    
    if not user:
        raise HTTPException(status_code=400, detail="操作员不存在")
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 插入保养记录
    record_sql = """
    INSERT INTO maintenance_records (
        task_id, device_id, operator_id, maintenance_date,
        maintenance_content, maintenance_result, remark, photo_urls, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        record.task_id, record.device_id, record.operator_id,
        now, record.maintenance_content, record.maintenance_result,
        record.remark, record.photo_urls, now
    )
    
    record_id = db.execute_insert(record_sql, params)
    
    # 更新保养任务状态
    update_task_sql = """
    UPDATE maintenance_tasks 
    SET status = 'completed', 
        last_maintenance_hours = ?,
        next_maintenance_hours = ? + maintenance_cycle_hours,
        updated_at = ?
    WHERE id = ?
    """
    
    current_hours = device['total_running_hours']
    db.execute(update_task_sql, (current_hours, current_hours, now, record.task_id))
    
    # 更新设备的最后保养日期
    update_device_sql = """
    UPDATE devices 
    SET last_maintenance_date = date(?),
        next_maintenance_date = date(?, '+3 months'),
        updated_at = ?
    WHERE id = ?
    """
    db.execute(update_device_sql, (now, now, now, record.device_id))
    
    return ApiResponse(
        code=200,
        message="保养记录创建成功",
        data={"id": record_id}
    )


@router.get("/overview/stats", response_model=ApiResponse)
async def get_maintenance_overview():
    """
    获取保养任务统计概览
    """
    # 统计各状态任务数量
    sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
        SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) as overdue_count,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
        SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority_count
    FROM maintenance_tasks
    """
    
    stats = db.query_one(sql)
    
    # 获取即将到期的任务（运行时长接近下次保养时长的80%）
    upcoming_sql = """
    SELECT mt.*, d.device_name, d.device_code, d.total_running_hours
    FROM maintenance_tasks mt
    LEFT JOIN devices d ON mt.device_id = d.id
    WHERE mt.status IN ('pending', 'overdue')
        AND d.total_running_hours >= (mt.next_maintenance_hours * 0.8)
    ORDER BY 
        CASE mt.status WHEN 'overdue' THEN 1 ELSE 2 END,
        (d.total_running_hours / mt.next_maintenance_hours) DESC
    LIMIT 10
    """
    
    upcoming_tasks = db.query_all(upcoming_sql)
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "statistics": stats,
            "upcoming_tasks": upcoming_tasks
        }
    )

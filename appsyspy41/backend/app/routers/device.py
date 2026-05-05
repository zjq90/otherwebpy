"""
设备管理路由
提供设备相关的API接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.database.connection import db
from app.models.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    DeviceStatus, ApiResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/devices", tags=["设备管理"])


@router.get("/", response_model=PaginatedResponse)
async def get_devices(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    device_type: Optional[str] = Query(None, description="设备类型"),
    status: Optional[str] = Query(None, description="设备状态"),
    keyword: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取设备列表（分页）
    
    支持按设备类型、状态和关键词筛选
    """
    # 构建查询条件
    conditions = ["1=1"]
    params = []
    
    if device_type:
        conditions.append("device_type = ?")
        params.append(device_type)
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    if keyword:
        conditions.append("(device_code LIKE ? OR device_name LIKE ? OR location LIKE ?)")
        keyword_param = f"%{keyword}%"
        params.extend([keyword_param, keyword_param, keyword_param])
    
    where_clause = " AND ".join(conditions)
    sql = f"SELECT * FROM devices WHERE {where_clause} ORDER BY id DESC"
    
    # 分页查询
    result = db.query_paginated(sql, tuple(params), page, page_size)
    
    # 为每个设备添加当前状态
    for item in result['items']:
        # 获取最新状态
        status_sql = """
        SELECT * FROM device_status_history 
        WHERE device_id = ? 
        ORDER BY recorded_at DESC 
        LIMIT 1
        """
        latest_status = db.query_one(status_sql, (item['id'],))
        if latest_status:
            item['current_status'] = DeviceStatus(**latest_status).dict()
        else:
            item['current_status'] = None
    
    return PaginatedResponse(
        code=200,
        message="success",
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages'],
        data={"items": result['items']}
    )


@router.get("/{device_id}", response_model=ApiResponse)
async def get_device(device_id: int):
    """
    获取单个设备详情
    
    包括设备基本信息和最新运行状态
    """
    # 查询设备信息
    sql = "SELECT * FROM devices WHERE id = ?"
    device = db.query_one(sql, (device_id,))
    
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 获取最新状态
    status_sql = """
    SELECT * FROM device_status_history 
    WHERE device_id = ? 
    ORDER BY recorded_at DESC 
    LIMIT 1
    """
    latest_status = db.query_one(status_sql, (device_id,))
    
    device_dict = dict(device)
    if latest_status:
        device_dict['current_status'] = DeviceStatus(**latest_status).dict()
    
    return ApiResponse(
        code=200,
        message="success",
        data=device_dict
    )


@router.post("/", response_model=ApiResponse)
async def create_device(device: DeviceCreate):
    """
    创建设备
    
    设备编号必须唯一
    """
    # 检查设备编号是否已存在
    check_sql = "SELECT id FROM devices WHERE device_code = ?"
    existing = db.query_one(check_sql, (device.device_code,))
    
    if existing:
        raise HTTPException(status_code=400, detail="设备编号已存在")
    
    # 插入设备
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
    INSERT INTO devices (
        device_code, device_name, device_type, location, install_date,
        specification, manufacturer, status, total_running_hours,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        device.device_code, device.device_name, device.device_type,
        device.location, device.install_date,
        device.specification, device.manufacturer, device.status,
        device.total_running_hours, now, now
    )
    
    device_id = db.execute_insert(sql, params)
    
    return ApiResponse(
        code=200,
        message="设备创建成功",
        data={"id": device_id}
    )


@router.put("/{device_id}", response_model=ApiResponse)
async def update_device(device_id: int, device: DeviceUpdate):
    """
    更新设备信息
    """
    # 检查设备是否存在
    check_sql = "SELECT id FROM devices WHERE id = ?"
    existing = db.query_one(check_sql, (device_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 构建更新字段
    update_fields = []
    params = []
    
    device_dict = device.dict(exclude_unset=True)
    for key, value in device_dict.items():
        update_fields.append(f"{key} = ?")
        params.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    # 添加更新时间
    update_fields.append("updated_at = ?")
    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    params.append(device_id)
    
    sql = f"UPDATE devices SET {', '.join(update_fields)} WHERE id = ?"
    db.execute(sql, tuple(params))
    
    return ApiResponse(
        code=200,
        message="设备更新成功"
    )


@router.delete("/{device_id}", response_model=ApiResponse)
async def delete_device(device_id: int):
    """
    删除设备
    
    注意：有外键关联的设备无法直接删除
    """
    # 检查设备是否存在
    check_sql = "SELECT id FROM devices WHERE id = ?"
    existing = db.query_one(check_sql, (device_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 删除设备
    try:
        sql = "DELETE FROM devices WHERE id = ?"
        db.execute(sql, (device_id,))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")
    
    return ApiResponse(
        code=200,
        message="设备删除成功"
    )


@router.get("/{device_id}/status-history", response_model=PaginatedResponse)
async def get_device_status_history(
    device_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间")
):
    """
    获取设备状态历史记录（分页）
    """
    # 检查设备是否存在
    check_sql = "SELECT id FROM devices WHERE id = ?"
    existing = db.query_one(check_sql, (device_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 构建查询条件
    conditions = ["device_id = ?"]
    params = [device_id]
    
    if start_time:
        conditions.append("recorded_at >= ?")
        params.append(start_time)
    
    if end_time:
        conditions.append("recorded_at <= ?")
        params.append(end_time)
    
    where_clause = " AND ".join(conditions)
    sql = f"SELECT * FROM device_status_history WHERE {where_clause} ORDER BY recorded_at DESC"
    
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


@router.post("/{device_id}/status", response_model=ApiResponse)
async def add_device_status(device_id: int, status: DeviceStatus):
    """
    上报设备状态数据
    
    用于传感器或设备主动上报运行状态
    """
    # 检查设备是否存在
    check_sql = "SELECT id FROM devices WHERE id = ?"
    existing = db.query_one(check_sql, (device_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 插入状态记录
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
    INSERT INTO device_status_history (
        device_id, current, temperature, voltage, power,
        running_hours, status, alarm_level, recorded_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        device_id, status.current, status.temperature,
        status.voltage, status.power, status.running_hours,
        status.status, status.alarm_level, now
    )
    
    record_id = db.execute_insert(sql, params)
    
    # 更新设备的运行时长和状态
    update_sql = """
    UPDATE devices SET 
        total_running_hours = ?,
        status = ?,
        updated_at = ?
    WHERE id = ?
    """
    db.execute(update_sql, (status.running_hours or 0, status.status, now, device_id))
    
    return ApiResponse(
        code=200,
        message="状态上报成功",
        data={"id": record_id}
    )


@router.get("/overview/summary", response_model=ApiResponse)
async def get_device_overview():
    """
    获取设备概览统计
    
    用于首页展示设备统计信息
    """
    # 统计各类设备数量
    sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'normal' THEN 1 ELSE 0 END) as normal_count,
        SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warning_count,
        SUM(CASE WHEN status = 'fault' THEN 1 ELSE 0 END) as fault_count,
        SUM(CASE WHEN device_type = 'mixer' THEN 1 ELSE 0 END) as mixer_count,
        SUM(CASE WHEN device_type = 'belt_scale' THEN 1 ELSE 0 END) as belt_scale_count,
        SUM(CASE WHEN device_type = 'compressor' THEN 1 ELSE 0 END) as compressor_count
    FROM devices
    """
    
    stats = db.query_one(sql)
    
    # 获取故障设备列表
    fault_sql = """
    SELECT d.*, 
        (SELECT s.status FROM device_status_history s 
         WHERE s.device_id = d.id ORDER BY s.recorded_at DESC LIMIT 1) as current_status
    FROM devices d WHERE d.status IN ('warning', 'fault')
    ORDER BY 
        CASE d.status WHEN 'fault' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,
        d.id
    """
    
    fault_devices = db.query_all(fault_sql)
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "statistics": stats,
            "fault_devices": fault_devices
        }
    )

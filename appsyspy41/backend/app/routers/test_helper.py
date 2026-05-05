"""
测试辅助功能模块
提供系统功能测试的辅助接口
"""

import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database.connection import db
from app.models.schemas import ApiResponse

router = APIRouter(prefix="/api/test", tags=["测试辅助"])


@router.post("/reset-database", response_model=ApiResponse)
async def reset_database():
    """
    重置数据库
    
    警告：此操作将清空所有数据并重新初始化
    仅用于开发测试环境
    """
    try:
        from app.database.init_db import init_database
        
        # 删除现有数据库
        import os
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'device_management.db')
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # 重新初始化
        init_database()
        
        return ApiResponse(
            code=200,
            message="数据库重置成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置失败: {str(e)}")


@router.post("/generate-device-status", response_model=ApiResponse)
async def generate_device_status(
    device_id: Optional[int] = Query(None, description="设备ID，不指定则为所有设备"),
    count: int = Query(24, ge=1, le=100, description="生成数据条数")
):
    """
    生成设备状态测试数据
    
    用于模拟设备实时状态上报
    """
    # 获取设备列表
    if device_id:
        devices = db.query_all("SELECT id, device_name, total_running_hours FROM devices WHERE id = ?", (device_id,))
    else:
        devices = db.query_all("SELECT id, device_name, total_running_hours FROM devices")
    
    if not devices:
        raise HTTPException(status_code=404, detail="没有找到设备")
    
    now = datetime.now()
    generated_count = 0
    
    for device in devices:
        base_current = 100 + device['id'] * 10
        base_temp = 35 + device['id'] * 2
        
        for i in range(count):
            # 生成随机波动
            current = round(base_current + random.uniform(-10, 10), 2)
            temperature = round(base_temp + random.uniform(-5, 8), 1)
            voltage = 380 + random.uniform(-5, 5)
            power = round(current * voltage * 0.85 / 1000, 2)
            running_hours = device['total_running_hours'] + (i / 24)
            
            # 随机生成状态（主要是normal，偶尔warning，少量fault）
            rand = random.random()
            if rand < 0.92:
                status = 'normal'
                alarm_level = 'none'
            elif rand < 0.97:
                status = 'warning'
                alarm_level = 'medium'
                temperature = round(temperature + 10, 1)
            else:
                status = 'fault'
                alarm_level = 'high'
                temperature = round(temperature + 20, 1)
                current = round(current + 30, 2)
            
            recorded_at = (now - timedelta(hours=count - i)).strftime('%Y-%m-%d %H:%M:%S')
            
            sql = """
            INSERT INTO device_status_history (
                device_id, current, temperature, voltage, power,
                running_hours, status, alarm_level, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db.execute_insert(sql, (
                device['id'], current, temperature, voltage, power,
                running_hours, status, alarm_level, recorded_at
            ))
            
            generated_count += 1
    
    return ApiResponse(
        code=200,
        message=f"成功生成 {generated_count} 条设备状态数据",
        data={"count": generated_count}
    )


@router.post("/generate-fault-alarm", response_model=ApiResponse)
async def generate_fault_alarm(
    device_id: int,
    fault_type: str = Query("temperature", description="故障类型: temperature/current/general")
):
    """
    模拟设备故障报警
    
    用于测试故障报警功能
    """
    # 检查设备是否存在
    device = db.query_one("SELECT id, device_name, status FROM devices WHERE id = ?", (device_id,))
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 根据故障类型生成不同的数据
    if fault_type == "temperature":
        current = round(120 + device_id * 10 + random.uniform(-5, 5), 2)
        temperature = round(95 + random.uniform(0, 10), 1)
        status = 'fault'
        alarm_level = 'high'
    elif fault_type == "current":
        current = round(200 + random.uniform(0, 50), 2)
        temperature = round(45 + random.uniform(0, 5), 1)
        status = 'fault'
        alarm_level = 'high'
    else:
        current = round(120 + device_id * 10, 2)
        temperature = round(50 + random.uniform(0, 5), 1)
        status = 'warning'
        alarm_level = 'medium'
    
    # 插入状态记录
    sql = """
    INSERT INTO device_status_history (
        device_id, current, temperature, voltage, power,
        running_hours, status, alarm_level, recorded_at
    ) VALUES (?, ?, ?, 380, ?, 1500 + ?, ?, ?, ?)
    """
    power = round(current * 380 * 0.85 / 1000, 2)
    
    db.execute_insert(sql, (
        device_id, current, temperature, power,
        device_id * 10, status, alarm_level, now
    ))
    
    # 更新设备状态
    update_sql = """
    UPDATE devices SET status = ?, updated_at = ? WHERE id = ?
    """
    db.execute(update_sql, (status, now, device_id))
    
    return ApiResponse(
        code=200,
        message=f"设备 {device['device_name']} 已触发{status}报警",
        data={
            "device_id": device_id,
            "device_name": device['device_name'],
            "status": status,
            "alarm_level": alarm_level,
            "current": current,
            "temperature": temperature
        }
    )


@router.get("/dashboard-overview", response_model=ApiResponse)
async def get_dashboard_overview():
    """
    获取首页仪表盘数据
    
    聚合所有模块的统计数据，用于首页展示
    """
    # 设备统计
    device_stats = db.query_one("""
    SELECT 
        COUNT(*) as total_devices,
        SUM(CASE WHEN status = 'normal' THEN 1 ELSE 0 END) as normal_devices,
        SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warning_devices,
        SUM(CASE WHEN status = 'fault' THEN 1 ELSE 0 END) as fault_devices,
        SUM(CASE WHEN device_type = 'mixer' THEN 1 ELSE 0 END) as mixer_count,
        SUM(CASE WHEN device_type = 'belt_scale' THEN 1 ELSE 0 END) as belt_scale_count,
        SUM(CASE WHEN device_type = 'compressor' THEN 1 ELSE 0 END) as compressor_count
    FROM devices
    """)
    
    # 保养任务统计
    maintenance_stats = db.query_one("""
    SELECT 
        COUNT(*) as total_tasks,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
        SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) as overdue_tasks,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
        SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority_tasks
    FROM maintenance_tasks
    """)
    
    # 故障报修统计
    fault_stats = db.query_one("""
    SELECT 
        COUNT(*) as total_reports,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_reports,
        SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_reports,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_reports,
        SUM(CASE WHEN fault_level = 'high' THEN 1 ELSE 0 END) as high_level_reports
    FROM fault_reports
    """)
    
    # 获取故障设备列表
    fault_devices = db.query_all("""
    SELECT d.*,
        (SELECT s.temperature FROM device_status_history s 
         WHERE s.device_id = d.id ORDER BY s.recorded_at DESC LIMIT 1) as current_temp,
        (SELECT s.current FROM device_status_history s 
         WHERE s.device_id = d.id ORDER BY s.recorded_at DESC LIMIT 1) as current_current
    FROM devices d WHERE d.status IN ('warning', 'fault')
    ORDER BY 
        CASE d.status WHEN 'fault' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,
        d.id
    LIMIT 10
    """)
    
    # 获取待处理保养任务
    pending_maintenance = db.query_all("""
    SELECT mt.*, d.device_name, d.device_code, d.total_running_hours
    FROM maintenance_tasks mt
    LEFT JOIN devices d ON mt.device_id = d.id
    WHERE mt.status IN ('pending', 'overdue')
    ORDER BY 
        CASE mt.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        CASE mt.status WHEN 'overdue' THEN 1 ELSE 2 END
    LIMIT 5
    """)
    
    # 获取待处理故障报修
    pending_faults = db.query_all("""
    SELECT fr.*, d.device_name, d.device_code, u.real_name as reporter_name
    FROM fault_reports fr
    LEFT JOIN devices d ON fr.device_id = d.id
    LEFT JOIN users u ON fr.reporter_id = u.id
    WHERE fr.status IN ('pending', 'processing')
    ORDER BY 
        CASE fr.fault_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        fr.created_at ASC
    LIMIT 5
    """)
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "device_stats": device_stats,
            "maintenance_stats": maintenance_stats,
            "fault_stats": fault_stats,
            "fault_devices": fault_devices,
            "pending_maintenance": pending_maintenance,
            "pending_faults": pending_faults
        }
    )


@router.get("/quick-stats", response_model=ApiResponse)
async def get_quick_stats():
    """
    获取快速统计数据
    
    用于首页顶部卡片展示
    """
    # 设备统计
    device_sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'normal' THEN 1 ELSE 0 END) as normal,
        SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warning,
        SUM(CASE WHEN status = 'fault' THEN 1 ELSE 0 END) as fault
    FROM devices
    """
    device_stats = db.query_one(device_sql)
    
    # 保养统计
    maintenance_sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) as overdue,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
    FROM maintenance_tasks
    """
    maintenance_stats = db.query_one(maintenance_sql)
    
    # 故障统计
    fault_sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
    FROM fault_reports
    """
    fault_stats = db.query_one(fault_sql)
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "devices": device_stats,
            "maintenance": maintenance_stats,
            "faults": fault_stats
        }
    )


@router.post("/clear-test-data", response_model=ApiResponse)
async def clear_test_data():
    """
    清除测试数据
    
    保留初始化的基础数据，清除测试生成的数据
    """
    try:
        # 清除状态历史（保留前100条初始化数据）
        db.execute("""
        DELETE FROM device_status_history 
        WHERE id NOT IN (SELECT id FROM device_status_history ORDER BY id LIMIT 100)
        """)
        
        # 清除测试生成的保养任务（保留基础任务）
        # 这里简单处理，实际可以根据创建时间等条件筛选
        
        return ApiResponse(
            code=200,
            message="测试数据已清除"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除失败: {str(e)}")

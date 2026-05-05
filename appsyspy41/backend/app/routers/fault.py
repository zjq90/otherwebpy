"""
故障报修处理路由
提供故障报修和维修记录相关的API接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.database.connection import db
from app.models.schemas import (
    FaultReportCreate, FaultReportUpdate, FaultReportResponse,
    RepairRecordCreate, RepairRecordResponse,
    ApiResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/fault", tags=["故障管理"])


# ==================== 故障报修相关接口 ====================

@router.get("/reports", response_model=PaginatedResponse)
async def get_fault_reports(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    device_id: Optional[int] = Query(None, description="设备ID"),
    reporter_id: Optional[int] = Query(None, description="上报人ID"),
    assigned_to: Optional[int] = Query(None, description="维修人员ID"),
    status: Optional[str] = Query(None, description="报修状态"),
    fault_level: Optional[str] = Query(None, description="故障级别")
):
    """
    获取故障报修列表（分页）
    
    支持按设备ID、上报人、维修人员、状态和故障级别筛选
    """
    conditions = ["1=1"]
    params = []
    
    if device_id:
        conditions.append("fr.device_id = ?")
        params.append(device_id)
    
    if reporter_id:
        conditions.append("fr.reporter_id = ?")
        params.append(reporter_id)
    
    if assigned_to:
        conditions.append("fr.assigned_to = ?")
        params.append(assigned_to)
    
    if status:
        conditions.append("fr.status = ?")
        params.append(status)
    
    if fault_level:
        conditions.append("fr.fault_level = ?")
        params.append(fault_level)
    
    where_clause = " AND ".join(conditions)
    sql = f"""
    SELECT fr.*, 
        d.device_name, d.device_code,
        u1.real_name as reporter_name,
        u2.real_name as assignee_name
    FROM fault_reports fr
    LEFT JOIN devices d ON fr.device_id = d.id
    LEFT JOIN users u1 ON fr.reporter_id = u1.id
    LEFT JOIN users u2 ON fr.assigned_to = u2.id
    WHERE {where_clause}
    ORDER BY 
        CASE fr.fault_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        CASE fr.status 
            WHEN 'pending' THEN 1 
            WHEN 'processing' THEN 2 
            WHEN 'completed' THEN 3 
            ELSE 4 
        END,
        fr.created_at DESC
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


@router.get("/reports/{report_id}", response_model=ApiResponse)
async def get_fault_report(report_id: int):
    """
    获取单个故障报修详情
    
    包含报修信息、设备信息、上报人信息和维修记录
    """
    sql = """
    SELECT fr.*, 
        d.device_name, d.device_code, d.location,
        u1.real_name as reporter_name, u1.phone as reporter_phone,
        u2.real_name as assignee_name, u2.phone as assignee_phone
    FROM fault_reports fr
    LEFT JOIN devices d ON fr.device_id = d.id
    LEFT JOIN users u1 ON fr.reporter_id = u1.id
    LEFT JOIN users u2 ON fr.assigned_to = u2.id
    WHERE fr.id = ?
    """
    report = db.query_one(sql, (report_id,))
    
    if not report:
        raise HTTPException(status_code=404, detail="故障报修不存在")
    
    # 获取维修记录
    records_sql = """
    SELECT rr.*, u.real_name as operator_name
    FROM repair_records rr
    LEFT JOIN users u ON rr.operator_id = u.id
    WHERE rr.report_id = ?
    ORDER BY rr.created_at ASC
    """
    repair_records = db.query_all(records_sql, (report_id,))
    
    result = dict(report)
    result['repair_records'] = repair_records
    
    return ApiResponse(
        code=200,
        message="success",
        data=result
    )


@router.post("/reports", response_model=ApiResponse)
async def create_fault_report(report: FaultReportCreate, reporter_id: int):
    """
    提交故障报修申请
    
    操作员发现设备故障后提交报修申请
    """
    # 检查设备是否存在
    check_sql = "SELECT id, device_name FROM devices WHERE id = ?"
    device = db.query_one(check_sql, (report.device_id,))
    
    if not device:
        raise HTTPException(status_code=400, detail="设备不存在")
    
    # 检查上报人是否存在
    check_user_sql = "SELECT id FROM users WHERE id = ?"
    user = db.query_one(check_user_sql, (reporter_id,))
    
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    # 插入报修记录
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
    INSERT INTO fault_reports (
        device_id, reporter_id, fault_title, fault_description,
        fault_level, photo_urls, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
    """
    
    params = (
        report.device_id, reporter_id, report.fault_title,
        report.fault_description, report.fault_level,
        report.photo_urls, now, now
    )
    
    report_id = db.execute_insert(sql, params)
    
    # 更新设备状态为故障
    update_device_sql = """
    UPDATE devices SET status = 'fault', updated_at = ? WHERE id = ?
    """
    db.execute(update_device_sql, (now, report.device_id))
    
    return ApiResponse(
        code=200,
        message="故障报修提交成功",
        data={"id": report_id}
    )


@router.put("/reports/{report_id}", response_model=ApiResponse)
async def update_fault_report(report_id: int, report: FaultReportUpdate):
    """
    更新故障报修信息
    
    可用于更新状态、分配维修人员等
    """
    # 检查报修是否存在
    check_sql = "SELECT id, device_id FROM fault_reports WHERE id = ?"
    existing = db.query_one(check_sql, (report_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="故障报修不存在")
    
    # 构建更新字段
    update_fields = []
    params = []
    
    report_dict = report.dict(exclude_unset=True)
    for key, value in report_dict.items():
        update_fields.append(f"{key} = ?")
        params.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    # 添加更新时间
    update_fields.append("updated_at = ?")
    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    params.append(report_id)
    
    sql = f"UPDATE fault_reports SET {', '.join(update_fields)} WHERE id = ?"
    db.execute(sql, tuple(params))
    
    return ApiResponse(
        code=200,
        message="故障报修更新成功"
    )


@router.post("/reports/{report_id}/assign", response_model=ApiResponse)
async def assign_fault_report(report_id: int, repair_user_id: int):
    """
    分配故障报修给维修人员
    
    系统自动派单或管理员手动分配
    """
    # 检查报修是否存在
    check_sql = "SELECT id, status, device_id FROM fault_reports WHERE id = ?"
    report = db.query_one(check_sql, (report_id,))
    
    if not report:
        raise HTTPException(status_code=404, detail="故障报修不存在")
    
    # 检查维修人员是否存在且是维修角色
    check_user_sql = "SELECT id, real_name, role FROM users WHERE id = ?"
    user = db.query_one(check_user_sql, (repair_user_id,))
    
    if not user:
        raise HTTPException(status_code=400, detail="维修人员不存在")
    
    # 更新报修状态
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_sql = """
    UPDATE fault_reports 
    SET assigned_to = ?, status = 'processing', updated_at = ?
    WHERE id = ?
    """
    db.execute(update_sql, (repair_user_id, now, report_id))
    
    # 添加维修记录
    record_sql = """
    INSERT INTO repair_records (
        report_id, operator_id, action, description, progress, created_at
    ) VALUES (?, ?, 'assigned', ?, 10, ?)
    """
    description = f"工单已分配给{user['real_name']}进行处理"
    db.execute_insert(record_sql, (report_id, repair_user_id, description, now))
    
    return ApiResponse(
        code=200,
        message=f"工单已分配给{user['real_name']}"
    )


@router.post("/reports/{report_id}/complete", response_model=ApiResponse)
async def complete_fault_report(report_id: int, operator_id: int):
    """
    完成故障报修
    
    维修完成后由申请人确认验收
    """
    # 检查报修是否存在
    check_sql = "SELECT id, status, device_id FROM fault_reports WHERE id = ?"
    report = db.query_one(check_sql, (report_id,))
    
    if not report:
        raise HTTPException(status_code=404, detail="故障报修不存在")
    
    # 更新报修状态
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_sql = """
    UPDATE fault_reports 
    SET status = 'completed', updated_at = ?
    WHERE id = ?
    """
    db.execute(update_sql, (now, report_id))
    
    # 添加维修记录
    record_sql = """
    INSERT INTO repair_records (
        report_id, operator_id, action, description, progress, created_at
    ) VALUES (?, ?, 'completed', ?, 100, ?)
    """
    description = "维修完成，已验收通过"
    db.execute_insert(record_sql, (report_id, operator_id, description, now))
    
    # 更新设备状态为正常
    update_device_sql = """
    UPDATE devices SET status = 'normal', updated_at = ? WHERE id = ?
    """
    db.execute(update_device_sql, (now, report['device_id']))
    
    return ApiResponse(
        code=200,
        message="故障报修已完成，设备状态恢复正常"
    )


@router.delete("/reports/{report_id}", response_model=ApiResponse)
async def delete_fault_report(report_id: int):
    """
    删除故障报修
    """
    # 检查报修是否存在
    check_sql = "SELECT id FROM fault_reports WHERE id = ?"
    existing = db.query_one(check_sql, (report_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="故障报修不存在")
    
    # 删除报修
    try:
        # 先删除维修记录
        delete_records_sql = "DELETE FROM repair_records WHERE report_id = ?"
        db.execute(delete_records_sql, (report_id,))
        
        # 删除报修
        sql = "DELETE FROM fault_reports WHERE id = ?"
        db.execute(sql, (report_id,))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除失败: {str(e)}")
    
    return ApiResponse(
        code=200,
        message="故障报修删除成功"
    )


# ==================== 维修记录相关接口 ====================

@router.get("/records", response_model=PaginatedResponse)
async def get_repair_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    report_id: Optional[int] = Query(None, description="报修单ID"),
    operator_id: Optional[int] = Query(None, description="操作员ID")
):
    """
    获取维修记录列表（分页）
    """
    conditions = ["1=1"]
    params = []
    
    if report_id:
        conditions.append("rr.report_id = ?")
        params.append(report_id)
    
    if operator_id:
        conditions.append("rr.operator_id = ?")
        params.append(operator_id)
    
    where_clause = " AND ".join(conditions)
    sql = f"""
    SELECT rr.*, 
        u.real_name as operator_name,
        fr.fault_title, d.device_name
    FROM repair_records rr
    LEFT JOIN users u ON rr.operator_id = u.id
    LEFT JOIN fault_reports fr ON rr.report_id = fr.id
    LEFT JOIN devices d ON fr.device_id = d.id
    WHERE {where_clause}
    ORDER BY rr.created_at DESC
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


@router.post("/records", response_model=ApiResponse)
async def create_repair_record(record: RepairRecordCreate):
    """
    创建维修记录
    
    维修人员可实时更新维修进度
    """
    # 检查报修是否存在
    check_sql = "SELECT id FROM fault_reports WHERE id = ?"
    report = db.query_one(check_sql, (record.report_id,))
    
    if not report:
        raise HTTPException(status_code=400, detail="故障报修不存在")
    
    # 检查操作员是否存在
    check_user_sql = "SELECT id FROM users WHERE id = ?"
    user = db.query_one(check_user_sql, (record.operator_id,))
    
    if not user:
        raise HTTPException(status_code=400, detail="操作员不存在")
    
    # 插入维修记录
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
    INSERT INTO repair_records (
        report_id, operator_id, action, description,
        progress, photo_urls, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        record.report_id, record.operator_id, record.action,
        record.description, record.progress, record.photo_urls, now
    )
    
    record_id = db.execute_insert(sql, params)
    
    return ApiResponse(
        code=200,
        message="维修记录创建成功",
        data={"id": record_id}
    )


@router.get("/overview/stats", response_model=ApiResponse)
async def get_fault_overview():
    """
    获取故障报修统计概览
    """
    # 统计各状态报修数量
    sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
        SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_count,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
        SUM(CASE WHEN fault_level = 'high' THEN 1 ELSE 0 END) as high_level_count
    FROM fault_reports
    """
    
    stats = db.query_one(sql)
    
    # 获取待处理的报修
    pending_sql = """
    SELECT fr.*, d.device_name, d.device_code, u.real_name as reporter_name
    FROM fault_reports fr
    LEFT JOIN devices d ON fr.device_id = d.id
    LEFT JOIN users u ON fr.reporter_id = u.id
    WHERE fr.status IN ('pending', 'processing')
    ORDER BY 
        CASE fr.fault_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        fr.created_at ASC
    LIMIT 10
    """
    
    pending_reports = db.query_all(pending_sql)
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "statistics": stats,
            "pending_reports": pending_reports
        }
    )

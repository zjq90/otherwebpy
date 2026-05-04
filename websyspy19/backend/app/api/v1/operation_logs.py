"""
操作日志相关API路由
处理操作日志的查询、统计、删除等
"""

from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.operation_log import operation_log_crud
from app.models.user import User
from app.schemas.operation_log import OperationLogQuery, OperationLogResponse
from app.schemas.common import ResponseModel, PaginatedResponse, SuccessResponse
from app.middleware.auth_middleware import require_permission


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[dict], summary="获取操作日志列表")
def get_operation_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="操作用户�?),
    operation_type: Optional[str] = Query(None, description="操作类型"),
    module: Optional[str] = Query(None, description="所属模�?),
    status: Optional[str] = Query(None, description="操作状�?),
    start_time: Optional[datetime] = Query(None, description="开始时�?),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: User = Depends(require_permission("log:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    分页获取操作日志列表
    
    需�?`log:read` 权限
    
    参数:
        page: 页码
        page_size: 每页数量
        username: 操作用户名筛�?
        operation_type: 操作类型筛�?
        module: 所属模块筛�?
        status: 操作状态筛�?
        start_time: 开始时�?
        end_time: 结束时间
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        分页的操作日志列�?
    """
    # 构建查询参数
    query_params = OperationLogQuery(
        page=page,
        page_size=page_size,
        username=username,
        operation_type=operation_type,
        module=module,
        status=status,
        start_time=start_time,
        end_time=end_time
    )
    
    # 获取操作日志列表
    logs, total = operation_log_crud.get_multi(db, query_params=query_params)
    
    # 构建响应数据
    log_data = []
    for log in logs:
        log_data.append({
            "id": log.id,
            "operation_type": log.operation_type,
            "operation_name": log.operation_name,
            "operation_desc": log.operation_desc,
            "request_method": log.request_method,
            "request_url": log.request_url,
            "request_ip": log.request_ip,
            "user_id": log.user_id,
            "username": log.username,
            "module": log.module,
            "status": log.status,
            "error_message": log.error_message,
            "duration": log.duration,
            "created_at": log.created_at
        })
    
    # 计算总页�?
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return PaginatedResponse(
        code=200,
        message="获取成功",
        data=log_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{log_id}", response_model=ResponseModel[OperationLogResponse], summary="获取操作日志详情")
def get_operation_log(
    log_id: int,
    current_user: User = Depends(require_permission("log:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单个操作日志的详细信�?
    
    需�?`log:read` 权限
    
    参数:
        log_id: 日志ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        操作日志详细信息
    """
    # 获取操作日志
    log = operation_log_crud.get_by_id(db, log_id=log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="操作日志不存�?
        )
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=log
    )


@router.get("/statistics", response_model=ResponseModel[dict], summary="获取操作日志统计")
def get_log_statistics(
    start_time: Optional[datetime] = Query(None, description="开始时�?),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: User = Depends(require_permission("log:read")),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取操作日志统计信息
    
    需�?`log:read` 权限
    
    参数:
        start_time: 开始时�?
        end_time: 结束时间
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        统计信息
    """
    # 获取统计信息
    stats = operation_log_crud.get_statistics(db, start_time=start_time, end_time=end_time)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=stats
    )


@router.delete("/{log_id}", response_model=SuccessResponse, summary="删除操作日志")
def delete_operation_log(
    log_id: int,
    current_user: User = Depends(require_permission("log:delete")),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除单个操作日志
    
    需�?`log:delete` 权限
    
    参数:
        log_id: 日志ID
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        成功响应
    """
    # 获取操作日志
    log = operation_log_crud.get_by_id(db, log_id=log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="操作日志不存�?
        )
    
    # 删除操作日志
    operation_log_crud.remove(db, log_id=log_id)
    
    return SuccessResponse(
        code=200,
        message="删除成功"
    )


@router.post("/batch-delete", response_model=ResponseModel[dict], summary="批量删除操作日志")
def batch_delete_operation_logs(
    log_ids: List[int],
    current_user: User = Depends(require_permission("log:delete")),
    db: Session = Depends(get_db)
) -> Any:
    """
    批量删除操作日志
    
    需�?`log:delete` 权限
    
    参数:
        log_ids: 日志ID列表
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        删除结果
    """
    # 批量删除
    count = operation_log_crud.batch_remove(db, log_ids=log_ids)
    
    return ResponseModel(
        code=200,
        message=f"成功删除 {count} 条记�?,
        data={"deleted_count": count}
    )


@router.post("/cleanup-old", response_model=ResponseModel[dict], summary="清理旧操作日�?)
def cleanup_old_logs(
    days: int = Query(30, ge=1, description="保留天数，默�?0�?),
    current_user: User = Depends(require_permission("log:delete")),
    db: Session = Depends(get_db)
) -> Any:
    """
    清理指定天数之前的旧操作日志
    
    需�?`log:delete` 权限
    
    参数:
        days: 保留天数
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        清理结果
    """
    # 清理旧日�?
    count = operation_log_crud.cleanup_old_logs(db, days=days)
    
    return ResponseModel(
        code=200,
        message=f"成功清理 {days} 天前的旧日志，共删除 {count} 条记�?,
        data={"deleted_count": count, "days": days}
    )

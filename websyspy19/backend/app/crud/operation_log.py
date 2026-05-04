"""
操作日志数据访问�?
封装操作日志相关的数据库增删改查操作
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogCreate, OperationLogQuery


class CRUDOperationLog:
    """
    操作日志数据访问�?
    封装操作日志相关的所有数据库操作
    """
    
    def get_by_id(self, db: Session, log_id: int) -> Optional[OperationLog]:
        """
        根据ID获取操作日志
        
        参数:
            db: 数据库会�?
            log_id: 日志ID
        
        返回:
            操作日志对象，如果不存在则返回None
        """
        return db.query(OperationLog).filter(OperationLog.id == log_id).first()
    
    def get_multi(
        self, 
        db: Session, 
        query_params: OperationLogQuery
    ) -> tuple:
        """
        分页获取操作日志列表
        
        参数:
            db: 数据库会�?
            query_params: 查询参数
        
        返回:
            (操作日志列表, 总记录数)
        """
        query = db.query(OperationLog)
        
        # 用户名筛�?
        if query_params.username:
            query = query.filter(OperationLog.username.contains(query_params.username))
        
        # 操作类型筛�?
        if query_params.operation_type:
            query = query.filter(OperationLog.operation_type == query_params.operation_type)
        
        # 模块筛�?
        if query_params.module:
            query = query.filter(OperationLog.module == query_params.module)
        
        # 状态筛�?
        if query_params.status:
            query = query.filter(OperationLog.status == query_params.status)
        
        # 时间范围筛�?
        if query_params.start_time:
            query = query.filter(OperationLog.created_at >= query_params.start_time)
        if query_params.end_time:
            query = query.filter(OperationLog.created_at <= query_params.end_time)
        
        # 获取总记录数
        total = query.count()
        
        # 分页查询，按创建时间倒序
        logs = query.order_by(OperationLog.created_at.desc()).offset(
            (query_params.page - 1) * query_params.page_size
        ).limit(query_params.page_size).all()
        
        return logs, total
    
    def create(self, db: Session, obj_in: OperationLogCreate) -> OperationLog:
        """
        创建新操作日�?
        
        参数:
            db: 数据库会�?
            obj_in: 操作日志创建数据
        
        返回:
            创建的操作日志对�?
        """
        db_obj = OperationLog(
            operation_type=obj_in.operation_type,
            operation_name=obj_in.operation_name,
            operation_desc=obj_in.operation_desc,
            request_method=obj_in.request_method,
            request_url=obj_in.request_url,
            request_params=obj_in.request_params,
            request_ip=obj_in.request_ip,
            user_agent=obj_in.user_agent,
            response_status=obj_in.response_status,
            response_data=obj_in.response_data,
            user_id=obj_in.user_id,
            username=obj_in.username,
            module=obj_in.module,
            status=obj_in.status,
            error_message=obj_in.error_message,
            duration=obj_in.duration
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def create_simple(
        self,
        db: Session,
        operation_type: str,
        operation_name: str,
        operation_desc: str = None,
        request_method: str = None,
        request_url: str = None,
        request_params: str = None,
        request_ip: str = None,
        user_agent: str = None,
        response_status: int = None,
        response_data: str = None,
        user_id: int = None,
        username: str = None,
        module: str = None,
        status: str = "success",
        error_message: str = None,
        duration: int = None
    ) -> OperationLog:
        """
        简单创建操作日志的方法
        方便在代码中直接调用
        
        参数:
            db: 数据库会�?
            各种日志字段参数
        
        返回:
            创建的操作日志对�?
        """
        db_obj = OperationLog(
            operation_type=operation_type,
            operation_name=operation_name,
            operation_desc=operation_desc,
            request_method=request_method,
            request_url=request_url,
            request_params=request_params,
            request_ip=request_ip,
            user_agent=user_agent,
            response_status=response_status,
            response_data=response_data,
            user_id=user_id,
            username=username,
            module=module,
            status=status,
            error_message=error_message,
            duration=duration
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def remove(self, db: Session, log_id: int) -> Optional[OperationLog]:
        """
        删除操作日志
        
        参数:
            db: 数据库会�?
            log_id: 日志ID
        
        返回:
            删除的操作日志对象，如果不存在则返回None
        """
        obj = db.query(OperationLog).filter(OperationLog.id == log_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def batch_remove(self, db: Session, log_ids: List[int]) -> int:
        """
        批量删除操作日志
        
        参数:
            db: 数据库会�?
            log_ids: 日志ID列表
        
        返回:
            删除的记录数
        """
        count = db.query(OperationLog).filter(OperationLog.id.in_(log_ids)).delete(synchronize_session=False)
        db.commit()
        return count
    
    def cleanup_old_logs(self, db: Session, days: int = 30) -> int:
        """
        清理指定天数之前的旧日志
        
        参数:
            db: 数据库会�?
            days: 保留天数，默�?0�?
        
        返回:
            删除的记录数
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = db.query(OperationLog).filter(OperationLog.created_at < cutoff_date).delete(synchronize_session=False)
        db.commit()
        return count
    
    def get_statistics(self, db: Session, start_time: datetime = None, end_time: datetime = None) -> dict:
        """
        获取操作日志统计信息
        
        参数:
            db: 数据库会�?
            start_time: 开始时�?
            end_time: 结束时间
        
        返回:
            统计信息字典
        """
        query = db.query(OperationLog)
        
        if start_time:
            query = query.filter(OperationLog.created_at >= start_time)
        if end_time:
            query = query.filter(OperationLog.created_at <= end_time)
        
        # 总操作数
        total_count = query.count()
        
        # 成功操作�?
        success_count = query.filter(OperationLog.status == "success").count()
        
        # 失败操作�?
        failed_count = query.filter(OperationLog.status == "failed").count()
        
        # 按操作类型统�?
        from sqlalchemy import func
        type_stats = db.query(
            OperationLog.operation_type,
            func.count(OperationLog.id).label('count')
        ).filter(
            OperationLog.created_at >= start_time if start_time else True,
            OperationLog.created_at <= end_time if end_time else True
        ).group_by(OperationLog.operation_type).all()
        
        # 按模块统�?
        module_stats = db.query(
            OperationLog.module,
            func.count(OperationLog.id).label('count')
        ).filter(
            OperationLog.created_at >= start_time if start_time else True,
            OperationLog.created_at <= end_time if end_time else True,
            OperationLog.module.isnot(None)
        ).group_by(OperationLog.module).all()
        
        return {
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "type_stats": {stat.operation_type: stat.count for stat in type_stats},
            "module_stats": {stat.module: stat.count for stat in module_stats}
        }


# 创建操作日志CRUD实例
operation_log_crud = CRUDOperationLog()

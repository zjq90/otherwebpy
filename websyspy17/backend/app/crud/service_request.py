from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.service_request import ServiceRequest, ServiceProgress, ServiceStatus
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestUpdate, ServiceProgressCreate


def get_service_request_by_id(db: Session, request_id: int) -> Optional[ServiceRequest]:
    """
    根据 ID 获取服务请求
    
    Args:
        db: 数据库会话
        request_id: 服务请求 ID
        
    Returns:
        服务请求对象，不存在返回 None
    """
    return db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()


def get_service_requests(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    service_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[ServiceRequest]:
    """
    获取服务请求列表
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        user_id: 提交用户 ID 过滤
        assignee_id: 处理人 ID 过滤
        service_type: 服务类型过滤
        status: 状态过滤
        
    Returns:
        服务请求列表
    """
    query = db.query(ServiceRequest)
    
    if user_id is not None:
        query = query.filter(ServiceRequest.user_id == user_id)
    if assignee_id is not None:
        query = query.filter(ServiceRequest.assignee_id == assignee_id)
    if service_type is not None:
        query = query.filter(ServiceRequest.service_type == service_type)
    if status is not None:
        query = query.filter(ServiceRequest.status == status)
    
    return query.order_by(ServiceRequest.created_at.desc()).offset(skip).limit(limit).all()


def create_service_request(db: Session, request: ServiceRequestCreate, user_id: int) -> ServiceRequest:
    """
    创建新服务请求
    
    Args:
        db: 数据库会话
        request: 服务请求创建数据
        user_id: 提交用户 ID
        
    Returns:
        创建的服务请求对象
    """
    db_request = ServiceRequest(
        title=request.title,
        description=request.description,
        service_type=request.service_type,
        user_id=user_id,
        room_number=request.room_number,
        contact_name=request.contact_name,
        contact_phone=request.contact_phone,
        priority=request.priority,
        location=request.location,
        status=ServiceStatus.PENDING.value
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    create_service_progress(
        db=db,
        service_request_id=db_request.id,
        progress=ServiceProgressCreate(
            action="创建工单",
            description=f"业主提交了新的{request.service_type}请求"
        ),
        operator_id=user_id
    )
    
    return db_request


def update_service_request(
    db: Session, 
    request_id: int, 
    request: ServiceRequestUpdate,
    operator_id: int
) -> Optional[ServiceRequest]:
    """
    更新服务请求信息
    
    Args:
        db: 数据库会话
        request_id: 服务请求 ID
        request: 服务请求更新数据
        operator_id: 操作人 ID
        
    Returns:
        更新后的服务请求对象，不存在返回 None
    """
    db_request = get_service_request_by_id(db, request_id)
    if not db_request:
        return None
    
    old_status = db_request.status
    update_data = request.model_dump(exclude_unset=True)
    
    if "status" in update_data and update_data["status"] != old_status:
        new_status = update_data["status"]
        status_desc = {
            ServiceStatus.PENDING.value: "待处理",
            ServiceStatus.ASSIGNED.value: "已派单",
            ServiceStatus.PROCESSING.value: "处理中",
            ServiceStatus.COMPLETED.value: "已完成",
            ServiceStatus.CLOSED.value: "已关闭"
        }
        
        create_service_progress(
            db=db,
            service_request_id=request_id,
            progress=ServiceProgressCreate(
                action="状态变更",
                description=f"状态从 {status_desc.get(old_status, old_status)} 变更为 {status_desc.get(new_status, new_status)}"
            ),
            operator_id=operator_id,
            from_status=old_status,
            to_status=new_status
        )
        
        if new_status == ServiceStatus.COMPLETED.value:
            db_request.completed_at = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_request, key, value)
    
    db.commit()
    db.refresh(db_request)
    return db_request


def delete_service_request(db: Session, request_id: int) -> bool:
    """
    删除服务请求
    
    Args:
        db: 数据库会话
        request_id: 服务请求 ID
        
    Returns:
        是否删除成功
    """
    db_request = get_service_request_by_id(db, request_id)
    if not db_request:
        return False
    
    db.query(ServiceProgress).filter(ServiceProgress.service_request_id == request_id).delete()
    db.delete(db_request)
    db.commit()
    return True


def create_service_progress(
    db: Session, 
    service_request_id: int, 
    progress: ServiceProgressCreate,
    operator_id: int,
    from_status: Optional[str] = None,
    to_status: Optional[str] = None
) -> ServiceProgress:
    """
    创建服务进度记录
    
    Args:
        db: 数据库会话
        service_request_id: 服务请求 ID
        progress: 进度创建数据
        operator_id: 操作人 ID
        from_status: 变更前状态
        to_status: 变更后状态
        
    Returns:
        创建的进度记录对象
    """
    db_progress = ServiceProgress(
        service_request_id=service_request_id,
        action=progress.action,
        description=progress.description,
        operator_id=operator_id,
        from_status=from_status,
        to_status=to_status
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


def get_service_progresses(db: Session, service_request_id: int) -> List[ServiceProgress]:
    """
    获取服务请求的所有进度记录
    
    Args:
        db: 数据库会话
        service_request_id: 服务请求 ID
        
    Returns:
        进度记录列表
    """
    return db.query(ServiceProgress).filter(
        ServiceProgress.service_request_id == service_request_id
    ).order_by(ServiceProgress.created_at.asc()).all()

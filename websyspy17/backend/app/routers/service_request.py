from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.service_request import ServiceStatus, ServiceType
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestResponse,
    ServiceProgressCreate,
    ServiceProgressResponse
)
from app.crud import service_request as sr_crud
from app.routers.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/api/service-requests", tags=["服务请求"])


@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_service_request(
    request: ServiceRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建服务请求
    
    业主可以提交报修、投诉、咨询等服务请求
    
    - **title**: 请求标题
    - **description**: 请求描述
    - **service_type**: 服务类型：repair(报修), complaint(投诉), consult(咨询)
    - **room_number**: 房间号
    - **contact_name**: 联系人姓名
    - **contact_phone**: 联系电话
    - **priority**: 优先级：1-普通，2-紧急，3-非常紧急
    - **location**: 具体位置描述
    """
    return sr_crud.create_service_request(db=db, request=request, user_id=current_user.id)


@router.get("/", response_model=List[ServiceRequestResponse])
def read_service_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_type: Optional[str] = Query(None, description="服务类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取服务请求列表
    
    业主只能看到自己的请求，管理员和物业人员可以看到所有请求
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **service_type**: 服务类型过滤
    - **status**: 状态过滤
    """
    user_id = None if current_user.role in ["admin", "property"] else current_user.id
    requests = sr_crud.get_service_requests(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        service_type=service_type,
        status=status
    )
    return requests


@router.get("/my", response_model=List[ServiceRequestResponse])
def read_my_service_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_type: Optional[str] = Query(None, description="服务类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户提交的服务请求列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **service_type**: 服务类型过滤
    - **status**: 状态过滤
    """
    requests = sr_crud.get_service_requests(
        db=db,
        skip=skip,
        limit=limit,
        user_id=current_user.id,
        service_type=service_type,
        status=status
    )
    return requests


@router.get("/assigned", response_model=List[ServiceRequestResponse])
def read_assigned_service_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service_type: Optional[str] = Query(None, description="服务类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分配给当前用户的服务请求列表
    
    仅管理员和物业人员可以访问
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **service_type**: 服务类型过滤
    - **status**: 状态过滤
    """
    if current_user.role not in ["admin", "property"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    requests = sr_crud.get_service_requests(
        db=db,
        skip=skip,
        limit=limit,
        assignee_id=current_user.id,
        service_type=service_type,
        status=status
    )
    return requests


@router.get("/{request_id}", response_model=ServiceRequestResponse)
def read_service_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取服务请求详情
    
    业主只能查看自己的请求，管理员和物业人员可以查看所有请求
    
    - **request_id**: 服务请求 ID
    """
    db_request = sr_crud.get_service_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务请求不存在"
        )
    
    if current_user.role not in ["admin", "property"] and db_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return db_request


@router.put("/{request_id}", response_model=ServiceRequestResponse)
def update_service_request(
    request_id: int,
    request: ServiceRequestUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新服务请求
    
    业主只能更新自己的待处理请求，管理员和物业人员可以更新所有请求
    
    - **request_id**: 服务请求 ID
    - **request**: 更新数据
    """
    db_request = sr_crud.get_service_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务请求不存在"
        )
    
    if current_user.role not in ["admin", "property"]:
        if db_request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        if db_request.status != ServiceStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能更新待处理状态的请求"
            )
    
    updated_request = sr_crud.update_service_request(
        db=db,
        request_id=request_id,
        request=request,
        operator_id=current_user.id
    )
    return updated_request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_request(
    request_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除服务请求
    
    仅管理员可以删除
    
    - **request_id**: 服务请求 ID
    """
    success = sr_crud.delete_service_request(db, request_id=request_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务请求不存在"
        )


@router.get("/{request_id}/progress", response_model=List[ServiceProgressResponse])
def read_service_progress(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取服务请求的进度记录
    
    - **request_id**: 服务请求 ID
    """
    db_request = sr_crud.get_service_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务请求不存在"
        )
    
    if current_user.role not in ["admin", "property"] and db_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    progresses = sr_crud.get_service_progresses(db, service_request_id=request_id)
    return progresses


@router.post("/{request_id}/assign", response_model=ServiceRequestResponse)
def assign_service_request(
    request_id: int,
    assignee_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    分配服务请求
    
    管理员或物业人员可以将服务请求分配给指定人员
    
    - **request_id**: 服务请求 ID
    - **assignee_id**: 处理人 ID
    """
    db_request = sr_crud.get_service_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务请求不存在"
        )
    
    update_data = ServiceRequestUpdate(
        assignee_id=assignee_id,
        status=ServiceStatus.ASSIGNED.value
    )
    
    updated_request = sr_crud.update_service_request(
        db=db,
        request_id=request_id,
        request=update_data,
        operator_id=current_user.id
    )
    return updated_request


@router.post("/{request_id}/status", response_model=ServiceRequestResponse)
def update_service_status(
    request_id: int,
    new_status: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新服务请求状态
    
    - **request_id**: 服务请求 ID
    - **new_status**: 新状态
    """
    db_request = sr_crud.get_service_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务请求不存在"
        )
    
    if current_user.role not in ["admin", "property"]:
        if new_status != ServiceStatus.CLOSED.value or db_request.status != ServiceStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        if db_request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    update_data = ServiceRequestUpdate(status=new_status)
    updated_request = sr_crud.update_service_request(
        db=db,
        request_id=request_id,
        request=update_data,
        operator_id=current_user.id
    )
    return updated_request

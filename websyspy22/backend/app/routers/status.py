"""
状态管理API路由
提供会员账户冻结、解冻、注销等功能，状态变更时自动发送短信通知
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.member import Member, MemberStatus, StatusChangeLog
from app.schemas.member import (
    StatusChangeRequest,
    StatusChangeReason,
)
from app.schemas.common import (
    ApiResponse,
    SuccessResponse,
    PaginatedResponse,
)
from app.services.sms_service import sms_service

router = APIRouter(
    prefix="/api/status",
    tags=["状态管理"],
    responses={404: {"description": "未找到"}},
)


@router.post(
    "/{member_id}/freeze",
    response_model=ApiResponse[dict],
    summary="冻结会员账户",
    description="冻结指定会员的账户，状态变更后自动发送短信通知",
)
def freeze_member(
    member_id: int,
    request: StatusChangeReason,
    db: Session = Depends(get_db),
):
    """
    冻结会员账户
    - **member_id**: 会员ID
    - **request**: 包含变更原因和操作人
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 检查当前状态
    if member.status == MemberStatus.FROZEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该会员账户已处于冻结状态"
        )
    
    if member.status == MemberStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该会员账户已注销，无法冻结"
        )
    
    old_status = member.status
    
    # 更新会员状态
    member.status = MemberStatus.FROZEN
    member.status_reason = request.reason
    
    # 记录状态变更日志
    log = StatusChangeLog(
        member_id=member_id,
        old_status=old_status,
        new_status=MemberStatus.FROZEN,
        reason=request.reason,
        operator=request.operator
    )
    db.add(log)
    
    db.commit()
    db.refresh(member)
    
    # 发送短信通知
    sms_result = sms_service.send_status_change_notification(
        db,
        member.phone,
        member.id,
        old_status,
        MemberStatus.FROZEN,
        request.reason
    )
    
    return ApiResponse(
        code=200,
        message="会员账户已冻结",
        data={
            "member_id": member.id,
            "name": member.name,
            "old_status": old_status.value,
            "new_status": MemberStatus.FROZEN.value,
            "reason": request.reason,
            "sms_notification": sms_result
        }
    )


@router.post(
    "/{member_id}/unfreeze",
    response_model=ApiResponse[dict],
    summary="解冻会员账户",
    description="解冻已冻结的会员账户，状态变更后自动发送短信通知",
)
def unfreeze_member(
    member_id: int,
    request: StatusChangeReason,
    db: Session = Depends(get_db),
):
    """
    解冻会员账户
    - **member_id**: 会员ID
    - **request**: 包含变更原因和操作人
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 检查当前状态
    if member.status != MemberStatus.FROZEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该会员账户不处于冻结状态，无法解冻"
        )
    
    old_status = member.status
    
    # 更新会员状态
    member.status = MemberStatus.ACTIVE
    member.status_reason = request.reason
    
    # 记录状态变更日志
    log = StatusChangeLog(
        member_id=member_id,
        old_status=old_status,
        new_status=MemberStatus.ACTIVE,
        reason=request.reason,
        operator=request.operator
    )
    db.add(log)
    
    db.commit()
    db.refresh(member)
    
    # 发送短信通知
    sms_result = sms_service.send_status_change_notification(
        db,
        member.phone,
        member.id,
        old_status,
        MemberStatus.ACTIVE,
        request.reason
    )
    
    return ApiResponse(
        code=200,
        message="会员账户已解冻",
        data={
            "member_id": member.id,
            "name": member.name,
            "old_status": old_status.value,
            "new_status": MemberStatus.ACTIVE.value,
            "reason": request.reason,
            "sms_notification": sms_result
        }
    )


@router.post(
    "/{member_id}/cancel",
    response_model=ApiResponse[dict],
    summary="注销会员账户",
    description="注销指定会员的账户，状态变更后自动发送短信通知，注销后无法恢复",
)
def cancel_member(
    member_id: int,
    request: StatusChangeReason,
    db: Session = Depends(get_db),
):
    """
    注销会员账户
    - **member_id**: 会员ID
    - **request**: 包含变更原因和操作人
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 检查当前状态
    if member.status == MemberStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该会员账户已注销"
        )
    
    old_status = member.status
    
    # 更新会员状态
    member.status = MemberStatus.CANCELLED
    member.status_reason = request.reason
    
    # 记录状态变更日志
    log = StatusChangeLog(
        member_id=member_id,
        old_status=old_status,
        new_status=MemberStatus.CANCELLED,
        reason=request.reason,
        operator=request.operator
    )
    db.add(log)
    
    db.commit()
    db.refresh(member)
    
    # 发送短信通知
    sms_result = sms_service.send_status_change_notification(
        db,
        member.phone,
        member.id,
        old_status,
        MemberStatus.CANCELLED,
        request.reason
    )
    
    return ApiResponse(
        code=200,
        message="会员账户已注销",
        data={
            "member_id": member.id,
            "name": member.name,
            "old_status": old_status.value,
            "new_status": MemberStatus.CANCELLED.value,
            "reason": request.reason,
            "sms_notification": sms_result,
            "warning": "账户已注销，此操作不可逆"
        }
    )


@router.put(
    "/{member_id}/change",
    response_model=ApiResponse[dict],
    summary="变更会员状态",
    description="通用的会员状态变更接口，支持冻结、解冻、注销三种状态转换",
)
def change_member_status(
    member_id: int,
    request: StatusChangeRequest,
    db: Session = Depends(get_db),
):
    """
    变更会员状态
    - **member_id**: 会员ID
    - **request**: 包含新状态、变更原因和操作人
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 检查状态转换是否合法
    old_status = member.status
    new_status = request.new_status
    
    # 已注销的账户不能再变更状态
    if old_status == MemberStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已注销的账户无法变更状态"
        )
    
    # 检查目标状态与当前状态是否相同
    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"会员账户已处于{new_status.value}状态"
        )
    
    # 更新会员状态
    member.status = new_status
    member.status_reason = request.reason
    
    # 记录状态变更日志
    log = StatusChangeLog(
        member_id=member_id,
        old_status=old_status,
        new_status=new_status,
        reason=request.reason,
        operator=request.operator
    )
    db.add(log)
    
    db.commit()
    db.refresh(member)
    
    # 发送短信通知
    sms_result = sms_service.send_status_change_notification(
        db,
        member.phone,
        member.id,
        old_status,
        new_status,
        request.reason
    )
    
    return ApiResponse(
        code=200,
        message="会员状态变更成功",
        data={
            "member_id": member.id,
            "name": member.name,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "reason": request.reason,
            "operator": request.operator,
            "sms_notification": sms_result
        }
    )


@router.get(
    "/{member_id}/logs",
    response_model=ApiResponse[PaginatedResponse[dict]],
    summary="获取会员状态变更日志",
    description="获取指定会员的所有状态变更历史记录",
)
def get_member_status_logs(
    member_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """
    获取会员状态变更日志
    - **member_id**: 会员ID
    - **page**: 页码
    - **page_size**: 每页数量
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会员ID {member_id} 不存在"
        )
    
    # 查询日志
    query = db.query(StatusChangeLog).filter(StatusChangeLog.member_id == member_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    logs = query.order_by(StatusChangeLog.created_at.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    # 格式化日志数据
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "member_id": log.member_id,
            "old_status": log.old_status.value if log.old_status else None,
            "new_status": log.new_status.value,
            "reason": log.reason,
            "operator": log.operator,
            "created_at": log.created_at
        })
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=log_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/logs",
    response_model=ApiResponse[PaginatedResponse[dict]],
    summary="获取所有状态变更日志",
    description="获取系统中所有会员的状态变更历史记录",
)
def get_all_status_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    member_id: Optional[int] = Query(None, description="按会员ID筛选"),
    new_status: Optional[MemberStatus] = Query(None, description="按新状态筛选"),
    operator: Optional[str] = Query(None, description="按操作人筛选"),
    db: Session = Depends(get_db),
):
    """
    获取所有状态变更日志
    - **page**: 页码
    - **page_size**: 每页数量
    - **member_id**: 按会员ID筛选
    - **new_status**: 按新状态筛选
    - **operator**: 按操作人筛选
    """
    query = db.query(StatusChangeLog)
    
    # 应用筛选条件
    if member_id:
        query = query.filter(StatusChangeLog.member_id == member_id)
    if new_status:
        query = query.filter(StatusChangeLog.new_status == new_status)
    if operator:
        query = query.filter(StatusChangeLog.operator.contains(operator))
    
    total = query.count()
    offset = (page - 1) * page_size
    logs = query.order_by(StatusChangeLog.created_at.desc()).offset(offset).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    # 格式化日志数据
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "member_id": log.member_id,
            "old_status": log.old_status.value if log.old_status else None,
            "new_status": log.new_status.value,
            "reason": log.reason,
            "operator": log.operator,
            "created_at": log.created_at
        })
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=log_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )

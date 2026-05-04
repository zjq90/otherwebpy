"""
储物柜管理API路由模块
提供储物柜的增删改查、状态监控、分配与归还等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime, timedelta
import random
import string

from database import get_db
from models import Locker, LockerUsage, Member
from schemas import (
    LockerCreate, LockerUpdate, LockerResponse, 
    LockerAssignRequest, LockerReturnRequest, LockerUsageResponse,
    LockerStatus, ApiResponse, PaginatedResponse
)

# 创建路由实例
router = APIRouter(
    prefix="/api/lockers",
    tags=["储物柜管理"]
)


def generate_password(length: int = 6) -> str:
    """
    生成随机密码（用于密码锁）
    
    - **length**: 密码长度
    """
    return ''.join(random.choices(string.digits, k=length))


@router.get("/", response_model=PaginatedResponse, summary="获取储物柜列表")
def get_lockers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    locker_no: Optional[str] = Query(None, description="储物柜编号"),
    status: Optional[LockerStatus] = Query(None, description="储物柜状态"),
    locker_type: Optional[str] = Query(None, description="储物柜类型"),
    db: Session = Depends(get_db)
):
    """
    分页获取储物柜列表，支持多条件筛选
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **locker_no**: 按储物柜编号筛选
    - **status**: 按状态筛选（available: 空闲, occupied: 占用, maintenance: 故障）
    - **locker_type**: 按类型筛选
    """
    # 构建查询
    query = db.query(Locker)
    
    # 编号筛选
    if locker_no:
        query = query.filter(Locker.locker_no.contains(locker_no))
    
    # 状态筛选
    if status:
        query = query.filter(Locker.status == status.value)
    
    # 类型筛选
    if locker_type:
        query = query.filter(Locker.locker_type == locker_type)
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    lockers = query.order_by(Locker.locker_no.asc()).offset(offset).limit(page_size).all()
    
    # 转换为响应模型
    items = [LockerResponse.model_validate(locker).model_dump() for locker in lockers]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=ApiResponse, summary="获取储物柜统计")
def get_locker_stats(
    db: Session = Depends(get_db)
):
    """
    获取储物柜使用统计数据
    """
    # 总数
    total = db.query(Locker).count()
    
    # 各状态数量
    available = db.query(Locker).filter(Locker.status == LockerStatus.AVAILABLE.value).count()
    occupied = db.query(Locker).filter(Locker.status == LockerStatus.OCCUPIED.value).count()
    maintenance = db.query(Locker).filter(Locker.status == LockerStatus.MAINTENANCE.value).count()
    
    # 各类型数量
    small = db.query(Locker).filter(Locker.locker_type == "small").count()
    medium = db.query(Locker).filter(Locker.locker_type == "medium").count()
    large = db.query(Locker).filter(Locker.locker_type == "large").count()
    
    # 当前使用中的记录数
    active_usages = db.query(LockerUsage).filter(LockerUsage.status == "active").count()
    
    return ApiResponse(
        success=True,
        message="获取统计成功",
        data={
            "total": total,
            "by_status": {
                "available": available,
                "occupied": occupied,
                "maintenance": maintenance
            },
            "by_type": {
                "small": small,
                "medium": medium,
                "large": large
            },
            "active_usages": active_usages
        }
    )


@router.get("/{locker_id}", response_model=LockerResponse, summary="根据ID获取储物柜详情")
def get_locker(
    locker_id: int,
    db: Session = Depends(get_db)
):
    """
    根据储物柜ID获取详细信息
    
    - **locker_id**: 储物柜ID
    """
    locker = db.query(Locker).filter(Locker.id == locker_id).first()
    if not locker:
        raise HTTPException(status_code=404, detail=f"储物柜ID {locker_id} 不存在")
    return locker


@router.post("/", response_model=LockerResponse, summary="创建储物柜")
def create_locker(
    locker_data: LockerCreate,
    db: Session = Depends(get_db)
):
    """
    创建新储物柜
    
    - **locker_data**: 储物柜信息
    """
    # 检查储物柜编号是否已存在
    existing = db.query(Locker).filter(Locker.locker_no == locker_data.locker_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"储物柜编号 {locker_data.locker_no} 已存在")
    
    # 创建储物柜
    new_locker = Locker(
        locker_no=locker_data.locker_no,
        location=locker_data.location,
        locker_type=locker_data.locker_type,
        status=locker_data.status.value if isinstance(locker_data.status, LockerStatus) else locker_data.status,
        remarks=locker_data.remarks
    )
    
    db.add(new_locker)
    db.commit()
    db.refresh(new_locker)
    
    return new_locker


@router.put("/{locker_id}", response_model=LockerResponse, summary="更新储物柜信息")
def update_locker(
    locker_id: int,
    locker_data: LockerUpdate,
    db: Session = Depends(get_db)
):
    """
    更新储物柜信息
    
    - **locker_id**: 储物柜ID
    - **locker_data**: 需要更新的储物柜信息
    """
    locker = db.query(Locker).filter(Locker.id == locker_id).first()
    if not locker:
        raise HTTPException(status_code=404, detail=f"储物柜ID {locker_id} 不存在")
    
    # 更新字段
    update_data = locker_data.model_dump(exclude_unset=True)
    
    # 处理状态枚举
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value
        update_data["status_updated_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(locker, key, value)
    
    db.commit()
    db.refresh(locker)
    
    return locker


@router.post("/assign", response_model=ApiResponse, summary="分配储物柜")
def assign_locker(
    assign_data: LockerAssignRequest,
    db: Session = Depends(get_db)
):
    """
    分配储物柜给会员
    支持自动分配（不传locker_id）和手动选择（传入locker_id）
    
    - **member_id**: 会员ID
    - **locker_id**: 储物柜ID（可选，不传则自动分配）
    - **assign_type**: 分配方式（auto: 自动分配, manual: 手动选择）
    - **password**: 密码（可选，不传则自动生成）
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == assign_data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {assign_data.member_id} 不存在")
    
    # 检查会员是否已有使用中的储物柜
    active_usage = db.query(LockerUsage).filter(
        LockerUsage.member_id == assign_data.member_id,
        LockerUsage.status == "active"
    ).first()
    
    if active_usage:
        # 获取正在使用的储物柜信息
        used_locker = db.query(Locker).filter(Locker.id == active_usage.locker_id).first()
        return ApiResponse(
            success=False,
            message=f"会员 {member.name} 已有正在使用的储物柜: {used_locker.locker_no if used_locker else '未知'}",
            data={
                "member_id": assign_data.member_id,
                "active_locker_id": active_usage.locker_id,
                "active_locker_no": used_locker.locker_no if used_locker else ""
            }
        )
    
    locker = None
    password = assign_data.password or generate_password()
    
    if assign_data.locker_id:
        # 手动选择储物柜
        locker = db.query(Locker).filter(Locker.id == assign_data.locker_id).first()
        if not locker:
            raise HTTPException(status_code=404, detail=f"储物柜ID {assign_data.locker_id} 不存在")
        
        if locker.status != LockerStatus.AVAILABLE.value:
            raise HTTPException(
                status_code=400, 
                detail=f"储物柜 {locker.locker_no} 状态为 {locker.status}，无法分配"
            )
    else:
        # 自动分配：查找第一个可用的储物柜
        locker = db.query(Locker).filter(
            Locker.status == LockerStatus.AVAILABLE.value
        ).order_by(Locker.locker_no.asc()).first()
        
        if not locker:
            raise HTTPException(status_code=400, detail="没有可用的储物柜")
    
    # 更新储物柜状态
    locker.status = LockerStatus.OCCUPIED.value
    locker.status_updated_at = datetime.now()
    
    # 创建使用记录
    usage = LockerUsage(
        member_id=assign_data.member_id,
        locker_id=locker.id,
        assign_type=assign_data.assign_type,
        password=password,
        start_time=datetime.now(),
        status="active"
    )
    
    db.add(usage)
    db.commit()
    db.refresh(usage)
    db.refresh(locker)
    
    return ApiResponse(
        success=True,
        message=f"储物柜 {locker.locker_no} 分配成功",
        data={
            "usage_id": usage.id,
            "locker_id": locker.id,
            "locker_no": locker.locker_no,
            "locker_type": locker.locker_type,
            "location": locker.location,
            "password": password,
            "assign_type": assign_data.assign_type,
            "member_id": member.id,
            "member_name": member.name,
            "start_time": usage.start_time.isoformat()
        }
    )


@router.post("/return", response_model=ApiResponse, summary="归还储物柜")
def return_locker(
    return_data: LockerReturnRequest,
    db: Session = Depends(get_db)
):
    """
    归还储物柜
    
    - **member_id**: 会员ID
    - **locker_id**: 储物柜ID
    """
    # 查找使用记录
    usage = db.query(LockerUsage).filter(
        LockerUsage.member_id == return_data.member_id,
        LockerUsage.locker_id == return_data.locker_id,
        LockerUsage.status == "active"
    ).first()
    
    if not usage:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到会员 {return_data.member_id} 使用储物柜 {return_data.locker_id} 的记录"
        )
    
    # 更新使用记录
    usage.status = "returned"
    usage.end_time = datetime.now()
    
    # 更新储物柜状态
    locker = db.query(Locker).filter(Locker.id == return_data.locker_id).first()
    if locker:
        locker.status = LockerStatus.AVAILABLE.value
        locker.status_updated_at = datetime.now()
    
    db.commit()
    db.refresh(usage)
    
    # 获取会员信息
    member = db.query(Member).filter(Member.id == return_data.member_id).first()
    
    return ApiResponse(
        success=True,
        message=f"储物柜 {locker.locker_no if locker else ''} 归还成功",
        data={
            "usage_id": usage.id,
            "locker_id": locker.id if locker else None,
            "locker_no": locker.locker_no if locker else "",
            "member_id": return_data.member_id,
            "member_name": member.name if member else "",
            "start_time": usage.start_time.isoformat(),
            "end_time": usage.end_time.isoformat() if usage.end_time else None,
            "duration_minutes": int((usage.end_time - usage.start_time).total_seconds() / 60) if usage.end_time else 0
        }
    )


@router.get("/usage/member/{member_id}", response_model=ApiResponse, summary="获取会员的储物柜使用记录")
def get_member_usages(
    member_id: int,
    status: Optional[str] = Query(None, description="使用状态"),
    db: Session = Depends(get_db)
):
    """
    获取会员的储物柜使用记录
    
    - **member_id**: 会员ID
    - **status**: 使用状态筛选
    """
    # 检查会员是否存在
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"会员ID {member_id} 不存在")
    
    # 查询使用记录
    query = db.query(LockerUsage).filter(LockerUsage.member_id == member_id)
    
    if status:
        query = query.filter(LockerUsage.status == status)
    
    usages = query.order_by(LockerUsage.start_time.desc()).all()
    
    # 构建响应数据
    items = []
    for usage in usages:
        locker = db.query(Locker).filter(Locker.id == usage.locker_id).first()
        items.append({
            "usage_id": usage.id,
            "locker_id": usage.locker_id,
            "locker_no": locker.locker_no if locker else "",
            "locker_type": locker.locker_type if locker else "",
            "location": locker.location if locker else "",
            "assign_type": usage.assign_type,
            "password": usage.password,
            "start_time": usage.start_time.isoformat(),
            "end_time": usage.end_time.isoformat() if usage.end_time else None,
            "status": usage.status
        })
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "member_id": member_id,
            "member_name": member.name,
            "usages": items
        }
    )


@router.get("/usage/active", response_model=PaginatedResponse, summary="获取当前使用中的储物柜记录")
def get_active_usages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    分页获取当前使用中的储物柜记录
    
    - **page**: 页码
    - **page_size**: 每页数量
    """
    # 计算总数
    total = db.query(LockerUsage).filter(LockerUsage.status == "active").count()
    
    # 分页查询
    offset = (page - 1) * page_size
    usages = db.query(LockerUsage).filter(
        LockerUsage.status == "active"
    ).order_by(LockerUsage.start_time.desc()).offset(offset).limit(page_size).all()
    
    # 构建响应数据
    items = []
    for usage in usages:
        member = db.query(Member).filter(Member.id == usage.member_id).first()
        locker = db.query(Locker).filter(Locker.id == usage.locker_id).first()
        
        # 计算使用时长（分钟）
        duration = int((datetime.now() - usage.start_time).total_seconds() / 60)
        
        # 检查是否逾期（超过24小时算逾期）
        is_overdue = duration > 1440
        
        items.append({
            "usage_id": usage.id,
            "locker_id": usage.locker_id,
            "locker_no": locker.locker_no if locker else "",
            "locker_type": locker.locker_type if locker else "",
            "location": locker.location if locker else "",
            "member_id": usage.member_id,
            "member_name": member.name if member else "",
            "member_no": member.member_no if member else "",
            "assign_type": usage.assign_type,
            "password": usage.password,
            "start_time": usage.start_time.isoformat(),
            "duration_minutes": duration,
            "is_overdue": is_overdue
        })
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

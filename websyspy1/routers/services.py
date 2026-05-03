"""
服务管理路由模块
提供服务的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from database import get_db
from models import Service, User
from schemas import ServiceCreate, ServiceUpdate, ServiceResponse, ApiResponse
from routers.auth import get_current_admin_user
from config import PAGE_SIZE

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def get_services(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取服务列表接口（公开访问）
    支持分页、关键词搜索
    
    参数:
        page: 页码
        page_size: 每页数量
        keyword: 搜索关键词
        db: 数据库会话
    
    返回:
        ApiResponse: 服务列表数据
    """
    # 构建查询，只查询启用的服务
    query = db.query(Service).filter(Service.is_active == True)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Service.name.contains(keyword)) |
            (Service.description.contains(keyword))
        )
    
    # 计算总数
    total = query.count()
    
    # 分页，按排序权重降序，创建时间降序
    offset = (page - 1) * page_size
    services = query.order_by(
        Service.sort_order.desc(),
        Service.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    # 转换为响应模型
    service_responses = [ServiceResponse.from_orm(service) for service in services]
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": service_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/{service_id}", response_model=ApiResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    获取服务详情接口（公开访问）
    
    参数:
        service_id: 服务ID
        db: 数据库会话
    
    返回:
        ApiResponse: 服务详情
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在或已禁用"
        )
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"service": ServiceResponse.from_orm(service)}
    )


@router.post("/", response_model=ApiResponse)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    创建服务接口（管理员专用）
    
    参数:
        service_data: 服务数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 创建结果
    """
    new_service = Service(
        name=service_data.name,
        description=service_data.description,
        content=service_data.content,
        icon=service_data.icon,
        image_url=service_data.image_url,
        sort_order=service_data.sort_order or 0,
        is_active=True
    )
    
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    return ApiResponse(
        success=True,
        message="服务创建成功",
        data={"service": ServiceResponse.from_orm(new_service)}
    )


@router.put("/{service_id}", response_model=ApiResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    更新服务接口（管理员专用）
    
    参数:
        service_id: 服务ID
        service_data: 服务更新数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 更新结果
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 更新字段
    update_data = service_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)
    
    db.commit()
    db.refresh(service)
    
    return ApiResponse(
        success=True,
        message="服务更新成功",
        data={"service": ServiceResponse.from_orm(service)}
    )


@router.delete("/{service_id}", response_model=ApiResponse)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    删除服务接口（管理员专用）
    
    参数:
        service_id: 服务ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 删除结果
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    db.delete(service)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="服务已删除"
    )


@router.put("/{service_id}/toggle-active", response_model=ApiResponse)
def toggle_service_active(
    service_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    切换服务启用状态接口（管理员专用）
    
    参数:
        service_id: 服务ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    service.is_active = not service.is_active
    db.commit()
    db.refresh(service)
    
    return ApiResponse(
        success=True,
        message=f"服务已{'启用' if service.is_active else '禁用'}",
        data={"service": ServiceResponse.from_orm(service)}
    )

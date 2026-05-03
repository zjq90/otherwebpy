"""
案例管理路由模块
提供案例的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from database import get_db
from models import Case, User
from schemas import CaseCreate, CaseUpdate, CaseResponse, ApiResponse
from routers.auth import get_current_admin_user
from config import PAGE_SIZE

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def get_cases(
    page: int = 1,
    page_size: int = PAGE_SIZE,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取案例列表接口（公开访问）
    支持分页、分类过滤、关键词搜索、推荐过滤
    
    参数:
        page: 页码
        page_size: 每页数量
        category: 案例分类
        keyword: 搜索关键词
        featured: 是否推荐
        db: 数据库会话
    
    返回:
        ApiResponse: 案例列表数据
    """
    # 构建查询，只查询启用的案例
    query = db.query(Case).filter(Case.is_active == True)
    
    # 分类过滤
    if category:
        query = query.filter(Case.category == category)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Case.title.contains(keyword)) |
            (Case.description.contains(keyword))
        )
    
    # 推荐过滤
    if featured is not None:
        query = query.filter(Case.is_featured == featured)
    
    # 计算总数
    total = query.count()
    
    # 分页，按排序权重降序，创建时间降序
    offset = (page - 1) * page_size
    cases = query.order_by(
        Case.sort_order.desc(),
        Case.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    
    # 转换为响应模型
    case_responses = [CaseResponse.from_orm(case) for case in cases]
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={
            "items": case_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )


@router.get("/{case_id}", response_model=ApiResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """
    获取案例详情接口（公开访问）
    
    参数:
        case_id: 案例ID
        db: 数据库会话
    
    返回:
        ApiResponse: 案例详情
    """
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.is_active == True
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案例不存在或已禁用"
        )
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"case": CaseResponse.from_orm(case)}
    )


@router.post("/", response_model=ApiResponse)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    创建案例接口（管理员专用）
    
    参数:
        case_data: 案例数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 创建结果
    """
    new_case = Case(
        title=case_data.title,
        description=case_data.description,
        content=case_data.content,
        image_url=case_data.image_url,
        client_name=case_data.client_name,
        category=case_data.category,
        is_featured=case_data.is_featured or False,
        sort_order=case_data.sort_order or 0,
        is_active=True
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    return ApiResponse(
        success=True,
        message="案例创建成功",
        data={"case": CaseResponse.from_orm(new_case)}
    )


@router.put("/{case_id}", response_model=ApiResponse)
def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    更新案例接口（管理员专用）
    
    参数:
        case_id: 案例ID
        case_data: 案例更新数据
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 更新结果
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案例不存在"
        )
    
    # 更新字段
    update_data = case_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)
    
    db.commit()
    db.refresh(case)
    
    return ApiResponse(
        success=True,
        message="案例更新成功",
        data={"case": CaseResponse.from_orm(case)}
    )


@router.delete("/{case_id}", response_model=ApiResponse)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    删除案例接口（管理员专用）
    
    参数:
        case_id: 案例ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 删除结果
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案例不存在"
        )
    
    db.delete(case)
    db.commit()
    
    return ApiResponse(
        success=True,
        message="案例已删除"
    )


@router.put("/{case_id}/toggle-active", response_model=ApiResponse)
def toggle_case_active(
    case_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    切换案例启用状态接口（管理员专用）
    
    参数:
        case_id: 案例ID
        db: 数据库会话
        current_admin: 当前管理员用户
    
    返回:
        ApiResponse: 操作结果
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案例不存在"
        )
    
    case.is_active = not case.is_active
    db.commit()
    db.refresh(case)
    
    return ApiResponse(
        success=True,
        message=f"案例已{'启用' if case.is_active else '禁用'}",
        data={"case": CaseResponse.from_orm(case)}
    )

"""
作物管理路由
处理作物的增删改查操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from database import get_db
from models import Crop, User
from schemas import (
    CropCreate, CropUpdate, CropResponse, 
    APIResponse, PaginatedResponse
)
from routers.auth import get_current_active_user
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由
router = APIRouter(prefix="/crops", tags=["作物管理"])


@router.get("", response_model=PaginatedResponse)
async def get_crops(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取作物列表
    支持分页、搜索和筛选
    """
    # 构建查询
    query = select(Crop)
    
    # 搜索关键词
    if keyword:
        query = query.where(
            or_(
                Crop.name.contains(keyword),
                Crop.variety.contains(keyword),
                Crop.description.contains(keyword)
            )
        )
    
    # 分类筛选
    if category:
        query = query.where(Crop.category == category)
    
    # 启用状态筛选
    if is_active is not None:
        query = query.where(Crop.is_active == is_active)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Crop.created_at.desc())
    
    result = await db.execute(query)
    crops = result.scalars().all()
    
    # 转换为响应模型
    crop_responses = [CropResponse.model_validate(crop) for crop in crops]
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        success=True,
        message="获取成功",
        data=crop_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/all", response_model=APIResponse)
async def get_all_crops(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有启用的作物
    用于下拉选择等场景
    """
    query = select(Crop).where(Crop.is_active == True).order_by(Crop.name)
    result = await db.execute(query)
    crops = result.scalars().all()
    
    crop_responses = [CropResponse.model_validate(crop) for crop in crops]
    
    return APIResponse(
        success=True,
        message="获取成功",
        data={"crops": [crop.model_dump() for crop in crop_responses]}
    )


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个作物详情
    """
    query = select(Crop).where(Crop.id == crop_id)
    result = await db.execute(query)
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作物不存在"
        )
    
    return crop


@router.post("", response_model=APIResponse)
async def create_crop(
    crop_data: CropCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新作物
    """
    # 检查名称是否已存在
    query = select(Crop).where(Crop.name == crop_data.name)
    result = await db.execute(query)
    existing_crop = result.scalar_one_or_none()
    
    if existing_crop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="作物名称已存在"
        )
    
    # 创建新作物
    new_crop = Crop(**crop_data.model_dump())
    db.add(new_crop)
    await db.commit()
    await db.refresh(new_crop)
    
    return APIResponse(
        success=True,
        message="创建成功",
        data={"crop_id": new_crop.id}
    )


@router.put("/{crop_id}", response_model=APIResponse)
async def update_crop(
    crop_id: int,
    crop_data: CropUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新作物信息
    """
    query = select(Crop).where(Crop.id == crop_id)
    result = await db.execute(query)
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作物不存在"
        )
    
    # 检查名称是否与其他作物重复
    update_data = crop_data.model_dump(exclude_unset=True)
    if "name" in update_data:
        name_query = select(Crop).where(
            Crop.name == update_data["name"],
            Crop.id != crop_id
        )
        name_result = await db.execute(name_query)
        if name_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="作物名称已存在"
            )
    
    # 更新字段
    for key, value in update_data.items():
        setattr(crop, key, value)
    
    await db.commit()
    
    return APIResponse(
        success=True,
        message="更新成功"
    )


@router.delete("/{crop_id}", response_model=APIResponse)
async def delete_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除作物（逻辑删除）
    """
    query = select(Crop).where(Crop.id == crop_id)
    result = await db.execute(query)
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作物不存在"
        )
    
    # 逻辑删除
    crop.is_active = False
    await db.commit()
    
    return APIResponse(
        success=True,
        message="删除成功"
    )


@router.post("/{crop_id}/restore", response_model=APIResponse)
async def restore_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    恢复已删除的作物
    """
    query = select(Crop).where(Crop.id == crop_id)
    result = await db.execute(query)
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作物不存在"
        )
    
    crop.is_active = True
    await db.commit()
    
    return APIResponse(
        success=True,
        message="恢复成功"
    )

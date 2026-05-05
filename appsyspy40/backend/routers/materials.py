"""
原材料管理路由
包含原材料的增删改查功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_current_user, require_admin
from models.models import User, Material, MaterialInspection
from schemas.schemas import (
    MaterialCreate, MaterialUpdate, MaterialResponse,
    MaterialInspectionCreate, MaterialInspectionResponse,
    ApiResponse, PaginatedResponse
)


router = APIRouter(prefix="/api/materials", tags=["原材料管理"])


@router.post("", response_model=ApiResponse, summary="添加原材料")
async def create_material(
    material_data: MaterialCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    添加新原材料
    需要管理员权限
    """
    # 检查原材料编码是否已存在
    existing_material = db.query(Material).filter(
        Material.material_code == material_data.material_code
    ).first()
    if existing_material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原材料编码已存在"
        )
    
    # 创建新原材料
    new_material = Material(**material_data.model_dump())
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    
    return ApiResponse(
        code=200,
        message="添加成功",
        data={"material": MaterialResponse.model_validate(new_material).model_dump()}
    )


@router.get("", response_model=PaginatedResponse, summary="获取原材料列表")
async def get_materials(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    material_type: Optional[str] = Query(None, description="原材料类型"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分页获取原材料列表
    支持按类型和关键词筛选
    """
    query = db.query(Material)
    
    # 按类型筛选
    if material_type:
        query = query.filter(Material.material_type == material_type)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Material.material_name.contains(keyword)) |
            (Material.material_code.contains(keyword))
        )
    
    # 计算总数
    total = query.count()
    
    # 分页
    materials = query.order_by(Material.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    material_list = [MaterialResponse.model_validate(m).model_dump() for m in materials]
    
    return PaginatedResponse(
        code=200,
        message="success",
        data={"items": material_list},
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{material_id}", response_model=ApiResponse, summary="获取原材料详情")
async def get_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取原材料详情
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    
    return ApiResponse(
        code=200,
        message="success",
        data={"material": MaterialResponse.model_validate(material).model_dump()}
    )


@router.put("/{material_id}", response_model=ApiResponse, summary="更新原材料")
async def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新原材料信息
    需要管理员权限
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    
    # 更新字段
    update_data = material_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(material, key, value)
    
    db.commit()
    db.refresh(material)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"material": MaterialResponse.model_validate(material).model_dump()}
    )


@router.delete("/{material_id}", response_model=ApiResponse, summary="删除原材料")
async def delete_material(
    material_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    删除原材料（软删除，标记为不激活）
    需要管理员权限
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="原材料不存在"
        )
    
    # 检查是否有关联的检验记录
    inspections = db.query(MaterialInspection).filter(
        MaterialInspection.material_id == material_id
    ).first()
    if inspections:
        # 软删除
        material.is_active = False
        db.commit()
        return ApiResponse(
            code=200,
            message="原材料已标记为不激活（存在关联记录，无法物理删除）"
        )
    
    # 物理删除
    db.delete(material)
    db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功"
    )
